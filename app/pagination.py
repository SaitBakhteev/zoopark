from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database import requests as db_req


# Универсальная кнопка пагинации
async def get_pagination_keyboard(current_index: int, total_count: int,
                                  prefix: str, apply_text: str,
                                  service_pagination=False):
    keyboard = InlineKeyboardBuilder()

    # Кнопка "Назад"
    if current_index > 0:
        keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data=f"{prefix}_prev_{current_index}"))
    else:
        keyboard.add(InlineKeyboardButton(text=" ", callback_data='ignore'))  # Пустая кнопка

    # Текущая страница в формате "X/Y"
    keyboard.add(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data='nothing'))

    # Кнопка "Вперед"
    if current_index < total_count - 1:
        keyboard.add(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"{prefix}_next_{current_index}"))
    else:
        keyboard.add(InlineKeyboardButton(text=" ", callback_data='ignore'))  # Пустая кнопка

    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="return_callback"))

    if service_pagination:
        keyboard.add(InlineKeyboardButton(text=f'{apply_text}', callback_data=f'apply_{prefix}'))
    else:
        # keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_{text}_{current_index}'))
        keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_{prefix}'))
    keyboard.adjust(3)
    return keyboard.as_markup()


# Отображение информации о текущем объекте при пагинации
async def show_object(message: Message, object_info: str,
                      current_index: int, total_count: int,
                      prefix: str, apply_text: str, service_pagination=True):

    await message.delete()
    await message.answer(f'<b>{object_info}</b>',
                         reply_markup=await get_pagination_keyboard(current_index=current_index,
                                                                    total_count=total_count,
                                                                    prefix=prefix,
                                                                    apply_text=apply_text,
                                                                    service_pagination=service_pagination),
                         parse_mode='HTML')


async def pagination_handler(callback_query: CallbackQuery, state: FSMContext,
                             prefix: str, apply_text: str,
                             service_pagination=True):

    # Переменные, которым передаются параметры обратного вызова при пагинации
    data = callback_query.data.split("_")
    direction, current_index = data[1], int(data[2])
    new_index = current_index - 1 if direction == "prev" else current_index + 1

    # Получаем текущий индекс объекта и краткую информацию о нем из списка словарей
    data = await state.get_data()
    object_list = data.get(f'{prefix}_list')
    object_id, object_info = (object_list[new_index][f'{prefix}_id'],
                              str(object_list[new_index][f'{prefix}_info']))

    # Обновление записи в state по id объекта при пагинации
    if prefix=='category':
        await state.update_data(category_id=object_id)
    elif prefix=='animal':
        await state.update_data(animal_id=object_id)

    # Отображаем новый объект
    await show_object(callback_query.message, object_info,
                      new_index, len(object_list),
                      prefix, apply_text, service_pagination)

    # Убираем уведомление о нажатии кнопки
    # await callback_query.answer()
