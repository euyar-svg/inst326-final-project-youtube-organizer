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

def input_parser():
    # This function will parse the input from the user
    # which is the YouTube playlist URL
    # It will return the playlist ID and the channel ID
    pass

def transcript_fetcher(playlist_id):
    # This function will fetch the transcripts of the videos
    # in the playlist and will return a list of transcripts
    pass

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