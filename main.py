from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from database import berths, cost_queue, database

class ShipType(str, Enum):
    BulkCarrier = "BulkCarrier"
    Other = "Other"

class ShipPurpose(str, Enum):
    TransportBulkLiquid = "TransportBulkLiquid"
    TransportBulkSolid = "TransportBulkSolid"
    TransportGeneralCargo = "TransportGeneralCargo"
    Other = "Other"

class CargoType(str, Enum):
    Bulk = "Bulk"
    General = "General"

class ShipDTO(BaseModel):
    code: str
    is_off_shore: bool
    ship_name: str
    ship_type: ShipType
    ship_purpose: ShipPurpose
    draft_size_in_meters: float
    cargo_weight: float
    cargo_type: CargoType
    estimated_mooring: datetime
    estimated_unmooring: datetime
    needs_fiscalization: bool

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return { "message": "Hello, world!" }

@app.post("/cost-queue/")
async def create_queue_entry(ship: ShipDTO):

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


