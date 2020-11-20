from ortools.linear_solver import pywraplp

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
                # TODO: add cost_score to berth
                cost_matrix[i].append(ship['cost_score'] + j)

        matrix_vars = {}
        for i, berth in enumerate(self.berths):
            for j in range(num_ships):
                matrix_vars[i, j] = solver.IntVar(0, 1, f"berth={berth['id']}")
        
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
                            berths[berth_id].ships.append(ship)
                        else:
                            berths[berth_id].ships = [ship]
        return self.__assemble_berth_list(berths)
    
    def __assemble_berth_list(self, berths):
        berth_list = []
        for berth_id in berths:
            berth_list.append({
                'berth_id': berth_id,
                'ships': berths[berth_id]['ships']
            })
        return berth_list
