import os
import sys
import re
import json
import tempfile
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url_or_id: str) -> str:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "9HPfMm4K0mM"
    video_id = extract_video_id(target)
    print(f"Fetching transcript for Video ID: {video_id}...")

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)

    snippets_data = []
    full_text = []

    for s in transcript.snippets:
        snippets_data.append({
            "start": s.start,
            "duration": s.duration,
            "text": s.text
        })
        full_text.append(s.text)

    # Attempt to write to local directory first, fallback to temp if blocked by Windows CFA
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_json = os.path.join(script_dir, "transcript_structured.json")
    local_txt = os.path.join(script_dir, "transcript.txt")

    try:
        with open(local_json, "w", encoding="utf-8") as f:
            json.dump(snippets_data, f, indent=2, ensure_ascii=False)
        with open(local_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(full_text))
        print(f"Saved locally: {local_json} and {local_txt}")
    except (OSError, PermissionError, FileNotFoundError):
        temp_dir = tempfile.gettempdir()
        temp_json = os.path.join(temp_dir, f"{video_id}_structured.json")
        temp_txt = os.path.join(temp_dir, f"{video_id}.txt")
        with open(temp_json, "w", encoding="utf-8") as f:
            json.dump(snippets_data, f, indent=2, ensure_ascii=False)
        with open(temp_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(full_text))
        print(f"Notice: Local write protected by OS. Saved to Temp:\n - {temp_json}\n - {temp_txt}")

if __name__ == "__main__":
    main()
