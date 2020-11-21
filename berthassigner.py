from ortools.linear_solver import pywraplp
from rule import BerthRuleData, ShipRuleData, RuleCostCalculator, BerthDepthVsShipDepthRule, BerthHasFiscalizationVsShipNeedsFiscalization
import math

class BerthAssigner():
    def __init__(self, berths, queued_ships):
        self.berths = berths
        self.queued_ships = queued_ships
    
    def calculate_prioritization(self):
        cost_matrix = []
        num_ships = len(self.queued_ships)
        num_berths = len(self.berths)
        solver = pywraplp.Solver.CreateSolver('SCIP')

        for i in range(num_berths):
            cost_matrix.append([])

        for i, berth in enumerate(self.berths):
            for j, ship in enumerate(self.queued_ships):
                berth_rule_data = BerthRuleData(
                    has_fiscalization = berth['has_fiscalization'],
                    depth_in_meters = berth['depth']
                )
                ship_rule_data = ShipRuleData(
                    draft_size_in_meters = ship['ship_details']['draft_size_in_meters'],
                    needs_fiscalization = ship['ship_details']['needs_fiscalization']
                )
                rules = [rule(berth_rule_data, ship_rule_data) for rule in [BerthDepthVsShipDepthRule, BerthHasFiscalizationVsShipNeedsFiscalization]]
                cost_calculator = RuleCostCalculator(rules)
                cost_matrix[i].append(int(ship['ship_details']['cost_score'] + math.ceil(berth['total_ships_in_queue'] * 0.7) + cost_calculator.calculate_aggregate_cost_for_rules()))

        matrix_vars = {}
        for i in range(num_berths):
            for j in range(num_ships):
                matrix_vars[i, j] = solver.IntVar(0, 1, '')
        
        for i in range(num_berths):
            solver.Add(solver.Sum([matrix_vars[i, j] for j in range(num_ships)]) <= 1)

        for j in range(num_ships):
            solver.Add(solver.Sum([matrix_vars[i, j] for i in range(num_berths)]) == 1)

        objective_terms = []
        for i in range(num_berths):
            for j in range(num_ships):
                objective_terms.append(cost_matrix[i][j] * matrix_vars[i, j])
        solver.Minimize(solver.Sum(objective_terms))

        berths = {}
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            for i in range(num_berths):
                for j in range(num_ships):
                    if matrix_vars[i, j].solution_value() > 0.5:
                        berth = self.berths[i]
                        berth_id = berth['id']
                        ship = self.queued_ships[j]
                        if berth_id in berths:
                            berths[berth_id].append(ship)
                        else:
                            berths[berth_id] = [ship]
        return self.__assemble_berth_list(berths)
    
    def __assemble_berth_list(self, berths):
        berth_list = []
        for berth_id in berths:
            berth_list.append({
                'berth_id': berth_id,
                'ships': berths[berth_id]
            })
        return berth_list

