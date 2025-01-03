import requests, json, argparse
from pathlib import Path
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

base_url = "https://api.remanga.org/api/titles/chapters/"
referer = "https://remanga.org/"

headers = {
    "accept": "*/*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,hy;q=0.5,ay;q=0.4,uk;q=0.3",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://remanga.org",
    "priority": "u=1, i",
    "referer": "https://remanga.org/",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


def fetch_chapters(branch_id, start_from=None, limit=None):
    count = 40
    page = 1
    chapter_ids = []

    while True:
        url = f"{base_url}?branch_id={branch_id}&ordering=index&count={count}&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Ошибка загрузки страницы: {response.status_code}")
            break

        data = response.json()
        chapters = data.get('content', [])

        if len(chapters) == 0:
            print("Достигнут конец страниц или нет данных.", page)
            break

        for chapter in chapters:
            chapter_number = int(chapter['chapter'])
            if start_from and chapter_number < start_from:
                continue
            chapter_ids.append((chapter['id'], chapter_number))

        page += 1

        if limit and len(chapter_ids) >= limit:
            return chapter_ids[0:limit]

    return chapter_ids


def fetch_images(chapters):
    chapter_images = {}

    for chapter_id, chapter_number in chapters:
        # Инициализируем список изображений для данной главы
        chapter_images[chapter_number] = []

        # Формируем URL для запроса
        response = requests.get(f"{base_url}{chapter_id}", headers=headers)
        if response.status_code != 200:
            print(f"Ошибка загрузки страницы: {response.status_code}")
            break

        # Получаем данные в формате JSON
        data = response.json()
        # Проверяем наличие ключа 'content'
        content = data.get('content', [])

        if 'pages' not in content:
            print("Страницы отсутствуют в контенте")
            continue

        # Извлекаем ссылки на изображения
        for page_images in content['pages']:
            for image in page_images:
                chapter_images[chapter_number].append(image['link'])

    return chapter_images


def download_images(chapter_images, branch_dir):
    for chapter, images in chapter_images.items():
        # Путь к директории для сохранения изображений текущей главы
        chapter_dir = branch_dir / str(chapter)
        chapter_dir.mkdir(parents=True, exist_ok=True)

        total = len(images)
        print(f"Downloading {total} images for '{chapter}'...")

        for index, image_url in enumerate(images, start=1):
            # Извлекаем название файла из URL
            filename = image_url.split('/')[-1].split('?')[0]
            # Установка расширения .jpg
            filename = f"{index:03d}.jpg"
            file_path = chapter_dir / filename

            # Загрузка изображения с обработкой ошибок
            response = requests.get(image_url, headers=headers, stream=True)
            if response.status_code == 200:
                try:
                    # Считываем изображение и конвертируем в формат JPG
                    image = Image.open(BytesIO(response.content))
                    image.convert('RGB').save(file_path, 'JPEG')

                    print(f"Saved - {index}/{total}: {file_path}")
                except Exception as e:
                    print(f"Failed to process image {image_url}. Error: {e}")
            else:
                print(f"Failed to download image. Status code: {response.status_code}, URL: {image_url}")


def process_branch(branch, output, start_from, limit):
    chapters = fetch_chapters(branch, start_from=start_from, limit=limit)
    images = fetch_images(chapters)

    branch_dir = Path(output) / str(branch)
    download_images(images, branch_dir)


def main(branches, output, start_from, limit):
    with ThreadPoolExecutor(max_workers=4) as executor:
        for branch in branches:
            executor.submit(process_branch, branch, output, start_from, limit)


if __name__ == "__main__":
    branches = [18032]
    start_from = 1
    limit = 1
    output = './raw'
    main(branches, output, start_from, limit)
