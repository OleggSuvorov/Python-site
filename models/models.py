# -*- coding:utf-8 -*-

from datetime import datetime
from schematics.models import Model
from schematics.types import StringType, EmailType, BooleanType, IntType, ListType, ModelType, DateTimeType
from .my_types import One2One
CommentsModel = None

class UserType(Model):
    _name = 'user_type'
    id = IntType(required=False)
    type_name = StringType(required=True)
    create_time = DateTimeType(required=True, default=datetime.now())


class UserAddModel(Model):
    _name = 'users_add'
    id = IntType(required=False)
    age = IntType(default=None, required=False)
    create_time = DateTimeType(required=True, default=datetime.now())
    phone = StringType(default=None, required=False)
    address = StringType(default=None, required=False)
    sex = IntType(default=None, required=False)
    users = IntType(default=None, required=False)


class UserModel(Model):
    _name = 'users'
    id = IntType(required=False)
    first_name = StringType(required=True)
    last_name = StringType(required=False, default='')
    type = ModelType(UserType, required=True)
    descr = StringType(required=False, default='')
    user_photo = StringType(required=False, default='')
    user_photos = StringType(required=False, default='')
    email = EmailType(required=True)
    nickname = StringType(required=True)
    password = StringType(required=True)
    create_time = DateTimeType(required=True, default=datetime.now())
    users_add = One2One(UserAddModel)


class UserRelation(Model):
    _name = 'user_relation'
    id = IntType(required=False)
    user1 = IntType(required=True)
    user2 = IntType(required=True)
    block = IntType(required=True, default=0)
    create_time = DateTimeType(required=True, default=datetime.now())


class GroupUserModel(Model):
    id = IntType(required=False)
    group = ModelType(UserModel, required=True)
    user = ModelType(UserModel, required=True)
    create_time = DateTimeType(required=True, default=datetime.now())

class PostModel(Model):
    _name = 'post'
    id = IntType(required=False)
    title = StringType(required=True)
    photos = StringType(required=False, default='')
    text = StringType(required=False, default=None)
    likes = IntType(required=True, default=0)
    user = ModelType(UserModel, required=True)
    create_time = DateTimeType(required=True, default=datetime.now())



class CommentsModel(Model):
    _name = 'comment'
    id = IntType(required=False)
    text = StringType(required=False, default=None)
    likes = IntType(required=True, default=0)
    user = ModelType(UserModel, required=True)
    post = ModelType(PostModel, required=True)
    create_time = DateTimeType(required=True, default=datetime.now())

PostModel.comment = ListType(ModelType(CommentsModel), required=False)

# class PostCommentModel(Model):
#     _name = 'post_comment'
#     id = IntType(required=False)
#     post = ModelType(PostModel, required=True)
#     comment = ModelType(CommentsModel, required=True)
#     create_time = DateTimeType(required=True, default=datetime.now())


class MessageModel(Model):
    id = IntType(required=False)
    user_from = ModelType(UserModel, required=True)
    user_to = ModelType(UserModel, required=True)
    is_read = BooleanType(required=True, default=False)
    create_time = DateTimeType(required=True, default=datetime.now())


if __name__ == '__main__':
    pass
