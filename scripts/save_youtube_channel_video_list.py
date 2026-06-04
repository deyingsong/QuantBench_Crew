#!/usr/bin/env python3
"""Save the public video list for a YouTube channel without scraping subtitles."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from scrape_youtube_channel_subtitles import DEFAULT_CHANNEL_URL, format_duration, get_channel_videos


def video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def write_csv(path: Path, videos: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["index", "video_id", "title", "url", "duration", "upload_date"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for index, video in enumerate(videos, start=1):
            video_id = video.get("id") or ""
            writer.writerow(
                {
                    "index": index,
                    "video_id": video_id,
                    "title": video.get("title") or "",
                    "url": video_url(video_id),
                    "duration": format_duration(video.get("duration")),
                    "upload_date": video.get("upload_date") or "",
                }
            )


def write_markdown(path: Path, videos: list[dict[str, Any]], channel_url: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write("# Chat With Traders Podcast Videos\n\n")
        file.write(f"Channel: <{channel_url}>\n\n")
        file.write(f"Total public videos: {len(videos)}\n\n")
        for index, video in enumerate(videos, start=1):
            video_id = video.get("id") or ""
            title = video.get("title") or "Untitled"
            duration = format_duration(video.get("duration"))
            suffix = f" ({duration})" if duration else ""
            file.write(f"{index}. [{title}]({video_url(video_id)}){suffix}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel-url", default=DEFAULT_CHANNEL_URL)
    parser.add_argument("--csv", default="chat_with_traders_video_list.csv")
    parser.add_argument("--markdown", default="chat_with_traders_video_list.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Fetching public video list from {args.channel_url}")
    videos = get_channel_videos(args.channel_url)
    write_csv(Path(args.csv), videos)
    write_markdown(Path(args.markdown), videos, args.channel_url)
    print(f"Saved {len(videos)} videos")
    print(f"CSV: {Path(args.csv).resolve()}")
    print(f"Markdown: {Path(args.markdown).resolve()}")


if __name__ == "__main__":
    main()
