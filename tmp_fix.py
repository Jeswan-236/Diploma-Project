import os
import sys
import urllib.parse

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import search_youtube_video, fetch_youtube_video_details, supabase

def fix_thumbnails():
    # Find all videos that still have search_query in their URL
    response = supabase.table("videos").select("*").ilike("url", "%search_query%").execute()
    
    if not response.data:
        print("No videos with search_query URLs found.")
        return

    for video in response.data:
        parsed = urllib.parse.urlparse(video['url'])
        query = urllib.parse.parse_qs(parsed.query)
        search_query = query.get('search_query', [None])[0]
        
        if search_query:
            print(f"Fixing video: {video['title']} (Query: {search_query})")
            video_id = search_youtube_video(search_query)
            if video_id:
                details = fetch_youtube_video_details(video_id)
                if details:
                    print(f" -> Found YouTube Video: {details['title']}")
                    print(f" -> Thumbnail: {details['thumbnail']}")
                    
                    # Update database
                    supabase.table("videos").update({
                        "thumbnail_url": details['thumbnail'],
                        "url": details['watch_url']
                    }).eq("id", video['id']).execute()
                    print(" -> Update successful!")
                else:
                    print(" -> Failed to fetch details.")
            else:
                print(" -> Search returned no video ID.")

if __name__ == "__main__":
    fix_thumbnails()
    print("All done!")
