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

load_dotenv()

# Настройка брокера Redis для Dramatiq
broker = RedisBroker(url="redis://redis:6379")
dramatiq.set_broker(broker)

# Локальная директория для хранения файлов
local_storage_path = os.getenv('LOCAL_STORAGE_PATH')

# Инициализация базы данных
init_db()


def update_task_status(task_id, status):
    data = {"task_id": task_id, "status": status}

    # Получаем данные задачи и проверяем существование
    task = get_task(task_id)
    if not task:
        logging.error(f"Task with ID {task_id} not found.")
        return

    # Определяем путь и ключ файла по статусу
    file_info = {
        "mask_completed": ("mask.png", "mask"),
        "cleaner_completed": ("result.png", "result")
    }.get(status)

    # Условно задаем `file_path` и `file_key`
    file_path, file_key = (os.path.join(local_storage_path, f"{task_id}/{file_info[0]}"),
                           file_info[1]) if file_info else (None, None)

    # Отправка вебхука
    if task.webhook:
        # Инициализация переменной files
        files = None

        try:
            files = {file_key: open(file_path, 'rb')} if file_path and os.path.exists(file_path) else None
            response = requests.post(task.webhook, data=data, files=files, json=None if files else data)
            response.raise_for_status()
            logging.info(f"Webhook sent successfully for task {task_id} with status {status}")
        except requests.RequestException as e:
            logging.error(f"Failed to send webhook for task {task_id}: {e}")
        finally:
            if files:
                files[file_key].close()  # Закрываем файл, если он был открыт


@dramatiq.actor
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


@dramatiq.actor
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

