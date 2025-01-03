from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

# Укажите путь к модели и изображению
model_path = "/Users/antonshever/Desktop/toonyou_beta6"
input_image_path = "/Users/antonshever/Desktop/004.png"  # Укажите путь к изображению персонажа
output_animation_path = "/Users/antonshever/Desktop/output.gif"  # Имя файла результата

# Загрузка модели
pipe = StableDiffusionPipeline.from_pretrained(
    model_path,
    torch_dtype=torch.float16  # Оптимизация для GPU
).to("cuda")  # Используйте GPU, если доступно

print("Модель успешно загружена!")


# Функция анимации персонажа
def animate_character(image_path, prompt, steps=50, output_path="output.gif"):
    # Загружаем изображение
    image = Image.open(image_path).convert("RGB")

    # Генерация анимации
    animation = pipe(prompt=prompt, image=image, num_inference_steps=steps)

    # Сохранение анимации в GIF
    animation.save(output_path)
    print(f"Анимация сохранена: {output_path}")


# Определите текстовый запрос для анимации
prompt = "Animate the character speaking with subtle lip movements."

# Запуск анимации
animate_character(input_image_path, prompt, output_path=output_animation_path)
