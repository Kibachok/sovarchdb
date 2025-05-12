from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


# ========== ТАБЛИЦЫ ==========
class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    climate_zone = Column(String, nullable=False)
    series = relationship("Series", back_populates="region")


class Series(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    period = Column(Integer, nullable=True)
    material = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    houses = relationship("House", back_populates="series")


class TypeTable(Base):
    __tablename__ = 'type_tables'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_series = Column(Integer, ForeignKey('series.id'), nullable=False)
    name = Column(String(50), nullable=False)
    override_period = Column(Integer, nullable=True)
    description = Column(String(500), nullable=True)
    series = relationship("Series", back_populates="types")
    region = relationship("Region", back_populates="series")
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)


class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    houses = relationship("House", back_populates="city")


class HouseType(Base):
    __tablename__ = 'house_types'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    houses = relationship("House", back_populates="type")


class House(Base):
    __tablename__ = 'houses'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey('house_types.id'), nullable=True)
    series_id = Column(Integer, ForeignKey('series.id'), nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    address_primary = Column(String(100), nullable=False)
    address_num = Column(Integer, nullable=False)
    address_postfix = Column(String(10), nullable=True)
    description = Column(String(500), nullable=True)
    forumlink = Column(String(200), nullable=True)

    __table_args__ = (
        CheckConstraint(
            '(type_id IS NULL AND series_id IS NOT NULL) OR (type_id IS NOT NULL AND series_id IS NULL)',
            name='type_xor_series'
        ),
    )

    type = relationship("HouseType", back_populates="houses")
    series = relationship("Series", back_populates="houses")
    city = relationship("City", back_populates="houses")


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String, nullable=False)
    password = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    role = Column(Integer, nullable=True)
    register_date = Column(String, nullable=True)


# ========== ИНИЦИАЛИЗАЦИЯ И ДЕМО-ДАННЫЕ ==========
engine = create_engine('sqlite:///house_series.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def demo_data():
    # Добавляем регионы и серии
    if not session.query(Region).first():
        regions = [
            Region(name="Южный регион", climate_zone="IV A"),
            Region(name="Уральский регион", climate_zone="II B")
        ]
        session.add_all(regions)

        series = [
            Series(
                name="П-44Т",
                period=4,
                material=1,
                description="Современная панельная серия",
                forumlink="link1",
                region=regions[0]
            ),
            Series(
                name="1-528КП",
                period=2,
                material=2,
                description="Кирпичные дома",
                forumlink="link2",
                region=regions[1]
            )
        ]
        session.add_all(series)
        session.commit()  # Важно: коммитим перед созданием связанных домов

    # Добавляем города
    if not session.query(City).first():
        cities = [
            City(name="Москва"),
            City(name="Санкт-Петербург")
        ]
        session.add_all(cities)
        session.commit()

    # Добавляем типы домов
    if not session.query(HouseType).first():
        types = [
            HouseType(name="Многоэтажный дом"),
            HouseType(name="Частный дом")
        ]
        session.add_all(types)
        session.commit()

    # Добавляем дома
    if not session.query(House).first():
        houses = [
            House(
                series_id=1,
                city_id=1,
                address_primary="ул. Тверская",
                address_num=15,
                description="Дом с арками"
            ),
            House(
                type_id=2,
                city_id=2,
                address_primary="Невский пр.",
                address_num=120,
                address_postfix="а"
            )
        ]
        session.add_all(houses)
        session.commit()


demo_data()
