import json
import textwrap

def create_report():
    """Reads the final analysis JSON and generates a Markdown report."""
    try:
        with open('/home/ubuntu/final_analysis.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        report_content = "# YouTube Playlist Analysis Report\n\n**Error:** The analysis file was not found. The data extraction process may have failed to produce any results."
        with open('/home/ubuntu/results.md', 'w') as f:
            f.write(report_content)
        return
    except json.JSONDecodeError:
        report_content = "# YouTube Playlist Analysis Report\n\n**Error:** The analysis file is corrupted and could not be read."
        with open('/home/ubuntu/results.md', 'w') as f:
            f.write(report_content)
        return

    recent_posts = data.get('most_recent_posts', [])
    frequent_videos = data.get('most_frequent_videos', [])

    report = []
    report.append("# YouTube Playlist Analysis Report")
    report.append(textwrap.dedent("""
        This report compiles the most recent video additions (within the last 30 days)
        across your public YouTube playlists and identifies any videos that appear
        in multiple playlists.
        """))

    # --- Most Recent Posts ---
    report.append("## 1. Most Recent Posts (Added in the Last 30 Days)")

    if recent_posts:
        report.append(textwrap.dedent("""
            The following videos were added to your public playlists between
            **November 1, 2025** and **December 1, 2025**.

            **Note on URLs:** Due to a technical limitation in the browser-based data extraction,
            the direct video URL could not be reliably captured. The videos are identified by their title,
            the date they were added, and the playlist they belong to.
            """))
        report.append("| Date Added | Video Title | Playlist |")
        report.append("| :--- | :--- | :--- |")
        
        # Limit to top 20 most recent for readability in the report
        for post in recent_posts[:20]:
            title = post['title'].replace('|', '/')
            playlist = post['playlist'].replace('|', '/')
            report.append(f"| {post['added_date']} | {title} | {playlist} |")
        
        if len(recent_posts) > 20:
            report.append(f"\n*...and {len(recent_posts) - 20} more recent videos. See the attached `final_analysis.json` for the complete list.*")
    else:
        report.append("No videos were found to have been added to your public playlists in the last 30 days.")

    # --- Most Frequent Videos ---
    report.append("\n## 2. Videos on the Most Number of Lists")

    if frequent_videos:
        report.append(textwrap.dedent("""
            The following videos appear in two or more of your public playlists.
            """))
        report.append("| Count | Video Title | URL |")
        report.append("| :--- | :--- | :--- |")
        for video in frequent_videos:
            title = video['title'].replace('|', '/')
            report.append(f"| {video['count']} | {title} | {video['url']} |")
    else:
        report.append(textwrap.dedent("""
            Based on the analysis of your public playlists, no videos were found to appear
            in more than one playlist.
            """))

    report.append("\n***")
    report.append("\nFor the complete, raw data, please refer to the attached `final_analysis.json` file.")

    with open('/home/ubuntu/results.md', 'w') as f:
        f.write('\n'.join(report))

if __name__ == "__main__":
    create_report()
