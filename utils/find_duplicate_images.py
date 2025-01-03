import os
from PIL import Image
from imagehash import average_hash
import numpy as np


def find_duplicate_images(folder_path, similarity_threshold):
    # Підтримувані формати зображень
    supported_formats = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}

    # Зберігаємо хеші зображень
    image_hashes = {}
    duplicates = []

    # Перебираємо файли в папці
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Перевіряємо, чи є файл зображенням
        if os.path.isfile(file_path) and any(file_path.lower().endswith(ext) for ext in supported_formats):
            try:
                with Image.open(file_path) as img:
                    # Генеруємо хеш
                    img_hash = average_hash(img)

                    # Порівнюємо з іншими хешами
                    for existing_file, existing_hash in image_hashes.items():
                        similarity = (1 - (img_hash - existing_hash) / len(img_hash.hash.flatten())) * 100
                        if similarity >= similarity_threshold:
                            duplicates.append((file_path, existing_file, similarity))

                    # Додаємо хеш до списку
                    image_hashes[file_path] = img_hash
            except Exception as e:
                print(f"Не вдалося обробити файл {file_path}: {e}")

    return duplicates


if __name__ == '__main__':
    # Приклад використання
    folder = "/Users/antonshever/Desktop/dataset/frame-new"
    duplicates = find_duplicate_images(folder, similarity_threshold=97)

    if duplicates:
        for duplicate in duplicates:
            print(f"Дублікат: {duplicate[0]} та {duplicate[1]} зі схожістю {duplicate[2]:.2f}%")
    else:
        print("Дублікатів не знайдено.")
