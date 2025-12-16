import json
import glob
from collections import defaultdict

def analyze_playlist_data():
    """
    Aggregates data from all playlist JSON files to find the most recent
    additions and the most frequently appearing videos.
    """
    all_recent_videos = []
    video_frequency = defaultdict(lambda: {'count': 0, 'title': '', 'url': ''})

    # Find all JSON files in the playlist_data directory
    json_files = glob.glob('/home/ubuntu/playlist_data/*.json')

    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading or parsing {file_path}: {e}")
            continue

        # 1. Aggregate recent videos (already filtered to last 30 days)
        for video in data.get('recent_videos', []):
            all_recent_videos.append({
                'title': video['title'],
                'url': video.get('url', 'URL_MISSING'), # Safely get URL
                'added_date': video['added_date'],
                'playlist_title': data['playlist_title']
            })

        # 2. Calculate video frequency across ALL videos in all playlists
        for video in data.get('all_videos', []):
            video_url = video.get('url')
            if not video_url or video_url == 'URL_MISSING':
                # If URL is missing, we cannot track frequency reliably, so skip
                continue

            video_frequency[video_url]['count'] += 1
            video_frequency[video_url]['title'] = video['title']
            video_frequency[video_url]['url'] = video_url

    # --- 1. Most Recent Posts (from the last 30 days) ---
    # Sort by added_date (most recent first)
    all_recent_videos.sort(key=lambda x: x['added_date'], reverse=True)

    # Prepare the list for output
    recent_posts_output = []
    for video in all_recent_videos:
        # Format the date back to a readable string
        # Assuming date format is "YYYY-MM-DD HH:MM:SS" based on sample
        date_str = video['added_date'].split(' ')[0]
        recent_posts_output.append({
            'title': video['title'],
            'url': video['url'],
            'added_date': date_str,
            'playlist': video['playlist_title']
        })

    # --- 2. Videos on the Most Number of Lists ---
    # Convert dictionary values to a list and sort by count (most frequent first)
    frequent_videos_list = list(video_frequency.values())
    frequent_videos_list.sort(key=lambda x: x['count'], reverse=True)

    # Filter out videos that only appear once, as they are not "most number of lists"
    frequent_videos_output = [
        {'title': v['title'], 'url': v['url'], 'count': v['count']}
        for v in frequent_videos_list if v['count'] > 1
    ]

    # Combine results into a final dictionary
    final_results = {
        'most_recent_posts': recent_posts_output,
        'most_frequent_videos': frequent_videos_output
    }

    # Output as JSON
    print(json.dumps(final_results, indent=2))

if __name__ == "__main__":
    analyze_playlist_data()
