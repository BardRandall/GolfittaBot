from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext

from handlers import list_games_handlers, add_game_handlers
from utils import db_utils, strings, states, markups


async def entry_point(message: types.Message):
    await message.answer(strings.SPORTSMAN_MENU_WELCOME, reply_markup=markups.get_sportsman_menu_markup())
    await states.SportsmanStates.menu_choice.set()


async def menu_choice(message: types.Message, state: FSMContext):
    if message.text == strings.STATISTICS_BTN:
        await message.answer("Функция скоро будет добавлена :)")
    elif message.text == strings.ADD_GAME_BTN:
        await add_game_handlers.entry_point(message)
    elif message.text == strings.LIST_GAMES_BTN:
        await list_games_handlers.entry_point(message, state)
    elif message.text == strings.TRAINER_BTN:
        user = await db_utils.get_user_by_tg_id(message.from_user.id)
        if user.trainer_id is None:
            await message.answer("У вас нет тренера на данный момент",
                                 reply_markup=markups.get_list_with_return_markup([
                                     strings.ADD_TRAINER_BTN
                                 ]))
        else:
            trainer = await db_utils.get_user_by_id(user.trainer_id)
            await message.answer("Ваш тренер: <b>{}</b>".format(trainer.name),
                                 reply_markup=markups.get_list_with_return_markup([
                                     strings.REMOVE_TRAINER_BTN
                                 ]))
        await states.SportsmanStates.trainer_action_choose.set()
    else:
        await message.answer(strings.RETRY_KEYBOARD)


async def trainer_action_choose(message: types.Message):
    if message.text == strings.ADD_TRAINER_BTN:
        await message.answer("Для поиска тренера введите фамилию:", reply_markup=markups.remove_markup())
        await states.SportsmanStates.add_trainer_input.set()
    elif message.text == strings.REMOVE_TRAINER_BTN:
        user = await db_utils.get_user_by_tg_id(message.from_user.id)
        trainer = await db_utils.get_user_by_id(user.trainer_id)
        user.trainer_id = None
        await user.commit()
        bot = Bot.get_current()
        await bot.send_message(trainer.tg_id, strings.REMOVE_CALLBACK_FOR_TRAINER.format(user.name))
        await message.answer(strings.REMOVE_TRAINER_SUCCESSFUL)
        await entry_point(message)
    elif message.text == strings.RETURN_BTN:
        await entry_point(message)
    else:
        await message.answer(strings.RETRY_KEYBOARD)



async def add_trainer_input(message: types.Message):
    if message.text == strings.RETURN_BTN:
        await entry_point(message)
        return
    users = await db_utils.find_users_like(message.text, only_trainer=True)
    if not users:
        await message.answer(strings.NO_USERS_MATCH)
        return
    users_names = [user.name for user in users]
    await message.answer(strings.ADD_TRAINER_CHOOSE,
                         reply_markup=markups.get_list_with_cancel_markup(users_names))
    await states.SportsmanStates.add_trainer_choose.set()


async def add_trainer_choose(message: types.Message):
    if message.text == strings.CANCEL_BTN:
        await entry_point(message)
        return
    trainer = await db_utils.get_user_by_name(message.text)
    if trainer is None:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    user = await db_utils.get_user_by_tg_id(message.from_user.id)
    user.trainer_id = trainer.id
    await user.commit()
    await message.answer(strings.ADD_TRAINER_SUCCESSFUL.format(message.text))
    await entry_point(message)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(menu_choice, state=states.SportsmanStates.menu_choice)
    dp.register_message_handler(add_trainer_input, state=states.SportsmanStates.add_trainer_input)
    dp.register_message_handler(add_trainer_choose, state=states.SportsmanStates.add_trainer_choose)
    dp.register_message_handler(trainer_action_choose, state=states.SportsmanStates.trainer_action_choose)
