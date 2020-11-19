from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from database import berths, cost_queue, database
from models import (
    Ship, ShipDTO,
    calculate_scores_for_ship
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return { "ping": "pong!" }

@app.post("/cost-queue/")
async def create_queue_entry(ship_dto: ShipDTO):

    ship = await calculate_scores_for_ship(ship_dto, database)

    ship_json = jsonable_encoder(ship)

    query = cost_queue.insert().returning(cost_queue.c.id).values(ship_details = ship_json, created_at = datetime.now())

    entry_id = await database.execute(query)

    return {
        'entry': {
            'id': entry_id,
            'ship': ship_json,
            'createdAt': datetime.today()
        }
    }

@app.get("/cost-queue/")
async def read_cost_queue_entries():
    query = cost_queue.select()
    entries = await database.fetch_all(query)

    return {
        'entries': entries
    }

