# worker.py
from dramatiq import set_broker
from app.tasks import broker

set_broker(broker)  # Устанавливаем брокер
