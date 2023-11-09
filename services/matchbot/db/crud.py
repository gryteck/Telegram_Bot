import logging
import traceback
from database import DBSession
from sqlalchemy import func, select
from .models import User


class DB:
    def __init__(self):
        self.session = DBSession()

    def get_user(self, id: int) -> User:
        return self.session.query(User).filter(User.id == id).first()

    def get_random_user(self, id: int) -> User:
        user = self.session.query(User).filter(User.id == id).first()
        if user.interest == 'Девушки':
            return self.session.query(User).filter(User.id != id, User.age >= user.age - 2, User.age <= user.age + 5,
                                                   User.banned == 'false', User.visible == 'true',
                                                   User.gender == 'Девушка').order_by(func.random()).first()
        else:
            return self.session.query(User).filter(User.id != id, User.age >= user.age - 5, User.age <= user.age + 2,
                                                   User.banned == 'false', User.visible == 'true',
                                                   User.gender == 'Парень').order_by(func.random()).first()

    def create_user(self, username: str, id: int, gender: str, interest: str, name: str, age: int, photo: str,
                    text: str) -> User:
        new_user = User(id=id, username=username, name=name, age=age, photo=photo, text=text, gender=gender,
                        interest=interest)
        self.session.begin()
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def update_user(self, id: int, **kwargs) -> User:
        self.session.begin()
        user = self.session.query(User).filter(User.id == id).first()
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.session.commit()
        return user

    def filter_liked(self, liked: list) -> list:
        query = self.session.query(User.id).filter(User.id.in_(liked)).filter(User.visible == 'true').\
            filter(User.banned == 'false')
        user_ids = [row[0] for row in query.all()]
        return user_ids


db = DB()
