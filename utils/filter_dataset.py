import os
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Папка с изображениями
IMAGES_DIR = "/Users/antonshever/Desktop/dataset/bubble-unsorted"  # Замените на путь к вашей папке
IMAGES_PER_PAGE = 100  # Количество изображений на страницу

# Целевые папки для перемещения
TARGET_DIRS = {
    "frame": "/Users/antonshever/Desktop/dataset/bubble-frame",
    # "shadow": "/Users/antonshever/Desktop/dataset/bubble-shadow",
    # "unique": "/Users/antonshever/Desktop/dataset/bubble-unique",

    # "narrative": "/Users/antonshever/Desktop/dataset/bubble-narrative",
    # "dialog": "/Users/antonshever/Desktop/dataset/bubble-dialog",
    # "thought": "/Users/antonshever/Desktop/dataset/bubble-thought",
    # "shout": "/Users/antonshever/Desktop/dataset/bubble-shout",
    # "system": "/Users/antonshever/Desktop/dataset/bubble-system",
    # "sfx": "/Users/antonshever/Desktop/dataset/bubble-sfx",
}

# Создайте целевые папки, если они не существуют
for target in TARGET_DIRS.values():
    os.makedirs(target, exist_ok=True)


@app.route("/")
def index():
    images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    images.sort()

    page = int(request.args.get("page", 1))
    start = (page - 1) * IMAGES_PER_PAGE
    end = start + IMAGES_PER_PAGE
    total_pages = (len(images) + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE

    return render_template(
        "filter_dataset/index.html",
        images=images[start:end],
        page=page,
        total_pages=total_pages,
        total_images=len(images),
        target_dirs=TARGET_DIRS,
        current_folder=None,  # Главная страница
        folder_path=IMAGES_DIR,
    )



@app.route("/move/<source>/<filename>/<target>", methods=["POST"])
def move_image(source, filename, target):
    # Определяем исходную и целевую папки
    source_path = os.path.join(IMAGES_DIR if source == "main" else TARGET_DIRS.get(source, ""), filename)
    destination_path = os.path.join(IMAGES_DIR if target == "main" else TARGET_DIRS.get(target, ""), filename)

    # Проверяем, существует ли исходный файл
    if not os.path.exists(source_path):
        return jsonify({"success": False, "message": "Source file not found"}), 404

    # Проверяем корректность целевой папки
    if target != "main" and target not in TARGET_DIRS:
        return jsonify({"success": False, "message": "Invalid target folder"}), 400

    try:
        shutil.move(source_path, destination_path)
        return jsonify({"success": True, "message": f"Image moved to {target}"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/images/<folder>/<filename>")
def get_image(folder, filename):
    if folder == "main":
        directory = IMAGES_DIR
    elif folder in TARGET_DIRS:
        directory = TARGET_DIRS[folder]
    else:
        return "Invalid folder", 404

    return send_from_directory(directory, filename)


@app.route("/folder/<target>")
def view_folder(target):
    if target not in TARGET_DIRS:
        return "Invalid folder", 404

    folder_path = TARGET_DIRS[target]
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    images.sort()

    # Пагинация
    page = int(request.args.get("page", 1))  # Текущая страница
    start = (page - 1) * IMAGES_PER_PAGE
    end = start + IMAGES_PER_PAGE
    total_pages = (len(images) + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE

    return render_template(
        "filter_dataset/index.html",
        images=images[start:end],
        page=page,
        total_pages=total_pages,
        total_images=len(images),
        target_dirs=TARGET_DIRS,
        current_folder=target,
        folder_path=folder_path,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)

