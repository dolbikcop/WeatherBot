import os
from typing import Any, Dict

from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, DateTime, Float, select, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, Mapped, sessionmaker

load_dotenv()
engine = create_engine(os.getenv("DB_URL"), echo=True)
Base = declarative_base()


class CityWeather(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_name: Mapped[str] = mapped_column(String, index=True)
    datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    temp: Mapped[int] = mapped_column(Float)
    wind_speed: Mapped[int] = mapped_column(Integer)
    wind_dir: Mapped[str] = mapped_column(String)

    def __init__(self, **kwargs):
        self.city_name = kwargs['name']
        self.temp = kwargs['temp']
        self.wind_speed = kwargs['wind_speed']
        self.wind_dir = kwargs['wind_dir']


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def db_add_weather_info(weather: Dict[str, Any]):
    weather = CityWeather(**weather)
    session.add(weather)
    session.commit()


def db_get_weather_info(city_name: str):
    weather_journal = session.execute(
        select(CityWeather)
        .filter(CityWeather.city_name == city_name))

    return weather_journal.scalars().all()
