import fs from "node:fs/promises";
import path from "node:path";

function csv(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

const [markdownArg, csvArg] = process.argv.slice(2);
if (!markdownArg || !csvArg) {
  throw new Error("Usage: node scripts/markdown_playlist_to_csv.mjs PLAYLIST.md OUTPUT.csv");
}

const markdownPath = path.resolve(markdownArg);
const csvPath = path.resolve(csvArg);
const markdown = await fs.readFile(markdownPath, "utf8");
const videos = [...markdown.matchAll(/^(\d+)\. \[(.+)\]\((https:\/\/www\.youtube\.com\/watch\?v=([^)]+))\)$/gm)]
  .map((match) => ({
    index: match[1],
    video_id: match[4],
    title: match[2],
    url: match[3],
    duration: "",
    upload_date: "",
  }));

if (!videos.length) {
  throw new Error(`No playlist videos found in ${markdownPath}`);
}

const fields = ["index", "video_id", "title", "url", "duration", "upload_date"];
const output = [
  fields.join(","),
  ...videos.map((video) => fields.map((field) => csv(video[field])).join(",")),
].join("\n");

await fs.mkdir(path.dirname(csvPath), { recursive: true });
await fs.writeFile(csvPath, `${output}\n`, "utf8");
console.log(`Saved ${videos.length} videos to ${csvPath}`);
