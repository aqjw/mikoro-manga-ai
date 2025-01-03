import numpy as np
from PIL import Image, ImageOps
import cv2
from app.lama import clean_image
from app.predict import predict


def fill_distance_to_borders(mask, max_distance=10):
    """
    Заполняет пробелы в маске около границ изображения.
    """
    h, w = mask.shape
    for x in range(w):
        for y in range(h):
            if mask[y, x] == 0 and (
                y < max_distance or y > h - max_distance or x < max_distance or x > w - max_distance
            ):
                mask[y, x] = 255
    return mask


def predict_mask(img, model, dilation_pixels=4, max_distance=10):
    """
    Предсказание маски баблов на изображении.
    """
    # Преобразуем изображение в numpy массив
    img_np = np.array(img)
    h, w, _ = img_np.shape

    # Запускаем предсказание
    results = model.predict(source=img_np, show=False, save=False)

    result = results[0]
    img = np.copy(result.orig_img)
    final_mask = np.zeros(img.shape[:2], np.uint8)

    # Обрабатываем контуры объектов
    for ci, c in enumerate(result):
        contour = c.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
        _ = cv2.drawContours(final_mask, [contour], -1, (255, 255, 255), cv2.FILLED)

    # Применяем дилатацию
    if dilation_pixels > 0:
        kernel = np.ones((dilation_pixels, dilation_pixels), np.uint8)
        final_mask = cv2.dilate(final_mask, kernel, iterations=1)

    # Заполняем пробелы около границ изображения
    final_mask = fill_distance_to_borders(final_mask, max_distance)

    # Конвертируем маску обратно в PIL
    mask_image = Image.fromarray(final_mask)

    return mask_image


def segment_and_clean_bubbles(image_path, model, output_dir):
    """
    Сегментация и очистка изображения от баблов.
    """
    # Загружаем изображение и конвертируем в numpy
    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
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
                0,
                y_offset + region_height,
                image_width,
                y_offset + region_height + slice_height,
            )
            analysis_region = image_np[analysis_box[1]:analysis_box[3], :, :]
            analysis_pil = Image.fromarray(analysis_region)

            # Предсказание баблов
            mask = predict_mask(analysis_pil, model)

            if np.any(np.array(mask)):
                # Если баблы найдены, расширяем текущую область
                region_height += step
            else:
                # Если баблов нет, выходим из цикла проверки
                break

        # Очистка текущей области, если баблы не пересекаются
        clean_box = (0, y_offset, image_width, y_offset + region_height)
        clean_region = image_np[clean_box[1]:clean_box[3], :, :]
        mask = np.zeros(clean_region.shape[:2], dtype=np.uint8)
        clean_segment = clean_image(clean_region, mask)
        image_np[clean_box[1]:clean_box[3], :, :] = clean_segment

        # Переход к следующему сегменту
        y_offset += region_height

    # Сохранение финального изображения
    final_image = Image.fromarray(image_np)
    final_image.save(f"{output_dir}/cleaned_image.png")
    print(f"Процесс завершен. Результаты сохранены в {output_dir}.")


if __name__ == "__main__":
    from ultralytics import YOLO

    # Пути к файлам
    model_path = "/Users/antonshever/Desktop/yolo-seg-bubble-best.pt"
    image_path = "/Users/antonshever/Desktop/001.jpg"
    output_dir = "/Users/antonshever/Desktop"

    # Загрузка модели
    model = YOLO(model_path)

    # Запуск
    segment_and_clean_bubbles(image_path, model, output_dir)
