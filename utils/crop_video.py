import ffmpeg

# Load the video
input_path = "/Users/antonshever/Desktop/output_video.mp4"
output_path = "/Users/antonshever/Desktop/input_video.mp4"

# Crop first 20 seconds
try:
    ffmpeg.input(input_path, ss=0, t=20).output(output_path).run(overwrite_output=True)
    print("Video successfully cropped to 20 seconds.")
except ffmpeg.Error as e:
    print("An error occurred:", e)