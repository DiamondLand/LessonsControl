from tortoise import fields
from tortoise.models import Model


class User(Model): # Для пользователей
    user_id = fields.BigIntField(pk=True)
