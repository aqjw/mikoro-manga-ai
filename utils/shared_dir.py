import os
from flask import Flask, request, send_from_directory, render_template, redirect, url_for

app = Flask(__name__)

# Папка для скачивания и загрузки файлов
DOWNLOAD_FOLDER = "/Users/antonshever/Desktop/dataset"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Создайте папку, если её нет


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Загрузка файла
        if "file" in request.files:
            file = request.files["file"]
            if file.filename:  # Проверка наличия имени файла
                file.save(os.path.join(DOWNLOAD_FOLDER, file.filename))

    # Получить список файлов в папке, исключая директории и скрытые файлы
    files = [
        f for f in os.listdir(DOWNLOAD_FOLDER)
        if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f)) and not f.startswith(".")
    ]
    return render_template("shared_dir.html", files=files)


@app.route("/download/<filename>")
def download_file(filename):
    # Отдать файл пользователю
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
