from docplex.mp.model import Model

from src.ip.ip_utils import post_process


def solve_by_cplex(config, inp):
    model = Model("DASTS2-CPLEX")

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
                    x[i, j, k] = model.binary_var(f"x[{i},{j},{k}]")

    for d in range(num_drone):
        for r in range(num_drone_trip):
            for i in C21:
                for j in C22:
                    if i != j:
                        y[i, j, d, r] = model.binary_var(f"y[{i},{j},{d},{r}]")

    for k in range(num_staff):
        A[k] = model.continuous_var(lb=0, name=f"A[{k}]")

    for d in range(num_drone):
        B[d] = model.continuous_var(lb=0, name=f"B[{d}]")

    for d in range(num_drone):
        for r in range(num_drone_trip):
            T[d, r] = model.continuous_var(lb=0, name=f"T[{d},{r}]")

    for k in range(num_staff):
        l[0, k] = model.integer_var(lb=0, name=f"l[0,{k}]")
        l[num_cus + 1, k] = model.integer_var(lb=0, name=f"l[{num_cus + 1},{k}]")
        for i in C:
            l[i, k] = model.integer_var(lb=0, name=f"l[{i},{k}]")

    for d in range(num_drone):
        for r in range(num_drone_trip):
            l[0, d, r] = model.integer_var(lb=0, name=f"l[{0},{d},{r}]")
            l[num_cus + 1, d, r] = model.integer_var(lb=0, name=f"l[{num_cus + 1},{d},{r}]")

            for i in C2:
                l[i, d, r] = model.integer_var(lb=0, name=f"l[{i},{d},{r}]")
    # Obj
    var_lst = [A[k] for k in range(num_staff)]
    var_lst.extend([B[d] for d in range(num_drone)])

    model.minimize(model.max(var_lst))

    # constraint

    for k in range(num_staff):
        model.add_constraint(l[0, k] == 0)
        for i in C01:
            for j in C02:
                if i != j:
                    model.add_constraint((x[i, j, k] == 1) >> (l[j, k] == l[i, k] + 1))

    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.add_constraint(l[0, d, r] == 0)
            for i in C21:
                for j in C22:
                    if i != j:
                        model.add_constraint((y[i, j, d, r] == 1) >> (l[j, d, r] == l[i, d, r] + 1))
    # 7
    tmp7 = {}

    for k in range(num_staff):
        tmp7[k] = model.binary_var(f"tmp7[{k}]")
        model.add_constraint(tmp7[k] == model.sum(x[0, j, k] for j in C02 if j != num_cus + 1))
        model.add_constraint(tmp7[k] == model.sum(x[i, num_cus + 1, k] for i in C01 if i != 0))

        model.add_constraint((tmp7[k] == 0)
                             >> (model.sum(x[i, j, k] for i in C01 for j in C02 if i != j) == 0))

    # 8
    for k in range(num_staff):
        model.add_constraint(model.sum(x[0, j, k] for j in C02) <= 1)
    # 9
    tmp9 = {}
    for d in range(num_drone):
        for r in range(num_drone_trip):
            tmp9[d, r] = model.binary_var(f"tmp9[{d, r}]")
            model.add_constraint(tmp9[d, r] == model.sum(y[0, j, d, r] for j in C22 if j != num_cus + 1))
            model.add_constraint(tmp9[d, r] == model.sum(y[i, num_cus + 1, d, r] for i in C21 if i != 0))

            model.add_constraint((tmp9[d, r] == 0)
                                 >> (model.sum(y[i, j, d, r] for i in C21 for j in C22 if i != j) == 0))

    # 10
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.add_constraint(model.sum(y[0, j, d, r] for j in C22) <= 1)
    # 11
    for j in C2:
        model.add_constraint(model.sum(x[i, j, k] for i in C01 for k in range(num_staff) if i != j) + model.sum(
            y[i, j, d, r] for i in C21 for d in range(num_drone) for r in range(num_drone_trip) if i != j) == 1)
    # 12
    for j in C1:
        model.add_constraint(model.sum(x[i, j, k] for i in C01 for k in range(num_staff) if i != j) == 1)

    # 13
    for i in C2:
        model.add_constraint(model.sum(x[i, j, k] for j in C02 for k in range(num_staff) if i != j) + model.sum(
            y[i, j, d, r] for j in C22 for d in range(num_drone) for r in range(num_drone_trip) if i != j) == 1)

    # 14
    for i in C1:
        model.add_constraint(model.sum(x[i, j, k] for j in C02 for k in range(num_staff) if i != j) == 1)

    # 15
    for j in C:
        for k in range(num_staff):
            model.add_constraint(
                model.sum(x[i, j, k] for i in C01 if i != j) == model.sum(x[j, i, k] for i in C02 if i != j))

    # 16
    for j in C2:
        for d in range(num_drone):
            for r in range(num_drone_trip):
                model.add_constraint(model.sum(y[i, j, d, r] for i in C21 if i != j) == model.sum(
                    y[j, i, d, r] for i in C22 if i != j))
    # 17
    for d in range(num_drone):
        for r in range(num_drone_trip - 1):
            model.add_constraint(model.sum(y[0, j, d, r] for j in C2) >= model.sum(y[0, j, d, r + 1] for j in C2))

    # 18
    for k in range(num_staff):
        model.add_constraint(A[k] == model.sum(x[i, j, k] * t[i, j] for i in C01 for j in C02 if i != j))
    # 19
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.add_constraint(T[d, r] == model.sum(y[i, j, d, r] * t_a[i, j] for i in C21 for j in C22 if i != j))

    # 20
    for d in range(num_drone):
        model.add_constraint(B[d] == model.sum(T[d, r] for r in range(num_drone_trip)))

    # 21
    for k in range(num_staff):
        model.add_constraint(A[k] - model.sum(x[0, j, k] * t[0, j] for j in C02) <= L_w)

    # 22
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.add_constraint(T[d, r] - model.sum(y[0, j, d, r] * t_a[0, j] for j in C22) <= L_w)

    # 23
    for d in range(num_drone):
        for r in range(num_drone_trip):
            model.add_constraint(T[d, r] <= L_d)

    model.set_time_limit(config.solver.time_limit)

    try:
        special_params = config.solver.model_params.cplex
        for p_id, p_value in special_params.items():
            model.get_parameter_from_id(p_id).set(p_value)
    except Exception:
        print("Khong co config bo sung cho mo hinh")

    model.print_information()
    model.solve()

    model.print_solution()
    # print(result_status)
    #
    post_process(model, model.get_solve_status(), inp, config,
                 x, y, A, B, T)
