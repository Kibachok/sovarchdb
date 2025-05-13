from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


# ========== ТАБЛИЦЫ ==========
class Region(SqlAlchemyBase):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    climate_zone = Column(String, nullable=False)


class Series(SqlAlchemyBase):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    period = Column(Integer, ForeignKey('periods.id'))
    material = Column(Integer, ForeignKey('mats.id'))
    description = Column(String, nullable=True)


class TypeTable(SqlAlchemyBase):
    __tablename__ = 'type_tables'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_series = Column(Integer, ForeignKey('series.id'), nullable=False)
    name = Column(String(50), nullable=False)
    override_period = Column(Integer, ForeignKey('periods.id'), nullable=True)
    description = Column(String(500), nullable=True)
    region = Column(Integer, ForeignKey('regions.id'), nullable=True)


class City(SqlAlchemyBase):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)


class Period(SqlAlchemyBase):
    __tablename__ = 'periods'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(10), nullable=False, unique=True)


class Material(SqlAlchemyBase):
    __tablename__ = 'mats'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(8), nullable=False, unique=True)


class HouseType(SqlAlchemyBase):
    __tablename__ = 'house_types'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)


class House(SqlAlchemyBase):
    __tablename__ = 'houses'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('house_types.id'), nullable=True)
    series_id = Column(Integer, ForeignKey('series.id'), nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    address_primary = Column(String(100), nullable=False)
    address_num = Column(Integer, nullable=False)
    address_postfix = Column(String(10), nullable=True)
    description = Column(String(500), nullable=True)

    __table_args__ = (
        CheckConstraint(
            '(type_id IS NULL AND series_id IS NOT NULL) OR (type_id IS NOT NULL AND series_id IS NULL)',
            name='type_xor_series'
        ),
    )


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String)
    password = Column(String)
    nickname = Column(String, nullable=True)
    role = Column(Integer, default=0)
    register_date = Column(DateTime, default=datetime.now())
