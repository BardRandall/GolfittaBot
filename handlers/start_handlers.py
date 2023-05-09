from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from utils import db_utils, strings, states, markups
from handlers import sportsman_menu_handlers, trainer_menu_handlers


async def cmd_start(message: types.Message, state: FSMContext):
    user = await db_utils.get_user_by_tg_id(message.from_user.id)
    if user is None:
        await message.answer(strings.WELCOME_STRANGER,
                             reply_markup=markups.get_role_choice_markup())
        await states.RegisterStates.role_choice.set()
        return
    async with state.proxy() as storage:
        storage["is_trainer"] = user.is_trainer
        storage["user_id"] = str(user.id)
    if user.is_trainer:
        await trainer_menu_handlers.entry_point(message)
    else:
        await sportsman_menu_handlers.entry_point(message)


async def role_choice(message: types.Message, state: FSMContext):
    if message.text not in [strings.ROLE_SPORTSMAN_BTN, strings.ROLE_TRAINER_BTN]:
        await message.answer(strings.RETRY_KEYBOARD)
        return
    is_trainer = int(message.text == strings.ROLE_TRAINER_BTN)
    async with state.proxy() as storage:
        storage["is_trainer"] = is_trainer
    await message.answer(strings.NAME_INPUT, reply_markup=markups.remove_markup())
    await states.RegisterStates.name_input.set()


async def name_input(message: types.Message, state: FSMContext):
    if message.text is None or not message.text:
        return
    async with state.proxy() as storage:
        storage["name"] = message.text
        is_trainer = storage["is_trainer"]
        user_id = await db_utils.create_user(tg_id=message.from_user.id,
                                   name=storage["name"],
                                   is_trainer=storage["is_trainer"])
        storage["user_id"] = str(user_id)
    await message.answer(strings.REGISTER_FINISH.format(message.text))
    if is_trainer:
        await trainer_menu_handlers.entry_point(message)
    else:
        await sportsman_menu_handlers.entry_point(message)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(role_choice, state=states.RegisterStates.role_choice)
    dp.register_message_handler(name_input, state=states.RegisterStates.name_input)
