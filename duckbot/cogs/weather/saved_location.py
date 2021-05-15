from sqlalchemy import BigInteger, Column, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SavedLocation(Base):
    __tablename__ = "weather_locations"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city_id = Column(BigInteger, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
