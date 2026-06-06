#!/usr/bin/env python3
"""Scrape subtitles from public videos on a YouTube channel into Markdown files."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import time
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    IpBlocked,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


DEFAULT_CHANNEL_URL = "https://www.youtube.com/@chatwithtraderspodcast/videos"
NODE_RUNTIME = shutil.which("node")
YT_DLP_JS_RUNTIMES = {"node": {"path": NODE_RUNTIME}} if NODE_RUNTIME else {"deno": {}}


@dataclass(frozen=True)
class TranscriptResult:
    language: str
    source: str
    text: str


def parse_cookies_from_browser(value: str | None) -> tuple[str, str | None, str | None, str | None] | None:
    """Parse yt-dlp's BROWSER[+KEYRING][:PROFILE][::CONTAINER] cookie syntax."""
    if not value:
        return None
    match = re.fullmatch(
        r"(?P<name>[^+:]+)(?:\s*\+\s*(?P<keyring>[^:]+))?(?:\s*:\s*(?!:)(?P<profile>.+?))?(?:\s*::\s*(?P<container>.+))?",
        value,
    )
    if not match:
        raise ValueError(f"Invalid --cookies-from-browser value: {value}")
    browser_name, keyring, profile, container = match.group("name", "keyring", "profile", "container")
    return (browser_name.lower(), profile, keyring.upper() if keyring else None, container)


def extract_video_id(video_url: str) -> str:
    """Extract a YouTube video ID from a watch, short, or youtu.be URL."""
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a YouTube video ID from: {video_url}")


