import fs from "node:fs/promises";
import path from "node:path";

function parseCsvLine(line) {
  const out = [];
  let cur = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        cur += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === "," && !inQuotes) {
      out.push(cur);
      cur = "";
    } else {
      cur += ch;
    }
  }
  out.push(cur);
  return out;
}

function sanitizeFilename(value) {
  return (
    value
      .normalize("NFKD")
      .replace(/[\\/:*?"<>|]/g, "-")
      .replace(/[\u0000-\u001f]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .replace(/[. ]+$/g, "")
      .slice(0, 180) || "untitled"
  );
}

function yaml(value) {
  return String(value || "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

export async function setupCwtNotebookLm({ tab, nodeRepl }) {
  const csvPath = path.join(
    nodeRepl.cwd,
    "Source_data/transcript/chat_with_traders_video_list.csv",
  );
  const text = await fs.readFile(csvPath, "utf8");
  const lines = text.trim().split(/\r?\n/);
  const header = parseCsvLine(lines[0]);
  const videos = lines.slice(1).map((line) => {
    const vals = parseCsvLine(line);
    return Object.fromEntries(header.map((h, i) => [h, vals[i] || ""]));
  });
  const outDir = path.join(nodeRepl.tmpDir, "notebooklm_cwt_transcripts");
  const statusPath = path.join(outDir, "_status.jsonl");

  async function snapshotText(max = 12000) {
    return (await tab.playwright.domSnapshot()).slice(0, max);
  }

  async function closeAnyDialog() {
    for (const name of ["Close", "Cancel"]) {
      const btn = tab.playwright.getByRole("button", { name });
      const count = await btn.count();
      if (count === 1) {
        await btn.click({});
        await tab.playwright.waitForTimeout(700);
        return true;
      }
    }
    return false;
  }

  async function createFreshNotebook() {
    await closeAnyDialog().catch(() => false);
    let create = tab.playwright.getByRole("button", { name: "Create notebook" });
    let count = await create.count();
    if (count !== 1) {
      create = tab.playwright.getByRole("button", { name: "Create new notebook" });
      count = await create.count();
    }
    if (count !== 1) {
      throw new Error(`Create notebook count during recovery: ${count}\n${await snapshotText(4000)}`);
    }
    await create.click({});
    await tab.playwright.waitForTimeout(2500);
  }

  async function ensureSourcesList() {
    let snap = await tab.playwright.domSnapshot();
    if (snap.includes('button "Back"') && snap.includes("Source guide")) {
      const back = tab.playwright.getByRole("button", { name: "Back" });
      if ((await back.count()) === 1) {
        await back.click({});
        await tab.playwright.waitForTimeout(1000);
      }
    }
    snap = await tab.playwright.domSnapshot();
    if (!snap.includes('tabpanel "Sources"') || snap.includes('tabpanel "Chat"')) {
      const sources = tab.playwright.getByRole("tab", { name: "Sources" });
      if ((await sources.count()) === 1) {
        await sources.click({});
        await tab.playwright.waitForTimeout(1500);
      }
    }
  }

  async function openWebsiteDialog() {
    let snap = await tab.playwright.domSnapshot();
    if (snap.includes("Website and YouTube URLs")) return;
    if (snap.includes("Create Audio and Video Overviews")) {
      const websites = tab.playwright.getByRole("button", { name: "Websites" });
      if ((await websites.count()) !== 1) {
        throw new Error(`Websites unavailable\n${await snapshotText(4000)}`);
      }
      await websites.click({});
      await tab.playwright.waitForTimeout(800);
      return;
    }
    await ensureSourcesList();
    const add = tab.playwright.getByRole("button", { name: "Add source" });
    if ((await add.count()) !== 1) {
      throw new Error(`Add source unavailable\n${await snapshotText(4000)}`);
    }
    await add.click({});
    await tab.playwright.waitForTimeout(900);
    const websites = tab.playwright.getByRole("button", { name: "Websites" });
    if ((await websites.count()) !== 1) {
      throw new Error(`Websites unavailable after add\n${await snapshotText(4000)}`);
    }
    await websites.click({});
    await tab.playwright.waitForTimeout(800);
  }

  async function importUrl(video) {
    await openWebsiteDialog();
    const urlBox = tab.playwright.getByRole("textbox", { name: "Enter URLs" });
    if ((await urlBox.count()) !== 1) {
      throw new Error(`URL textbox unavailable\n${await snapshotText(4000)}`);
    }
    await urlBox.fill(video.url, {});
    const insert = tab.playwright.getByRole("button", { name: "Insert" });
    if ((await insert.count()) !== 1) throw new Error("Insert unavailable");
    if (!(await insert.isEnabled())) throw new Error(`Insert disabled for ${video.url}`);
    await insert.click({});

    const deadline = Date.now() + 120000;
    let last = "";
    while (Date.now() < deadline) {
      await tab.playwright.waitForTimeout(3000);
      last = await tab.playwright.domSnapshot();
      const sourceListSuccess = last.includes(video.title) && last.includes("Select all sources");
      const chatSuccess = last.includes("1 source") && last.includes('tabpanel "Chat"');
      if (sourceListSuccess || chatSuccess) {
        await ensureSourcesList();
        return;
      }
      if (/upload failed|couldn.t import|not supported|failed/i.test(last)) {
        throw new Error(`NotebookLM import failure UI: ${last.slice(0, 4000)}`);
      }
    }
    throw new Error(`Timed out waiting for imported source or chat summary: ${video.title}\n${last.slice(0, 5000)}`);
  }

  async function openImportedSource(video) {
    await ensureSourcesList();
    let source = tab.playwright.getByRole("button", { name: video.title });
    let count = await source.count();
    if (count !== 1) {
      await tab.playwright.waitForTimeout(3000);
      source = tab.playwright.getByRole("button", { name: video.title });
      count = await source.count();
    }
    if (count !== 1) {
      throw new Error(`Imported source button count for exact title: ${count}\n${await snapshotText(6000)}`);
    }
    let last = "";
    for (let attempt = 1; attempt <= 4; attempt += 1) {
      if (attempt === 2) await source.dblclick({});
      else if (attempt === 4) await source.press("Enter", {});
      else await source.click({});
      await tab.playwright.waitForTimeout(3500);
      last = await tab.playwright.domSnapshot();
      if (last.includes("Source guide") && last.includes('button "Back"')) return;
    }
    throw new Error(`Source did not open after retries: ${video.title}\n${last.slice(0, 6000)}`);
  }

  async function extractTranscript() {
    const deadline = Date.now() + 90000;
    let best = "";
    while (Date.now() < deadline) {
      best = await tab.playwright.evaluate(() => {
        const preferred = document.querySelector("labs-tailwind-doc-viewer, element-list-renderer");
        const fromPreferred = preferred ? (preferred.textContent || "").replace(/\s+/g, " ").trim() : "";
        if (fromPreferred.length > 300) return fromPreferred;
        const candidates = Array.from(
          document.querySelectorAll("span.ng-star-inserted, div.paragraph, paragraph-element-view, labs-tailwind-doc-viewer, element-list-renderer"),
        )
          .map((el) => (el.textContent || "").replace(/\s+/g, " ").trim())
          .filter((item) => item.length > 300)
          .sort((a, b) => b.length - a.length);
        return candidates.find((item) => !item.includes("NotebookLM") && !item.includes("SourcesChatStudio")) || candidates[0] || "";
      }, undefined, { timeoutMs: 20000 });
      if (best.length > 300) return best;
      await tab.playwright.waitForTimeout(2500);
    }
    throw new Error(`Timed out waiting for transcript text; best length=${best.length}\n${await snapshotText(5000)}`);
  }

  async function saveTranscript(video, transcript, usedNames) {
    await fs.mkdir(outDir, { recursive: true });
    const base = sanitizeFilename(video.title);
    let name = `${base}.md`;
    if (usedNames.has(name)) name = `${base} - ${video.video_id}.md`;
    usedNames.add(name);
    const md = `---\ntitle: "${yaml(video.title)}"\nvideo_id: "${yaml(video.video_id)}"\nurl: "${yaml(video.url)}"\nduration: "${yaml(video.duration)}"\nsource: "NotebookLM YouTube transcript import"\n---\n\n# ${video.title}\n\n[Watch on YouTube](${video.url})\n\n## Transcript\n\n${transcript}\n`;
    const file = path.join(outDir, name);
    await fs.writeFile(file, md, "utf8");
    return file;
  }

  async function removeOnlySource() {
    await ensureSourcesList();
    const more = tab.playwright.getByRole("button", { name: "More" });
    const count = await more.count();
    if (count !== 1) throw new Error(`More button count: ${count}\n${await snapshotText(5000)}`);
    await more.click({});
    await tab.playwright.waitForTimeout(600);
    const remove = tab.playwright.getByRole("menuitem", { name: "Remove source" });
    if ((await remove.count()) !== 1) {
      throw new Error(`Remove source unavailable\n${await snapshotText(5000)}`);
    }
    await remove.click({});
    await tab.playwright.waitForTimeout(700);
    const del = tab.playwright.getByRole("button", { name: "Delete" });
    if ((await del.count()) !== 1) {
      throw new Error(`Delete confirm unavailable\n${await snapshotText(5000)}`);
    }
    await del.click({});
    await tab.playwright.waitForTimeout(1800);
  }

  async function processVideo(video, usedNames) {
    await importUrl(video);
    await openImportedSource(video);
    const transcript = await extractTranscript();
    const file = await saveTranscript(video, transcript, usedNames);
    await removeOnlySource();
    return { status: "saved", index: video.index, video_id: video.video_id, title: video.title, file, chars: transcript.length };
  }

  async function runBatch(startIndex1Based, count) {
    await fs.mkdir(outDir, { recursive: true });
    const usedNames = new Set((await fs.readdir(outDir).catch(() => [])).filter((file) => file.endsWith(".md")));
    const results = [];
    for (const video of videos.slice(startIndex1Based - 1, startIndex1Based - 1 + count)) {
      try {
        const result = await processVideo(video, usedNames);
        results.push(result);
        await fs.appendFile(statusPath, `${JSON.stringify(result)}\n`, "utf8");
      } catch (err) {
        const result = {
          status: "error",
          index: video.index,
          video_id: video.video_id,
          title: video.title,
          url: video.url,
          reason: String((err && err.stack) || err).slice(0, 8000),
        };
        results.push(result);
        await fs.appendFile(statusPath, `${JSON.stringify(result)}\n`, "utf8");
        try {
          await createFreshNotebook();
        } catch (recoverErr) {
          result.recovery_error = String((recoverErr && recoverErr.stack) || recoverErr).slice(0, 3000);
        }
      }
    }
    return {
      outDir,
      statusPath,
      start: startIndex1Based,
      count,
      saved: results.filter((item) => item.status === "saved").length,
      errors: results.filter((item) => item.status !== "saved").length,
      results,
    };
  }

  return { videos, outDir, statusPath, runBatch, processVideo, createFreshNotebook };
}
