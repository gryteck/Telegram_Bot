import logging
from sqlalchemy import func, exc, select, update

from .models import User, Actions
from database import pg_session


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


class Postgre:
    @classmethod
    async def exists_user(cls, id) -> User:
        async with pg_session() as session:
            query = select(User).filter(User.id == id)
            user = await session.execute(query)
            return user.scalar_one_or_none()

    @classmethod
    async def get_user(cls, id) -> User:
        async with pg_session() as session:
            query = select(User).filter(User.id == id)
            user = await session.execute(query)
            return user.scalars().one()

    @classmethod
    async def get_liked(cls, id: int) -> list:
        async with pg_session() as session:
            query = select(Actions.to_id).filter(Actions.from_id == id).filter(Actions.action_type == 'like')
            rows = await session.execute(query)
            return rows.scalars().all()

    @classmethod
    async def get_claims(cls, id: int) -> list:
        async with pg_session() as session:
            query = select(Actions.to_id).filter(Actions.from_id == id).filter(Actions.action_type == 'claim')
            rows = await session.execute(query)
            return rows.scalars().all()

    @classmethod
    async def get_random_user(cls, id: int) -> User:
        async with pg_session() as session:
            user = await Postgre.get_user(id)
            if user.interest == 'Девушки':
                query = select(User).filter(User.id != id, User.age >= user.age - 5, User.age <= user.age + 2,
                                            User.banned.is_(False), User.visible.is_(True),
                                            User.gender == 'Девушка').order_by(func.random()).limit(1)
                user = await session.execute(query)
                return user.scalar_one_or_none()
            else:
                query = select(User).filter(User.id != id, User.age >= user.age - 2, User.age <= user.age + 5,
                                            User.banned.is_(False), User.visible.is_(True),
                                            User.gender == 'Парень').order_by(func.random()).limit(1)
                user = await session.execute(query)
                return user.scalar_one_or_none()

    @classmethod
    async def create_user(cls, username: str, id: int, gender: str, interest: str, name: str, age: int, photo: str,
                          text: str) -> User:
        async with pg_session() as session:
            new_user = User(id=id, username=username, name=name, age=age, photo=photo, text=text, gender=gender,
                            interest=interest)
            session.add(new_user)
            await session.commit()
            return new_user

    @classmethod
    async def create_action(cls, from_id: int, to_id: int, action_type: str):
        async with pg_session() as session:
            new_action = Actions(from_id=from_id, to_id=to_id, action_type=action_type)
            session.add(new_action)
            await session.commit()
            return new_action

    # @classmethod
    # async def update_user(cls, id, **kwargs):
    #     async with pg_session() as session:
    #         async with session.begin():
    #             user = await cls.get_user(id)
    #             if user:
    #                 for attr, value in kwargs.items():
    #                     setattr(user, attr, value)
    #                 await session.commit()
    #                 return user

    @classmethod
    async def update_user(cls, id, **kwargs) -> User:
        async with pg_session() as session:
            query = update(User).where(User.id == id).values(**kwargs).returning(User)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            await session.commit()
            return user

    @classmethod
    async def filter_liked(cls, liked: list):
        async with pg_session() as session:
            query = select(User.id).filter(User.id.in_(liked), User.banned.is_(False), User.visible.is_(True))
            rows = (await session.execute(query)).scalars().all()
            return rows
