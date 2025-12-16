import re
import os
import json
from datetime import datetime, timedelta

def parse_relative_date(relative_time_str):
    """Converts a relative time string (e.g., '12 days ago') to a datetime object."""
    relative_time_str = relative_time_str.lower().strip()
    
    # Clean up the string to only contain the relative time part
    match = re.search(r'(\d+)\s*(day|week|month|year|hour)s?\s*ago', relative_time_str)
    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    now = datetime.now()
    if 'day' in unit:
        return now - timedelta(days=value)
    elif 'week' in unit:
        return now - timedelta(weeks=value)
    elif 'month' in unit:
        return now - timedelta(days=value * 30) # Approximation
    elif 'year' in unit:
        return now - timedelta(days=value * 365) # Approximation
    elif 'hour' in unit:
        return now - timedelta(hours=value)
    else:
        return None

def parse_playlist_markdown(file_path, playlist_id):
    """Parses a YouTube playlist markdown file to extract video data and filters for recent additions."""
    videos = []
    playlist_title = "Unknown Playlist"
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {"playlist_id": playlist_id, "playlist_title": playlist_title, "recent_videos": []}

    # 1. Extract playlist title
    for line in lines:
        title_match = re.search(r'#\s*(.*?)\s*-\s*YouTube', line, re.IGNORECASE)
        if title_match:
            playlist_title = title_match.group(1).strip()
            break

    # 2. Extract video data using line-by-line pattern matching
    recent_videos = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for video index (e.g., '1', '2', '3') which marks the start of a video block
        if re.match(r'^\d+$', line) and i + 3 < len(lines):
            current_video = {}
            
            # Find the title line
            title_line_index = -1
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip() and not re.match(r'^\d+:\d+$', lines[j].strip()) and lines[j].strip() not in ['Now playing', '•']:
                    current_video['title'] = lines[j].strip()
                    title_line_index = j
                    break
            
            if title_line_index != -1:
                # Find the date line
                date_line_index = -1
                for j in range(title_line_index + 1, min(title_line_index + 10, len(lines))):
                    if 'views •' in lines[j] and 'ago' in lines[j]:
                        date_line_index = j
                        break
                
                if date_line_index != -1:
                    date_line = lines[date_line_index].strip()
                    date_match = re.search(r'views •\s*(.*?)\s*ago', date_line)
                    
                    if date_match:
                        relative_time = date_match.group(1).strip() + " ago"
                        added_date = parse_relative_date(relative_time)
                        
                        if added_date and added_date > thirty_days_ago:
                            # The URL is not in the markdown, so we'll use the title as a unique key
                            recent_videos.append({
                                'title': current_video['title'],
                                'added_date': added_date.strftime('%Y-%m-%d %H:%M:%S'),
                                'playlist_id': playlist_id,
                                'playlist_title': playlist_title
                            })

    return {"playlist_id": playlist_id, "playlist_title": playlist_title, "recent_videos": recent_videos}

if __name__ == '__main__':
    # This part is for testing the script's output format
    example_file = '/home/ubuntu/page_texts/www.youtube.com_playlist_list_PLrq7heytJY0lvuxCQ0fTm0AYvhCbOIMDS.md'
    example_id = 'PLrq7heytJY0lvuxCQ0fTm0AYvhCbOIMDS'
    if os.path.exists(example_file):
        result = parse_playlist_markdown(example_file, example_id)
        print(json.dumps(result, indent=4))
    else:
        print(f"Example file not found: {example_file}")
