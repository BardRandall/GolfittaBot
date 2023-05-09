from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from bson import ObjectId

import config
from handlers import trainer_menu_handlers, sportsman_menu_handlers
from utils import db_utils, strings, states, markups
from utils.util import generate_table, yes_no_from_int


async def entry_point(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        user_id = ObjectId(storage["user_id"])
    user = await db_utils.get_user_by_id(user_id)
    games = await db_utils.get_sportsman_games(user.id)
    games_names = [game.competition_name + f" ({str(game.date)})" for game in games]
    await message.answer(f"Игры пользователя <b>{user.name}</b>",
                         reply_markup=markups.get_list_with_return_markup(games_names))
    await states.ListGamesStates.game_choice.set()


async def return_btn(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        is_trainer = storage["is_trainer"]
    if is_trainer:
        await trainer_menu_handlers.entry_point(message)
    else:
        await sportsman_menu_handlers.entry_point(message)


async def game_choice(message: types.Message, state: FSMContext):
    if message.text == strings.RETURN_BTN:
        await return_btn(message, state)
        return
    async with state.proxy() as storage:
        user_id = ObjectId(storage["user_id"])
        game_name = " ".join(message.text.split()[:-1])
        game = await db_utils.get_game_by_user_and_name(user_id, game_name)
        if game is None:
            await message.answer(strings.RETRY_KEYBOARD)
            return
        storage["game_id"] = str(game.id)
    await message.answer(f"Информация об игре:\n"
                         f"Дата: {str(game.date)}\n"
                         f"Название соревнования: {game.competition_name}\n"
                         f"Название поля: {game.field_name}\n"
                         f"Количество лунок: {game.hole_number}\n"
                         f"Tee: {game.tee}",
                         reply_markup=markups.get_game_markup())
    await states.ListGamesStates.menu_choice.set()


async def holes_stats(message: types.Message, state: FSMContext):
    msg = await message.answer("Статистика генерируется, ожидайте...")
    async with state.proxy() as storage:
        game_id = ObjectId(storage["game_id"])
    table_data = [
        ["Hole"],
        ["Fairway"],
        ["Green in regulation"],
        ["Up and Down"],
        ["Putt"],
        ["Hit"],
        ["Par"]
    ]
    holes = await db_utils.get_all_holes_by_game(game_id)
    holes.sort(key=lambda x: x.hole_number)

    colors = [
        [config.COLOR_WHITE for _ in range(len(holes) + 2)]
        for _ in range(len(table_data))
    ]

    fairway_sum = 0
    green_sum = 0
    up_and_down_sum = 0
    putt_sum = 0
    hit_sum = 0
    par_sum = 0
    for i, hole in enumerate(holes):
        table_data[0].append(str(hole.hole_number))
        table_data[1].append(yes_no_from_int(hole.fairway))
        table_data[2].append(yes_no_from_int(hole.green))
        table_data[3].append(yes_no_from_int(hole.up_and_down))
        table_data[4].append(str(hole.putt))
        table_data[5].append(str(hole.hit))
        table_data[6].append(str(hole.par))
        if hole.hit > hole.par:
            colors[5][i + 1] = config.COLOR_RED
        if hole.hit < hole.par:
            colors[5][i + 1] = config.COLOR_GREEN
        fairway_sum += hole.fairway
        green_sum += hole.green
        up_and_down_sum += hole.up_and_down % 2
        putt_sum += hole.putt
        hit_sum += hole.hit
        par_sum += hole.par
    table_data[0].append("Сумма")
    table_data[1].append(str(fairway_sum))
    table_data[2].append(str(green_sum))
    table_data[3].append(str(up_and_down_sum))
    table_data[4].append(str(putt_sum))
    table_data[5].append(str(hit_sum))
    table_data[6].append(str(par_sum))
    generate_table(table_data, colors, str(game_id))
    with open(f"images/{str(game_id)}.png", "rb") as photo:
        await message.answer_photo(photo)
    await msg.delete()


async def menu_choice(message: types.Message, state: FSMContext):
    if message.text == strings.RETURN_BTN:
        await return_btn(message, state)
        return
    async with state.proxy() as storage:
        game_id = ObjectId(storage["game_id"])
        game = await db_utils.get_game_by_id(game_id)
    if message.text == strings.HOLE_STAT_BTN:
        await holes_stats(message, state)
    elif message.text == strings.SHOW_COMMENT_BTN:
        btns = []
        async with state.proxy() as storage:
            if storage["is_trainer"]:
                btns.append(strings.EDIT_COMMENT_BTN)
        await message.answer(f"Комментарий тренера:\n"
                             f"{game.trainer_comment}",
                             reply_markup=markups.get_list_with_return_markup(btns))
        await states.ListGamesStates.comment_menu.set()
    else:
        await message.answer(strings.RETRY_KEYBOARD)


async def comment_menu(message: types.Message, state: FSMContext):
    if message.text == strings.RETURN_BTN:
        await return_btn(message, state)
        return
    if message.text == strings.EDIT_COMMENT_BTN:
        await message.answer("Введите обновлённый комментарий", reply_markup=markups.remove_markup())
        await states.ListGamesStates.comment_input.set()
    else:
        await message.answer(strings.RETRY_KEYBOARD)


async def comment_input(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        game_id = ObjectId(storage["game_id"])
        game = await db_utils.get_game_by_id(game_id)
    game.trainer_comment = message.text
    await game.commit()
    await message.answer("Комментарий успешно сохранён!")
    await return_btn(message, state)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(game_choice, state=states.ListGamesStates.game_choice)
    dp.register_message_handler(menu_choice, state=states.ListGamesStates.menu_choice)
    dp.register_message_handler(comment_menu, state=states.ListGamesStates.comment_menu)
    dp.register_message_handler(comment_input, state=states.ListGamesStates.comment_input)
