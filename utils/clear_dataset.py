import os
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Папка с изображениями
IMAGES_DIR = "/Users/antonshever/Desktop/dataset/bubble-new"  # Замените на путь к вашей папке
IMAGES_PER_PAGE = 100  # Количество изображений на страницу

# Убедитесь, что папка существует
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)


@app.route("/")
def index():
    # Получить список изображений
    images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    images.sort()  # Сортировка для предсказуемого порядка

    # Пагинация
    page = int(request.args.get("page", 1))  # Текущая страница
    start = (page - 1) * IMAGES_PER_PAGE
    end = start + IMAGES_PER_PAGE
    total_pages = (len(images) + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE

    return render_template(
        "clear_dataset.html",
        images=images[start:end],
        page=page,
        total_pages=total_pages,
        total_images=len(images),
    )


@app.route("/delete/<filename>", methods=["POST"])
def delete_image(filename):
    # Удалить файл
    file_path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"success": True, "message": "Image deleted successfully"})
    return jsonify({"success": False, "message": "Image not found"}), 404


@app.route("/images/<filename>")
def get_image(filename):
    # Отдать изображение клиенту
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)