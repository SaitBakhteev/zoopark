import logging

from app.user import keyboards as user_kb
from app.pagination import get_pagination_keyboard, show_object, pagination_handler

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart

from app.database import requests as db_req
from app import states as st


from pprint import pprint
logger = logging.getLogger(__name__)

adm = Router()


''' СОЗДАНИЕ КАТЕГОРИИ ВОПРОСОВ'''

@adm.message(F.text=='Добавить категорию')
async def add_category(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('введите название название категории:')
    await state.set_state(st.CreateCategoryFSM.title)

@adm.message(st.CreateCategoryFSM.title)
async def add_category_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Введите список животных этой категории через запятую:')
    await state.set_state(st.CreateCategoryFSM.animals)

@adm.message(st.CreateCategoryFSM.animals)
async def add_category_title(message: Message, state: FSMContext):
    try:
        await state.update_data(animals=message.text.split(','))
        data = await state.get_data()
        await db_req.create_category(data)
        await message.answer(f'Категория <b><i>{data.get('title')}</i></b> '
                             f'добавлена успешно.', parse_mode='HTML')
        await state.clear()
    except:
        await message.answer('Нужно ввести хотя бы одно животное')
        return


''' СОЗДАНИЕ ВОПРОСA '''

@adm.message(F.text=='Добавить вопрос')
async def add_question_begin(message: Message, state: FSMContext):
    await state.clear()
    categories = await db_req.get_category()
    if not categories:
        await message.answer("У вас нет в базе ни одной категории вопроса")
        await state.clear()
    else:
        category_list = [{'category_id': category.id, 'category_info': category} for category in categories]
        category_id = category_list[0]['category_id']
        await state.update_data(category_list=category_list, category_id=category_id)
        category_count, category_info = len(category_list), str(category_list[0]['category_info'])

        await message.answer('Выберите категорию вопроса:')
        await show_object(message, object_info=category_info,
                          current_index=0, total_count=category_count,
                          prefix='category', apply_text='Принять категорию')
        await state.set_state(st.CreateQuestionFSM.category)

        # Установка флага состояния, указывающего когда кнопки пагинации будут работать
        await state.update_data(select_category=True) # Флаг

# Пагинация категории
@adm.callback_query(F.data.startswith('category_prev_') | F.data.startswith('category_next_'))
async def category_pagination(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('select_category')==True:
        await pagination_handler(callback_query=query, state=state,
                                 prefix='category', apply_text='Принять категорию')

# Принятие выбранной категории
@adm.callback_query(F.data=='apply_category' and st.CreateQuestionFSM.category)
async def apply_category(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data.get('category_id')
    category = await db_req.get_category(id=category_id)
    animal_list = category.animals
    animal_count, animal = len(animal_list), str(animal_list[0])
    await query.message.answer(f'Выбрана категория <b>{str(category)}</b>.\n'
                               f'Теперь выберите животное из этой категории,'
                               f' которому будет посвящен вопрос', parse_mode='HTML')
    await state.set_state(st.CreateQuestionFSM.animal)
    await state.update_data(animal_list=animal_list, animal=animal,
                            select_category=False, select_animal=True)
    await show_object(query.message, object_info=animal,
                      current_index=0, total_count=animal_count,
                      prefix='animal', apply_text='Выбрать животное')

# Пагинация выбора животного
@adm.callback_query(F.data.startswith('animal_prev_') | F.data.startswith('animal_next_'))
async def select_animal(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('select_animal'):
        animal_list = data.get('animal_list')
        await pagination_handler(callback_query=query, state=state,
                                 prefix='animal', apply_text='Выбрать животное',
                                 total_count=len(animal_list))

# Принятие выбранного животного
@adm.callback_query(F.data=='apply_animal' and st.CreateQuestionFSM.animal)
async def apply_animal(query: CallbackQuery, state: FSMContext):
    await state.update_data(select_category=False)
    await query.message.answer('Введите текст вопроса:')
    await state.set_state(st.CreateQuestionFSM.text)

@adm.message(st.CreateQuestionFSM.text)
async def add_question_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer('Введите 4 варианта ответов разделяя их через слэш <b><i>"/"</i></b>', parse_mode='HTML')
    await state.set_state(st.CreateQuestionFSM.answers)

@adm.message(st.CreateQuestionFSM.answers)
async def add_answers(message: Message, state: FSMContext):
    await state.update_data(answer_text=message.text)
    data = await state.get_data()
    try:
        answers_text = str(data.get('answer_text'))
        answers = [{'answer': i, 'is_correct_answer': False}
                   for i in answers_text.split('/')]
        if len(answers) == 4:

            # Запись ответов в виде списка словарей в поле БД JSON-формата
            await state.update_data(answers=answers)

            await state.set_state(st.CreateQuestionFSM.correct_answers)

            # Отображение сформировавшегося вопроса
            show_question_text = (f'<b>{str(data.get('text'))}</b\n>'
                                  f'Варианты ответов:'
                                  f'1. {answers[0]['answer']}\n'
                                  f'2. {answers[1]['answer']}\n'
                                  f'3. {answers[2]['answer']}\n'
                                  f'4. {answers[3]['answer']}\n')
            await message.answer(show_question_text, parse_mode='HTML')

            await message.answer('Введите номер правильного варианта ответа от 1 до 4.')
        else:
            await message.answer('Количество вариантов ответов должно'
                                 ' быть строго 4. Аовторите ввод ответов')
            return
    except:
        await message.answer('Произошла неизвестная ошибка!')
        return

# Добавление номера правильного варианта ответа
@adm.message(st.CreateQuestionFSM.correct_answers)
async def last_step_create_question(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get('answers')
    # try:
    num = int(message.text)
    answers[num-1]['is_correct_answer'] = True
    await state.update_data(answers=answers)
    data = await state.get_data()
    await db_req.create_question(data)
    question_text = str(data.get('text'))
    await message.answer(f"Вопрос <b>{question_text}</b> добавлен успешно!", parse_mode='HTML')
    await state.clear()
    # except:
    #     await message.answer('Укаазн неорректный номер правильного ответа, повторите ввод.')
    #     return
    # await message

# @adm.callback_query(F.data.startswith("category_prev_") | F.data.startswith("category_next_"))
# async def training_types_pagination_handler(callback_query: CallbackQuery, state: FSMContext):
# # переменные, которым передаются параметры обратного вызова при пагинации
#     data = callback_query.data.split("_")
#     direction = data[1]
#     current_index = int (data[2])
#
#     if direction == "prev":
#         new_index = current_index - 1
#     else:
#         new_index = current_index + 1
#
#     # Получаем залы из базы данных
#     training_type = await db_req.get_training_types()
#     training_type_id = training_type[new_index].id
#     await state.update_data(training_type_id=training_type_id)
#
#     # Отображаем новый объект
#     await show_training_type(callback_query.message, training_type[new_index], new_index, len(training_type))
#
#     # Убираем уведомление о нажатии кнопки
#     await callback_query.answer()
#
# @user.callback_query(F.data=='apply_gym')
# async def apply_gym(callback_query: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     gym_id = int(data.get('id'))
#     gym = await db_req.get_gyms(gym_id)
#     await callback_query.answer(f'Выбран зал по адресу: {gym.address}')


#
# @adm.message(st.CreateCategoryFSM.title)
# async def add_question(message: Message, state: FSMContext):
#     await state.clear()
#     await state.set_state(st.CreateQuestionFSM.text)
#     await message.answer('Введите текст вопроса')
#
# @adm.message(st.CreateQuestionFSM.text)
# async def add_question_text(message: Message, state: FSMContext):
#     await state.update_data(text=message.text)
#     await state.set_state(st.CreateQuestionFSM.first_variant)
#     await message.answer('Введите текст 1-го варианта ответа')
#
# @adm.message(st.CreateQuestionFSM.first_variant)
# async def add_first_answer(message: Message, state: FSMContext):
#     await state.update_data(text=message.text)
#     await state.set_state(st.CreateQuestionFSM.first_variant)
#     await message.answer('Введите текст 2-го варианта ответа')


'''TEST'''
@adm.message(Command('admts'))
async def admts(message: Message):
    cat = await db_req.get_category()
    await message.answer(f'{cat[-1].title }')
