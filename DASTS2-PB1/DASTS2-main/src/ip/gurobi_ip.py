import gurobipy as gp
from gurobipy import GRB

from src.ip.ip_utils import make_dirs_if_not_present, post_process


def solve_by_gurobi(config, inp):
    model = gp.Model("DASTS2-GUROBI")

    if config.solver.time_limit > 0:
        model.setParam("TimeLimit", config.solver.time_limit)
    if config.solver.num_worker > 0:
        model.setParam("Threads", config.solver.worker)
    model.setParam("IntegralityFocus", 1)
    model.setParam("IntFeasTol", 1e-9)

    try:
        special_params = config.solver.model_params.gurobi
        for p_name, p_value in special_params.items():
            model.setParam(p_name, p_value)
    except Exception:
        print("Khong co config bo sung cho mo hinh")

    make_dirs_if_not_present(config.result_folder)
    if config.solver.solver_log:
        model.setParam("LogFile", config.result_folder + "/" + inp['data_set'] + ".log")

    # param
    num_staff = config.params["num_staff"]
    num_drone = config.params["num_drone"]
    L_w = config.params["L_w"]
    L_d = config.params["L_d"]

    t = inp["tau"]
    t_a = inp["tau_a"]
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

    # declare var
    x = {}
    y = {}
    A = {}
    B = {}
    T = {}
    l = {}

    for k in range(num_staff):
        for i in C01:
            for j in C02:
                if i != j:
                    x[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f"x[{i},{j},{k}]")

    for d in range(num_drone):
        for r in range(num_drone_trip):
            for i in C21:
                for j in C22:
                    if i != j:
                        y[i, j, d, r] = model.addVar(vtype=GRB.BINARY, name=f"y[{i},{j},{d},{r}]")

    for k in range(num_staff):
        A[k] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"A[{k}]")

    for d in range(num_drone):
        B[d] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"B[{d}]")

    for d in range(num_drone):
        for r in range(num_drone_trip):
            T[d, r] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"T[{d},{r}]")

    for k in range(num_staff):
        l[0, k] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"l[0,{k}]")
        l[num_cus + 1, k] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"l[{num_cus + 1},{k}]")
        for i in C:
            l[i, k] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"l[{i},{k}]")

    for d in range(num_drone):
        for r in range(num_drone_trip):
            l[0, d, r] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"l[{0},{d},{r}]")
            l[num_cus + 1, d, r] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"l[{num_cus + 1},{d},{r}]")

            for i in C2:
                l[i, d, r] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"l[{i},{d},{r}]")
    # Obj
    tmp_obj = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"tmp_obj")
    var_lst = [A[k] for k in range(num_staff)]
    var_lst.extend([B[d] for d in range(num_drone)])
    model.addGenConstrMax(tmp_obj, var_lst, 0.0, "max_time")
    model.setObjective(tmp_obj, GRB.MINIMIZE)

    # constraint

    for k in range(num_staff):
        model.addConstr(l[0, k] == 0)
        for i in C01:
            for j in C02:
                if i != j:
                    model.addConstr((x[i, j, k] == 1) >> (l[j, k] == l[i, k] + 1))

    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.addConstr(l[0, d, r] == 0)
            for i in C21:
                for j in C22:
                    if i != j:
                        model.addConstr((y[i, j, d, r] == 1) >> (l[j, d, r] == l[i, d, r] + 1))
    # 7
    tmp7 = {}

    for k in range(num_staff):
        tmp7[k] = model.addVar(vtype=GRB.BINARY, name=f"tmp7[{k}]")
        model.addConstr(tmp7[k] == gp.quicksum(x[0, j, k] for j in C02 if j != num_cus + 1), name=f"c_tmp7[{k}]")
        model.addConstr(tmp7[k] == gp.quicksum(x[i, num_cus + 1, k] for i in C01 if i != 0),
                        name=f"inOutTech_tech[{k}]")

        model.addConstr((tmp7[k] == 0)
                        >> (gp.quicksum(x[i, j, k] for i in C01 for j in C02 if i != j) == 0),
                        name=f"inOutTech2_tech[{k}]")

    # 8
    for k in range(num_staff):
        model.addConstr(gp.quicksum(x[0, j, k] for j in C02) <= 1, name=f"outTech_tech[{k}]")
    # 9
    tmp9 = {}
    for d in range(num_drone):
        for r in range(num_drone_trip):
            tmp9[d, r] = model.addVar(vtype=GRB.BINARY, name=f"tmp9[{d, r}]")
            model.addConstr(tmp9[d, r] == gp.quicksum(y[0, j, d, r] for j in C22 if j != num_cus + 1),
                            name=f"c_tmp9[{d, r}]")
            model.addConstr(tmp9[d, r] == gp.quicksum(y[i, num_cus + 1, d, r] for i in C21 if i != 0),
                            name=f"inOutDrone_trip[{r}]_drone[{d}]")

            model.addConstr((tmp9[d, r] == 0)
                            >> (gp.quicksum(y[i, j, d, r] for i in C21 for j in C22 if i != j) == 0),
                            name=f"inOutDrone2_trip[{r}]_drone[{d}]")

    # 10
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.addConstr(gp.quicksum(y[0, j, d, r] for j in C22) <= 1, name=f"outDrone_trip[{r}]_drone[{d}]")
    # 11
    for j in C2:
        model.addConstr(gp.quicksum(x[i, j, k] for i in C01 for k in range(num_staff) if i != j) + gp.quicksum(
            y[i, j, d, r] for i in C21 for d in range(num_drone) for r in range(num_drone_trip) if i != j) == 1,
                        name=f"service1_node[{j}]")
    # 12
    for j in C1:
        model.addConstr(gp.quicksum(x[i, j, k] for i in C01 for k in range(num_staff) if i != j) == 1,
                        name=f"service2_node[{j}]")

    # 13
    for i in C2:
        model.addConstr(gp.quicksum(x[i, j, k] for j in C02 for k in range(num_staff) if i != j) + gp.quicksum(
            y[i, j, d, r] for j in C22 for d in range(num_drone) for r in range(num_drone_trip) if i != j) == 1,
                        name=f"service3_node[{i}]")

    # 14
    for i in C1:
        model.addConstr(gp.quicksum(x[i, j, k] for j in C02 for k in range(num_staff) if i != j) == 1,
                        name=f"service4_node[{i}]")

    # 15
    for j in C:
        for k in range(num_staff):
            model.addConstr(
                gp.quicksum(x[i, j, k] for i in C01 if i != j) == gp.quicksum(x[j, i, k] for i in C02 if i != j),
                name=f"inOutCusTech_node[{j}]_tech[{k}]")

    # 16
    for j in C2:
        for d in range(num_drone):
            for r in range(num_drone_trip):
                model.addConstr(gp.quicksum(y[i, j, d, r] for i in C21 if i != j) == gp.quicksum(
                    y[j, i, d, r] for i in C22 if i != j),
                                name=f"inOutCusDrone_node[{j}]_drone[{d}]_trip[{r}]")
    # 17
    for d in range(num_drone):
        for r in range(num_drone_trip - 1):
            model.addConstr(gp.quicksum(y[0, j, d, r] for j in C2) >= gp.quicksum(y[0, j, d, r + 1] for j in C2),
                            name=f"existDroneTrip_drone[{d}]_trip[{r}]")

    # 18
    for k in range(num_staff):
        model.addConstr(A[k] == gp.quicksum(x[i, j, k] * t[i, j] for i in C01 for j in C02 if i != j),
                        name=f"techCompleteTime_tech[{k}]")
    # 19
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.addConstr(T[d, r] == gp.quicksum(y[i, j, d, r] * t_a[i, j] for i in C21 for j in C22 if i != j),
                            name=f"droneTripCompleteTime_drone[{d}]_trip[{r}]")

    # 20
    for d in range(num_drone):
        model.addConstr(B[d] == gp.quicksum(T[d, r] for r in range(num_drone_trip)),
                        name=f"droneCompleteTime_drone[{d}]")

    # 21
    for k in range(num_staff):
        model.addConstr(A[k] - gp.quicksum(x[0, j, k] * t[0, j] for j in C02) <= L_w, name=f"cusWaitTimeTech_tech[{k}]")

    # 22
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.addConstr(T[d, r] - gp.quicksum(y[0, j, d, r] * t_a[0, j] for j in C22) <= L_w,
                            name=f"cusWaitTimeDrone_drone[{d}]_trip[{r}]")

    # 23
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.addConstr(T[d, r] <= L_d, name=f"flyTimeDrone_drone[{d}]_trip[{r}]")

    model.optimize()
    model.write(config.result_folder + "/" + f"model_{inp['data_set']}.lp")

    if model.status == GRB.OPTIMAL:
        print('Optimal objective: %g' % model.objVal)
    elif model.status == GRB.INF_OR_UNBD:
        print('Model is infeasible or unbounded')
    elif model.status == GRB.INFEASIBLE:
        print('Model is infeasible')
    elif model.status == GRB.UNBOUNDED:
        print('Model is unbounded')
    else:
        print('===\nOptimization ended with status %d' % model.status)

    print('Obj: %g' % model.objVal)

    post_process(model, model.status, inp, config,
                 x, y, A, B, T)
