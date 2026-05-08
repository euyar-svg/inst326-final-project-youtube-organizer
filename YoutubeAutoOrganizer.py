# Youtube Auto Organizer
# Course: INST326: Object-Oriented Programming
# Authors: Emre Uyar, Jason Shen, Nizar Ghourmari
#
# What this script does:
#   1. Ask the user for a YouTube playlist link
#   2. Get all the video transcripts from that playlist
#      (falls back to description or comments if no captions)
#   3. Clean up the transcripts
#   4. Figure out what category each video belongs to
#   5. Create new playlists for each category
#   6. Add the videos to the right playlists

import re
import time
import json
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

SCOPES = ["https://www.googleapis.com/auth/youtube"]


# ---------------------------------------------------------------
# Class
# ---------------------------------------------------------------

class YoutubeAutoOrganizer:
    """
    A class to automatically organize YouTube playlists based on video content.

    Attributes:
        playlist_id (str): The ID of the YouTube playlist to organize.
        categorized_data (dict): Maps video IDs to their assigned categories.
    """

    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        self.categorized_data = {}

    def update_categories(self, video_id, category):
        """Add a category to a video. Appends if the video already has one."""
        if video_id in self.categorized_data:
            self.categorized_data[video_id].append(category)
        else:
            self.categorized_data[video_id] = [category]


# ---------------------------------------------------------------
# Function 1: Input Parser (Emre)
# ---------------------------------------------------------------

def input_parser():
    """
    Ask the user for a YouTube playlist URL, pull out the playlist ID,
    and log in to Google.

    Args:
        none — prompts the user for input

    Returns:
        playlist_id (str) : the ID pulled from the URL
        credentials       : Google login so we can use the API
    """

    url = input("Paste your YouTube playlist URL: ").strip()

    # Pull the playlist ID out of the URL using regex
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)

    if not match:
        print("Invalid URL. Make sure it contains 'list=' in it.")
        print("Example: https://www.youtube.com/playlist?list=PLxxxxxx")
        raise SystemExit(1)

    playlist_id = match.group(1)
    print(f"Found playlist ID: {playlist_id}")

    credentials = _get_credentials()
    return playlist_id, credentials


def _get_credentials():
    """
    Log in to Google using OAuth2.
    Saves login to token.json so you only have to do this once.

    Returns:
        credentials : Google login info needed to use the API
    """

    credentials = None

    # If we logged in before, reuse that saved login
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no saved login, open a browser window to log in
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
        credentials = flow.run_local_server(port=0)

        # Save it so we don't need to log in again next time
        with open("token.json", "w") as f:
            f.write(credentials.to_json())
        print("Logged in successfully. Login saved to token.json.")

    return credentials


# ---------------------------------------------------------------
# Function 2: Transcript Fetcher (Emre)
# ---------------------------------------------------------------

def transcript_fetcher(playlist_id, youtube):
    """
    Get every video ID from the playlist, then try to get text for each
    video in this order:
      1. Captions / transcript
      2. Video description (if no captions)
      3. Top comments   (if no description either)
    Videos with no text at all are stored as "" and will land in the
    "Needs Manual Review" playlist.

    Args:
        playlist_id (str) : the ID of the YouTube playlist
        youtube           : the YouTube API client

    Returns:
        transcripts (dict) : { "videoID": "text to categorize", ... }
    """

    video_ids = _get_video_ids(playlist_id, youtube)
    print(f"Found {len(video_ids)} videos in the playlist.\n")

    transcripts = {}

    for video_id in video_ids:
        text = ""

        # Try 1: captions / transcript
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join(entry["text"] for entry in data)
            print(f"  [transcript]  {video_id}")

        except Exception:
            print(f"  [no captions] {video_id} — trying description...")

            # Try 2: video description
            try:
                response = youtube.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                items = response.get("items", [])
                if items:
                    description = items[0]["snippet"].get("description", "").strip()
                    if description:
                        text = description
                        print(f"  [description] {video_id} — got description")
                    else:
                        print(f"  [no desc]     {video_id} — trying comments...")

            except Exception:
                print(f"  [desc failed] {video_id} — trying comments...")

            # Try 3: top comments
            if not text:
                try:
                    response = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=20,
                        order="relevance"
                    ).execute()

                    comments = []
                    for item in response.get("items", []):
                        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                        comments.append(comment)

                    if comments:
                        text = " ".join(comments)
                        print(f"  [comments]    {video_id} — got {len(comments)} comments")
                    else:
                        print(f"  [nothing]     {video_id} — will need manual review")

                except Exception:
                    print(f"  [nothing]     {video_id} — will need manual review")

        # Store whatever text we found (empty string = manual review later)
        transcripts[video_id] = text
        time.sleep(0.5)

    return transcripts


