#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/29 14:45
# @Author  : 张大鹏
# @Github  : https://github.com/zhangdapeng520
# @File    : hello.py
# @Software: PyCharm
# @Description: 基本用法

from zdppy_orm.peewee import *

db = MySQLDatabase('test', user='root', password='root', host='localhost', port=3306)


class Person(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db  # This model uses the "people.db" database.


class Pet(Model):
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db  # this model uses the "people.db" database


db.connect()
db.create_tables([Person, Pet])

# 添加数据
from datetime import date

uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15))
uncle_bob.save()  # bob is now stored in the database
grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1))
herb = Person.create(name='Herb', birthday=date(1950, 5, 5))

# 修改数据
grandma.name = 'Grandma L.'
grandma.save()  # Update grandma's name in the database.
# Returns: 1

# 添加宠物
bob_kitty = Pet.create(owner=uncle_bob, name='Kitty', animal_type='cat')
herb_fido = Pet.create(owner=herb, name='Fido', animal_type='dog')
herb_mittens = Pet.create(owner=herb, name='Mittens', animal_type='cat')
herb_mittens_jr = Pet.create(owner=herb, name='Mittens Jr', animal_type='cat')

# 修改外键
herb_fido.owner = uncle_bob
herb_fido.save()

# 查询数据
grandma = Person.select().where(Person.name == 'Grandma L.').get()
# grandma = Person.get(Person.name == 'Grandma L.')

for person in Person.select():
    print(person.name)

query = Pet.select().where(Pet.animal_type == 'cat')
for pet in query:
    print(pet.name, pet.owner.name)

# 关联查询
query = (Pet
         .select(Pet, Person)
         .join(Person)
         .where(Pet.animal_type == 'cat'))

for pet in query:
    print(pet.name, pet.owner.name)
for pet in Pet.select().join(Person).where(Person.name == 'Bob'):
    print(pet.name)

for pet in Pet.select().where(Pet.owner == uncle_bob):
    print(pet.name)

# 排序
for pet in Pet.select().where(Pet.owner == uncle_bob).order_by(Pet.name):
    print(pet.name)
for person in Person.select().order_by(Person.birthday.desc()):
    print(person.name, person.birthday)

# 多条件合并
d1940 = date(1940, 1, 1)
d1960 = date(1960, 1, 1)
query = (Person
         .select()
         .where((Person.birthday < d1940) | (Person.birthday > d1960)))

for person in query:
    print(person.name, person.birthday)

query = (Person
         .select()
         .where(Person.birthday.between(d1940, d1960)))

for person in query:
    print(person.name, person.birthday)

# 聚合查询
for person in Person.select():
    print(person.name, person.pets.count(), 'pets')

query = (Person
         .select(Person, fn.COUNT(Pet.id).alias('pet_count'))
         .join(Pet, JOIN.LEFT_OUTER)  # include people without pets.
         .group_by(Person)
         .order_by(Person.name))

for person in query:
    # "pet_count" becomes an attribute on the returned model instances.
    print(person.name, person.pet_count, 'pets')

query = (Person
         .select(Person, Pet)
         .join(Pet, JOIN.LEFT_OUTER)
         .order_by(Person.name, Pet.name))
for person in query:
    # We need to check if they have a pet instance attached, since not all
    # people have pets.
    if hasattr(person, 'pet'):
        print(person.name, person.pet.name)
    else:
        print(person.name, 'no pets')

# 预加载
query = Person.select().order_by(Person.name).prefetch(Pet)
for person in query:
    print(person.name)
    for pet in person.pets:
        print('  *', pet.name)

# SQL函数
expression = fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g'
for person in Person.select().where(expression):
    print(person.name)

# 关闭连接
db.close()
