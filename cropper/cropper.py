from PIL import Image, ImageOps
import numpy as np
from pathlib import Path
import os, sys
from concurrent.futures import ThreadPoolExecutor
from divider.divider import find_dividers


def print_line(content):
    sys.stdout.write("\r{}".format(content))
    sys.stdout.flush()


def load_images(images_dir):
    images = {}

    # Проходим по всем поддиректориям в указанной директории
    for subdir in sorted(Path(images_dir).iterdir(), key=lambda x: x.name):
        if subdir.is_dir():
            # Создаем список путей к файлам изображений в поддиректории
            file_paths = [subdir / filename for filename in os.listdir(subdir)
                          if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]

            # Сортируем список путей по номеру, извлекаемому из имени файла
            file_paths.sort(key=lambda f: int(''.join(filter(str.isdigit, f.stem))))

            files_len = len(file_paths)
            print_line(f"Loading {files_len} images from '{subdir.name}'...")

            # Инициализируем список изображений для данной поддиректории
            images[subdir.name] = []

            # Загружаем изображения по отсортированным путям
            for index, path in enumerate(file_paths, start=1):
                print_line(f"Load Image {index}/{files_len} from '{path}'")

                with Image.open(path) as img:
                    if img.height > min_dimensions[0] and img.width > min_dimensions[1]:
                        images[subdir.name].append(img.copy())

    return images


def create_vertical_image(img_1, img_2):
    """Создает вертикальное изображение из двух изображений с одинаковой шириной."""
    # Находим изображение с меньшей шириной
    min_width = min(img_1.width, img_2.width)

    # Изменяем размер изображений, чтобы их ширина была одинаковой
    if img_1.width != min_width:
        img_1 = img_1.resize((min_width, int(img_1.height * min_width / img_1.width)), Image.Resampling.LANCZOS)
    if img_2.width != min_width:
        img_2 = img_2.resize((min_width, int(img_2.height * min_width / img_2.width)), Image.Resampling.LANCZOS)

    # Объединяем изображения вертикально
    total_height = img_1.height + img_2.height
    new_img = Image.new('RGB', (min_width, total_height))
    new_img.paste(img_1, (0, 0))
    new_img.paste(img_2, (0, img_1.height))

    return new_img


def split_image(img, dividers, min_dimensions):
    min_width, min_height = min_dimensions

    if img.width < min_width:
        return []

    parts = []
    start = 0

    for start_divider, end_divider in dividers:
        if start_divider - start >= min_height:
            # Извлекаем часть изображения между текущим `start` и `start_divider`
            part = img.crop((0, start, img.width, start_divider))
            if is_not_empty(part):
                parts.append(part)

        # Обновляем начало на конец текущего разделителя
        start = end_divider + 1

    # Добавляем последнюю часть, если она соответствует критериям
    if img.height - start >= min_height:
        part = img.crop((0, start, img.width, img.height))
        if is_not_empty(part):
            parts.append(part)

    return parts


def is_not_empty(img, threshold=5):
    """Определяет, не является ли часть изображения 'пустой'."""
    data = np.array(img)
    if np.std(data) < threshold:
        return False
    return True


def remove_image_whitespace(img, tolerance=5):
    # Конвертируем изображение в RGB
    img = img.convert("RGB")

    # Преобразуем изображение в массив numpy
    img_array = np.array(img)

    # Рассчитываем стандартное отклонение по строкам и столбцам
    row_std = np.std(img_array, axis=(1, 2))  # Отклонение по строкам
    col_std = np.std(img_array, axis=(0, 2))  # Отклонение по столбцам

    # Определяем строки и столбцы с вариативностью цвета
    non_uniform_rows = row_std > tolerance
    non_uniform_cols = col_std > tolerance

    # Проверяем, есть ли строки и столбцы с вариативностью
    if not np.any(non_uniform_rows) or not np.any(non_uniform_cols):
        # Если нет вариативных строк или столбцов, возвращаем оригинальное изображение
        return img

    # Находим границы для обрезки
    upper = np.argmax(non_uniform_rows)  # Первая строка с вариативностью
    lower = len(non_uniform_rows) - np.argmax(non_uniform_rows[::-1])  # Последняя строка
    left = np.argmax(non_uniform_cols)  # Первый столбец с вариативностью
    right = len(non_uniform_cols) - np.argmax(non_uniform_cols[::-1])  # Последний столбец

    # Обрезаем изображение по найденным границам
    return img.crop((left, upper, right, lower))


