# -*- coding:utf-8 -*-
from schematics.models import Model
from schematics.types import ModelType

from .bool_where import BoolWhereDelete, BoolWhereSelect
from .models import UserModel, UserAddModel, UserType
from .executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from .my_types import One2One , One2Many
class SNBaseManager():
    update_sql = 'UPDATE {} SET {} WHERE id = {}'
    update_sql_set = ' {0} = {1} '
    insert_sql = 'INSERT INTO {} VALUES ({})'
    insert_sql_values = '{1}'

    def __init__(self, class_model=None):
        if class_model:
            self.object = class_model()
        self._table_to_update = []

    def itemToUpdate(self):
        atoms = self.object.atoms()
        result = []
        for item in atoms:
            if item.field.typeclass != One2One:
                result.append(item.name)
        return result

    def _chooseTemp(self, item):
        if isinstance(item, type(None)):
            return 'NULL'
        elif isinstance(item, dict):
            return item['id']
        elif isinstance(item, int):
            return item
        elif isinstance(item, ModelType):
            return item.id
        return repr(str(item))

    def _sqlValues(self, template):
        keys = self.itemToUpdate()
        primitive = self.object.to_primitive()
        result = '{},' * len(keys)
        result = result.rstrip(',')
        return result.format(*[template.format(key, self._chooseTemp(primitive[key])) for key in keys])

    def save(self):
        atoms = self.object.atoms()
        for atom in atoms:
            if atom.field.typeclass == ModelType:
                man = SNBaseManager()
                man.object = atom.value
                man.save()
            elif atom.field.typeclass == One2One:
                man = SNBaseManager()
                man.object = atom.value
                self._table_to_update.append(man)
            elif atom.field.typeclass == One2Many:
                for mod in atom.value:
                    man = SNBaseManager()
                    man.object = mod
                    self._table_to_update.append(man)

        if not self.object.id:
            id = self._save()
        else:
            id = self.object.id
            self._save()
        self._update_child(self.object._name, id)
        return True

    def _update_child(self, table, id):
        for man in self._table_to_update:
            if man.object:
                man.object[table] = id
                man.save()

    def _save(self):
        if self.object.id:
            sql = self.update_sql.format(self.object._name, self._sqlValues(self.update_sql_set), self.object.id)
        else:
            sql = self.insert_sql.format(self.object._name, self._sqlValues(self.insert_sql_values))
        print(sql)
        return executeSQL(sql)

    def delete(self):
        return BoolWhereDelete(self)

    def _delete(self, sql):
        return executeSQL(sql)

    def fillModel(self, sql):
        resultd = {}
        resultl = []
        atoms = self.object.atoms()
        datal = executeSelectAll(sql)
        for data in datal:
            for atom in atoms:
                if atom.field.typeclass == ModelType:
                    man = SNBaseManager(atom.field.model_class)
                    sql = man.select().And([('id', '=', data[atom.name])]).sql
                    raw_data = executeSelectAll(sql)
                    if raw_data:
                        raw_data = raw_data[0]
                    resultd[atom.name] = atom.field.model_class().import_data(raw_data=raw_data)
                elif atom.field.typeclass == One2One:
                    man = SNBaseManager(atom.field.model_class)
                    sql = man.select().And([(str(self.object._name), '=', data['id'])]).sql
                    raw_data = executeSelectOne(sql)
                    if not raw_data:
                        raw_data = {}
                    resultd[atom.name] = atom.field.model_class().import_data(raw_data)
                elif atom.field.typeclass == One2Many:
                    man = SNBaseManager(atom.field.model_class)
                    sql = man.select().And([(str(self.object._name), '=', data['id'])]).sql
                    raw_data_list = executeSelectAll(sql)
                    if not raw_data_list:
                        raw_data_list = [{}]
                    for index,raw_data in enumerate(raw_data_list):
                        raw_data_list[index] = atom.field.model_class().import_data(raw_data)
                    resultd[atom.name] = atom.field.model_class().import_data(raw_data_list)
                else:
                    resultd[atom.name] = data[atom.name]
            resultl.append(resultd)

        if resultd:
            self.object.import_data(resultd)

    def select(self):
        return BoolWhereSelect(self)


if __name__ == '__main__':
    man = SNBaseManager(UserModel)
    typep = UserType()
    typep.id = 2
    typep.type_name = 'group'
    man.object.id = 17
    man.object.first_name = 'test'
    man.object.last_name = 'test'
    man.object.type = typep
    man.object.descr = 'test'
    man.object.user_photo = 'test'
    man.object.user_photos = ['test']
    man.object.email = 'testtest.test'
    man.object.nickname = 'test'
    man.object.password = 'test'
    man.object.users_add = UserAddModel()
    man.object.users_add.id = 1
    man.object.users_add.age = '12'
    man.object.users_add.phone = '123123132'
    man.object.users_add.address = 'test'
    man.object.users_add.sex = '1'
    man.object.users_add.users = 17
    man.save()
