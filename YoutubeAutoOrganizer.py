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
 # Ask the user for the URL
    url = input("Paste your YouTube playlist URL here: ").strip()
    
# Pull out the playlist ID using regex
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    playlist_id = match.group(1) if match else None

    # Placeholder for channel ID - you would need to use the YouTube Data API to fetch this
    channel_id = "user_channel_id"

    return playlist_id, channel_id


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

  # First get all the video IDs in the playlist
    video_ids =  get_video_ids(playlist_id, youtube)
    print(f"Found {len(video_ids)} videos in the playlist.")
 
    transcripts = {}
 
    # Loop through each video and try to get its transcript
    for video_id in video_ids:
        try:
            # Get the transcript from YouTube
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
 
            # transcript_data is a list of {"text": "...", "start": ...}
            # We just want the text, so we join it all together
            full_text = " ".join(entry["text"] for entry in transcript_data)
 
            transcripts[video_id] = full_text
            print(f"  Got transcript for: {video_id}")
 
        except Exception:
            # Some videos don't have captions — just skip them
            print(f"  Skipping {video_id} (no captions available)")
 
        # Small pause so we don't send too many requests at once
        time.sleep(0.5)
 
    return transcripts




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
    pass


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
    pass
