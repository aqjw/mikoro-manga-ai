import numpy as np
from PIL import Image, ImageOps
import cv2
from app.lama import clean_image
from ultralytics import YOLO


def has_bubble(img_np, model):
    results = model.predict(source=img_np, show=False, save=False)
    result = results[0]
    return result.masks is not None


def predict_mask(img_np, model):
    # Запускаем предсказание
    results = model.predict(source=img_np, show=False, save=False)

    result = results[0]
    img = np.copy(result.orig_img)
    final_mask = np.zeros(img.shape[:2], np.uint8)

    # Обрабатываем контуры объектов
    for ci, c in enumerate(result):
        contour = c.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
        _ = cv2.drawContours(final_mask, [contour], -1, (255, 255, 255), cv2.FILLED)

    return final_mask


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


def segment_and_clean_bubbles(image_path, model, output_dir):
    """
    Сегментация и очистка изображения от баблов.
    """
    # Загружаем изображение и конвертируем в numpy
    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
    masks_np = []
    image_width, image_height = image.size

    # Начальные параметры для сегментации
    initial_height = 640
    slice_height = 200
    step = 100
    y_offset = 0

    while y_offset < image_height:
        region_height = initial_height  # Текущая область для очистки

        while y_offset + region_height + slice_height <= image_height:
            # Берем анализируемый слой
            analysis_box = (
                region_height,
                region_height + slice_height,
            )
            analysis_region = image_np[analysis_box[0]:analysis_box[1], :, :]

            if not has_bubble(analysis_region, model):
                break
            region_height += step
            # while end

        # Берем слой
        clear_region = image_np[y_offset:y_offset + region_height, :, :]
        mask = predict_mask(clear_region, model)
        masks_np.append(mask)

        y_offset += region_height
        # while end

    # Склеиваем массивы по вертикали
    final_mask = np.vstack(masks_np)

    dilation_pixels = 10
    # Apply dilation if required
    if dilation_pixels > 0:
        kernel = np.ones((dilation_pixels, dilation_pixels), np.uint8)
        final_mask = cv2.dilate(final_mask, kernel, iterations=1)

    # Заполняем пробелы около границ изображения
    final_mask = fill_distance_to_borders(final_mask)

    # Сохранение финального изображения
    final_image = Image.fromarray(final_mask)
    final_image.save(f"{output_dir}/cleaned_image.png")
    print(f"Процесс завершен. Результаты сохранены в {output_dir}.")


if __name__ == "__main__":
    # Пути к файлам
    model_path = "/Users/antonshever/Desktop/yolo-seg-bubble-best.pt"
    image_path = "/Users/antonshever/Desktop/5.jpeg"
    output_dir = "/Users/antonshever/Desktop"

    # image_np = np.array(Image.open(image_path).convert("RGB"))
    # mask = np.array(Image.open("/Users/antonshever/Desktop/mask.png").convert("L"))
    # mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
    # mask_np = cv2.bitwise_not(mask)
    # clean_segment = clean_image(image_np, mask_np)
    # Image.fromarray(clean_segment).save(f"{output_dir}/cleaned_image.png")

    model = YOLO(model_path)
    segment_and_clean_bubbles(image_path, model, output_dir)
