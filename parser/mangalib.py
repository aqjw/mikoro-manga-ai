from pathlib import Path
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import requests

# URL and headers for the API request
base_url = 'https://api.mangalib.me/api/manga'
img_server_url = 'https://img33.imgslib.link/'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept": "*/*",
}


def get_download_url_by_site_id(site_id):
    url = "https://api.lib.social/api/constants?fields[]=imageServers"

    try:
        # Sending GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parsing JSON response
        data = response.json()
        image_servers = data.get("data", {}).get("imageServers", [])
        # print('image_servers',image_servers)

        # Finding the 'download' URL for the given site_id
        for server in image_servers:
            if server["id"] == "download" and site_id in server.get("site_ids", []):
                return server["url"]

        return None  # If no match found

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except ValueError:
        print("Failed to parse JSON response.")
        return None


def fetch_chapters(title, start_from=None, limit=None):
    chapter_numbers = []

    response = requests.get(f"{base_url}/{title}/chapters", headers=headers)
    if response.status_code != 200:
        print(f"Ошибка загрузки страницы: {response.status_code}")
        return None

    data = response.json()
    chapters = data.get('data', [])

    for chapter in chapters:
        if start_from and chapter['index'] < start_from:
            continue
        chapter_numbers.append((chapter['volume'], chapter['number']))

    if limit and len(chapter_numbers) >= limit:
        return chapter_numbers[0:limit]

    return chapter_numbers


def fetch_images(title, chapters):
    chapter_images = {}

    for chapter_volume, chapter_number in chapters:
        key = f"{chapter_volume}-{chapter_number}"
        # Инициализируем список изображений для данной главы
        chapter_images[key] = []

        print('fetch_images', title, key)
        # Формируем URL для запроса
        response = requests.get(f"{base_url}/{title}/chapter?number={chapter_number}&volume={chapter_volume}",
                                headers=headers)
        if response.status_code != 200:
            print(f"Ошибка загрузки страницы: {response.status_code}")
            break

        # Получаем данные в формате JSON
        data = response.json()
        content = data.get('data', [])

        if 'pages' not in content:
            print("Страницы отсутствуют в контенте")
            continue

        # Извлекаем ссылки на изображения
        chapter_images[key] = [f"{img_server_url}{image['url']}" for image in content['pages']]

    return chapter_images


def download_images(chapter_images, branch_dir):
    for chapter, images in chapter_images.items():
        # Путь к директории для сохранения изображений текущей главы
        chapter_dir = branch_dir / str(chapter)
        chapter_dir.mkdir(parents=True, exist_ok=True)

        total = len(images)
        print(f"Downloading {total} images for '{chapter}'...")

        for index, image_url in enumerate(images, start=1):
            # Установка расширения .jpg
            filename = f"{index:03d}.jpg"
            file_path = chapter_dir / filename

            # Загрузка изображения с обработкой ошибок
            print('download_images', file_path)
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


def process_branch(title, output, branch, limit=1):
    chapter_numbers = fetch_chapters(title, start_from=branch, limit=limit)
    images = fetch_images(title, chapter_numbers)
    branch_dir = Path(output) / str(title)
    download_images(images, branch_dir)


# Main script logic
if __name__ == "__main__":
    # SQLite setup
    db_name = 'manga_data.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Fetch N titles from the database
    cursor.execute("SELECT id, slug_url FROM manga WHERE is_parsed = 0 LIMIT 50")
    selected_titles = cursor.fetchall()
    conn.close()

    # - - - - - - - - - - - - - - - - - - - - - - -
    # img_server_url = get_download_url_by_site_id(1)
    output = '../dataset/raw'

    def process_and_update(title_id, title_slug, output):
        branches = [1, 3, 5, 7, 9]
        for branch in branches:
            process_branch(title_slug, output, branch)

        branch_dir = Path(output) / str(title_slug)

        # Update `is_parsed` based on directory existence
        with sqlite3.connect(db_name) as conn_update:
            cursor_update = conn_update.cursor()
            if branch_dir.exists() and branch_dir.is_dir():
                cursor_update.execute("UPDATE manga SET is_parsed = 1 WHERE id = ?", (title_id,))
            else:
                cursor_update.execute("UPDATE manga SET is_parsed = 2 WHERE id = ?", (title_id,))
            conn_update.commit()


    # Start processing with threads
    with ThreadPoolExecutor(max_workers=1) as executor:
        for title_id, title_slug in selected_titles:
            executor.submit(process_and_update, title_id, title_slug, output)