def _get_video_ids(playlist_id, youtube):
    """
    Page through the playlist and collect all video IDs.
    Handles playlists longer than 50 videos automatically.

    Args:
        playlist_id (str) : the playlist ID
        youtube           : the YouTube API client

    Returns:
        ids (list) : all video ID strings in the playlist
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

        for item in response["items"]:
            ids.append(item["contentDetails"]["videoId"])

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    return ids


# ---------------------------------------------------------------
# Function 3: Data Sanitizer (Jason)
# ---------------------------------------------------------------

def sanitize_transcript(transcript):
    """
    Clean up raw text before categorizing.
    Removes timestamps, HTML tags, and filler words.

    Args:
        transcript (str): Raw text from captions, description, or comments.

    Returns:
        cleaned_text (str): Cleaned text ready to categorize.
    """

    if not transcript:
        return ""

    text = transcript

    # Remove timestamps like [00:01] or [00:01:30]
    parts = text.split()
    cleaned_parts = []
    for word in parts:
        if "[" in word and ":" in word and "]" in word:
            continue
        cleaned_parts.append(word)
    text = " ".join(cleaned_parts)

    # Remove HTML tags like <b> or </b>
    parts = text.split()
    cleaned_parts = []
    for word in parts:
        if word.startswith("<") and word.endswith(">"):
            continue
        cleaned_parts.append(word)
    text = " ".join(cleaned_parts)

    # Remove filler words
    filler_words = ["um", "uh", "like", "you know", "basically", "literally"]
    for word in filler_words:
        text = re.sub(rf"\b{word}\b", "", text, flags=re.IGNORECASE)

    # Clean up leftover extra spaces
    text = " ".join(text.split())

    # Only keep the first 3000 characters
    return text[:3000]


# ---------------------------------------------------------------
# Function 4: AI Tagger (Jason)
# ---------------------------------------------------------------

def categorize_video(text):
    """
    Look at the cleaned text and assign a category using keyword matching.
    If there is no text at all, returns "Needs Manual Review".

    Args:
        text (str): Cleaned transcript / description / comment text.

    Returns:
        category (str): A category label like "Gaming" or "Education".
    """

    # No text at all — transcript, description, and comments all failed
    if not text:
        return "Needs Manual Review"

    text = text.lower()

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

    elif "cook" in text or "recipe" in text or "food" in text:
        return "Cooking"

    elif "workout" in text or "fitness" in text or "exercise" in text:
        return "Health & Fitness"

    # Text exists but no keywords matched
    return "Other"


# ---------------------------------------------------------------
# Function 5: Playlist Generator (Nizar)
# ---------------------------------------------------------------

def generate_playlists(categories, credentials):
    """
    Creates one private YouTube playlist for each category.

    Args:
        categories (list) : category name strings
        credentials       : the OAuth2 Google login info

    Returns:
        playlist_id_map (dict) : { "Gaming": "PLxxxxxx", ... }
    """

    youtube = build("youtube", "v3", credentials=credentials)
    playlist_id_map = {}

    for category in categories:
        try:
            response = youtube.playlists().insert(
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
            ).execute()

            playlist_id_map[category] = response["id"]
            print(f"  Created playlist: '{category}'")

        except Exception as e:
            print(f"  Failed to create playlist for '{category}': {e}")

    return playlist_id_map


# ---------------------------------------------------------------
# Function 6: Video Batch Adder (Nizar)
# ---------------------------------------------------------------

def batch_add_videos(video_category_map, playlist_id_map, credentials):
    """
    Adds every video to its matching playlist.
    Pauses every 10 inserts to stay within YouTube's daily API quota.

    Args:
        video_category_map (dict) : { "Gaming": ["vid1", "vid2"], ... }
        playlist_id_map    (dict) : { "Gaming": "PLxxxxxx", ... }
        credentials               : the OAuth2 Google login info

    Returns:
        nothing
    """

    youtube = build("youtube", "v3", credentials=credentials)

    for category, video_ids in video_category_map.items():
        playlist_id = playlist_id_map.get(category)

        if not playlist_id:
            print(f"  Warning: no playlist found for '{category}', skipping.")
            continue

        print(f"\n  Adding {len(video_ids)} videos to '{category}'...")

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

                print(f"    Added: {video_id}")

            except Exception as e:
                print(f"    Failed to add {video_id}: {e}")

            # Every 10 videos, pause to avoid hitting the API quota
            if (i + 1) % 10 == 0:
                print("    Pausing to respect API rate limit...")
                time.sleep(2)


# ---------------------------------------------------------------
# Main — runs the whole program top to bottom
# ---------------------------------------------------------------

if __name__ == "__main__":
    print("=== YouTube Auto Organizer ===\n")

    # Step 1: Get the playlist URL and log in to Google
    playlist_id, credentials = input_parser()

    # Step 2: Fetch text for every video (transcript, description, or comments)
    youtube = build("youtube", "v3", credentials=credentials)
    print("\nFetching transcripts...")
    transcripts = transcript_fetcher(playlist_id, youtube)

    # Steps 3 & 4: Clean and categorize each video
    print("\nCategorizing videos...")
    video_category_map = {}

    for video_id, raw_text in transcripts.items():
        clean_text = sanitize_transcript(raw_text)
        category = categorize_video(clean_text)
        print(f"  {video_id}  ->  {category}")

        if category not in video_category_map:
            video_category_map[category] = []
        video_category_map[category].append(video_id)

    # Tell the user how many need manual review
    manual = video_category_map.get("Needs Manual Review", [])
    if manual:
        print(f"\n  Note: {len(manual)} video(s) had no text available.")
        print("  They will get a 'Needs Manual Review' playlist for you to sort by hand.")

    # Step 5: Create a YouTube playlist for each category
    print("\nCreating playlists...")
    playlist_id_map = generate_playlists(list(video_category_map.keys()), credentials)

    # Step 6: Add each video to its playlist
    print("\nAdding videos to playlists...")
    batch_add_videos(video_category_map, playlist_id_map, credentials)

    # Save results to a file so you can see what went where
    with open("results.json", "w") as f:
        json.dump(video_category_map, f, indent=2)
    print("\nSaved full results to results.json")

    # Save the manual review list separately so it's easy to find
    if manual:
        with open("manual_review.json", "w") as f:
            json.dump(manual, f, indent=2)
        print(f"Saved {len(manual)} uncategorized video IDs to manual_review.json")

    print("\nAll done!")
