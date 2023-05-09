from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterStates(StatesGroup):
    role_choice = State()
    name_input = State()


class TrainerStates(StatesGroup):
    menu_choice = State()
    remove_choice = State()
    add_input = State()
    add_choose = State()
    list_choose = State()


class SportsmanStates(StatesGroup):
    menu_choice = State()
    trainer_action_choose = State()
    add_trainer_input = State()
    add_trainer_choose = State()


class ListGamesStates(StatesGroup):
    game_choice = State()
    menu_choice = State()
    comment_menu = State()
    comment_input = State()


class AddGameStates(StatesGroup):
    game_name_input = State()
    golf_field_name_input = State()
    holes_number_input = State()
    tee_input = State()
    hole_fairway = State()
    hole_green = State()
    hole_up_and_down = State()
    hole_putt = State()
    hole_hit = State()
    hole_par = State()
