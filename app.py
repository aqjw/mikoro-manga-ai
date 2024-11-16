# app.py
import requests
from flask import Flask, jsonify, request
import os
from PIL import Image
from app.database import init_db, create_task
from dotenv import load_dotenv
from app.tasks import generate_mask

load_dotenv()

local_storage_path = os.getenv('LOCAL_STORAGE_PATH')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

# Initialize database
init_db()

# Supported models
MODELS = [
    'lama', 'ldm', 'zits', 'mat', 'fcf', 'sd1.5',
    'anything4', 'realisticVision1.4', 'cv2', 'manga',
    'sd2', 'paint_by_example', 'instruct_pix2pix'
]


def process_upload(task_id, image_url):
    local_task_dir = f"{local_storage_path}/{task_id}"

    # Создаем директорию для сохранения результатов, если она еще не существует
    os.makedirs(local_task_dir, exist_ok=True)

    # Путь для сохранения оригинального изображения
    processed_image_path = os.path.join(local_task_dir, "original.png")

    # Скачиваем изображение из URL и сразу сохраняем его как "original.png"
    image_path = download_image(image_url, local_task_dir)
    # Конвертируем изображение в RGB и сохраняем под именем "original.png"
    image = Image.open(image_path).convert("RGB")
    image.save(processed_image_path)

    # Удаляем временный файл, если он был сохранен под другим именем
    if image_path != processed_image_path:
        os.remove(image_path)


def process_upload_and_queue(image_url, model_name, webhook_url, task_id):
    # Обработка изображения
    process_upload(task_id, image_url)

    # Создаем задачу в базе данных
    create_task(task_id, model_name, webhook_url)

    # Запуск задачи в очереди
    generate_mask.send(task_id)

    return True


def download_image(image_url, save_dir):
    """
    Скачивает изображение по URL и сохраняет его в указанной директории.
    """
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        image_path = os.path.join(save_dir, "downloaded_image.png")
        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return image_path
    else:
        raise Exception(f"Не удалось скачать изображение. Код ответа: {response.status_code}")


@app.route('/api/process', methods=['POST'])
def upload_image():
    data = request.get_json()
    task_id = data.get('task_id')
    image_url = data.get('image_url')
    cleaning_model = data.get('cleaning_model')
    webhook_url = data.get('webhook_url')

    # Validate required fields
    if not image_url:
        return jsonify({"error": "Invalid image url"}), 400
    if not webhook_url:
        return jsonify({"error": "Invalid webhook url"}), 400
    if cleaning_model not in MODELS:
        return jsonify({"error": "Invalid cleaning model"}), 400

    # Check image format before processing
    if not image_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({"error": "Invalid image format"}), 400

    # Process image and add to queue
    queued = process_upload_and_queue(image_url, cleaning_model, webhook_url, task_id)

    if queued:
        return jsonify({"is": 'ok'}), 200
    else:
        return jsonify({"error": "Unknown error"}), 400


#
# @app.route('/api/result/<task_id>', methods=['GET'])
# def get_task_image(task_id):
#     task = get_task(task_id)
#     if not task:
#         return jsonify({"error": "Invalid task_id"}), 404
#
#     files = {
#         "original": generate_presigned_url(f"{task_id}/original.png"),
#         "mask": generate_presigned_url(f"{task_id}/mask.png"),
#         "result": generate_presigned_url(f"{task_id}/result.png")
#     }
#     task_info = {
#         "task_id": task.id,
#         "status": task.status.capitalize(),
#         "creation_date": datetime.fromisoformat(task.creation_date).strftime("%d.%m.%Y %H:%M:%S"),
#         "files": files
#     }
#
#     return jsonify(task_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5310)
