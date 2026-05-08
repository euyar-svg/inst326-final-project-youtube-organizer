# Youtube Auto Organizer
# Course: INST326: Object-Oriented Programming

# This script automatically organizes your YouTube 
# watch later playlist into smaller  playlists based on the meta data

# What this script does:
#   1. Ask the user for a YouTube playlist link
#   2. Get all the video transcripts from that playlist
#   3. Clean up the transcripts
#   4. Use AI to figure out what category each video belongs to
#   5. Create new playlists for each category
#   6. Add the videos to the right playlists

# It will operate with  a total of 6 functions:
# Input Parser (Emre)
# Transcript Fetcher (emre)
# Data Sanititzer (Jason)
# Ai Tagging (Jason)
# Playlist Generator (Nizar)
# Video Batch Adder (Nizar)
#-----------------------------------------------------------------------------------------------------------------------------------------
from shutil import which

import re # this will be used to parse the playlist url and extract the playlist id and channel id
import time # this will be used to implement the waiting between batches of requests to avoid rate limiting
import json # this will be used to save the mapping of categories to playlist ids for later use
import os # this will be used to check if the mapping file already exists and to save the new mapping file
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

SCOPES = ["https://www.googleapis.com/auth/youtube"]

#----------------------------------------------------------------------------------------------------------------------------------------
#class:

class YoutubeAutoOrganizer:
    """
    A class to automatically organize YouTube playlists based on video transcripts.

    This class encapsulates the entire workflow of fetching video transcripts,
    sanitizing them, categorizing videos using AI, and creating new playlists
    based on those categories.

    Attributes:
        playlist_id: The ID of the YouTube playlist to organize.
        categorized_data: A mapping of video IDs to their assigned categories.

    Methods:
        input_parser(): Parses user input for playlist URL and extracts IDs.
        transcript_fetcher(playlist_id): Fetches transcripts for videos in a playlist.
        sanitize_transcript(transcript): Cleans up transcript text for AI processing.
        categorize_video(text): Categorizes a video based on its transcript.
        generate_playlists(categories, credentials): Creates new playlists for each category.
        batch_add_videos(video_category_map, playlist_id_map, credentials): Adds videos to the appropriate playlists in batches.
    """
    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        self.categorized_data = {} # this will be a dictionary that maps video ids to their categories
        
    def update_categories(self, video_id, category):
        if video_id in self.categorized_data:
            self.categorized_data[video_id].append(category)
        else:
            self.categorized_data[video_id] = [category]
            
#-----------------------------------------------------------------------------------------------------------------------------------------------
#function 1: Input Parser (Emre)
# Ask the user for a YouTube playlist URL and log in to Google
  
def input_parser():

 """
The purpose of this function is to parse/ take the input from the user, which is the YouTube playlist URL
It will then extract and return the playlist ID and the channel ID
This information will then be used later in the script to fetch the transcripts of the videos in the playlist and to categorize them.

args:
none, the function will prompt the user for input 
    
returns:   
playlist_id: the id of the playlist to be organized
    channel_id: the id of the channel that owns the playlist
"""

   url = input("Paste your YouTube playlist URL: ").strip()
 
    # Use regex to find the playlist ID inside the URL
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
 
    # If no match was found, the URL is wrong — stop the program
    if not match:
        print("Invalid URL. Make sure it contains 'list=' in it.")
        print("Example: https://www.youtube.com/playlist?list=PLxxxxxx")
        raise SystemExit(1)
 
    playlist_id = match.group(1)
    print(f"Found playlist ID: {playlist_id}")
 
    # Log in to Google
    credentials = _get_credentials()
 
    return playlist_id, credentials
 
 
def _get_credentials():
    """
    Log in to Google using OAuth2.
    If we've logged in before, load the saved login from token.json.
    If not, open a browser window to log in, then save it for next time.
 
    Returns:
        credentials : the Google login info we need to use the API
    """
 
    credentials = None
 
    # Check if we already have a saved login
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
 
    # If no saved login (or it's expired), open the browser to log in
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
        credentials = flow.run_local_server(port=0)
 
        # Save the login so we don't have to do this again
        with open("token.json", "w") as f:
            f.write(credentials.to_json())
        print("Logged in successfully. Login saved to token.json.")
 
    return credentials

#--------------------------------------------------------------------------------------------------------------------------------------
# function 2: Transcript Fetcher (Emre)
# Get the transcript (captions) for every video in the playlist

