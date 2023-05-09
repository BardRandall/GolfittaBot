import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks import MotorAsyncIOInstance
from umongo import Document, fields

import config

db = AsyncIOMotorClient(config.DB_HOST)[config.DB_NAME]
instance = MotorAsyncIOInstance(db)


@instance.register
class User(Document):
    tg_id = fields.IntegerField()
    name = fields.StringField()
    is_trainer = fields.IntegerField(default=0)
    trainer_id = fields.ObjectIdField(default=None, allow_none=True)


@instance.register
class Game(Document):
    user_id = fields.ObjectIdField()
    date = fields.DateField()
    competition_name = fields.StringField()
    field_name = fields.StringField()
    hole_number = fields.IntegerField()
    tee = fields.StringField()
    trainer_comment = fields.StringField(default="Нет комментария")


@instance.register
class Hole(Document):
    game_id = fields.ObjectIdField()
    hole_number = fields.IntegerField()
    fairway = fields.IntegerField()
    green = fields.IntegerField()
    up_and_down = fields.IntegerField()
    putt = fields.IntegerField()
    hit = fields.IntegerField()
    par = fields.IntegerField()


async def main():
    await User.ensure_indexes()
    await Game.ensure_indexes()
    await Hole.ensure_indexes()


asyncio.get_event_loop().create_task(main())
