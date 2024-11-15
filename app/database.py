# database.py

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# База данных и сессии SQLAlchemy
DATABASE_URL = 'sqlite:///database.db'
engine = create_engine(DATABASE_URL, echo=False)

# Сессия как синглтон
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Базовый класс для моделей
Base = declarative_base()


# Модель задачи
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    model_name = Column(String, nullable=False)
    webhook = Column(String, nullable=False)


# Функции для управления базой данных
def init_db():
    """Initialize the database and create tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_task(task_id, model_name, webhook):
    """Create a new task entry in the database."""
    with SessionLocal() as session:
        task = Task(
            id=task_id,
            model_name=model_name,
            webhook=webhook,
        )
        session.add(task)
        session.commit()
        return task


def get_task(task_id):
    """Retrieve a specific task by its ID."""
    with SessionLocal() as session:
        return session.query(Task).get(task_id)
