import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


# class to store user info
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    image = Column(String(250))
    provider = Column(String(25))


# class for Store Database
class ClothDB(Base):
    __tablename__ = "clothes"

    id = Column(Integer, primary_key=True)
    brandName = Column(String(250), nullable=False)
    color = Column(String(50), nullable=False)
    price = Column(String(8), nullable=False)
    description = Column(String(450), nullable=False)
    category = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # return book data in serializable format
        return {
            'id': self.id,
            'name': self.brandName,
            'color': self.color,
            'category': self.category,
            'price': self.price,
            'description': self.description
        }

engine = create_engine('sqlite:///ClothesCatalog.db')
Base.metadata.create_all(engine)
