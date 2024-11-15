import os
import requests
from PIL import Image
import openai

# Инициализация ключа API для OpenAI (загружайте из окружения для безопасности)
openai.api_key = os.getenv('OPENAI_API_KEY')
local_storage_path = os.getenv('LOCAL_STORAGE_PATH')


def apply_mask_to_image(image_path, mask_path):
    """Apply mask to image for transparency."""
    image = Image.open(image_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")
    image.putalpha(mask)
    image.save(mask_path, format="PNG")


def clean_image_with_dalle(image_path, mask_path, task_id):
    """Process image with mask and send it to DALL-E for background regeneration."""

    # Применяем альфа-канал к изображению
    apply_mask_to_image(image_path, mask_path)

    # Prompt для DALL-E
    prompt = (
        "Erase all text bubbles in the masked area and restore the original background only. "
        "Ensure no text bubbles, empty shapes, or new elements appear in the result. "
        "The masked area should look as if it has no bubbles or added shapes, only the background texture."
    )

    # Отправка на DALL-E для редактирования
    send_to_dalle_edit(image_path, mask_path, prompt, task_id)


def send_to_dalle_edit(image_path, mask_path, prompt, task_id):
    """Send image and mask to DALL-E for editing and save result."""
    result_path = f"{local_storage_path}/{task_id}/result.png"

    try:
        response = openai.Image.create_edit(
            image=open(image_path, "rb"),
            mask=open(mask_path, "rb"),
            prompt=prompt,
            n=1,
        )
        image_url = response["data"][0]["url"]

        # Загрузка результата и масштабирование к исходному размеру
        original_image = Image.open(image_path)
        result_image = Image.open(requests.get(image_url, stream=True).raw)
        result_image_resized = result_image.resize(original_image.size)

        # Сохранение обработанного изображения временно, затем загрузка в S3
        result_image_resized.save(result_path)

    except Exception as e:
        print(f"Error in send_to_dalle_edit: {e}")

    finally:
        # Удаляем временные файлы после загрузки
        if os.path.exists(result_path):
            os.remove(result_path)
