# Youtube Auto Organizer

# This script automatically organizes your YouTube 
# watch later playlist into smaller  playlists based on the meta data
# It will operate with  a total of 6 functions:
# Input Parser (Emre)
# Transcript Fetcher (emre)
# Data Sanititzer (Jason)
# Ai Tagging (Jason)
# Playlist Generator (Nizar)
# Video Batch Adder (Nizar)

from shutil import which


def input_parser():

 """
The purpose of this function is to parse/ take the input from the user, which is the YouTube playlist URL
It will then extract and return the playlist ID and the channel ID
This information will then be used later in the script to fetch the transcripts of the videos in the playlist and to categorize them.
"""
    
def transcript_fetcher(playlist_id):
    
    """ 
This function will fetch the transcripts of the videos in the playlist with the Youtube Data Api and will return a list of transcripts
to prepare the necessary data for processing.      
    """


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
