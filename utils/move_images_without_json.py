import os
import shutil
from PIL import Image
import json


def move_images_without_json(src_folder, dest_folder, height_threshold=2500):
    # Создать целевую папку, если её нет
    os.makedirs(dest_folder, exist_ok=True)

    # Получить список всех файлов в исходной папке
    files = os.listdir(src_folder)

    for file_name in files:
        file_path = os.path.join(src_folder, file_name)
        try:
            # Обрабатывать только изображения
            if file_name.lower().endswith(('png', 'jpg', 'jpeg')):
                with Image.open(file_path) as img:
                    _, height = img.size
                    # Проверить высоту изображения
                    if height < height_threshold:
                        # Проверить, существует ли JSON с таким же именем
                        json_file = os.path.splitext(file_name)[0] + ".json"
                        json_path = os.path.join(src_folder, json_file)
                        if not os.path.exists(json_path):
                            # Переместить изображение
                            shutil.move(file_path, os.path.join(dest_folder, file_name))
                            print(f"Перемещено: {file_name} (JSON отсутствует)")

        except Exception as e:
            print(f"Ошибка при обработке {file_name}: {e}")


# Пример использования
src_folder = "/Users/antonshever/Desktop/dataset/fragment"
dest_folder = "/Users/antonshever/Desktop/dataset/fragment-small-height"
move_images_without_json(src_folder, dest_folder)
