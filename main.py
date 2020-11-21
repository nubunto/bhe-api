from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy import desc, select,func
from database import berths, cost_queue, berths_priority_queue, database
from berthassigner import BerthAssigner
from models import (
    Ship, ShipDTO,
    calculate_scores_for_ship
)
from pspmetrics import PspMetrics

app = FastAPI()
metrics = PspMetrics(database)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"]
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return { "ping": "pong!" }

@app.post("/prioritize")
async def prioritize():

    pqueue_query = cost_queue.select()
    pqueue_list = await database.fetch_all(pqueue_query)

    ship_quantity_query = select([berths.c.id, func.count(berths_priority_queue.c.ship_details).label('count')]).select_from(berths_priority_queue.join(berths)).group_by(berths.c.id)
    berth_and_ship_quantity = await database.fetch_all(ship_quantity_query)

    queued_ships = [dict(ship_details = entry.get('ship_details'), entry_id = entry.get('id')) for entry in pqueue_list]
    berth_list = [dict(id = entry.get('id'), total_ships_in_queue = entry.get('count')) for entry in berth_and_ship_quantity]

    print(berth_list)

    assigner = BerthAssigner(berth_list, queued_ships)
    berth_assignments = assigner.calculate_prioritization()

    for registry in berth_assignments:
        for ship in registry['ships']:
            entry_id = ship['entry_id']
            
            insert_query = berths_priority_queue.insert()
            await database.execute(insert_query, values={'berth_id': registry['berth_id'] ,'priority':ship['ship_details']['priority_score'] , 'ship_details': ship['ship_details']})
            
            delete_query = cost_queue.delete().where(cost_queue.c.id == entry_id)
            await database.execute(delete_query)

    return berth_assignments

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

@app.get("/berths/")
async def get_berths():
    entries = await database.fetch_all(berths.select())

    return {
        'entries': entries
    }


@app.get("/cost-queue/")
async def read_cost_queue_entries():
    entries = await database.fetch_all(cost_queue.select())

    return {
        'entries': entries
    }

@app.get("/priority-queue/{berth_id}")
async def priority_queue_for_berth(berth_id: int):
    query = berths_priority_queue.select().select_from(berths_priority_queue.join(berths)).where(berths_priority_queue.c.berth_id == berth_id).order_by(desc(berths_priority_queue.c.priority))
    entries = await database.fetch_all(query)

    response = [dict(details = entry.get('ship_details'), entry_id = entry.get('id')) for entry in entries]
    return response

@app.delete("/priority-queue/{berth_id}/{entry_id}")
async def delete_entry_for_berth_priority_queue(berth_id: int, entry_id: int):
    query = berths_priority_queue.delete().where(berths_priority_queue.c.berth_id == berth_id).where(berths_priority_queue.c.id == entry_id).order_by(desc(berths_priority_queue.c.priority))
    await database.execute(query)
    return {'message': 'OK'}

@app.get("/priority-queue/")
async def priority_queue_for_all_berths():
    query = berths_priority_queue.select().select_from(berths_priority_queue.join(berths))
    entries = await database.fetch_all(query)

    response = {}
    for entry in entries:
        berth_id = entry.get('berth_id')
        ship = {
            'details': entry.get('ship_details'),
            'entry_id': entry.get('id')
        }
        if berth_id in response:
            response[berth_id]['ships'].append(ship)
        else:
            response[berth_id] = dict(ships = [ship])
    
    return response


@app.get("/pspmetrics/time/purposes")
async def avg_wait_time_by_ship_purpose():
    entries = await metrics.avg_wait_time_by_ship_purpose()

    return {
        'entries': entries
    }

@app.get("/pspmetrics/time/mooring/")
async def avg_mooring_time_late():
    entries = await metrics.avg_mooring_time_late()

    return {
        'entries': entries
    }

@app.get("/pspmetrics/time/unmooring/")
async def avg_unmooring_time_late():
    entries = await metrics.avg_unmooring_time_late()

    return {
        'entries': entries
    }

@app.get("/pspmetrics/count/moorings-per-month")
async def count_moorings_per_month(year: int):
    entries = await metrics.moorings_per_month_in_year(year)

    return {
        'entries': entries
    }
