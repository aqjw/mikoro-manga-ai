import os
import shutil
import sys
from random import shuffle
from PIL import Image

source_dir = "../dataset/cropped"
destination_dir = "/Users/antonshever/Desktop/dataset/bubble-unsorted"
image_extensions = (".jpg", ".jpeg", ".png")

# Ensure destination folder exists
os.makedirs(destination_dir, exist_ok=True)

# Gather all files from subdirectories
all_files = []
for root, _, files in os.walk(source_dir):
    for file in files:
        if file.lower().endswith(image_extensions) and 'visual' not in file:
            all_files.append(os.path.join(root, file))

# Shuffle all collected files
shuffle(all_files)

# Copy files to the destination directory if height < 2000
for counter, source_path in enumerate(all_files, start=1):
    ext = os.path.splitext(source_path)[1]
    destination_path = os.path.join(destination_dir, f"{str(counter).zfill(4)}{ext}")
    try:
        with Image.open(source_path) as img:
            if img.height < 2000 or True: # TODO
                shutil.copy(source_path, destination_path)
                sys.stdout.write("\r{}".format(destination_path))
                sys.stdout.flush()
    except Exception as e:
        print(f"\nFailed to process {source_path} due to {e}")

print("\nAll eligible images have been moved!")
