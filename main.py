from fastapi import FastAPI
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

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

@app.get("/")
async def root():
    return { "message": "Hello, world!" }

@app.post("/cost-queue/")
async def create_queue_entry(ship: ShipDTO):
    return {
        'entry': {
            'id': 1,
            'ship': ship,
            'createdAt': datetime.today()
        }
    }


