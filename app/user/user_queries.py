import logging

from datetime import datetime, timedelta
import datetime as dt

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.calendar import NewCalendar

from aiogram_calendar import SimpleCalendarCallback

from app.database import requests as db_req

import app.user.keyboards as kb
import app.states as st
from app.administrator.keyboards import admin_panel

from config import TYPE_CHOICES

logger = logging.getLogger(__name__)

user = Router()


# ----- ОБРАБОТКА /start -----------
@user.message(CommandStart())
async def start(message: Message):
    if user := await db_req.get_user(message.from_user.id):
        text = 'Вы повторно хотите пройти викторину'
        if user.admin_permissions:

            '''Если пользователь обладает правами админа,
             появляется панель кнопок внизу за пределами окна переписки'''
            await message.answer(text, reply_markup=admin_panel)

        else:
            await message.answer(text)
    else:
        await db_req.create_user(message.from_user)
        await message.answer('Добро пожаловать в наш чат-бот!😊\n'
                             'Ты здесь, потому что любишь животных.\n'
                             'Ну что ж начнем нашу увлкательную викторину 😁 Поехали!')

#
#
# # ----- RETURN_CALLBACK -----------
# @user.callback_query(F.data == "return_callback")
# async def return_callback(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await callback.message.delete()
#     await callback.message.answer('Вы в главном меню', reply_markup=kb.main_kb)
#
# @user.callback_query(F.data == "ignore") # Для кнопок которые ничего не делают
# async def ignore_callback(callback_query: CallbackQuery):
#     await callback_query.answer()
#
#
# # ----- ДОБАВЛЕНИЕ АВТО В БАЗУ -----------
# @user.message(F.text.lower() == "добавить авто")
# async def message_car_add(message: Message, state: FSMContext):
#     await message.answer(
#         "Для добавления вашего авто пожалуйста введите марку вашего авто",
#         reply_markup=kb.return_kb,
#     )
#     await state.set_state(st.CreateAutoFSM.brand)
#
# @user.callback_query(F.data == "car_add_callback")
# async def cq_car_add(callback: CallbackQuery, state: FSMContext):
#     await callback.message.delete()
#     await callback.message.answer(
#         "Пожалуйста введите марку вашего авто",
#         reply_markup=kb.return_kb,
#     )
#     await state.set_state(st.CreateAutoFSM.brand)
#
#
# @user.message(st.CreateAutoFSM.brand)
# async def create_auto_brand(message: Message, state: FSMContext):
#     await state.update_data(brand=message.text, id=message.from_user.id)
#     await message.answer("Введите модель вашего авто", reply_markup=kb.return_kb)
#     await state.set_state(st.CreateAutoFSM.model)
#
#
# @user.message(st.CreateAutoFSM.model)
# async def create_auto_model(message: Message, state: FSMContext):
#     await state.update_data(model=message.text)
#     await message.answer("Введите год выпуска авто", reply_markup=kb.return_kb)
#     await state.set_state(st.CreateAutoFSM.year)
#
#
# @user.message(st.CreateAutoFSM.year)
# async def create_auto_model(message: Message, state: FSMContext):
#     text = message.text
#     try:
#         text = int(text)
#         if text < 1900 or text > datetime.now().year:
#             raise ValueError
#         await state.update_data(year=text)
#         await message.answer("Введите объём двигателя", reply_markup=kb.return_kb)
#         await state.set_state(st.CreateAutoFSM.engine)
#     except:
#         await message.answer(
#             f"Год должен быть в формате числа, ввод ограничен от 1900г до {datetime.now().year}\nПопробуйте ещё раз",
#             reply_markup=kb.return_kb,
#         )
#         return
#
#
# @user.message(st.CreateAutoFSM.engine)
# async def create_auto_engine(message: Message, state: FSMContext):
#     text = message.text
#     try:
#         text = float(text)
#         if text < 0 or text > 20:
#             raise ValueError
#         await state.update_data(engine=message.text)
#         await message.answer(
#             "Почти у цели!\nВведите пробег вашего авто в киллометрах(укажите только число)",
#             reply_markup=kb.return_kb,
#         )
#         await state.set_state(st.CreateAutoFSM.mileage)
#     except:
#         await message.answer(
#             "Объем двигателя не подходит, попробуйте ещё раз\nВводите в формате числа, или числа с точкой от 0 до 20",
#             reply_markup=kb.return_kb,
#         )
#         return
#
#
# @user.message(st.CreateAutoFSM.mileage)
# async def create_auto_mileage(message: Message, state: FSMContext):
#     text = message.text
#     try:
#         text = int(text)
#         await state.update_data(mileage=message.text)
#         await message.answer(
#             "Хотите загрузить изображение вашего авто? Пришлите файл или пропустите этот шаг, нажав /skip.",
#             reply_markup=kb.return_kb,
#         )
#         await state.set_state(st.CreateAutoFSM.image)
#     except:
#         await message.answer('Введите пробег в формате числа без лишних символов!', reply_markup=kb.return_kb)
#
#
#
# @user.message(Command('skip'))
# async def skip_image(message: Message, state: FSMContext):
#     await create_car(data=await state.get_data())
#     await state.clear()
#     await message.answer(
#         "Автомобиль добавлен без изображения!", reply_markup=kb.main_kb
#     )
#
#
# @user.message(st.CreateAutoFSM.image)
# async def create_auto_image(message: Message, state: FSMContext):
#     file_name = f"media/cars/{message.from_user.id}_{message.photo[-1].file_id}.jpg"
#
#     await message.bot.download(file=message.photo[-1].file_id, destination=file_name)
#
#     await state.update_data(image=file_name)
#
#     await create_car(data=await state.get_data())
#     await state.clear()
#     await message.answer("Автомобиль и изображение добавлены!", reply_markup=kb.main_kb)
#
#
# # ----- МЕНЮ -----------
# @user.message(Command("menu"))
# async def menu_cmd(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer(
#         "Вы в главном меню!\nВыберите действие используя встроенную клавиатуру",
#         reply_markup=kb.main_kb,
#     )
#
#
# @user.message(F.text.lower() == 'меню')
# async def menu_text_cmd(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer('Вы в главном меню!\nВыберите действие используя встроенную клавиатуру',
#                          reply_markup=kb.main_kb)
#
# @user.message(Command('help'))
# async def help_cmd(message: Message):
#     help_text = (
#         "<b>📋 Доступные команды:</b>\n\n"
#         "🔹 <b>/start</b> — начать работу с ботом\n"
#         "🔹 <b>/menu</b> — главное меню\n"
#         "🔹 <b>/profile</b> — посмотреть профиль и автомобили\n"
#         "🔹 <b>/settings</b> — настройки бота\n"
#         "🔹 <b>/help</b> — показать это сообщение\n\n"
#         "<b>🚗 Управление автомобилями:</b>\n"
#         "🔸 Добавить автомобиль — <code>Добавить Авто</code>\n"
#         "🔸 Удалить автомобиль — <code>Удалить Авто</code>\n"
#         "🔸 Создать заметку о расходах — <code>Создать заметку о расходах</code>\n\n"
#         "<b>📅 Напоминания:</b>\n"
#         "🔔 Создать напоминание — <code>Создать напоминание</code>\n"
#         "❌ Удалить напоминание — <code>Удалить напоминание</code>\n\n"
#         "<b>🛍 Покупки и избранное:</b>\n"
#         "✨ Добавить товар в избранное — <code>Добавить товар в избранное</code>\n"
#         "📜 Мои товары — <code>Мои товары</code>\n\n"
#         "❓ Если у вас возникли вопросы, напишите нам! 😊 — <b>/bug</b>"
#     )
#     await message.answer(help_text, parse_mode="HTML")
#
# @user.message(Command('bug'))
# async def cmd_bug(message: Message):
#     await message.answer('Coming soon...')
#
#
# # ----- ПРОФИЛЬ -----------
# @user.message(F.text.lower() == "автомобили") # Отлов сообщения
# async def profile_text_cmd(message: Message):
#     await profile_cmd_def(message=message)
# @user.message(Command('profile')) # отлов команды
# async def profile_cmd(message: Message):
#     await profile_cmd_def(message=message)
#
#
# async def profile_cmd_def(message): # общвя функция для отловов
#     cars = await get_all_user_cars(message.from_user.id)
#     expenses = await get_all_user_nots_per_year(message.from_user.id)
#     cars_text = "Автомобили:\n"
#
#     if cars:
#         for car in cars:
#             brand = car["brand"]
#             model = car["model"]
#             year = car["year"]
#
#             car_info = f"- {brand} {model} | год выпуска: {year}\n"
#             cars_text += car_info
#     else:
#         cars_text = "У пользователя нет автомобилей.\n"
#
#     await message.answer(
#         f"Профиль пользователя: {message.from_user.username}\n\n{cars_text}\nТраты на автомобиль за год: {expenses}",
#         reply_markup=await kb.profile_kb(message.from_user.id),
#     )
#
# @user.callback_query(F.data.startswith("car_"))
# async def settings_car_callback(callback: CallbackQuery, state: FSMContext):
#     data = callback.data.split("_")
#     text = f'{data[1]} {data[2]}'
#     cars = await get_car_by_model(callback.from_user.id, text)
#     await callback.message.delete()
#     await state.clear()
#
#     if cars:
#         for car in cars:
#             car_info = (
#                 f"Автомобиль {car['brand']} {car['model']}:\n\n"
#                 f"Производитель - {car['brand']}\n"
#                 f"Модель - {car['model']}\n"
#                 f"Год выпуска - {car['year']}\n"
#                 f"Объём двигателя - {car['engine']}\n"
#                 f"Пробег - {car['mileage']}км\n"
#             )
#
#
#             image = car.get("image", None)
#
#             if image:
#                 try:
#                     logger.info(f"{image}")
#                     await callback.message.answer_photo(
#                         photo=FSInputFile(image, filename="Car"), caption=car_info, reply_markup=kb.add_service_kb
#                     )
#                 except FileNotFoundError:
#                     await callback.message.answer(
#                         f"Изображение не найдено для {car['brand']} {car['model']}", reply_markup=kb.main_kb)
#             else:
#                 await state.set_state(st.CreateServiceFSM.type)
#                 await callback.message.answer(car_info, reply_markup=kb.add_service_kb)
#             await state.update_data(car_id=f"{car['brand']} {car['model']}", id=callback.from_user.id)
#     else:
#         await callback.message.answer("У пользователя нет такого авто.", reply_markup=kb.main_kb)
#
#
# #--------- Работа с сервисами --------------
# async def show_services(message: Message, service, current_index, total_count):  # универсальная функция для вывода
#     text = (
#         f"Тип: {service}\n")
#
#     await message.delete()
#     await message.answer(
#         text=text,
#         reply_markup=await kb.get_pagination_keyboard_service(current_index, total_count)
#     )
#
# @user.callback_query(F.data=="add_service")
# async def add_service(callback: CallbackQuery, state: FSMContext):
#     await show_services(callback.message, TYPE_CHOICES[0],0,len(TYPE_CHOICES))
#     service = TYPE_CHOICES[0]
#     await state.update_data(type=service)
#
#
# @user.callback_query(F.data.startswith("ps_") | F.data.startswith("ns_"))
# async def pagination_handler(callback_query: CallbackQuery, state: FSMContext):
#     if st.CreateServiceFSM:
#         data = callback_query.data.split("_")
#         direction = data[0]
#         current_index = int(data[1])
#
#         if direction == "prev":
#             new_index = current_index - 1
#         else:
#             new_index = current_index + 1
#
#         # Обновляем индекс в состоянии
#         # await state.update_data(current_service=new_index)
#         service = TYPE_CHOICES[new_index]
#         await state.update_data(type=service)
#
#         # Отображаем новую покупку
#         await show_services(callback_query.message, service, new_index, len(TYPE_CHOICES))
#
#         # Убираем уведомление о нажатии кнопки
#         await callback_query.answer()
#
# @user.callback_query(F.data=='apply_service')
# async def apply_services(callback: CallbackQuery, state: FSMContext):
#     await callback.message.delete()
#     data= await state.get_data()
#     type = data.get('type')
#     date = datetime.now()
#     date = str(date).split(' ')[0]
#     await callback.answer(f'Выбран тип сервиса: {type}')
#     await callback.message.answer(f"Вы подтверждаете добавление записи о {type}, на {date}?", reply_markup= await kb.confirm_add_serv_kb(type))
#
#
# @user.callback_query(F.data.startswith('confirm_add_'))
# async def add_srvice_to_Db(callback: CallbackQuery, state: FSMContext):
#     data = callback.data.split('_')[2]
#     state_data = await state.get_data()
#     await create_service(state_data)
#     await callback.message.delete()
#     await callback.message.answer(f'Создали отметку о проведённом то: \nТип - {data}',reply_markup=kb.main_kb)
#
# #----------Конец по сервису --------------
#
#
# @user.callback_query(F.data == 'list_purchases')
# async def purchase_list_callback(callback: CallbackQuery):
#     message_note = await get_user_notes(tg_id=callback.from_user.id)
#     await callback.message.answer(f'Список ваших покупок:\n{message_note}', reply_markup=kb.main_kb)
#
# @user.callback_query(F.data == 'list_service')
# async def service_list_callback(callback: CallbackQuery):
#     message_serv = await get_all_user_serv(tg_id=callback.from_user.id)
#     await callback.message.delete()
#     await callback.message.answer(message_serv, reply_markup=await kb.profile_kb(tg_id=callback.from_user.id))
#
#
# # ----- НАСТРОЙКИ -----------
# @user.message(Command('settings'))
# async def settings_cmd(message: Message):
#     await message.answer("Выберите действие", reply_markup=kb.settings_kb)
#
#
# @user.message(F.text.lower() == "удалить авто")
# async def delete_car_cmd(message: Message, state: FSMContext):
#     await message.answer(
#         "Выберите авто на встроенной клавиатуре\nВнимание восстановить авто после удаления НЕЛЬЗЯ!!!",
#         reply_markup=await kb.all_cars_kb(message.from_user.id),
#     )
#     await state.set_state(st.CarDeleteFSM.car)
#
#
# @user.message(st.CarDeleteFSM.car)
# async def delete_car_fsm(message: Message, state: FSMContext):
#     success = await delete_car_by_model(message.from_user.id, message.text)
#     if success:
#         await message.answer("Авто успешно удалено.")
#     else:
#         await message.answer("Авто не найдено или уже удалено.")
#     await state.clear()  # Завершить состояние
#     await message.answer("Вы в главном меню", reply_markup=kb.main_kb)
#
#
# # ----- ДОБАВЛЕНИЕ ЗАМЕТКИ -----------
# @user.message(F.text.lower() == "создать заметку о расходах")
# async def notes_tittle_add(message: Message, state: FSMContext):
#     await state.clear()
#     await state.set_state(st.CreateNotesFSM.title)
#     await message.answer("Введите названия купленного товара для авто:",
#                          reply_markup=kb.return_kb)
#
#
#
# @user.message(st.CreateNotesFSM.title)
# async def notes_add_coast(message: Message, state: FSMContext):
#     await state.update_data(id=message.from_user.id, title=message.text)
#     await state.set_state(st.CreateNotesFSM.price)
#     await message.answer("Введите стоимость этого товара (в вашей валюте, только цифры):",
#                          reply_markup=kb.return_kb)
#
#
# @user.message(st.CreateNotesFSM.price)
# async def notes_add_final(message: Message, state: FSMContext):
#     try:
#         await state.update_data(price=int(message.text))
#     except ValueError:
#         await message.answer("Введен неверный формат цены. Повторите ввод: ",
#                              reply_markup=kb.return_kb)
#         return
#     data = await state.get_data()
#     await create_notes(data=data)
#     await message.answer(f"Заметка о покупке товара {data.get('title')} создана.",
#                          reply_markup=kb.main_kb)
#     await state.clear()
#
#
# @user.message(F.text.lower() == 'удалить заметку')
# async def cmd_del_note(message: Message):
#     await message.answer('Выберите заметку для удаления', reply_markup= await
#                          kb.delete_user_notes_kb(message.from_user.id))
#
#
# @user.callback_query(F.data.startswith("note_"))
# async def notes_delete_callback(callback_query: CallbackQuery,):
#     await callback_query.message.answer('Удаляем заметку...')
#     data = callback_query.data.split("_")[1]
#     try:
#         await delete_note_by_title(callback_query.from_user.id, data)
#         await callback_query.message.delete()
#         await callback_query.message.answer(f'Удалили запись о трате на: {data}', reply_markup= kb.main_kb)
#     except:
#         await callback_query.message.delete()
#         await callback_query.message.answer('Удалить не получилось...\nПопробуйте сного, если не получится напишите /start', reply_markup=kb.settings_kb)
#
#
#
# # ------ НАПОМИНАНИЯ -------------
# # ------ ДОБАВЛЕНИЕ НАПОМИНАНИЯ -------------
# @user.message(F.text.lower() == "создать напоминание")
# async def start_add_reminder(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer(
#         "Выберите дату напоминания в пределах от 1 до 365 дней:",
#         reply_markup=await NewCalendar().start_calendar(),
#
#     )
#
# @user.callback_query(SimpleCalendarCallback.filter())
# async def choose_total_date_reminder(
#         callback_query: CallbackQuery,
#         callback_data: SimpleCalendarCallback,
#         state: FSMContext,
#     ):
#     # await state.clear()
#
#     calendar = NewCalendar()
#     calendar.show_alerts = True
#
#     early_date = datetime.now() + timedelta(days=1)  # ранняя дата напоминания (завтра)
#     late_date = datetime.now() + timedelta(days=365)  # поздняя дата (через год)
#
#     calendar.set_dates_range(early_date, late_date)
#     selected, date = await calendar.process_selection(callback_query, callback_data)
#
#     if selected:
#         await state.set_state(st.CreateRemindersFSM.total_date)
#         await state.update_data(
#             date=dt.date(date.year, date.month, date.day), id=callback_query.from_user.id, created_at=datetime.now()
#         )
#         await callback_query.answer (f'Выбрана дата {date.strftime("%d.%m.%Y")}')
#     hour, minute = 15,00
#     data = await state.get_data()
#     date=data.get('date')
#     try:
#         reminder_time=dt.time(hour, minute)
#         total_date = dt.datetime.combine(date, reminder_time)
#         await state.update_data(service_date=total_date)
#         await state.update_data(total_date=total_date)
#         await state.set_state(st.CreateRemindersFSM.text)
#
#     except ValueError:
#         await callback_query. message.answer('Неверно указано время напоминания')
#         return
#     await callback_query.message.answer('Введите текст напоминания')
#
#
# @user.message(st.CreateRemindersFSM.text)
# async def add_text_and_final_reminder(message: Message, state: FSMContext):
#     await state.update_data(text=message.text)
#     data = await state.get_data()
#     await create_reminder(data)
#     await message.answer(f'Напоминание о событии {data.get("text")} добавлено успешно!')
#     await state.clear()
#
# @user.message(F.text.lower() == 'удалить напоминание')
# async def delete_reminder_cmd(message: Message):
#     await message.answer('Нажмите на кнопку для удаления', reply_markup=await kb.delete_user_reminders_kb(tg_id=message.from_user.id))
#
# @user.callback_query(F.data.startswith("reminder_"))
# async def delete_reminder_with_callback(callback: CallbackQuery):
#     await callback.message.delete()
#     await callback.message.answer('Удаляем...')
#     data = callback.data.split("_")[1]
#     try:
#         await delete_user_reminders_by_text(user_id=callback.from_user.id,data=data)
#         await callback.message.delete()
#         await callback.message.answer('Напоминание "{data}" Успешно удалено')
#     except Exception as e:
#         await callback.message.delete()
#         await callback.message.answer(f'Произошла ошибка, попробуйте ещё раз или напишите /start\nКод ошибки: {e}')
#
# # ------ ДОБАВЛЕНИЕ ИНТЕРСНЫХ ПОКУПОК -------------
# @user.message(F.text.lower() == "избранное")
# async def purchases_cmd(message: Message, state: FSMContext):
#     await message.answer(
#         'Добавление интересной покупки в ваш личный список, это поможет вам в будущем вспомнить, какой товар вы покупали', reply_markup=kb.favorites_kb)
#
#
# @user.message(F.text.lower() == "добавить товар в избранное")
# async def purchases_cmd(message: Message, state: FSMContext):
#     await state.set_state(st.CreatePurchasesFSM.text)
#     await message.answer("Введите всё нужную информацию о товаре ( цена будет отдельно ):",
#                          reply_markup=kb.skip_kb)
#
#
# @user.message(st.CreatePurchasesFSM.text)
# async def purchases_add_text(message: Message, state: FSMContext):
#     if message.text == 'пропустить':
#         await message.answer("Вы пропустили этот шаг!", reply_markup=kb.main_kb)
#         await state.update_data(id=message.from_user.id, text=None)
#     else:
#         await state.update_data(id=message.from_user.id, text=message.text)
#     await state.set_state(st.CreatePurchasesFSM.price)
#     await message.answer("Введите стоимость этого товара(только цифры):",
#                          reply_markup=kb.skip_kb)
#
#
# @user.message(st.CreatePurchasesFSM.price)
# async def purchases_add_price(message: Message, state: FSMContext):
#     if message.text == 'пропустить':
#         await message.answer("Вы пропустили этот шаг!", reply_markup=kb.main_kb)
#         await state.update_data(price=None)
#     else:
#         try:
#             await state.update_data(price=int(message.text))
#         except ValueError:
#             await message.answer(
#                 "Введен неверный формат цены. Повторите ввод( цена указывается в формате полного числа ): ",
#                 reply_markup=kb.skip_kb)
#             return
#     await state.set_state(st.CreatePurchasesFSM.image)
#     await message.answer("Пришлите фото этого товара:",
#                          reply_markup=kb.skip_kb)
#
#
# @user.message(st.CreatePurchasesFSM.image)
# async def purchases_add_image(message: Message, state: FSMContext):
#     if message.text == 'пропустить':
#         await message.answer("Вы пропустили этот шаг!", reply_markup=kb.main_kb)
#         await create_purchase(data=await state.get_data())
#     else:
#         file_name = f"media/purchases/{message.from_user.id}_{message.photo[-1].file_id}.jpg"
#         await message.bot.download(file=message.photo[-1].file_id, destination=file_name)
#         await state.update_data(image=file_name)
#         await create_purchase(data=await state.get_data())
#     await state.clear()
#     await message.answer("Покупка добавлена", reply_markup=kb.main_kb)
#
# # ------ Вывод избранных покупок -------------
# @user.message(F.text.lower() == "мои товары") # после команды обрабатывает пользователя и генерирует пагинацию
# async def purchases_cmd(message: Message, state: FSMContext):
#     purchases = await get_user_purchases(message.from_user.id)
#     if not purchases:
#         await message.answer("У вас нет сохранённых покупок.", reply_markup=kb.favorites_kb)
#         return
#
#     # Сохраняем индекс текущей покупки в состояние
#     await state.update_data(current_purchase=0)
#     await message.answer('Выводим...', reply_markup=kb.skip_menu_kb)
#     # Выводим первую покупку
#     await show_purchase(message, purchases[0], 0, len(purchases))
#
#
# async def show_purchase(message: Message, purchase, current_index, total_count): # универсальная функция для вывода
#     if purchase.price == None:
#         purchase.price = 0
#     text = (
#     f"Покупка: {purchase.text}\n"
#     f"Цена: {purchase.price:.2f} ₽\n\n")
#
#     await message.delete()
#     if purchase.image:
#         try:
#             await message.answer_photo(photo=FSInputFile(purchase.image, filename="Car"), caption=text, reply_markup=await kb.get_pagination_keyboard(current_index, total_count, purchase.text))
#         except Exception as e:
#             await message.answer(f"Столкнулись с ошибкой: {e}\n возможно картинка вашего товара была удалена, хотите удалить товар?")
#     else:
#         await message.answer(
#             text,
#             reply_markup=await kb.get_pagination_keyboard(current_index, total_count, purchase.text)
#         )
#
# @user.callback_query(F.data.startswith("prev_") | F.data.startswith("next_"))
# async def pagination_handler(callback_query: CallbackQuery, state: FSMContext):
#     data = callback_query.data.split("_")
#     direction = data[0]
#     current_index = int(data[1])
#
#     # Получаем покупки пользователя из базы данных
#     user = callback_query.from_user
#     purchases = await get_user_purchases(user.id)
#
#     if direction == "prev":
#         new_index = current_index - 1
#     else:
#         new_index = current_index + 1
#
#     await callback_query.answer('TEST 100')
#     # Обновляем индекс в состоянии
#     await state.update_data(current_purchase=new_index)
#
#     # Отображаем новую покупку
#     await show_purchase(callback_query.message, purchases[new_index], new_index, len(purchases))
#
#     # Убираем уведомление о нажатии кнопки
#     await callback_query.answer()
#
#
# @user.callback_query(F.data.startswith("delete_"))
# async def confirm_callback(callback_query: CallbackQuery):
#     await callback_query.message.delete()
#     data = callback_query.data.split("_")
#     text = data[1]
#     index = int(data[2])
#     index -= 1
#     await callback_query.message.answer(f'Вы уверенны, что хотите удалить покупку: {text}', reply_markup= await kb.confirmation_delete_kb(text, index))
#
# @user.callback_query(F.data.startswith('del_'))
# async def delete_callback(callback: CallbackQuery):
#     data = callback.data.split("_")
#     text = data[1]
#     await callback.message.delete()
#     await delete_user_purchases(user_id=callback.from_user.id, text=text)
#     await callback.message.answer('Удалено.', reply_markup = kb.main_kb)
