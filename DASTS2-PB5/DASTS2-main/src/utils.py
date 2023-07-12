import glob
import json
import os


def cal(staff_path_list, drone_path_list, tau, tau_a, num_cus, config,
        drone_trip_cal=None, staff_trip_cal=None, print_log=False):
    """

    :param staff_trip_cal:
    :param drone_trip_cal:
    :param staff_path_list:
    :param drone_path_list:
    :param tau:
    :param tau_a:
    :param num_cus:
    :param config:
    :param print_log:
    :return:
    """
    T = {}
    A = {}
    B = {}

    S = {}

    dz = 0
    cz = 0

    for i, staff in enumerate(staff_path_list):
        if staff_trip_cal is not None and i not in staff_trip_cal:
            continue

        if len(staff) == 0:
            continue
        tmp = tau[0, staff[0]]
        S[staff[0]] = tmp
        for j in range(len(staff) - 1):
            tmp += tau[staff[j], staff[j + 1]]
            S[staff[j + 1]] = tmp
        A[i] = tmp + tau[staff[-1], num_cus + 1]

    for i, drone in enumerate(drone_path_list):
        if drone_trip_cal is not None and i not in drone_trip_cal:
            continue
        tmp = 0
        for j, trip in enumerate(drone):
            if len(trip) == 0:
                continue
            tmp1 = tau_a[0, trip[0]]
            S[trip[0]] = tmp1
            for k in range(len(trip) - 1):
                tmp1 += tau_a[trip[k], trip[k + 1]]
                S[trip[k + 1]] = tmp1
            T[i, j] = tmp1 + tau_a[trip[-1], num_cus + 1]
            tmp += T[i, j]

        if tmp > 0:
            B[i] = tmp

    if len(A) == len(B) == 0:
        c = 0
    elif len(B) == 0:
        c = max(A.values())
    elif len(A) == 0:
        c = max(B.values())
    else:
        c = max(max(A.values()), max(B.values()))

    for i, staff in enumerate(staff_path_list):
        if staff_trip_cal is not None and i not in staff_trip_cal:
            continue

        if len(staff) == 0:
            continue
        for j in staff:
            cz += max(0, A[i] - S[j] - config.params["L_w"])
    for i, drone in enumerate(drone_path_list):
        if drone_trip_cal is not None and i not in drone_trip_cal:
            continue

        for j, trip in enumerate(drone):
            if len(trip) == 0:
                continue
            for k in trip:
                cz += max(0, T[i, j] - S[k] - config.params["L_w"])

            dz += max(0, T[i, j] - config.params["L_d"])

    if print_log:
        print(f"A: {A}")
        print(f"B: {B}")
        print(f"T: {T}")
        print(f"S: {S}")
        print(f"dz: {dz}")
        print(f"cz: {cz}")

    return c, dz, cz

def cal(staff_path_list, drone_path_list, tau, tau_a, num_cus, config, nested_tau, nested_tau_a, 
        drone_trip_cal=None, staff_trip_cal=None, print_log=False):
    """

    :param staff_trip_cal:
    :param drone_trip_cal:
    :param staff_path_list:
    :param drone_path_list:
    :param tau:
    :param tau_a:
    :param num_cus:
    :param config:
    :param print_log:
    :return:
    """
    T = {}
    A = {}
    B = {}

    S = {}

    dz = 0
    cz = 0

    for i, staff in enumerate(staff_path_list):

        if len(staff) == 0:
            continue
        # tmp = tau[0, staff[0]]
        staff_0 = staff[0]
        tmp = tau[0, staff_0]
        S[staff_0] = tmp
        for j in range(len(staff) - 1):
            tmp += tau[staff[j], staff[j + 1]] + nested_tau[staff[j]]
            S[staff[j + 1]] = tmp
        A[i] = tmp + tau[staff[-1], num_cus + 1] + nested_tau[staff[-1]]

    for i, drone in enumerate(drone_path_list):
        # if drone_trip_cal is not None and i not in drone_trip_cal:
        #     continue
        tmp = 0
        for j, trip in enumerate(drone):
            if len(trip) == 0:
                continue
            trip_0 = trip[0]
            tmp1 = tau_a[0, trip_0]
            S[trip_0] = tmp1
            for k in range(len(trip) - 1):
                tmp1 += tau_a[trip[k], trip[k + 1]] + nested_tau_a[trip[k]]
                S[trip[k + 1]] = tmp1
            T[i, j] = tmp1 + tau_a[trip[-1], num_cus + 1] + nested_tau_a[trip[-1]]
            tmp += T[i, j]

        if tmp > 0:
            B[i] = tmp

    if len(A) == len(B) == 0:
        c = 0
    elif len(B) == 0:
        c = max(A.values())
    elif len(A) == 0:
        c = max(B.values())
    else:
        c = max(max(A.values()), max(B.values()))

    for i, staff in enumerate(staff_path_list):
        if len(staff) == 0:
            continue
        for j in staff:
            cz += max(0, A[i] - S[j] - config.params["L_w"])
    for i, drone in enumerate(drone_path_list):
        for j, trip in enumerate(drone):
            if len(trip) == 0:
                continue
            for k in trip:
                cz += max(0, T[i, j] - S[k] - config.params["L_w"])

            dz += max(0, T[i, j] - config.params["L_d"])

    return c, dz, cz

def make_dirs(path):
    """

    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def make_dirs_if_not_present(path):
    """
    creates new directory if not present
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_result(config):
    paths = glob.glob(config.result.path)
    result = {}
    for data_path in paths:
        data = json.loads(open(data_path).read())
        if "ts" in data_path or "tabu" in data_path:
            optimal = {"tabu": data["tabu"]["tabu-score"],
                       "ejection": data["ejection"]["ejection-score"],
                       "inter": data["inter"]["inter-score"],
                       "intra": data["intra"]["intra-score"]}
        else:
            optimal = data["Optimal"]

        result[os.path.splitext(os.path.basename(data_path))[0]] = optimal
    with open(os.path.join(os.path.dirname(paths[0]), 'final_result.json'),
              'w') as json_file:
        json.dump(result, json_file, indent=2)


if __name__ == '__main__':
    pass
