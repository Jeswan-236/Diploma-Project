
import urllib.request
import re
import html
import json

def get_yt_initial_player_response(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html_text = response.read().decode("utf-8")
            
        print(f"HTML size: {len(html_text)}")
        
        # Look for the pattern
        patterns = [
            r"ytInitialPlayerResponse\s*=\s*(\{.+?\})\s*;",
            r"ytInitialPlayerResponse\s*=\s*(\{.+?\})\s*[<;]",
            r"var\s+ytInitialPlayerResponse\s*=\s*(\{.+?\});"
        ]
        
        for p in patterns:
            match = re.search(p, html_text, re.DOTALL)
            if match:
                print(f"Found match with pattern: {p}")
                try:
                    data = json.loads(match.group(1))
                    print("Successfully parsed JSON")
                    captions = data.get("captions", {})
                    renderer = captions.get("playerCaptionsTracklistRenderer", {})
                    tracks = renderer.get("captionTracks", [])
                    print(f"Number of caption tracks found: {len(tracks)}")
                    for t in tracks:
                        print(f" - Lang: {t.get('languageCode')}, Name: {t.get('name', {}).get('simpleText')}, Kind: {t.get('kind', 'manual')}")
                    return True
                except Exception as e:
                    print(f"JSON parse error for pattern {p}: {e}")
        
        print("No matches found in HTML.")
        return False
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    get_yt_initial_player_response("PkZNo7MFNFg")
