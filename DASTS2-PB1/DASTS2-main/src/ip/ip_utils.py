import json
import os

from docplex.util.status import JobSolveStatus as cp_status
from gurobipy import GRB

from src.utils import make_dirs_if_not_present


def get_variable_value(var, solver):
    if solver == "GUROBI":
        return var.X
    elif solver == "CPLEX":
        return var.solution_value
    else:
        return var.solution_value()


def get_obj_value(model, solver):
    if solver == "GUROBI":
        return model.objVal
    elif solver == "CPLEX":
        return model.objective_value
    else:
        return model.Objective().Value()


def get_runtime(model, solver):
    if solver == "GUROBI":
        return model.getAttr("Runtime")
    elif solver == "CPLEX":
        return -1
    else:
        return model.WallTime()


def get_num_constraint(model, solver):
    if solver == "GUROBI":
        return model.getAttr("NumConstrs")
    elif solver == "CPLEX":
        return model.number_of_constraints
    else:
        return model.NumConstraints()


def get_num_var(model, solver):
    if solver == "GUROBI":
        return model.getAttr("NumVars")
    elif solver == "CPLEX":
        return model.number_of_variables
    else:
        return model.NumVariables()


def get_status(status, solver):
    if solver == "GUROBI":
        return "OPTIMAL" if status == GRB.OPTIMAL else "FEASIBLE"
    elif solver == "CPLEX":
        return "OPTIMAL" if status == cp_status.OPTIMAL_SOLUTION else "FEASIBLE"


def post_process(model, status, inp, config, x, y, A, B, T):
    num_staff = config.params["num_staff"]
    num_drone = config.params["num_drone"]

    num_cus = inp["num_cus"]

    C = [i for i in range(1, num_cus + 1)]
    C1 = inp["C1"]
    C2 = [i for i in C if i not in C1]

    C01 = C[:]
    C01.append(0)
    C02 = C[:]
    C02.append(num_cus + 1)

    C21 = C2[:]
    C21.append(0)
    C22 = C2[:]
    C22.append(num_cus + 1)

    num_drone_trip = len(C2)

    result = {"x": {}, "y": {}, "T": {}, "A": {}, "B": {}}

    result.update(dict(config.params))
    result.update(dict(config.solver))

    if config.solver.solver == "GUROBI":
        result["model_params"] = dict(config.solver.model_params.gurobi)
    elif config.solver.solver == "CPLEX":
        result["model_params"] = dict(config.solver.model_params.cplex)

    make_dirs_if_not_present(config.result_folder)

    if config.solver.solver == "GUROBI" and not (status == GRB.OPTIMAL or status == GRB.TIME_LIMIT):
        result = {"status": "INFEASIBLE" if status == GRB.INFEASIBLE else status}
    if config.solver.solver == "CPLEX" and not (
            status == cp_status.OPTIMAL_SOLUTION or status == cp_status.FEASIBLE_SOLUTION):
        result = {"status": "INFEASIBLE" if status == cp_status.INFEASIBLE_SOLUTION
                                            or cp_status.INFEASIBLE_OR_UNBOUNDED_SOLUTION else status}
    else:
        for k in range(num_staff):
            for i in C01:
                for j in C02:
                    if i != j:
                        if get_variable_value(x[i, j, k], config.solver.solver) > 0:
                            result['x'][f"x[{i},{j},{k}]"] = get_variable_value(x[i, j, k], config.solver.solver)

        for d in range(num_drone):
            for r in range(num_drone_trip):
                for i in C21:
                    for j in C22:
                        if i != j:
                            if get_variable_value(y[i, j, d, r], config.solver.solver) > 0:
                                result['y'][f"y[{i},{j},{d},{r}]"] = get_variable_value(y[i, j, d, r],
                                                                                        config.solver.solver)

        for k in range(num_staff):
            if get_variable_value(A[k], config.solver.solver) > 0:
                result['A'][f"A[{k}]"] = get_variable_value(A[k], config.solver.solver)

        for d in range(num_drone):
            if get_variable_value(B[d], config.solver.solver) > 0:
                result['B'][f"B[{d}]"] = get_variable_value(B[d], config.solver.solver)

        for d in range(num_drone):
            for r in range(num_drone_trip):
                if get_variable_value(T[d, r], config.solver.solver) > 0:
                    result['T'][f"T[{d},{r}]"] = get_variable_value(T[d, r], config.solver.solver)

        result["Optimal"] = get_obj_value(model, config.solver.solver)
        result["Time"] = get_runtime(model, config.solver.solver)
        result["num_constraint"] = get_num_constraint(model, config.solver.solver)
        result['Number of variables'] = get_num_var(model, config.solver.solver)

        result["status"] = get_status(status, config.solver.solver)

    with open(os.path.join(config.result_folder, 'result_' + inp['data_set'] + '.json'), 'w') as json_file:
        json.dump(result, json_file, indent=2)