def transcript_fetcher(playlist_id, youtube):
    
    """
     
This function will fetch the transcripts of the videos in the playlist with the Youtube Data Api and will return a list of transcripts
to prepare the necessary data for processing.      

args:
playlist_id: the id of the playlist to fetch the transcripts
youtube: the YouTube Data API client

returns:
transcripts: a list of transcripts for the videos in the playlist

    """
 video_ids = _get_video_ids(playlist_id, youtube)
    print(f"Found {len(video_ids)} videos in the playlist.")
 
    transcripts = {}
 
    for video_id in video_ids:
        try:
            # Fetch the transcript — returns a list of {"text": "...", "start": ...}
            data = YouTubeTranscriptApi.get_transcript(video_id)
 
            # Join all the text pieces into one big string
            transcripts[video_id] = " ".join(entry["text"] for entry in data)
            print(f"  Got transcript: {video_id}")
 
        except Exception:
            # Some videos have captions turned off — just skip them
            print(f"  Skipping {video_id} (no captions available)")
 
        # Wait a little between requests so we don't get blocked
        time.sleep(0.5)
 
    return transcripts
 
 
def _get_video_ids(playlist_id, youtube):
    """
    Page through the playlist and collect all video IDs.
    Handles playlists longer than 50 videos using nextPageToken.
 
    Args:
        playlist_id : the playlist ID string
        youtube     : the YouTube API client
 
    Returns:
        ids : a list of video ID strings
    """
 
    ids = []
    next_page = None
 
    while True:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
 
        # Pull the video ID out of each item
        for item in response["items"]:
            ids.append(item["contentDetails"]["videoId"])
 
        # Check if there's another page of results
        next_page = response.get("nextPageToken")
        if not next_page:
            break   # no more pages, we're done
 
    return ids
 

#-----------------------------------------------------------------------------------------------------------------
#function 3:

def sanitize_transcript(transcript):
    """
    Clean up transcript text so it can be used for AI processing.

    This function removes timestamps, HTML tags, filler words,
    and extra whitespace.

    The "text editor" responsible for tokenization and noise reduction, 
    stripping out timestamps, HTML artifacts, and "filler" words 
    to optimize the character count for the AI’s processing limits.
    Args:
        transcript (str): Raw transcript text from a video.

    Returns:
        cleaned_text: Cleaned text.
    """

#function 4:

def categorize_video(text):
    """
    Categorize a video based on its transcript.

    The "decision engine" that feeds sanitized text into the Gemini API, 
    using structured prompt engineering to categorize each video 
    into a specific topic or genre via zero-shot classification.

    Args:
        text (str): Cleaned transcript text.

    Returns:
        category: Category label.
    """
    if not text:
        return "Unknown"

    text = text.lower()

    # basic keyword matching
    if "python" in text or "code" in text or "programming" in text:
        return "Programming"

    elif "game" in text or "gaming" in text or "playthrough" in text:
        return "Gaming"

    elif "music" in text or "song" in text or "album" in text:
        return "Music"

    elif "tutorial" in text or "learn" in text or "how to" in text:
        return "Education"

    elif "news" in text or "interview" in text:
        return "News"

    return "Other"

# function 5:

def generate_playlists(categories, credentials):
    """
    takes the list of categories the ai made and creates
    actual youtube playlists for each one. uses oauth so
    youtube knows it is us making the playlists.

    args:
        categories: list of category names from the ai tagger
        credentials: the oauth2 stuff for youtube api access

    returns:
        dictionary that maps each category name to its new playlist id
    """
    youtube = build("youtube", "v3", credentials=credentials)
    playlist_id_map = {}

    for category in categories:
        request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": category,
                    "description": f"Auto generated playlist for {category}"
                },
                "status": {
                    "privacyStatus": "private"
                }
            }
        )
        try:
            response = request.execute()
            playlist_id_map[category] = response["id"]
        except Exception as e:
            print(f"  Failed to create playlist for '{category}': {e}")

    return playlist_id_map


# function 6:

def batch_add_videos(video_category_map, playlist_id_map, credentials):
    """
    goes through all the videos and adds them to the right playlists.
    has to be careful with the 10000 unit daily quota so it batches
    the requests and waits between them so we do not get rate limited.
 
    args:
        video_category_map: dictionary of category to list of video ids
        playlist_id_map: dictionary of category to playlist id
        credentials: oauth2 stuff again for api calls
 
    returns:
        nothing
    """
    youtube = build("youtube", "v3", credentials=credentials)
 
    for category, video_ids in video_category_map.items():
        playlist_id = playlist_id_map.get(category)
 
        if not playlist_id:
            print(f"  Warning: no playlist found for category '{category}', skipping.")
            continue
 
        for i, video_id in enumerate(video_ids):
            try:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                ).execute()
 
            except Exception as e:
                print(f"  Failed to add {video_id} to '{category}': {e}")
 
            if (i + 1) % 10 == 0:
                time.sleep(2)