def check_image_dimensions(img, min_dimensions):
    # Получение размеров изображения
    width, height = img.size

    # Распаковка кортежа с минимальными размерами
    min_width, min_height = min_dimensions

    # Проверка размеров
    return width > min_width and height > min_height


def save_segment(segment, min_dimensions, save_path, border=10, border_color='white'):
    # Remove whitespace
    new_segment = remove_image_whitespace(segment)

    # Check dimensions
    if check_image_dimensions(new_segment, min_dimensions):
        new_segment.save(save_path)
        return True
        #
        # # Add border without overlapping the image
        # width, height = new_segment.size
        # new_canvas_size = (width + 2 * border, height + 2 * border)
        #
        # # Create new canvas with the border color
        # bordered_image = Image.new('RGB', new_canvas_size, border_color)
        #
        # # Paste the original image onto the center of the new canvas
        # bordered_image.paste(new_segment, (border, border))
        #
        # # Save the final image
        # bordered_image.save(save_path)
        # return True

    return False


def process(images, output, min_dimensions):
    images_len = len(images)

    current_img = images[0]
    saved_index = 1

    def save_path(prefix=''):
        """Формирует путь для сохранения сегмента изображения."""
        return os.path.join(output, f"{prefix}{saved_index:03d}.jpeg")

    for index, next_img in enumerate(images, start=1):
        print_line(f"Process Image... {index}/{images_len}")

        if images_len == 1 or index == 1:
            # Если изображение одно или первое, работаем с ним как с вертикальным
            vert_img = current_img
        elif not current_img:
            vert_img = current_img
        else:
            # Создание вертикального изображения из текущего и следующего
            vert_img = create_vertical_image(current_img, next_img)

        # Поиск разделителей на вертикальном изображении
        visual, dividers = find_dividers(vert_img)

        if len(dividers) == 0 and vert_img.height > 5_000:
            visual, dividers = find_dividers(vert_img, height_threshold=1.8)
            if len(dividers) == 0:
                if save_segment(vert_img, min_dimensions, save_path()):
                    saved_index += 1
                    current_img = None
                continue

        visual.save(save_path('visual-'))
        # Разделение изображения на сегменты
        segments = split_image(vert_img, dividers, min_dimensions)

        # print_line(f"{output} | height {current_img.height} | dividers {len(dividers)}")

        current_img = segments.pop()

        for segment in segments:
            if save_segment(segment, min_dimensions, save_path()):
                saved_index += 1

    # Сохранение последнего сегмента
    if save_segment(current_img, min_dimensions, save_path()):
        saved_index += 1

    print(f"\n{images_len} images are processed and divided into {saved_index - 1} segments.")


def get_folders(directory):
    # Получаем список всех папок на первой глубине
    return [folder for folder in Path(directory).iterdir() if folder.is_dir()]


def process_folder(folder, root_output, min_dimensions):
    print(f"Processing folder: {folder.name}")
    # Загрузка изображений из директорий
    chapter_images = load_images(folder)

    # Обработка изображений по главам
    for chapter, images in chapter_images.items():
        if len(images):
            print(f"\nProcessing chapter '{chapter}' with {len(images)} images.\n")

            # Создаем директорию для сохранения, включая поддиректорию для главы
            chapter_dir = Path(root_output) / folder.name / chapter
            chapter_dir.mkdir(parents=True, exist_ok=True)

            process(images, chapter_dir, min_dimensions)


if __name__ == "__main__":
    root_input = "../dataset/raw"
    root_output = "../dataset/cropped"
    min_dimensions = (100, 100)

    # Получаем список всех папок
    folders = get_folders(root_input)

    # Используем пул потоков
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Запускаем обработку папок в потоках
        for folder in folders:
            executor.submit(process_folder, folder, root_output, min_dimensions)
