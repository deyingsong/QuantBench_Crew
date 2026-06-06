import fs from "node:fs/promises";
import path from "node:path";

function parseCsvLine(line) {
  const values = [];
  let value = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"') {
      if (quoted && line[index + 1] === '"') {
        value += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      values.push(value);
      value = "";
    } else {
      value += char;
    }
  }
  values.push(value);
  return values;
}

function csv(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

const [videoListArg, transcriptDirArg] = process.argv.slice(2);
if (!videoListArg || !transcriptDirArg) {
  throw new Error("Usage: node scripts/build_notebooklm_transcript_index.mjs VIDEO_LIST.csv TRANSCRIPT_DIR");
}

const videoListPath = path.resolve(videoListArg);
const transcriptDir = path.resolve(transcriptDirArg);
const lines = (await fs.readFile(videoListPath, "utf8")).trim().split(/\r?\n/);
const header = parseCsvLine(lines[0]);
const videos = lines.slice(1).map((line) => {
  const values = parseCsvLine(line);
  return Object.fromEntries(header.map((name, index) => [name, values[index] ?? ""]));
});

const transcripts = new Map();
for (const filename of await fs.readdir(transcriptDir)) {
  if (!filename.endsWith(".md")) continue;
  const text = await fs.readFile(path.join(transcriptDir, filename), "utf8");
  const videoId = text.match(/^video_id: "([^"]+)"$/m)?.[1];
  if (videoId) transcripts.set(videoId, { filename, chars: text.length });
}

const rows = videos.map((video) => {
  const transcript = transcripts.get(video.video_id);
  return {
    index: video.index,
    status: transcript ? "saved" : "notebooklm_import_error",
    video_id: video.video_id,
    title: video.title,
    url: video.url,
    duration: video.duration,
    output_file: transcript?.filename ?? "",
    transcript_chars: transcript?.chars ?? "",
    source: transcript ? "NotebookLM YouTube transcript import" : "",
    note: transcript ? "" : "NotebookLM rejected the YouTube source after repeated standard, short, grouped, and isolated imports.",
  };
});

const fields = ["index", "status", "video_id", "title", "url", "duration", "output_file", "transcript_chars", "source", "note"];
const indexCsv = [
  fields.join(","),
  ...rows.map((row) => fields.map((field) => csv(row[field])).join(",")),
].join("\n");
await fs.writeFile(path.join(transcriptDir, "_notebooklm_transcript_index.csv"), `${indexCsv}\n`, "utf8");
await fs.writeFile(
  path.join(transcriptDir, "_final_status.jsonl"),
  `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`,
  "utf8",
);

console.log(`Videos: ${videos.length}`);
console.log(`Saved: ${rows.filter((row) => row.status === "saved").length}`);
console.log(`NotebookLM import errors: ${rows.filter((row) => row.status !== "saved").length}`);
