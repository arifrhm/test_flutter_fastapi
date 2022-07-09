from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+asyncpg://arifrahman:RSCunited2021@localhost:5432/flutter_db')

meta = MetaData()

conn = engine.connect()