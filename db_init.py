# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *

engine = create_engine('sqlite:///itemCatalog.db')

# clear the existing database if there is any
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)

# A DBSession() instance establishes all conversations with the database
# Session will be persisted into the database with session.commit()
# Changes can be reverted by user by session.rollback()
session = DBsession()

# Create user in the database
# Change the name, email and image to yours in order to log in and CRUD
user_1 = User(name="Bob Wang",
              email="wwwyyycss@gmail.com",
              image="https://bit.ly/29KRDC2")
session.add(user_1)
session.commit()

# Add category data to the database

cat1 = Category(name="Soccer", user_id=1)
session.add(cat1)
session.commit()

cat2 = Category(name="Basketball", user_id=1)
session.add(cat2)
session.commit()

cat3 = Category(name="Baseball", user_id=1)
session.add(cat3)
session.commit()

cat4 = Category(name="Frisbee", user_id=1)
session.add(cat4)
session.commit()

cat5 = Category(name="Snowboarding", user_id=1)
session.add(cat5)
session.commit()

cat6 = Category(name="Rock Climbing", user_id=1)
session.add(cat6)
session.commit()

cat7 = Category(name="Football", user_id=1)
session.add(cat7)
session.commit()

cat8 = Category(name="Skating", user_id=1)
session.add(cat8)
session.commit()

cat9 = Category(name="Hockey", user_id=1)
session.add(cat9)
session.commit()

# Add item data to the database

item1 = Item(name="Two shinguards",
             description="Two pieces of equipment worn on the front of "
                         "a player's shin to protect them from injury.",
             picture="https://bit.ly/2rQS4G2",
             category_id=1,
             user_id=1)

session.add(item1)
session.commit()

item2 = Item(name="Shinguards",
             description="A piece of equipment worn on the front of "
                         "a player's shin to protect them from injury.",
             picture="https://bit.ly/2rQS4G2",
             category_id=1,
             user_id=1)

session.add(item2)
session.commit()

item3 = Item(name="Jersey",
             description="The standard equipment and attire worn by players.",
             picture="https://bit.ly/2k7f4fC",
             category_id=1,
             user_id=1)

session.add(item3)
session.commit()

item4 = Item(name="Soccer Cleats",
             description="The classic soccer shoe with cleats/studs designed "
                         "to provide traction and stability on most "
                         "natural grass, outdoor soccer fields.",
             picture="https://bit.ly/2k7yxgk",
             category_id=1,
             user_id=1)

session.add(item4)
session.commit()

item5 = Item(name="Bat",
             description="A smooth wooden or metal club used in the sport "
                         "of baseball to hit the ball after it is thrown "
                         "by the pitcher.",
             picture="https://bit.ly/2La6ysy",
             category_id=3,
             user_id=1)

session.add(item5)
session.commit()

item6 = Item(name="Frisbee",
             description="A gliding toy or sporting item that is generally "
                         "plastic and roughly 20 to 25 centimetres "
                         "(8 to 10 in) in diameter with a lip.",
             picture="https://bit.ly/2k7i4Zq",
             category_id=4,
             user_id=1)

session.add(item6)
session.commit()

item7 = Item(name="Goggles",
             description="Forms of protective eyewear that usually enclose "
                         "or protect the area surrounding the eye in order "
                         "to prevent particulates, water or chemicals "
                         "from striking the eyes.",
             picture="https://bit.ly/2rSGavg",
             category_id=5,
             user_id=1)

session.add(item7)
session.commit()

item8 = Item(name="Snowboard",
             description="Boards where both feet are secured to the same "
                         "board, which are wider than skis, with "
                         "the ability to glide on snow.",
             picture="https://bit.ly/2GwIOvh",
             category_id=5,
             user_id=1)

session.add(item8)
session.commit()

item9 = Item(name="Stick",
             description="A piece of equipment used by the players in most "
                         "forms of hockey to move the ball or puck.",
             picture="https://bit.ly/2Iv6WnZ",
             category_id=9,
             user_id=1)

session.add(item9)
session.commit()

print("Item catalogs have been initiated!")
