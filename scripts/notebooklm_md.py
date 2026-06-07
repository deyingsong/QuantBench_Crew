import argparse
import re
import os
import time
import json
import subprocess
from google import genai


# 1. API Key Setup - Hardcoded fallback prevents the ValueError
api_key = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KbAt6VisQ9VasHfi2hTf0qggUHxg1M5b4BxHfsbMR_8Q")
client = genai.Client(api_key=api_key)



def run_notebooklm(cmd_args):
    """Safely runs notebooklm via python module and captures stdout."""
    command = f'python -m notebooklm {cmd_args}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def parse_cli_json(output):
    """Extracts JSON from CLI output, bypassing any terminal logs/warnings."""
    if not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        match = re.search(r'(\{.*\}|\[.*\])', output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
    return None

def extract_video_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def format_transcript_with_gemini(raw_text, video_id):
    prompt = (
        "The following text is a raw, unpunctuated transcript extracted from a YouTube video. "
        "Please fix the capitalization, insert correct punctuation, and format it as a highly readable Markdown document. "
        "Use Markdown elements like headings (##) to logically break up major topic shifts, and use paragraphs for readability. "
        "CRITICAL INSTRUCTION: Do not summarize, do not omit any words, and do not add any commentary. "
        "Return the full, exact polished transcript in Markdown format:\n\n" + raw_text
    )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    md_header = f"# Transcript: YouTube Video ({video_id})\n"
    md_header += f"**Source Link:** [https://youtu.be/{video_id}](https://youtu.be/{video_id})\n\n"
    md_header += "---\n\n"
    
    return md_header + response.text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("--output_dir", default="./transcripts_md")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    with open(args.input_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print("\n[NotebookLM] Setting up workspace...")
    create_out = run_notebooklm('create "YouTube Bulk Extractor" --json')
    create_data = parse_cli_json(create_out)
    
    nb_id = None
    if create_data:
        if "notebook" in create_data:
            nb_id = create_data["notebook"].get("id")
        elif "id" in create_data:
            nb_id = create_data.get("id")
            
    if nb_id:
        run_notebooklm(f'use {nb_id}')
        print(f"[NotebookLM] Workspace ready (ID: {nb_id})")
    else:
        print(f"[NotebookLM] Warning: Could not parse notebook ID. CLI Output: {create_out}")

    for url in urls:
        video_id = extract_video_id(url)
        if not video_id:
            continue
            
        print(f"\n[+] Processing Video: {video_id}")
        
        print("    [NotebookLM] Adding source and fetching transcript...")
        add_out = run_notebooklm(f'source add "{url}" --json')
        add_data = parse_cli_json(add_out)
        
        source_id = None
        if add_data:
            if "source" in add_data:
                source_id = add_data["source"].get("id")
            elif "id" in add_data:
                source_id = add_data.get("id")
                
        if not source_id:
            src_out = run_notebooklm('source list --json')
            src_data = parse_cli_json(src_out)
            if src_data and isinstance(src_data, list) and len(src_data) > 0:
                source_id = src_data[0].get("id") or src_data[0].get("source_id")

        if not source_id:
            print(f"    [Error] Could not retrieve source ID. Skipping.")
            continue
            
        # --- NEW POLLING LOGIC ---
        print("    [NotebookLM] Waiting for Google to index the transcript...")
        is_ready = False
        
        for _ in range(15):  # Poll every 5 seconds, up to 75 seconds
            time.sleep(5)
            status_out = run_notebooklm('source list --json')
            sources = parse_cli_json(status_out)
            
            if sources and isinstance(sources, list):
                # Find our specific video in the notebook
                current_source = next((s for s in sources if s.get("id") == source_id or s.get("source_id") == source_id), None)
                
                if current_source:
                    state = current_source.get("state", "UNKNOWN")
                    if state == "READY":
                        is_ready = True
                        break
                    elif state == "FAILED":
                        print("    [Error] NotebookLM explicitly FAILED to process this video. (Likely age-restricted or region-blocked by YouTube).")
                        break
                    
                    print(f"    [NotebookLM] Still processing... (State: {state})")
        
        if not is_ready:
            print("    [Error] Source never became READY. Skipping.")
            continue
            
        print("    [NotebookLM] Downloading raw transcript...")
        raw_text = run_notebooklm(f'source get-fulltext {source_id}')
        
        if raw_text and len(raw_text) > 50:
            print("    [Gemini] Formatting text into readable Markdown...")
            clean_md = format_transcript_with_gemini(raw_text, video_id)
            
            output_path = os.path.join(args.output_dir, f"{video_id}.md")
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(clean_md)
            print(f"    [Success] Saved cleanly to {output_path}")
        else:
            print("    [Error] Video became READY, but extracted text was empty. This video likely has NO closed captions.")

if __name__ == "__main__":
    main()