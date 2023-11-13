import logging
from database import DBSession
from sqlalchemy import func, exc
from .models import User, Actions


def db_exception(function):
    def inner(self, *args, **kwargs):
        try:
            res = function(self, *args, **kwargs)
        except exc.SQLAlchemyError as e:
            logging.warning(e)
            self.close()
            self.__init__()
            res = None
        return res
    return inner


class DB:
    def __init__(self):
        self.session = DBSession()
        logging.warning("Successful connection to Postgres")

    def close(self):
        logging.warning("Connection is closed")
        self.session.close()

    @db_exception
    def get_user(self, id: int) -> User:
        return self.session.query(User).filter(User.id == id).first()

    @db_exception
    def get_liked(self, id: int) -> list:
        query = self.session.query(Actions.to_id).filter(Actions.from_id == id).filter(Actions.action_type == 'like')
        user_ids = [row[0] for row in query.all()]
        return user_ids

    @db_exception
    def get_claims(self, id: int) -> list:
        query = self.session.query(Actions.to_id).filter(Actions.from_id == id).filter(Actions.action_type == 'claims')
        user_ids = [row[0] for row in query.all()]
        return user_ids

    @db_exception
    def get_random_user(self, id: int) -> User:
        user = self.session.query(User).filter(User.id == id).first()
        if user.interest == 'Девушки':
            return self.session.query(User).filter(User.id != id, User.age >= user.age - 5, User.age <= user.age + 2,
                                                   User.banned == 'false', User.visible == 'true',
                                                   User.gender == 'Девушка').order_by(func.random()).first()
        else:
            return self.session.query(User).filter(User.id != id, User.age >= user.age - 2, User.age <= user.age + 5,
                                                   User.banned == 'false', User.visible == 'true',
                                                   User.gender == 'Парень').order_by(func.random()).first()

    @db_exception
    def create_user(self, username: str, id: int, gender: str, interest: str, name: str, age: int, photo: str,
                    text: str) -> User:
        new_user = User(id=id, username=username, name=name, age=age, photo=photo, text=text, gender=gender,
                        interest=interest)
        self.session.begin()
        self.session.add(new_user)
        self.session.commit()
        return new_user

    @db_exception
    def create_action(self, from_id: int, to_id: int, action_type: str):
        self.session.begin()
        self.session.add(Actions(from_id=from_id, to_id=to_id, action_type=action_type))
        return self.session.commit()

    @db_exception
    def update_user(self, id: int, **kwargs) -> User:
        self.session.begin()
        user = self.session.query(User).filter(User.id == id).first()
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.session.commit()
        return user

    @db_exception
    def filter_liked(self, liked: list) -> list:
        query = self.session.query(User.id).filter(User.id.in_(liked)).filter(User.visible == 'true').\
            filter(User.banned == 'false')
        user_ids = [row[0] for row in query.all()]
        return user_ids


db = DB()