def sanitize_filename(value: str, max_length: int = 90) -> str:
    """Return a filesystem-safe filename stem."""
    value = html.unescape(value or "untitled")
    value = re.sub(r"[^\w\s.-]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return (value[:max_length].strip(" .") or "untitled")


def markdown_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return text.replace("\\", "\\\\").replace('"', '\\"')


def format_duration(seconds: Any) -> str:
    if not isinstance(seconds, (int, float)):
        return ""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def get_channel_videos(channel_url: str) -> list[dict[str, Any]]:
    """Use yt-dlp to extract public channel videos without downloading media."""
    ydl_opts = {
        "extract_flat": "in_playlist",
        "ignoreerrors": True,
        "js_runtimes": YT_DLP_JS_RUNTIMES,
        "quiet": True,
        "skip_download": True,
        "socket_timeout": 30,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        channel_info = ydl.extract_info(channel_url, download=False)

    entries = channel_info.get("entries") or []
    videos: list[dict[str, Any]] = []
    for entry in entries:
        if not entry:
            continue
        video_id = entry.get("id")
        if not video_id:
            continue
        videos.append(
            {
                "id": video_id,
                "title": entry.get("title") or "Untitled",
                "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                "duration": entry.get("duration"),
                "upload_date": entry.get("upload_date"),
            }
        )
    return videos


def transcript_items_from_api(video_id: str, languages: list[str]) -> tuple[str, list[dict[str, Any]]]:
    """Fetch transcript entries while supporting old and new package APIs."""
    api = YouTubeTranscriptApi()
    if hasattr(api, "fetch"):
        fetched = api.fetch(video_id, languages=languages)
        language = getattr(fetched, "language_code", None) or languages[0]
        snippets = getattr(fetched, "snippets", fetched)
        items = []
        for item in snippets:
            if isinstance(item, dict):
                items.append(
                    {
                        "text": item.get("text", ""),
                        "start": item.get("start"),
                        "duration": item.get("duration"),
                    }
                )
            else:
                items.append(
                    {
                        "text": getattr(item, "text", ""),
                        "start": getattr(item, "start", None),
                        "duration": getattr(item, "duration", None),
                    }
                )
        return language, items

    items = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    return languages[0], items


def get_transcript_via_api(video_id: str, languages: list[str]) -> TranscriptResult:
    language, items = transcript_items_from_api(video_id, languages)
    text = transcript_items_to_text(items)
    if not text:
        raise NoTranscriptFound(video_id, languages, {})
    return TranscriptResult(language=language, source="youtube-transcript-api", text=text)


def ytdlp_options(
    allow_remote_components: bool,
    cookies_file: str | None,
    cookies_from_browser: str | None,
) -> dict[str, Any]:
    ydl_opts = {
        "extractor_retries": 1,
        "ignoreerrors": True,
        "js_runtimes": YT_DLP_JS_RUNTIMES,
        "noplaylist": True,
        "quiet": True,
        "retries": 1,
        "skip_download": True,
        "socket_timeout": 20,
        "writesubtitles": True,
        "writeautomaticsub": True,
    }
    if allow_remote_components:
        ydl_opts["remote_components"] = ["ejs:github"]
    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file
    if cookies_from_browser:
        ydl_opts["cookiesfrombrowser"] = parse_cookies_from_browser(cookies_from_browser)
    return ydl_opts


def get_video_info(
    video_url: str,
    allow_remote_components: bool,
    cookies_file: str | None,
    cookies_from_browser: str | None,
) -> dict[str, Any]:
    ydl_opts = ytdlp_options(
        allow_remote_components=allow_remote_components,
        cookies_file=cookies_file,
        cookies_from_browser=cookies_from_browser,
    )
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(video_url, download=False) or {}


def subtitle_candidates(video_info: dict[str, Any], languages: Iterable[str]) -> list[tuple[str, str, str]]:
    preferred_exts = {"json3", "srv3", "vtt", "ttml"}
    candidates: list[tuple[str, str, str]] = []
    for subtitle_kind in ("subtitles", "automatic_captions"):
        subtitles = video_info.get(subtitle_kind) or {}
        for language in languages:
            for item in subtitles.get(language, []):
                ext = item.get("ext")
                url = item.get("url")
                if ext in preferred_exts and url:
                    candidates.append((language, ext, url))
    order = ["json3", "vtt", "ttml", "srv3"]
    candidates.sort(key=lambda row: order.index(row[1]) if row[1] in order else 9)
    return candidates


def fetch_url(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_url_with_ytdlp(ydl: yt_dlp.YoutubeDL, url: str) -> str:
    with ydl.urlopen(url) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_json3(data: str) -> list[dict[str, Any]]:
    payload = json.loads(data)
    items: list[dict[str, Any]] = []
    for event in payload.get("events", []):
        segments = event.get("segs") or []
        text = "".join(segment.get("utf8", "") for segment in segments).strip()
        if text:
            items.append(
                {
                    "text": text,
                    "start": event.get("tStartMs", 0) / 1000,
                    "duration": event.get("dDurationMs", 0) / 1000,
                }
            )
    return items


def parse_vtt(data: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current: list[str] = []
    for raw_line in data.splitlines():
        line = raw_line.strip()
        if not line or line == "WEBVTT" or "-->" in line or line.isdigit():
            if current:
                items.append({"text": " ".join(current)})
                current = []
            continue
        current.append(re.sub(r"<[^>]+>", "", html.unescape(line)))
    if current:
        items.append({"text": " ".join(current)})
    return items


def parse_ttml(data: str) -> list[dict[str, Any]]:
    text = re.sub(r"<br\s*/?>", " ", data)
    matches = re.findall(r"<p\b[^>]*>(.*?)</p>", text, flags=re.DOTALL | re.IGNORECASE)
    return [{"text": re.sub(r"<[^>]+>", "", html.unescape(match)).strip()} for match in matches]


def parse_srv3(data: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    root = ET.fromstring(data)
    for text_node in root.iter("text"):
        text = "".join(text_node.itertext()).strip()
        if text:
            items.append({"text": text})
    return items


def get_transcript_via_ytdlp(
    video_url: str,
    languages: list[str],
    allow_remote_components: bool = False,
    cookies_file: str | None = None,
    cookies_from_browser: str | None = None,
) -> TranscriptResult:
    ydl_opts = ytdlp_options(
        allow_remote_components=allow_remote_components,
        cookies_file=cookies_file,
        cookies_from_browser=cookies_from_browser,
    )
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(video_url, download=False) or {}
        for language, ext, url in subtitle_candidates(video_info, languages):
            data = fetch_url_with_ytdlp(ydl, url)
            if ext == "json3":
                items = parse_json3(data)
            elif ext == "vtt":
                items = parse_vtt(data)
            elif ext == "ttml":
                items = parse_ttml(data)
            else:
                items = parse_srv3(data)
            text = transcript_items_to_text(items)
            if text:
                return TranscriptResult(language=language, source=f"yt-dlp-{ext}", text=text)
        raise NoTranscriptFound(video_info.get("id", video_url), languages, {})


def transcript_items_to_text(items: Iterable[dict[str, Any]]) -> str:
    lines: list[str] = []
    previous = ""
    for item in items:
        text = html.unescape(str(item.get("text", ""))).replace("\n", " ").strip()
        text = re.sub(r"\s+", " ", text)
        if text and text != previous:
            lines.append(text)
            previous = text
    return "\n".join(lines)


def write_markdown(
    output_path: Path,
    video: dict[str, Any],
    transcript: TranscriptResult,
) -> None:
    title = video.get("title") or "Untitled"
    video_id = video.get("id") or ""
    url = video.get("url") or f"https://www.youtube.com/watch?v={video_id}"
    duration = format_duration(video.get("duration"))
    upload_date = video.get("upload_date") or ""

    with output_path.open("w", encoding="utf-8") as file:
        file.write("---\n")
        file.write(f'title: "{markdown_escape(title)}"\n')
        file.write(f'video_id: "{markdown_escape(video_id)}"\n')
        file.write(f'url: "{markdown_escape(url)}"\n')
        if upload_date:
            file.write(f'upload_date: "{markdown_escape(upload_date)}"\n')
        if duration:
            file.write(f'duration: "{markdown_escape(duration)}"\n')
        file.write(f'caption_language: "{markdown_escape(transcript.language)}"\n')
        file.write(f'caption_source: "{markdown_escape(transcript.source)}"\n')
        file.write("---\n\n")
        file.write(f"# {title}\n\n")
        file.write(f"[Watch on YouTube]({url})\n\n")
        file.write("## Transcript\n\n")
        file.write(transcript.text.strip())
        file.write("\n")


def write_index(index_path: Path, rows: list[dict[str, Any]]) -> None:
    with index_path.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "status",
            "video_id",
            "title",
            "url",
            "output_file",
            "caption_language",
            "caption_source",
            "reason",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rebuild_index(output_dir: Path, videos: list[dict[str, Any]]) -> None:
    transcripts: dict[str, Path] = {}
    for path in output_dir.glob("*.md"):
        match = re.search(r'^video_id: "([^"]+)"$', path.read_text(encoding="utf-8"), flags=re.MULTILINE)
        if match:
            transcripts[match.group(1)] = path

    rows = []
    for video in videos:
        video_id = video["id"]
        output_path = transcripts.get(video_id)
        rows.append(
            {
                "status": "saved" if output_path else "missing",
                "video_id": video_id,
                "title": video.get("title") or "Untitled",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "output_file": str(output_path) if output_path else "",
                "caption_language": "",
                "caption_source": "",
                "reason": "" if output_path else "not_fetched_or_no_public_english_caption",
            }
        )
    write_index(output_dir / "transcript_index.csv", rows)


def scrape_channel(
    channel_url: str,
    video_url: str | None,
    output_dir: Path,
    languages: list[str],
    sleep_seconds: float,
    overwrite: bool,
    method: str,
    start_index: int,
    limit: int | None,
    index_only: bool,
    allow_remote_components: bool,
    cookies_file: str | None,
    cookies_from_browser: str | None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if video_url:
        video_id = extract_video_id(video_url)
        videos = [
            {
                "id": video_id,
                "title": f"YouTube video {video_id}",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": None,
                "upload_date": None,
            }
        ]
        print(f"Using single video: {videos[0]['url']}")
    else:
        print(f"Fetching video list from {channel_url}")
        videos = get_channel_videos(channel_url)
        videos = videos[start_index - 1 :]
        if limit is not None:
            videos = videos[:limit]
        print(f"Found {len(videos)} public video entries.")

    if index_only:
        rebuild_index(output_dir, videos)
        print(f"Rebuilt index: {(output_dir / 'transcript_index.csv').resolve()}")
        return

    rows: list[dict[str, Any]] = []
    success_count = 0
    skipped_count = 0
    error_count = 0

    for index, video in enumerate(videos, start=start_index):
        video_id = video["id"]
        title = video.get("title") or "Untitled"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video["url"] = video_url
        filename = f"{index:04d}_{video_id}_{sanitize_filename(title)}.md"
        output_path = output_dir / filename

        if output_path.exists() and not overwrite:
            print(f"[{index}/{len(videos)}] exists: {title}")
            skipped_count += 1
            rows.append(
                {
                    "status": "exists",
                    "video_id": video_id,
                    "title": title,
                    "url": video_url,
                    "output_file": str(output_path),
                    "caption_language": "",
                    "caption_source": "",
                    "reason": "",
                }
            )
            continue

        print(f"[{index}/{len(videos)}] subtitles: {title}")
        try:
            if method == "api-only":
                getters = ((get_transcript_via_api, (video_id, languages)),)
            elif method == "ytdlp-only":
                getters = ((
                    get_transcript_via_ytdlp,
                    (video_url, languages, allow_remote_components, cookies_file, cookies_from_browser),
                ),)
            elif method == "api-first":
                getters = (
                    (get_transcript_via_api, (video_id, languages)),
                    (get_transcript_via_ytdlp, (video_url, languages, allow_remote_components, cookies_file, cookies_from_browser)),
                )
            else:
                getters = (
                    (get_transcript_via_ytdlp, (video_url, languages, allow_remote_components, cookies_file, cookies_from_browser)),
                    (get_transcript_via_api, (video_id, languages)),
                )

            errors: list[str] = []
            transcript = None
            for getter, params in getters:
                try:
                    transcript = getter(*params)
                    break
                except IpBlocked:
                    raise
                except Exception as exc:  # noqa: BLE001 - fall back across public caption methods.
                    errors.append(f"{getter.__name__}: {exc.__class__.__name__}")

            if transcript is None:
                raise NoTranscriptFound(video_id, languages, {"errors": errors})

            write_markdown(output_path, video, transcript)
            success_count += 1
            rows.append(
                {
                    "status": "saved",
                    "video_id": video_id,
                    "title": title,
                    "url": video_url,
                    "output_file": str(output_path),
                    "caption_language": transcript.language,
                    "caption_source": transcript.source,
                    "reason": "",
                }
            )
        except IpBlocked:
            print("  rate limited: stopping batch so it can be resumed later")
            break
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as exc:
            print(f"  unavailable: {exc}")
            error_count += 1
            rows.append(
                {
                    "status": "unavailable",
                    "video_id": video_id,
                    "title": title,
                    "url": video_url,
                    "output_file": "",
                    "caption_language": "",
                    "caption_source": "",
                    "reason": exc.__class__.__name__,
                }
            )
        except Exception as exc:  # noqa: BLE001 - capture scrape failures in the index.
            print(f"  error: {exc}")
            error_count += 1
            rows.append(
                {
                    "status": "error",
                    "video_id": video_id,
                    "title": title,
                    "url": video_url,
                    "output_file": "",
                    "caption_language": "",
                    "caption_source": "",
                    "reason": str(exc),
                }
            )

        write_index(output_dir / "transcript_index.csv", rows)
        time.sleep(sleep_seconds)

    write_index(output_dir / "transcript_index.csv", rows)
    print("\nDone.")
    print(f"Saved: {success_count}")
    print(f"Already existed: {skipped_count}")
    print(f"Unavailable/errors: {error_count}")
    print(f"Output folder: {output_dir.resolve()}")
    print(f"Index: {(output_dir / 'transcript_index.csv').resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel-url", default=DEFAULT_CHANNEL_URL)
    parser.add_argument("--video-url", default=None, help="Scrape one video instead of a channel.")
    parser.add_argument("--output-dir", default="chat_with_traders_transcripts")
    parser.add_argument("--languages", nargs="+", default=["en", "en-US", "en-GB"])
    parser.add_argument("--sleep-seconds", type=float, default=1.5)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--index-only", action="store_true", help="Rebuild the transcript index without fetching captions.")
    parser.add_argument(
        "--allow-remote-components",
        action="store_true",
        help="Allow yt-dlp to download the remote ejs:github challenge solver when YouTube requires it.",
    )
    parser.add_argument("--cookies-file", default=None, help="Netscape-format cookie file for yt-dlp.")
    parser.add_argument(
        "--cookies-from-browser",
        default=None,
        help="Browser cookie source for yt-dlp, e.g. chrome, safari, firefox:ProfileName.",
    )
    parser.add_argument(
        "--method",
        choices=["ytdlp-first", "api-first", "ytdlp-only", "api-only"],
        default="ytdlp-first",
        help="Which public-caption retrieval method to try first.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scrape_channel(
        channel_url=args.channel_url,
        video_url=args.video_url,
        output_dir=Path(args.output_dir),
        languages=args.languages,
        sleep_seconds=args.sleep_seconds,
        overwrite=args.overwrite,
        method=args.method,
        start_index=args.start_index,
        limit=args.limit,
        index_only=args.index_only,
        allow_remote_components=args.allow_remote_components,
        cookies_file=args.cookies_file,
        cookies_from_browser=args.cookies_from_browser,
    )


if __name__ == "__main__":
    main()
