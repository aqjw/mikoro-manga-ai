# task_proxy.py (dramatiq)

# Импорт задач из исходного модуля
from app.tasks import generate_mask, apply_mask

# Экспортируем задачи для внешнего использования
__all__ = ['generate_mask', 'apply_mask']
