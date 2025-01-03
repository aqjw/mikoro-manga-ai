import os
import shutil
from pathlib import Path


def copy_and_rename_clear_files(base_path: str, output_dir: str):
    base_path = Path(base_path)
    output_dir = Path(output_dir)

    # Создать выходную директорию, если её нет
    output_dir.mkdir(parents=True, exist_ok=True)

    file_counter = 1  # Начинаем с 1 для имен файлов

    # Проход по всем подпапкам в base_path
    for chapter_folder in base_path.iterdir():
        clear_folder = chapter_folder / "clear"

        # Проверяем, существует ли папка clear
        if clear_folder.exists() and clear_folder.is_dir():
            for file in clear_folder.iterdir():
                if file.is_file() and file.suffix == ".png":
                    # Формируем новое имя файла
                    new_filename = f"{file_counter:03}.png"
                    new_filepath = output_dir / new_filename

                    # Копируем файл
                    shutil.copy(file, new_filepath)
                    print(f"Copied: {file} -> {new_filepath}")

                    # Увеличиваем счетчик
                    file_counter += 1

    print(f"All files copied and renamed to {output_dir}")


# Пример использования
copy_and_rename_clear_files(
    base_path="/Users/antonshever/Sites/bubble-killer/storage/app/public/manga/1",
    output_dir="/Users/antonshever/Desktop/dataset/frame-new"
)
