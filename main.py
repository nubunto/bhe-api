from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
from database import berths, cost_queue, database
import math

class ShipType(str, Enum):
    BulkCarrier = "BulkCarrier"
    Other = "Other"

class ShipPurpose(str, Enum):
    # TODO: add missing purposes
    TransportBulkLiquid = "TransportBulkLiquid"
    TransportBulkSolid = "TransportBulkSolid"
    TransportGeneralCargo = "TransportGeneralCargo"
    Dredging = "Dredging"
    PortSupport = "PortSupport"
    Other = "Other"

    def map_to_str_purpose(self):
        # FIXME: return correct string
        if self == ShipPurpose.Dredging:
            return "Dragagem"
        elif self == ShipPurpose.PortSupport:
            return "Apoio Portuário"
        else:
            return "Transporte de Carga Geral"

class CargoType(str, Enum):
    Bulk = "Bulk"
    General = "General"

class ShipDTO(BaseModel):
    code: str
    is_off_shore: bool
    ship_name: str
    ship_type: ShipType
    ship_purpose: ShipPurpose
    ship_length_in_meters: float
    ship_capacity_in_teu: float
    draft_size_in_meters: float
    cargo_weight: float
    cargo_type: CargoType
    estimated_mooring: datetime
    estimated_unmooring: datetime
    needs_fiscalization: bool
    time_of_arrival_in_port: datetime

class Ship(BaseModel):
    code: str
    is_off_shore: bool
    ship_name: str
    ship_type: ShipType
    ship_purpose: ShipPurpose
    ship_length_in_meters: float
    ship_capacity_in_teu: float
    draft_size_in_meters: float
    cargo_weight: float
    cargo_type: CargoType
    estimated_mooring: datetime
    estimated_unmooring: datetime
    needs_fiscalization: bool
    time_of_arrival_in_port: datetime
    priority_score: int = 0
    cost_score: int = 0

async def calculate_scores_for_ship(ship: ShipDTO, database):
    priority_score = calculate_priority_score_for_ship(ship)
    cost_score = await calculate_cost_score_for_ship(ship, database)
    return Ship(**ship.dict(), priority_score = priority_score, cost_score = cost_score)

def calculate_priority_score_for_ship(ship: Ship):
    # FIXME: calculate priority score
    # FIXME: add the following attributes to ship:
    # - is_cargo_dangerous
    # - is_cargo_important
    # - cargo_validity_date
    # - has_living_animals
    return 10

async def calculate_cost_score_for_ship(ship: ShipDTO, database):
    base_score = 10

    if ship.needs_fiscalization:
        base_score += 10

    # add 5% of the ship's capacity to the cost
    base_score += math.floor(ship.ship_capacity_in_teu * 0.005)

    # add 1% of the ship's length to the cost
    base_score += math.ceil(ship.ship_length_in_meters * 0.01)

    # add 1% of the ship's draft size to the cost
    base_score += math.ceil(ship.draft_size_in_meters * 0.01)

    # add 1% of the weight of the ship's cargo to the cost
    base_score += math.ceil(ship.cargo_weight * 0.01)

    values = {
        "purpose": ship.ship_purpose.map_to_str_purpose()
    }

    avg_wait_time = await database.execute("""
            SELECT avg(desatracacao_efetiva - atracacao_efetiva)
            FROM estadia
            WHERE finalidade_embarcacao = :purpose
                  and (desatracacao_efetiva - atracacao_efetiva) > interval '1 hour'
    """, values=values)

    if avg_wait_time == None:
        avg_wait_time = timedelta(days=1)

    if avg_wait_time < timedelta(days = 1):
        base_score += 10
    elif avg_wait_time > timedelta(days = 1) < timedelta(days = 5):
        base_score += 20
    else:
        base_score += 40

    return base_score

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


