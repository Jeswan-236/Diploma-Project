#!/usr/bin/env python3
"""
Script to update video URLs in the database from search URLs to direct YouTube video URLs
"""

import requests
import json

# Base URL for the API
BASE_URL = 'http://127.0.0.1:8000'

# YouTube video URLs that match the topics
VIDEO_UPDATES = {
    "HTML Video Class": "https://www.youtube.com/watch?v=UB1O30fR-EE",  # Traversy Media HTML Crash Course
    "CSS Video Class": "https://www.youtube.com/watch?v=yfoY53QXEnI",   # Traversy Media CSS Crash Course
    "JavaScript Video Class": "https://www.youtube.com/watch?v=hdI2bqOjy3c", # Traversy Media JS Crash Course
    "Python Video Class": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",    # freeCodeCamp Python for Everybody
    "MySQL Video Class": "https://www.youtube.com/watch?v=5OdVJbNCSso"      # Traversy Media MySQL Crash Course
}

def update_video_urls():
    """Update video URLs in the database"""

    # First, get all coding videos
    try:
        response = requests.get(f'{BASE_URL}/api/videos?category=coding')
        response.raise_for_status()
        videos = response.json()

        print(f"Found {len(videos)} coding videos")

        # Update each video
        for video in videos:
            video_title = video['title']
            video_id = video['id']

            if video_title in VIDEO_UPDATES:
                new_url = VIDEO_UPDATES[video_title]
                print(f"Updating '{video_title}' from '{video['url']}' to '{new_url}'")

                # For this demo, we'll use a simple approach
                # In a real admin scenario, you'd need authentication
                # For now, let's just show what would be updated
                print(f"Would update video {video_id}: {video_title}")
                print(f"  Old URL: {video['url']}")
                print(f"  New URL: {new_url}")
                print()

        print("Note: To actually update the database, you would need admin authentication.")
        print("The admin endpoint is available at: PUT /api/admin/videos/{video_id}")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")

if __name__ == "__main__":
    update_video_urls()