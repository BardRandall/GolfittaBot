from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext

from handlers import list_games_handlers
from utils import db_utils, strings, states, markups


async def entry_point(message: types.Message):
    await message.answer(strings.TRAINER_MENU_WELCOME, reply_markup=markups.get_trainer_menu_markup())
    await states.TrainerStates.menu_choice.set()


async def menu_choice(message: types.Message):
    if message.text == strings.ADD_SPORTSMAN_BTN:
        await message.answer(strings.ADD_SPORTSMAN_TEXT, reply_markup=markups.get_cancel_markup())
        await states.TrainerStates.add_input.set()
    elif message.text == strings.LIST_SPORTSMAN_BTN:
        sportsmen = await db_utils.get_trainer_sportsmen(message.from_user.id)
        sportsmen_names = [s.name for s in sportsmen]
        await message.answer(strings.LIST_CHOOSE_TEXT,
                             reply_markup=markups.get_list_with_cancel_markup(sportsmen_names))
        await states.TrainerStates.list_choose.set()
    elif message.text == strings.REMOVE_SPORTSMAN_BTN:
        sportsmen = await db_utils.get_trainer_sportsmen(message.from_user.id)
        sportsmen_names = [s.name for s in sportsmen]
        await message.answer(strings.REMOVE_SPORTSMAN_CHOOSE,
                             reply_markup=markups.get_list_with_cancel_markup(sportsmen_names))
        await states.TrainerStates.remove_choice.set()
    else:
        await message.answer(strings.RETRY_KEYBOARD)


async def add_input(message: types.Message):
    if message.text == strings.CANCEL_BTN:
        await entry_point(message)
        return
    users = await db_utils.find_users_like(message.text, only_trainer=True)
    if not users:
        await message.answer(strings.NO_USERS_MATCH)
        return
    users_names = [user.name for user in users]
    await message.answer(strings.ADD_SPORTSMAN_CHOOSE,
                         reply_markup=markups.get_list_with_cancel_markup(users_names))
    await states.TrainerStates.add_choose.set()


async def add_choose(message: types.Message):
    if message.text == strings.CANCEL_BTN:
        await entry_point(message)
        return
    user = await db_utils.get_user_by_name(message.text)
    if user is None:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    trainer = await db_utils.get_user_by_tg_id(message.from_user.id)
    user.trainer_id = trainer.id
    await user.commit()
    await message.answer(strings.ADD_SPORTSMAN_SUCCESSFUL.format(message.text))
    await entry_point(message)


async def list_choose(message: types.Message, state: FSMContext):
    if message.text == strings.CANCEL_BTN:
        await entry_point(message)
        return
    user = await db_utils.get_user_by_name(message.text)
    if user is None:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    async with state.proxy() as storage:
        storage["user_id"] = str(user.id)
    await list_games_handlers.entry_point(message, state)


async def remove_choice(message: types.Message):
    if message.text == strings.CANCEL_BTN:
        await entry_point(message)
        return
    user = await db_utils.get_user_by_name(message.text)
    if user is None:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    user.trainer_id = None
    await user.commit()
    bot = Bot.get_current()
    await bot.send_message(user.tg_id, strings.REMOVE_CALLBACK_FOR_SPORTSMAN)
    await message.answer(strings.REMOVE_SPORTSMAN_SUCCESSFUL.format(message.text))
    await entry_point(message)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(menu_choice, state=states.TrainerStates.menu_choice)
    dp.register_message_handler(add_input, state=states.TrainerStates.add_input)
    dp.register_message_handler(add_choose, state=states.TrainerStates.add_choose)
    dp.register_message_handler(list_choose, state=states.TrainerStates.list_choose)
    dp.register_message_handler(remove_choice, state=states.TrainerStates.remove_choice)
