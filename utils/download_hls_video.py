import m3u8
import requests
from urllib.parse import urljoin


def download_hls_video_with_lib(playlist_url, output_file):
    # Parse the HLS playlist
    playlist = m3u8.load(playlist_url)

    if not playlist.segments:
        print("No segments found in the playlist.")
        return

    print(f"Found {len(playlist.segments)} segments. Starting download...")

    base_url = playlist_url.rsplit('/', 1)[0] + '/'

    with open(output_file, 'wb') as output:
        # Download and concatenate all segments
        for idx, segment in enumerate(playlist.segments):
            segment_url = urljoin(base_url, segment.uri)
            print(f"Downloading segment {idx + 1} from {segment_url}...")
            segment_response = requests.get(segment_url, stream=True)

            if segment_response.status_code == 200:
                for chunk in segment_response.iter_content(chunk_size=1024):
                    output.write(chunk)
            else:
                print(f"Failed to download segment {idx + 1}.")

    print("Download complete. Video saved as", output_file)


# Example usage
playlist_url = "https://sicarus.cloud.kodik-storage.com/useruploads/ada55837-6207-45c2-af0d-79405ddb578c/786f5a4a7602e7e1c7abf46f20070f43:2024121209/720.mp4:hls:manifest.m3u8"
output_file = "output_video.mp4"
download_hls_video_with_lib(playlist_url, output_file)