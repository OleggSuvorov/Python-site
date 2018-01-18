# -*- coding:utf-8 -*-
from models.models import UserType
from models.base_manager import SNBaseManager


class UserTypeManager(SNBaseManager):

    def __init__(self):
        class_model = UserType
        super(UserTypeManager, self).__init__(class_model)

    def getType(self, id=None, type_name=None):
        if id:
            self.select().And([('id', '=', str(id))]).run()
        elif type_name:
            self.select().And([('type_name', '=', str(type_name))]).run()

    def getTypeUser(self):
        self.select().And([('type_name', '=', 'user')]).run()

    def getTypeGroup(self):
        self.select().And([('type_name', '=', 'group')]).run()



    def getTypes(self):
        return self.select().run()
