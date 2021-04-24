from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, BigInteger, String, Float

Base = declarative_base()


class SavedLocation(Base):
    __tablename__ = "weather_locations"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city_id = Column(BigInteger, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
