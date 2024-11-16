# tasks.py
import os
import logging
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from app.lama import clean_image_with_lama
from app.dalle import clean_image_with_dalle
from model import model_singleton
from app.predict import train_predict
from PIL import ImageOps
from dotenv import load_dotenv
from app.database import init_db, get_task
import requests

# Загрузка переменных окружения
load_dotenv()

# Настройка воркера
redis_host = os.getenv('REDIS_HOST', 'localhost')
local_storage_path = os.getenv('LOCAL_STORAGE_PATH', '/workspace/storage')

# Настройка брокера Redis для Dramatiq
broker = RedisBroker(url=f"redis://{redis_host}:6379")


@dramatiq.actor(max_retries=3)
def generate_mask(task_id):
    logging.info("Starting generate_mask task")
    update_task_status(task_id, "mask_starting")

    # Пути к файлам в локальном хранилище
    image_path = os.path.join(local_storage_path, f"{task_id}/original.png")
    mask_path = os.path.join(local_storage_path, f"{task_id}/mask.png")

    # Генерация маски и инверсия
    mask = train_predict(model_singleton(), image_path)
    mask_image = mask.convert('L')
    inverted_mask = ImageOps.invert(mask_image)
    inverted_mask.save(mask_path, format="PNG", optimize=True)
    logging.info("Mask generation completed")

    # Обновляем статус задачи в базе данных
    update_task_status(task_id, "mask_completed")

    # Запуск задачи для применения маски к изображению
    apply_mask.send(task_id)


@dramatiq.actor(max_retries=3)
def apply_mask(task_id):
    logging.info("Starting apply_mask task")
    update_task_status(task_id, "cleaner_starting")

    # Получаем данные задачи из базы данных
    task = get_task(task_id)
    if not task:
        logging.error(f"Task with ID {task_id} not found.")
        return

    # Определяем путь к файлам в локальном хранилище
    image_path = f"{local_storage_path}/{task_id}/original.png"
    mask_path = f"{local_storage_path}/{task_id}/mask.png"

    # Проверяем, какой метод обработки использовать
    # if task.model_name.startswith('lama:'):
    logging.info("Using LAMA for image processing.")
    clean_image_with_lama(image_path, mask_path, task)
    # elif task.model_name == "dalle":
    #     logging.info("Using DALLE for image processing.")
    #     clean_image_with_dalle(image_path, mask_path, task_id)
    # else:
    #     logging.error(f"Unknown model name '{task.model_name}' for task ID {task_id}.")
    #     update_task_status(task_id, "FAILED")
    #     return

    # Путь к результату
    result_path = f"{local_storage_path}/{task_id}/result.png"

    # Обновляем статус задачи в базе данных
    update_task_status(task_id, "cleaner_completed")


def update_task_status(task_id, status):
    task = get_task(task_id)
    if not task:
        logging.error(f"Task with ID {task_id} not found.")
        return

    # Статус задачи
    file_key_map = {"mask_completed": "mask", "cleaner_completed": "result"}
    file_key = file_key_map.get(status)
    file_path = os.path.join(local_storage_path, f"{task_id}/{file_key}.png") if file_key else None

    # Отправка вебхука
    if task.webhook:
        files = {file_key: open(file_path, 'rb')} if file_path and os.path.exists(file_path) else None
        try:
            response = requests.post(task.webhook, data={"task_id": task_id, "status": status}, files=files)
            response.raise_for_status()
            logging.info(f"Webhook for task {task_id} sent successfully.")
        except requests.RequestException as e:
            logging.error(f"Error sending webhook for task {task_id}: {e}")
        finally:
            if files:
                files[file_key].close()


if __name__ == "__main__":
    # Инициализация базы данных
    init_db()
