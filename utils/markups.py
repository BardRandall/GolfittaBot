from aiogram import types

from utils import strings


def vertical_aligned_markup(btns_text):
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard_markup.add(*[types.KeyboardButton(btn_text) for btn_text in btns_text])
    return keyboard_markup


def horizontal_aligned_markup(btns_text):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.add(*[types.KeyboardButton(btn_text) for btn_text in btns_text])
    return keyboard_markup


def remove_markup():
    return types.reply_keyboard.ReplyKeyboardRemove()


# Common
def get_cancel_markup():
    return vertical_aligned_markup([strings.CANCEL_BTN])


def get_list_with_cancel_markup(lst):
    return vertical_aligned_markup(lst + [strings.CANCEL_BTN])


def get_list_with_return_markup(lst):
    return vertical_aligned_markup(lst + [strings.RETURN_BTN])


# Start markups
def get_role_choice_markup():
    return horizontal_aligned_markup([
        strings.ROLE_SPORTSMAN_BTN,
        strings.ROLE_TRAINER_BTN
    ])


# Trainer markups
def get_trainer_menu_markup():
    return vertical_aligned_markup([
        strings.ADD_SPORTSMAN_BTN,
        strings.LIST_SPORTSMAN_BTN,
        strings.REMOVE_SPORTSMAN_BTN
    ])


# Sportsman markups
def get_sportsman_menu_markup():
    return vertical_aligned_markup([
        strings.STATISTICS_BTN,
        strings.ADD_GAME_BTN,
        strings.LIST_GAMES_BTN,
        strings.TRAINER_BTN
    ])

# List game markups
def get_game_markup():
    return vertical_aligned_markup([
        strings.HOLE_STAT_BTN,
        strings.SHOW_COMMENT_BTN,
        strings.RETURN_BTN
    ])

# Add game markups
def get_yes_no_markup():
    return horizontal_aligned_markup([
        strings.YES_BTN,
        strings.NO_BTN
    ])


def get_yes_no_try_markup():
    return horizontal_aligned_markup([
        strings.YES_BTN,
        strings.NO_BTN,
        strings.TRY_BTN
    ])