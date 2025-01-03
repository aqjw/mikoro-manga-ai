from PIL import ImageDraw
import numpy as np


def resize_image(img, resize_width):
    """Resize image proportionally to a specified width."""
    aspect_ratio = img.height / img.width
    resize_height = int(resize_width * aspect_ratio)
    return img.resize((resize_width, resize_height))


def calculate_scale(img, resized_img):
    """Calculate the scale factor for height."""
    return img.height / resized_img.height


def is_row_uniform(row, color_tolerance):
    """Check if a row of pixels is uniform within a color tolerance."""
    return np.std(row, axis=0).max() <= color_tolerance


def find_horizontal_dividers(img_data, scale_y, height_threshold, color_tolerance):
    """Find divider ranges based on uniform rows."""
    dividers = []
    consecutive = 0
    start = None

    for y, row in enumerate(img_data):
        if is_row_uniform(row, color_tolerance):
            if consecutive == 0:
                start = y
            consecutive += 1
        else:
            if consecutive >= height_threshold:
                dividers.append((int(start * scale_y), int((start + consecutive) * scale_y)))
            consecutive = 0
            start = None

    if consecutive >= height_threshold:  # Handle last sequence
        dividers.append((int(start * scale_y), int((start + consecutive) * scale_y)))

    return dividers


def draw_dividers(img, dividers):
    """Draw dividers on the original image."""
    visual = img.convert("RGB")
    draw = ImageDraw.Draw(visual)
    for start, end in dividers:
        draw.rectangle(((0, start), (img.width, end)), outline=(255, 0, 0), fill=(255, 0, 0))
    return visual


def find_dividers(img, height_threshold=1.1, color_tolerance=1.5, resize_width=20):
    # Resize image and calculate scale
    resized_img = resize_image(img, resize_width)
    scale_y = calculate_scale(img, resized_img)

    # Convert resized image to NumPy array
    img_data = np.array(resized_img.convert("RGB"))

    # Find divider ranges
    dividers = find_horizontal_dividers(img_data, scale_y, height_threshold, color_tolerance)

    # Draw dividers
    visual = draw_dividers(img, dividers)

    return visual, dividers
