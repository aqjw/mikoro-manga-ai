from PIL import Image
import numpy as np
from pathlib import Path
import os, sys


def print_line(content):
    sys.stdout.write("\r{}".format(content))
    sys.stdout.flush()


def load_images(images_dir):
    """Loads images from all subdirectories, sorted by filename."""
    images = {}
    for subdir in sorted(Path(images_dir).iterdir(), key=lambda x: x.name):
        if subdir.is_dir():
            file_paths = [subdir / filename for filename in os.listdir(subdir)
                          if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
            file_paths.sort(key=lambda f: int(''.join(filter(str.isdigit, f.stem))))

            files_len = len(file_paths)
            print_line(f"Loading {files_len} images from '{subdir.name}'...")

            images[subdir.name] = [Image.open(path).copy() for path in file_paths]
    return images


def create_vertical_image(images):
    """Creates a single vertical image by combining all input images."""
    min_width = min(img.width for img in images)
    resized_images = [img.resize((min_width, int(img.height * min_width / img.width)), Image.Resampling.LANCZOS)
                      if img.width != min_width else img for img in images]

    total_height = sum(img.height for img in resized_images)
    new_img = Image.new('RGB', (min_width, total_height))

    current_height = 0
    for img in resized_images:
        new_img.paste(img, (0, current_height))
        current_height += img.height

    return new_img


def split_image_by_height(img, segment_height):
    """Splits an image into segments of specified height."""
    width, height = img.size
    segments = []

    for start in range(0, height, segment_height):
        end = min(start + segment_height, height)
        segments.append(img.crop((0, start, width, end)))

    return segments


def save_segment(segment, save_path):
    """Saves a segment to the specified path."""
    segment.save(save_path)


def process(images, output, segment_height):
    images_len = len(images)

    print(f"Processing {images_len} images...")
    vertical_image = create_vertical_image(images)

    segments = split_image_by_height(vertical_image, segment_height)

    for idx, segment in enumerate(segments, start=1):
        save_path = os.path.join(output, f"{idx:03d}.jpeg")
        save_segment(segment, save_path)

    print(f"{len(segments)} segments saved in '{output}'.")


def main(_input, output, segment_height):
    chapter_images = load_images(_input)
    for chapter, images in chapter_images.items():
        if images:
            print(f"Processing chapter '{chapter}' with {len(images)} images.")

            chapter_dir = Path(output) / chapter
            chapter_dir.mkdir(parents=True, exist_ok=True)

            process(images, chapter_dir, segment_height)


if __name__ == "__main__":
    _input = "./raw/18032"
    output = "./cropped_d/18032"
    segment_height = 900
    main(_input, output, segment_height)
