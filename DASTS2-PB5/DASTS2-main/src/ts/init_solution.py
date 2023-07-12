import random

import numpy as np


def init_by_distance(inp, config, reverse=False):
    solution = []
    num_drone = config.params.num_drone
    num_staff = config.params.num_staff
    for i in range(num_drone + num_staff):
        solution.append([])

    sorted_neighborhood = {}
    for cus in range(inp['num_cus'] + 1):
        tmp = {}
        for neighbor in range(inp['num_cus'] + 1):
            if cus != neighbor:
                tmp[neighbor] = inp['tau'][cus, neighbor]

        tmp = sorted(tmp.items(), key=lambda e: e[1], reverse=reverse)
        sorted_neighborhood[cus] = [i for i, _ in tmp]

    travel_time = [0] * (num_drone + num_staff)

    i = 0
    C1 = inp['C1']
    visited_cus = []
    n_iter = 0

    while len(visited_cus) < inp['num_cus'] and n_iter < (num_drone + num_staff) * inp['num_cus']:
        n_iter += 1
        time_dict = inp['tau']
        if i < num_drone and len(solution[i]) == 0:
            solution[i].append([])

        if i < num_drone:
            time_dict = inp['tau_a']
            cur_trip = solution[i][-1]
        else:
            cur_trip = solution[i]

        if len(cur_trip) == 0:
            last_cus = 0
        else:
            last_cus = cur_trip[-1]

        next_cus = None
        for nc in sorted_neighborhood[last_cus]:
            if nc == 0:
                continue
            if nc not in visited_cus:
                if i >= num_drone:
                    next_cus = nc
                    break
                if i < num_drone and i not in C1:
                    next_cus = nc
                    break

        if next_cus is None:
            continue

        if i < num_drone:
            if travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] > config.params.L_d or \
                    travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] \
                    - time_dict[0, next_cus if len(cur_trip) == 0 else cur_trip[0]] \
                    > config.params.L_w:
                solution[i].append([next_cus])
                travel_time[i] = time_dict[0, next_cus]
            else:
                cur_trip.append(next_cus)
                travel_time[i] = travel_time[i] + time_dict[last_cus, next_cus]
            visited_cus.append(next_cus)
        else:
            if travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] \
                    - time_dict[0, next_cus if len(cur_trip) == 0 else cur_trip[0]] \
                    <= config.params.L_w:
                cur_trip.append(next_cus)
                travel_time[i] = travel_time[i] + time_dict[last_cus, next_cus]
                visited_cus.append(next_cus)
        i += 1
        i %= num_drone + num_staff

    if len(visited_cus) < inp['num_cus']:
        return None

    return solution


def init_by_angle(inp, config, reverse=False, direction=None):
    if direction is None:
        direction = random.choice([1, -1])
    solution = []
    num_drone = config.params.num_drone
    num_staff = config.params.num_staff
    for i in range(num_drone + num_staff):
        solution.append([])

    sorted_neighborhood_by_distance = {}
    for cus in range(inp['num_cus'] + 1):
        tmp = {}
        for neighbor in range(inp['num_cus'] + 1):
            if cus != neighbor:
                tmp[neighbor] = inp['tau'][cus, neighbor]

        tmp = sorted(tmp.items(), key=lambda e: e[1], reverse=reverse)
        sorted_neighborhood_by_distance[cus] = [i for i, _ in tmp]

    coordinates_matrix = np.loadtxt(inp["data_path"], skiprows=2)[:, :2]
    pivot_cus = sorted_neighborhood_by_distance[0][0]

    inner = np.inner(coordinates_matrix[pivot_cus - 1], coordinates_matrix)
    norms = np.linalg.norm(coordinates_matrix, axis=1) * np.linalg.norm(coordinates_matrix[pivot_cus - 1])
    acos = inner / norms
    angle = np.arccos([min(1, acos[i]) for i in range(len(acos))])

    perpendicular = coordinates_matrix[pivot_cus - 1][[1, 0]] * [1, -1]
    if direction == 1:
        is_cc = np.dot(coordinates_matrix, perpendicular) < 0
    else:
        is_cc = np.dot(coordinates_matrix, perpendicular) > 0

    angle[is_cc] = 2 * np.pi - angle[is_cc]
    angle[pivot_cus - 1] = 0

    tmp = {}
    for neighbor in range(inp['num_cus']):
        tmp[neighbor + 1] = angle[neighbor]

    tmp = sorted(tmp.items(), key=lambda e: e[1])
    sorted_neighborhood_by_angle = [i for i, _ in tmp]

    travel_time = [0] * (num_drone + num_staff)
    i = 0
    C1 = inp['C1']
    visited_cus = []
    n_iter = 0
    while len(visited_cus) < inp['num_cus'] and n_iter < (num_drone + num_staff) * inp['num_cus']:
        n_iter += 1
        if i < num_drone:
            solution[i].append([])

        if i < num_drone:
            time_dict = inp['tau_a']
            current_trip = solution[i][-1]
            travel_time[i] = 0
        else:
            time_dict = inp['tau']
            current_trip = solution[i]
            if len(current_trip) > 0:
                i += 1
                i %= num_drone + num_staff  
                continue    
        j = 0
        last_cus = 0
        while j < len(sorted_neighborhood_by_angle):
            next_cus = sorted_neighborhood_by_angle[j]
            if i < num_drone and next_cus not in C1:
                if travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] <= config.params.L_d and \
                        travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] \
                        - time_dict[0, next_cus if len(current_trip) == 0 else current_trip[0]] <= config.params.L_w:
                    current_trip.append(next_cus)
                    travel_time[i] = travel_time[i] + time_dict[last_cus, next_cus]
                    visited_cus.append(next_cus)
                    sorted_neighborhood_by_angle.remove(next_cus)
                    last_cus = next_cus
                else:
                    j = j + 1
            else:
                if travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] - time_dict[
                    0, next_cus if len(current_trip) == 0 else current_trip[0]] <= config.params.L_w:
                    current_trip.append(next_cus)
                    travel_time[i] = travel_time[i] + time_dict[last_cus, next_cus]
                    visited_cus.append(next_cus)
                    sorted_neighborhood_by_angle.remove(next_cus)
                    last_cus = next_cus
                else:
                    j = j + 1

        i += 1
        i %= num_drone + num_staff

    if len(visited_cus) < inp['num_cus']:
        return None

    return solution