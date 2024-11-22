import numpy as np
from PIL import Image
from ultralytics import YOLO
import cv2

model = None  # Placeholder for the model


def fill_distance_to_borders(mask, max_distance=10):
    h, w = mask.shape
    filled_mask = mask.copy()

    # Find contours of the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pixels = []

    for contour in contours:
        for point in contour:
            x, y = point[0]

            # Find black pixels in all directions
            black_pixels = find_black_pixels(mask, x, y, max_distance)

            # Fill the black pixels with blue color
            for direction in black_pixels:
                for px, py in direction:
                    pixels.append((px, py))

    for px, py in pixels:
        filled_mask[px, py] = 255

    return filled_mask


def find_black_pixels(mask, start_x, start_y, max_distance):
    h, w = mask.shape
    temp = [[], [], [], []]
    result = [[], [], [], []]

    # Iterate through distances
    for i in range(1, max_distance + 1):  # Start range from 1
        points = [
            (start_x, start_y - i),  # top
            (start_x + i, start_y),  # right
            (start_x, start_y + i),  # bottom
            (start_x - i, start_y),  # left
        ]

        for index, (y, x) in enumerate(points):
            if len(result[index]):
                continue

            # Ensure the point is within mask boundaries
            if 0 <= x < h and 0 <= y < w:
                # Check if the pixel is black
                if mask[x, y] == 0:  # Assuming 0 represents black
                    temp[index].append((x, y))
                elif len(temp[index]):
                    result[index] = temp[index]
            elif len(temp[index]):
                result[index] = temp[index]

    return result


def predict_mask(img, dilation_pixels=4, max_distance=10):
    # Convert the image to a numpy array
    img_np = np.array(img)
    h, w, _ = img_np.shape

    # Run predictions using the model
    results = model.predict(source=img_np, show=False, save=False)

    result = results[0]
    img = np.copy(result.orig_img)
    final_mask = np.zeros(img.shape[:2], np.uint8)

    # Iterate each object contour
    for ci, c in enumerate(result):
        # Create contour mask
        contour = c.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
        _ = cv2.drawContours(final_mask, [contour], -1, (255, 255, 255), cv2.FILLED)

    # Apply dilation if required
    if dilation_pixels > 0:
        kernel = np.ones((dilation_pixels, dilation_pixels), np.uint8)
        final_mask = cv2.dilate(final_mask, kernel, iterations=1)

    # Fill gaps near image borders
    final_mask = fill_distance_to_borders(final_mask, max_distance)

    # Convert the mask back to a PIL image
    mask_image = Image.fromarray(final_mask)

    return mask_image


def predict(image_path):
    global model

    if not model:
        # Load the trained model
        model_path = "/Users/antonshever/Desktop/yolo-seg-bubble-best.pt"
        model = YOLO(model_path)

    # Open the image
    image = Image.open(image_path).convert("RGB")

    # Generate the mask image
    result_img = predict_mask(image)

    return result_img
