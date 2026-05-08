# inst326-final-project-youtube-organizer
a script that will automatically organize the videos in a youtube playlist
made by Emre, Nizar, and Jason

## What This Does
 
This script takes any YouTube playlist you own, reads the captions from every video, figures out what category each video belongs to (Gaming, Music, Education, etc.), and automatically creates new private playlists sorted by category — all without you having to do anything manually.
 
 
## How It Works
 
| Step | Function | Owner | What It Does |
|------|----------|-------|--------------|
| 1 | `input_parser` | Emre | Asks for playlist URL, logs into Google |
| 2 | `transcript_fetcher` | Emre | Downloads captions for every video |
| 3 | `sanitize_transcript` | Jason | Cleans up the raw caption text |
| 4 | `categorize_video` | Jason | Assigns a category based on keywords |
| 5 | `generate_playlists` | Nizar | Creates a new private playlist per category |
| 6 | `batch_add_videos` | Nizar | Adds videos into the right playlists |
 
 
## Setup (Do This Once)
 
### 1. Install dependencies
 
```
pip install google-api-python-client google-auth-oauthlib youtube-transcript-api
```
 
### 2. Get your Google credentials
 
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project
3. Go to **APIs & Services → Enable APIs** and enable **YouTube Data API v3**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Choose **Desktop App**, click Create, then click **Download JSON**
6. Rename that file to `client_secrets.json` and put it in the same folder as this script
### 3. Add yourself as a test user
 
Since the app isn't published, Google will block it unless you add yourself:
 
1. In Google Cloud Console, go to **APIs & Services → OAuth consent screen**
2. Scroll down to **Test users** and click **Add Users**
3. Add your own Gmail address
 
## How to Run
 
```
python YoutubeAutoOrganizer.py
```
 
A browser window will open asking you to log into Google — this only happens the first time. After that your login is saved to `token.json` automatically.
 
When prompted, paste a YouTube playlist URL that looks like this:
 
```
https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx
```
 
The playlist must belong to your account (the one you logged in with).
 
---
 
## What You'll Get
 
- New **private** playlists created in your YouTube account, one per category
- A `results.json` file in this folder showing which videos went where
- Console output showing progress as each step runs
---
 
## Notes
 
- Videos without captions are automatically skipped
- All new playlists are set to **private** — nothing is made public
- The script pauses every 10 video inserts to stay within YouTube's 10,000 unit daily API quota
- Your login is saved to `token.json` — don't share or commit this file
---
 
## Files in This Repo
 
| File | What It Is |
|------|------------|
| `YoutubeAutoOrganizer.py` | The main script |
| `organizer_test.py` | Unit tests |
| `client_secrets.json` | **You provide this** — downloaded from Google Cloud Console |
| `token.json` | Auto-generated after first login — do not share |
| `results.json` | Auto-generated after the script runs |
 
---
 
## Troubleshooting
 
**"This app isn't verified" warning in browser**
Click **Advanced → Go to app (unsafe)**. This is expected for student/test projects.
 
**`client_secrets.json` not found**
Make sure you downloaded it from Google Cloud Console and renamed it exactly `client_secrets.json`.
 
**Videos being skipped**
Some videos have captions disabled by the uploader. The script skips these automatically.
 
**Quota errors (403)**
You've hit YouTube's 10,000 unit daily limit. Wait 24 hours and run again — the script will pick up where it left off using `results.json`.
 