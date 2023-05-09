from datetime import date
import re

import pymongo

from utils import models

async def get_user_by_tg_id(tg_id):
    return await models.User.find_one({"tg_id": tg_id})


async def get_user_by_id(_id):
    return await models.User.find_one({"_id": _id})


async def create_user(tg_id, name, is_trainer=0):
    user = models.User(tg_id=tg_id, name=name, is_trainer=is_trainer)
    await user.commit()
    return user.id


async def get_trainer_sportsmen(trainer_tg_id):
    trainer = await get_user_by_tg_id(trainer_tg_id)
    return await models.User.find({"trainer_id": trainer.id}).to_list(length=None)


async def get_user_by_name(name):
    return await models.User.find_one({"name": name})


async def find_users_like(name, only_trainer=False):
    rgx = re.compile(f".*{name}.*", re.IGNORECASE)
    if only_trainer:
        return await models.User.find({"name": rgx, "is_trainer": 1}).to_list(length=None)
    return await models.User.find({"name": rgx, "is_trainer": 0}).to_list(length=None)


async def get_sportsman_games(user_id):
    return await models.Game.find({"user_id": user_id}).sort("date", pymongo.DESCENDING).to_list(length=None)


async def get_game_by_user_and_name(user_id, name):
    return await models.Game.find_one({"user_id": user_id, "competition_name": name})


async def get_game_by_id(game_id):
    return await models.Game.find_one({"_id": game_id})

async def create_game(user_id, comp_name, field_name, hole_number, tee):
    game = models.Game(user_id=user_id,
                       date=date.today(),
                       competition_name=comp_name,
                       field_name=field_name,
                       hole_number=hole_number,
                       tee=tee)
    await game.commit()
    return game.id


async def create_hole(game_id, hole_number, fairway, green, up_and_down, putt, hit, par):
    hole = models.Hole(game_id=game_id, hole_number=hole_number, fairway=fairway,
                       green=green, up_and_down=up_and_down, putt=putt, hit=hit, par=par)
    await hole.commit()
    return hole.id


async def get_all_holes_by_game(game_id):
    return await models.Hole.find({"game_id": game_id}).to_list(length=None)
