from enum import Enum
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from pspmetrics import PspMetrics
import math

class ShipType(str, Enum):
    BulkCarrier = "BulkCarrier"
    Other = "Other"

class ShipPurpose(str, Enum):
    Dredging = "Dredging"
    PortSupport = "PortSupport"
    Fishing = "Fishing"
    MaritimeSupport = "MaritimeSupport"
    Research = "Research"
    TransportBulkLiquidAndGeneral = "TransportBulkLiquidAndGeneral"
    GeneralTransport = "GeneralTransport"
    TubeRelease = "TubeRelease"
    TransportBulkSolidAndGeneral = "TransportBulkSolidAndGeneral"
    CableRelease = "CableRelease"
    TransportBulkSolid = "TransportBulkSolid"
    TransportBulkLiquid = "TransportBulkLiquid"
    Pleasure = "Pleasure"
    ContainerAndGeneral = "ContainerAndGeneral"  
    Recreation = "Recreation"
    ContainerTransport = "ContainerTransport"
    VehicleTransport = "VehicleTransport"
    PassengerTransport = "PassengerTransport"
    Other = "Other"

    def map_to_str_purpose(self):
        # FIXME: return correct string
        if self == ShipPurpose.Dredging:
            return "Dragagem"
        elif self == ShipPurpose.PortSupport:
            return "Apoio Portuário"
        elif self == ShipPurpose.Fishing:
            return "Pesca"
        elif self == ShipPurpose.MaritimeSupport:
            return "Apoio Marítimo"
        elif self == ShipPurpose.Research:
            return "Pesquisa"
        elif self == ShipPurpose.TransportBulkLiquidAndGeneral:
            return "Transporte de Granel Líquido e Carga Geral"
        elif self == ShipPurpose.GeneralTransport:
            return "Transporte de Carga Geral"
        elif self == ShipPurpose.TubeRelease:
            return "Lançamento de Tubos"
        elif self == ShipPurpose.TransportBulkSolidAndGeneral:
            return "Transporte de Granel Sólido e Carga Geral"
        elif self == ShipPurpose.CableRelease:
            return "Lançamento de Cabos"
        elif self == ShipPurpose.TransportBulkSolid:
            return "Transporte de Granel Sólido"
        elif self == ShipPurpose.TransportBulkLiquid:
            return "Transporte de Granel Líquido"
        elif self == ShipPurpose.Pleasure:
            return "Recreio"
        elif self == ShipPurpose.ContainerAndGeneral:
            return "Transporte de Contentores e Carga Geral"
        elif self == ShipPurpose.Recreation:
            return "Lazer"
        elif self == ShipPurpose.ContainerTransport:
            return "Transporte de Contentores"
        elif self == ShipPurpose.VehicleTransport:
            return "Transporte de Veiculos"
        elif self == ShipPurpose.PassengerTransport:
            return "Transporte de Passageiros"
        else:
            return "Other"


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
    is_cargo_dangerous: bool
    is_cargo_important: bool
    cargo_validity_date: datetime 
    has_living_animals: bool

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
    is_cargo_dangerous: bool
    is_cargo_important: bool
    cargo_validity_date: datetime
    has_living_animals: bool

async def calculate_scores_for_ship(ship: ShipDTO, database):
    priority_score = calculate_priority_score_for_ship(ship)
    cost_score = await calculate_cost_score_for_ship(ship, database)
    return Ship(**ship.dict(), priority_score = priority_score, cost_score = cost_score)

def calculate_priority_score_for_ship(ship: Ship):

    cost = 1

    if ship.is_cargo_dangerous == True:
        cost += 10
    

    if ship.is_cargo_important == True:
        cost += 10
    

    if ship.has_living_animals == True:
        cost += 10
    

    if calculate_is_validity_near(ship):
        cost += 10

    return cost

def calculate_is_validity_near(ship: ShipDTO):
    diff_in_days = abs((datetime.now(timezone.utc) - ship.cargo_validity_date).days)

    if diff_in_days < 30:
        return True
    else:
        return False

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

    avg_wait_time = PspMetrics.avg_wait_time(values)

    if avg_wait_time == None:
        avg_wait_time = timedelta(days=1)

    if avg_wait_time < timedelta(days = 1):
        base_score += 10
    elif avg_wait_time > timedelta(days = 1) < timedelta(days = 5):
        base_score += 20
    else:
        base_score += 40

    return base_score