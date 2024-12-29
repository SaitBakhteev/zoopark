import logging

from tortoise.exceptions import DoesNotExist
from datetime import datetime, timedelta

from app.database.models import User, Category, Question, Survey


logger = logging.getLogger(__name__)


''' СОЗДАНИЕ ОБЪЕКТОВ МОДЕЛЕЙ '''
async def create_user(from_user):  # создание пользователя
    try:
        await User.get_or_create(tg_id=from_user.id,
                                 tg_username=from_user.username,
                                 tg_name=from_user.first_name)
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return

async def create_category(data):  # создание категории вопроса
    try:
        await Category.create(title=data['title'],
                              animals=data['animals'])
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return

async def create_question(data):
    try:
        category = await Category.get(id=int(data['category_id']))
        await Question.create(text=data['text'],
                              category=category,
                              answers=data['answers'],
                              image_path=data['image_path'],
                              animal=data['animal'])
    except DoesNotExist:
        logger.error(f"Category does not exist")
    except Exception as e:
        logger.error(f"Error creating questions: {e}")
        return

async def create_answer(data):
    try:
        question = await Category.get(id=int(data['question_id']))
        await Question.create(text=data['text'],
                              question=question,
                              is_correct=data['is_correct'])
    except DoesNotExist:
        logger.error(f"Question does not exist")
    except Exception as e:
        logger.error(f"Error creating questions: {e}")
        return

async def create_survey(data):
    try:
        user = await Category.get(id=int(data['user_id']))
        await Question.create(user=user,
                              result=data['result'])
    except DoesNotExist:
        logger.error(f"Question does not exist")
    except Exception as e:
        logger.error(f"Error creating questions: {e}")
        return


''' ПОЛУЧЕНИЕ ОБЪЕКТОВ МОДЕЛЕЙ '''
async def get_user(tg_id=None) -> User():
    try:
        return await User.get(tg_id=tg_id) if tg_id else await User.all()
    except DoesNotExist:
        logger.error(f"User does not exist")
        return

async def get_category(id=None) -> Category():
    try:
        return await Category.get(id=id) if id else await Category.all()
    except DoesNotExist:
        logger.error(f"Category does not exist")
        return

