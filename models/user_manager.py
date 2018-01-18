# -*- coding:utf-8 -*-
from schematics.models import Model

from models.base_manager import SNBaseManager
from models.models import UserModel, UserAddModel, UserType
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from models.user_friend_manager import UserRelationManager
from models.user_type_manager import UserTypeManager

class UserManager(SNBaseManager):
    load_models = {}

    def __init__(self):
        class_model = UserModel
        super(UserManager, self).__init__(class_model)

    def getModelFromForm(self,form):
        self.object.first_name = form.get('first_name', '')
        self.object.last_name = form.get('last_name', '')
        type_manager = UserTypeManager()
        type_manager.getType(type_name=form.get('type_name', ''))
        self.object.type = type_manager.object
        self.object.email = form.get('email', '')
        self.object.nickname = form.get('nickname', '')
        if form.get('passw1', '') == form.get('passw2', ''):
            self.object.password = form.get('passw1', '')
        self.object.descr = form.get('descr', '')
        return self

    def add_friend(self, id=None, nickname=None):
        if not (id or nickname):
            return
        relationManager = UserRelationManager()
        relationManager.addFriend(self.object.id, id)


    def get_friends(self):
        relationManager = UserRelationManager()
        return relationManager.getFriends(self.object.id)


    def check_user(self):
        if self.object.type.type_name == 'user':
            self.select().And([('nickname','=',self.object.nickname),('email','=',self.object.email)]).run()
        else:
            self.select().And([('nickname','=',self.object.nickname)]).run()
        if self.object.id:
            return True
        return False

    def loginUser(self,login_form):
        email = login_form.get('email', '')
        password = login_form.get('passw', '')
        self.select().And([('email','=',email),('password','=',password)]).run()
        if self.object.id:
            self.load_models[self.object.nickname] = self
            return True
        return False

    def get_user(self,id):
        return self.select().And([('id', '=', str(id))]).run()


if __name__ == '__main__':
    manager = UserManager()
    manager.object.id = 1


