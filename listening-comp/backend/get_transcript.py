from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, List, Dict
import os
import re
from urllib.request import urlopen
import json


class YouTubeTranscriptDownloader:
    def __init__(self, languages: List[str] = ["ja", "en"]):
        self.languages = languages

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        if "v=" in url:
            return url.split("v=")[1][:11]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1][:11]
        return None

    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL"""
        playlist_pattern = r'(?:list=)([a-zA-Z0-9_-]+)'
        match = re.search(playlist_pattern, url)
        return match.group(1) if match else None

    def get_playlist_video_ids(self, playlist_url: str) -> List[str]:
        """Get all video IDs from a playlist URL"""
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print("No playlist ID found in URL")
            return []

        try:
            # Get playlist page
            url = f"https://www.youtube.com/playlist?list={playlist_id}"
            html = urlopen(url).read().decode()
            
            # Extract video IDs using regex
            video_ids = re.findall(r'"videoId":"([^"]+)"', html)
            
            # Remove duplicates while preserving order
            unique_ids = []
            seen = set()
            for vid in video_ids:
                if vid not in seen:
                    seen.add(vid)
                    unique_ids.append(vid)
            
            print(f"Found {len(unique_ids)} videos in playlist")
            return unique_ids
            
        except Exception as e:
            print(f"Error getting playlist videos: {str(e)}")
            return []

    def get_transcript(self, video_id: str) -> Optional[List[Dict]]:
        """
        Download YouTube Transcript
        
        Args:
            video_id (str): YouTube video ID or URL
            
        Returns:
            Optional[List[Dict]]: Transcript if successful, None otherwise
        """
        # Extract video ID if full URL is provided
        if "youtube.com" in video_id or "youtu.be" in video_id:
            video_id = self.extract_video_id(video_id)
            
        if not video_id:
            print("Invalid video ID or URL")
            return None

        print(f"Downloading transcript for video ID: {video_id}")
        
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=self.languages)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def save_transcript(self, transcript: List[Dict], filename: str) -> bool:
        """Save transcript to file"""
        # Use absolute path
        filename = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            f"backend/data/transcripts/{filename}.txt"
        )
        
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                for entry in transcript:
                    f.write(f"{entry['text']}\n")
            return True
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            return False

def main(video_url, print_transcript=False):
    # Initialize downloader
    downloader = YouTubeTranscriptDownloader()
    
    # Check if it's a playlist URL
    if "playlist" in video_url:
        # Get all video IDs first
        video_ids = downloader.get_playlist_video_ids(video_url)
        if not video_ids:
            print("No videos found in playlist")
            return
            
        print(f"Processing {len(video_ids)} videos...")
        for video_id in video_ids:
            try:
                transcript = downloader.get_transcript(video_id)
                if transcript and downloader.save_transcript(transcript, video_id):
                    print(f"Saved transcript for {video_id}")
                else:
                    print(f"No transcript available for {video_id}")
            except Exception as e:
                print(f"Failed to process video {video_id}: {str(e)}")
    else:
        # Process single video
        transcript = downloader.get_transcript(video_url)
        if transcript:
            video_id = downloader.extract_video_id(video_url)
            if downloader.save_transcript(transcript, video_id):
                print(f"Transcript saved successfully to {video_id}.txt")
                if print_transcript:
                    for entry in transcript:
                        print(f"{entry['text']}")

if __name__ == "__main__":
    playlist_url = "https://www.youtube.com/playlist?list=PLkGU7DnOLgRMl-h4NxxrGbK-UdZHIXzKQ"
    # video_id = "https://www.youtube.com/watch?v=sY7L5cfCWno&list=PLkGU7DnOLgRMl-h4NxxrGbK-UdZHIXzKQ"
    main(playlist_url, print_transcript=False)