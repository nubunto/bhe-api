from pydantic import BaseModel

__HIGH_COST = 1000

class BerthRuleData(BaseModel):
    depth_in_meters: float
    has_fiscalization: bool

class ShipRuleData(BaseModel):
    draft_size_in_meters: float
    needs_fiscalization: bool

class Rule():
    def __init__(self, berth: BerthRuleData, ship: ShipRuleData):
        self.berth = berth
        self.ship = ship
    
    def calculate_cost(self):
        pass

class BerthDepthVsShipDepthRule(Rule):
    def calculate_cost(self):
        if self.berth.depth_in_meters < self.ship.draft_size_in_meters:
            return __HIGH_COST
        return 0

class BerthHasFiscalizationVsShipNeedsFiscalization(Rule):
    def calculate_cost(self):
        if not self.berth.has_fiscalization and self.ship.needs_fiscalization:
            return __HIGH_COST
        return 0

class RuleCostCalculator:
    def __init__(self, rules):
        self.rules = rules
    
    def calculate_aggregate_cost_for_rules(self):
        base_score = 0
        for rule in rules:
            base_score += rule.calculate_cost()
        return base_score