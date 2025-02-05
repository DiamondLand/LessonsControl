import datetime

from tortoise import fields
from tortoise.models import Model


class BaseORM(Model):
    class Meta:
        abstract = True

    id: int = fields.IntField(pk=True)
    created_at: datetime.datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime.datetime = fields.DatetimeField(auto_now=True)


class User(BaseORM): # Для пользователей
    user_id = fields.BigIntField()

    firstname = fields.CharField(max_length=300, null=True)
    lastname = fields.CharField(max_length=300, null=True)
    group = fields.IntField(null=True)


class Attendance(BaseORM):  # Посещаемость
    user = fields.ForeignKeyField(
        "models.User", related_name="attendances", 
        on_delete=fields.CASCADE
    )
    date = fields.DateField()

    class Meta:
        unique_together = ("user", "date")
