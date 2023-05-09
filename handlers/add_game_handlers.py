from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from bson import ObjectId

from handlers import statistics_handlers, sportsman_menu_handlers
from utils import db_utils, strings, states, markups


async def entry_point(message: types.Message):
    await message.answer("Введите название соревнования", reply_markup=markups.remove_markup())
    await states.AddGameStates.game_name_input.set()


async def game_name_input(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage["game_name"] = message.text
    await message.answer("Введите название гольф-поля")
    await states.AddGameStates.golf_field_name_input.set()


async def golf_field_name_input(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage["golf_field_name"] = message.text
    await message.answer("Введите количество лунок")
    await states.AddGameStates.holes_number_input.set()


async def holes_number_input(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число")
        return
    number = int(message.text)
    if number < 1 or number > 18:
        await message.answer("Введите число от 1 до 18")
        return
    async with state.proxy() as storage:
        storage["holes_number"] = number
    await message.answer("Выберите Tee", reply_markup=markups.vertical_aligned_markup([
        "Красный",
        "Белый",
        "Синий",
        "Золотой",
        "Чёрный"
    ]))
    await states.AddGameStates.tee_input.set()


async def tee_input(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage["tee"] = message.text
        storage["current_hole"] = 1
        game_id = await db_utils.create_game(
            user_id=ObjectId(storage["user_id"]),
            comp_name=storage["game_name"],
            field_name=storage["golf_field_name"],
            hole_number=storage["holes_number"],
            tee=storage["tee"]
        )
        storage["game_id"] = str(game_id)
    await message.answer("Теперь заполним лунки", reply_markup=markups.remove_markup())
    await hole_start(message, state)


async def hole_start(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        await message.answer(f"Заполняем лунку номер {str(storage['current_hole'])}")
    await message.answer("Fairway", reply_markup=markups.get_yes_no_markup())
    await states.AddGameStates.hole_fairway.set()


def get_int_from_markup(text):
    if text == strings.YES_BTN:
        return 1
    elif text == strings.NO_BTN:
        return 0
    elif text == strings.TRY_BTN:
        return 2
    return None


async def hole_fairway(message: types.Message, state: FSMContext):
    fairway = get_int_from_markup(message.text)
    if fairway is None:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    async with state.proxy() as storage:
        storage["fairway"] = fairway
    await message.answer("Green in regulation", reply_markup=markups.get_yes_no_markup())
    await states.AddGameStates.hole_green.set()


async def hole_green(message: types.Message, state: FSMContext):
    green = get_int_from_markup(message.text)
    if green is None:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    async with state.proxy() as storage:
        storage["green"] = green
    await message.answer("Up and Down", reply_markup=markups.get_yes_no_try_markup())
    await states.AddGameStates.hole_up_and_down.set()


async def hole_up_and_down(message: types.Message, state: FSMContext):
    up_and_down = get_int_from_markup(message.text)
    if up_and_down is None:
        await message.answer(strings.RETRY_KEYBOARD)
    async with state.proxy() as storage:
        storage["up_and_down"] = up_and_down
    await message.answer("Putt", reply_markup=markups.remove_markup())
    await states.AddGameStates.hole_putt.set()


async def hole_putt(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число")
        return
    async with state.proxy() as storage:
        storage["putt"] = int(message.text)
    await message.answer("Hit")
    await states.AddGameStates.hole_hit.set()


async def hole_hit(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число")
        return
    async with state.proxy() as storage:
        storage["hit"] = int(message.text)
    await message.answer("Par", reply_markup=markups.horizontal_aligned_markup([
        "3", "4", "5"
    ]))
    await states.AddGameStates.hole_par.set()


async def hole_par(message: types.Message, state: FSMContext):
    if message.text not in ["3", "4", "5"]:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    async with state.proxy() as storage:
        storage["par"] = int(message.text)
        await db_utils.create_hole(
            game_id=ObjectId(storage["game_id"]),
            hole_number=storage["current_hole"],
            fairway=storage["fairway"],
            green=storage["green"],
            up_and_down=storage["up_and_down"],
            putt=storage["putt"],
            hit=storage["hit"],
            par=storage["par"]
        )
        await message.answer("Лунка заполнена!")
        storage["current_hole"] += 1
        current_hole, total = storage["current_hole"], storage["holes_number"]
        user_id = ObjectId(storage["user_id"])
    if current_hole > total:
        await message.answer("Заполнение игры завершено")
        user = await db_utils.get_user_by_id(user_id)
        if user.trainer_id is not None:
            trainer = await db_utils.get_user_by_id(user.trainer_id)
            bot = Bot.get_current()
            await bot.send_message(trainer.tg_id, f"Спортсмен <b>{user.name}</b> добавил новую игру")
        await sportsman_menu_handlers.entry_point(message)
    else:
        await hole_start(message, state)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(game_name_input, state=states.AddGameStates.game_name_input)
    dp.register_message_handler(golf_field_name_input, state=states.AddGameStates.golf_field_name_input)
    dp.register_message_handler(holes_number_input, state=states.AddGameStates.holes_number_input)
    dp.register_message_handler(tee_input, state=states.AddGameStates.tee_input)
    dp.register_message_handler(hole_fairway, state=states.AddGameStates.hole_fairway)
    dp.register_message_handler(hole_green, state=states.AddGameStates.hole_green)
    dp.register_message_handler(hole_up_and_down, state=states.AddGameStates.hole_up_and_down)
    dp.register_message_handler(hole_putt, state=states.AddGameStates.hole_putt)
    dp.register_message_handler(hole_hit, state=states.AddGameStates.hole_hit)
    dp.register_message_handler(hole_par, state=states.AddGameStates.hole_par)
