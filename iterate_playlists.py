import os
import json

PLAYLIST_IDS_FILE = '/home/ubuntu/playlist_ids.txt'
PROCESSED_INDEX_FILE = '/home/ubuntu/processed_index.txt'
BASE_URL = 'https://www.youtube.com/playlist?list='
OUTPUT_DIR = '/home/ubuntu/playlist_data/'
PARSER_SCRIPT = '/home/ubuntu/parse_playlist.py'
MARKDOWN_DIR = '/home/ubuntu/page_texts/'

def get_next_playlist_id():
    """Reads the next playlist ID to process."""
    try:
        with open(PLAYLIST_IDS_FILE, 'r') as f:
            all_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return None, None, "Playlist IDs file not found."

    try:
        with open(PROCESSED_INDEX_FILE, 'r') as f:
            last_index = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        last_index = -1

    next_index = last_index + 1

    if next_index >= len(all_ids):
        return None, None, "All playlists processed."

    next_id = all_ids[next_index]
    return next_id, next_index, None

def update_processed_index(index):
    """Updates the index of the last processed playlist."""
    with open(PROCESSED_INDEX_FILE, 'w') as f:
        f.write(str(index))

def generate_commands():
    """Generates the next set of commands for browser navigation and data parsing."""
    next_id, next_index, error = get_next_playlist_id()

    if error:
        return error, None, None

    # The browser navigation command is a tool call, so we can only output the next one.
    # The parsing command will be executed after the navigation.
    
    url = f"{BASE_URL}{next_id}"
    markdown_path = f"{MARKDOWN_DIR}{url.replace('https://www.youtube.com/', '').replace('?', '_').replace('/', '__').replace('=', '_')}.md"
    json_path = f"{OUTPUT_DIR}{next_id}.json"
    
    # We will update the index after the navigation and parsing are successful.
    # For now, we just output the commands.
    
    navigate_command = {
        "action": "browser_navigate",
        "brief": f"Navigate to playlist {next_index + 1} to extract video data.",
        "focus": "Extract the playlist title, and the list of videos with their titles and URLs.",
        "intent": "informational",
        "url": url
    }
    
    parse_command = f"python3 {PARSER_SCRIPT} {markdown_path} {next_id} > {json_path}"
    
    return next_id, navigate_command, parse_command

if __name__ == '__main__':
    # Initialize the index file if it doesn't exist
    if not os.path.exists(PROCESSED_INDEX_FILE):
        # We have already processed 6 playlists manually, so start from 6
        with open(PROCESSED_INDEX_FILE, 'w') as f:
            f.write('5') # Index is 0-based, so 5 means 6 playlists processed (0 to 5)

    next_id, navigate_command, parse_command = generate_commands()
    
    if next_id:
        print(f"NEXT_ID: {next_id}")
        print(f"NAVIGATE_COMMAND: {json.dumps(navigate_command)}")
        print(f"PARSE_COMMAND: {parse_command}")
    else:
        print(f"STATUS: {navigate_command}") # navigate_command is the error message here
