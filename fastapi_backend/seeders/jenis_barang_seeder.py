import gevent
from fastapi.logger import logger
from sqlalchemy import insert, select, text
from sqlalchemy.exc import SQLAlchemyError
from models import jenis_barang_models
from sqlalchemy.ext.asyncio.engine import AsyncEngine
import csv
import os

CSV_FILENAME = 'jenis_barang.csv'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This is project Root
DATA_PATH = os.path.join(ROOT_DIR, 'seeders/csv')


async def start(con: AsyncEngine):
    logger.info("Start Jenis Barang Seeding...")

    try:

        # check data already exist or not
        result = await con.execute(select(jenis_barang_models.JenisBarang.id).limit(1))
        await con.commit()
        if len(result.scalars().all()) <= 0:
            # data doesnt exists
            data_list = []
            with open(os.path.join(DATA_PATH, CSV_FILENAME), newline='') as csvfile:
                seed_reader = csv.reader(csvfile, delimiter=',')
                next(seed_reader)
                for row in seed_reader:
                    data_list.append((
                        row[0],
                        row[1]
                    ))

            # make string query
            parse_query = "INSERT INTO jenis_barang (id,jenis_barang) VALUES "
            for data in data_list:
                if data != data_list[-1]:
                    parse_query += str(data)+','
                else:
                    parse_query += str(data)

            # convert query to SQL text
            insert_query = text(parse_query)

            # execute
            await con.execute(insert_query)
            await con.commit()
            logger.info("Finish seeding...")
        else:
            logger.info("Data already exists, skip seeding...")

    except gevent.Timeout:
        logger.error("Seeding failed, DB timeout...")
    except SQLAlchemyError as e:
        logger.error(e)
        if len(result.scalars().all()) <= 0:
            # data doesnt exists
            data_list = []
            with open(os.path.join(DATA_PATH, CSV_FILENAME), newline='') as csvfile:
                seed_reader = csv.reader(csvfile, delimiter=',')
                next(seed_reader)
                for row in seed_reader:
                    data_list.append((
                        row[0],
                        row[1]
                    ))

            # make string query
            parse_query = "INSERT INTO jenis_barang (id,jenis_barang) VALUES "
            for data in data_list:
                if data != data_list[-1]:
                    parse_query += str(data)+','
                else:
                    parse_query += str(data)

            # convert query to SQL text
            insert_query = text(parse_query)

            # execute
            await con.execute(insert_query)
            await con.commit()
            logger.info("Finish seeding...")
        else:
            logger.info("Data already exists, skip seeding...")
        logger.error("Seeding failed, data already exist...")
