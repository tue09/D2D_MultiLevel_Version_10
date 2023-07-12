from src.ts.tabu import TabuSearch, TSUtils
import random
from copy import deepcopy
import numpy as np
from src.multilevel.mt_utils import MTUtils
from src.utils import cal
import openpyxl

class Multilevel:

    def __init__(self, inp, config, initial_state, ext=0) -> None:
        self.inp = deepcopy(inp)
        self.config = deepcopy(config)
        self.num_cus = self.inp["num_cus"]
        self.num_staff = self.config.params["num_staff"]
        self.pure_config = config
        self.pure_inp = inp
        self.num_level = self.config.multilevel_params["num_level"]
        self.match_percent = self.config.multilevel_params["percent_match"]
        self.penalty_params = self.config.tabu_params
        self.tabu_params = self.config.tabu_params
        self.mt_utils = MTUtils(config, inp)
        self.tabu_size = self.config.tabu_params["tabu_size"]
        self.max_steps = self.config.multilevel_params["tabu_max_iter"]
        self.tabu = TabuSearch(inp, config, initial_state, self.tabu_size, self.max_steps, ext)
        self.score_dict = {}
        self.ext = ext
        self.best_fitness = 10000000000
        self.num_drone = self.config.params["num_drone"]
        try:
            self.nested_tau = inp["nested_tau"]
            self.nested_tau_a = inp["nested_tau_a"]
        except:
            nested = {}
            for i in range(1, self.inp["num_cus"] + 1):
                nested[i] = 0
            self.nested_tau = nested
            self.nested_tau_a = nested
    
    def match_point(self, staff_path, drone_path, score_edge, match_percent, tau, tau_a, num_cus, nested_point_dict, nested_tau_dict, nested_tau_a_dict, c1):
        result = {}
        sorted_score_edge = []
        num_cus_match = int(num_cus*match_percent)
        point_will_match = []
        next_level_nested = {}
        # get highest score edges
        for i, trip in enumerate(staff_path):
            for j in range(len(trip) - 1):
                point = trip[j]
                next_point = trip[j + 1]
                edge = [point, next_point]
                score = score_edge[point - 1][next_point - 1]
                element = {'edge': edge, 'score': score}
                sorted_score_edge.append(element)
        for i in (drone_path):
            for trip in i:
                for j in range(len(trip) - 1):
                    point = trip[j]
                    next_point = trip[j + 1]
                    edge = [point, next_point]
                    score = score_edge[point - 1][next_point - 1]
                    element = {'edge': edge, 'score': score}
                    sorted_score_edge.append(element)   
        sorted_score_edge = sorted(sorted_score_edge, key= lambda x: x['score'], reverse= True)
        print(sorted_score_edge)
        for score_edge in sorted_score_edge:
            edge = score_edge['edge']
            if edge[0] not in point_will_match and edge[1] not in point_will_match:
                point_will_match.append(edge[0])
                point_will_match.append(edge[1])
            if len(point_will_match) >= num_cus_match*2:
                break
        
        # match point
        # variable
        new_num_cus = num_cus - num_cus_match
        new_solution = []
        new_nested_point = {}
        new_nested_tau = {}
        new_nested_tau_a = {}
        tmp_num_cus = 1
        new_tau = {}
        new_tau_a = {}
        new_C1 = []
        for i in (drone_path):
            drone = []
            for trip in i:
                new_trip = []
                j = 0
                while j < len(trip):
                    found_point = trip[j]
                    nested = []
                    nested_tau = 0
                    nested_tau_a = 0
                    nested_tau += nested_tau_dict[found_point]
                    nested_tau_a += nested_tau_a_dict[found_point]
                    if found_point in nested_point_dict.keys():
                        for element in nested_point_dict[found_point]:
                            nested.append(element)
                    else:
                        nested.append(found_point)
                    if found_point in point_will_match:
                        
                        next_point = trip[j + 1]
                        next_level_nested[tmp_num_cus] = [found_point, next_point]
                        j += 2
                        new_trip.append(tmp_num_cus)
                        nested_tau += tau[found_point, next_point] + nested_tau_dict[next_point]
                        nested_tau_a += tau_a[found_point, next_point] + nested_tau_a_dict[next_point]
                        if next_point in nested_point_dict.keys():
                            for element in nested_point_dict[next_point]:
                                nested.append(element)
                        else:
                            nested.append(next_point)
                        if found_point in c1 or next_point in c1:
                            new_C1.append(tmp_num_cus)
                    else:
                        next_level_nested[tmp_num_cus] = [found_point]
                        j += 1
                        new_trip.append(tmp_num_cus)
                        if found_point in c1:
                            new_C1.append(tmp_num_cus)
                    new_nested_point[tmp_num_cus] = nested
                    new_nested_tau[tmp_num_cus] = nested_tau
                    new_nested_tau_a[tmp_num_cus] = nested_tau_a
                    tmp_num_cus += 1
                drone.append(new_trip)
            new_solution.append(drone)
        for i, trip in enumerate(staff_path):
            new_trip = []
            j = 0
            while j < len(trip):
                found_point = trip[j]
                nested = []
                nested_tau = 0
                nested_tau_a = 0
                nested_tau += nested_tau_dict[found_point]
                nested_tau_a += nested_tau_a_dict[found_point]
                if found_point in nested_point_dict.keys():
                    for element in nested_point_dict[found_point]:
                        nested.append(element)
                else:
                    nested.append(found_point)
                if found_point in point_will_match:
                    next_point = trip[j + 1]
                    next_level_nested[tmp_num_cus] = [found_point, next_point]
                    j += 2
                    new_trip.append(tmp_num_cus)
                    nested_tau += tau[found_point, next_point] + nested_tau_dict[next_point]
                    nested_tau_a += tau_a[found_point, next_point] + nested_tau_a_dict[next_point]
                    if next_point in nested_point_dict.keys():
                        for element in nested_point_dict[next_point]:
                            nested.append(element)
                    else:
                        nested.append(next_point)
                    if found_point in c1 or next_point in c1:
                        new_C1.append(tmp_num_cus)
                else: 
                    next_level_nested[tmp_num_cus] = [found_point]
                    j += 1
                    new_trip.append(tmp_num_cus)
                    if found_point in c1:
                        new_C1.append(tmp_num_cus)
                new_nested_point[tmp_num_cus] = nested
                new_nested_tau[tmp_num_cus] = nested_tau
                new_nested_tau_a[tmp_num_cus] = nested_tau_a
                tmp_num_cus += 1
            new_solution.append(new_trip)
        # print(new_nested_point)
        new_num_cus = tmp_num_cus - 1
        for i in range(1, new_num_cus + 1):
            new_tau[0, i] = tau[0, next_level_nested[i][0]]
            new_tau_a[0, i] = tau_a[0, next_level_nested[i][0]]
            new_tau[i, new_num_cus + 1] = tau[next_level_nested[i][-1], num_cus + 1]
            new_tau_a[i, new_num_cus + 1] = tau_a[next_level_nested[i][-1], num_cus + 1]
            for j in range(1, new_num_cus + 1):
                if i == j:
                    new_tau[i, j] = 0
                    new_tau_a[i, j] = 0
                else:
                    new_tau[i, j] = tau[next_level_nested[i][-1], next_level_nested[j][0]]
                    new_tau_a[i, j] = tau_a[next_level_nested[i][-1], next_level_nested[j][0]]
        # print(tau)
        # print(new_tau)
        # print(tau_a)
        # print(new_tau_a)
        # print(new_nested_tau)
        # print(new_nested_tau_a)
        result["tau"] = new_tau
        result["tau_a"] = new_tau_a
        result["num_cus"] = new_num_cus
        result["solution"] = new_solution
        result["C1"] = new_C1
        result["nested_tau"] = new_nested_tau
        result["nested_tau_a"] = new_nested_tau_a
        result["nested_point"] = new_nested_point
        result["next_level_nested"] = next_level_nested
        result['sorted_score_edge'] = sorted_score_edge

        return result
    
    def _update_config(self, config, inp):
        self.inp = inp 
        self.config = config 
        self.num_cus = inp["num_cus"]
        self.num = config.params["num_staff"]
    
    def run_multilevel(self, verbose= True):
        nested_point_dict = {}
        nested_point = {}
        for i in range(1, self.num_cus + 1):
            nested_point[i] = [i]
        nested_point_dict[0] = nested_point
        nested_tau_dict = {}
        nested_tau = {}
        for i in range(1, self.num_cus + 1):
            nested_tau[i] = 0
        nested_tau_dict[0] = nested_tau
        nested_tau_a_dict = {}
        nested_tau_a = {}
        for i in range(1, self.num_cus + 1):
            nested_tau_a[i] = 0
        nested_tau_a_dict[0] = nested_tau_a
        level_nested_point = {}
        # level_0_nested = {}
        level_num_cus = {}
        level_num_cus[0] = self.num_cus
        level_c1 = {}
        level_c1[0] = self.inp["C1"]
        level_tau = {}
        level_tau[0] = self.inp["tau"]
        level_tau_a = {}
        level_tau_a[0] = self.inp["tau_a"]
        result_by_level = {}
        cur = self.tabu.initial_state
        for level in range(self.num_level):
            self.penalty_params = self.tabu_params
            # parse solution
            r = {}
            self.tabu._clear()

            # not_improve_iter = 0
            score_edge = np.zeros((self.num_cus, self.num_cus), int)
            tabu_list = [[], [], [], [], [], [], []]
            tabu_duration_list = [[], [], [], [], [], [], []]
            best_fitness = self.mt_utils.get_score(cur, self.penalty_params)[0]
            best_solution = cur
            local_best_solution = cur
            best_local_fitness_info = self.mt_utils.get_score(cur, self.penalty_params)
            if level != 0:
                num_iter = self.config.multilevel_params["tabu_max_iter"]
            else:
                num_iter = 2*self.config.multilevel_params["tabu_max_iter"]
            for iter in range(num_iter):
                # variables'
                best_local_fitness = 100000000000
                # parse solution
                drone_path = []
                staff_path = []
                for i in range(self.num_drone):
                    drone_path.append(cur[i])
                for i in range(self.num_drone, len(cur)):
                    staff_path.append(cur[i])
                act = random.randrange(1,6)
                # act = 5
                #move 10
                if act == 1:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip):
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                # intra
                                for next_point_idx in range(len_trip):
                                    if point_idx != next_point_idx:
                                        copy_cur = deepcopy(cur)
                                        
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        if next_point_idx > point_idx: 
                                            if next_point_idx == point_idx + 1:
                                                continue
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx, tmp)
                                        else:
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, tmp)
                                        
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx].pop(point_idx)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                copy_cur[drone_idx].pop(trip_idx)
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = tmp
                                            #tabu_duration = iter + self.tabu_size
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # create new trip in drone 
                                copy_cur = deepcopy(cur)
                                new_trip = [tmp]
                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                copy_cur[drone_idx].append(new_trip)
                                tabu = tmp
                                #tabu_duration = iter + self.tabu_size
                                if fitness - best_fitness < (-1)*0.000001:
                                    local_best_solution = copy_cur
                                    best_fitness =  fitness
                                    best_local_fitness = fitness
                                    best_solution = copy_cur
                                    best_local_fitness_info = fitness_info
                                    best_tabu = tabu
                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                    
                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                    best_local_fitness = fitness
                                    local_best_solution = copy_cur
                                    best_local_fitness_info = fitness_info 
                                    best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                                if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                    copy_cur[drone_idx].pop(trip_idx)   
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = tmp
                                                #tabu_duration = iter + self.tabu_size
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp]
                                        copy_cur[next_drone_idx].append(new_trip)
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].insert(  + 1, tmp)
                                        if len(copy_cur[drone_idx][trip_idx]) == 0:
                                            copy_cur[drone_idx].pop(trip_idx)
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu

                                    if len_staff_trip == 0:    
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].append(tmp)
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                    #                        
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip):
                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            # intra
                            for next_point_idx in range(len_staff_trip):
                                if point_idx != next_point_idx:
                                    copy_cur = deepcopy(cur)
                                    
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                    if next_point_idx > point_idx: 
                                        if next_point_idx == point_idx + 1:
                                            continue
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx, tmp)
                                    else:
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, tmp)
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = tmp
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                           
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    for next_point_idx in range(len_next_staff):
                                        copy_cur = deepcopy(cur)
                                        
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, tmp)

                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                    if len_next_staff == 0:    
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].append(tmp)
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                            # inter in drone
                            if cur[self.num_drone + staff_idx][point_idx] not in self.inp["C1"]:
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = tmp
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                    # create new trip in drone 
                                    copy_cur = deepcopy(cur)
                                    new_trip = [tmp]
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                    copy_cur[drone_idx].append(new_trip)
                                    tabu = tmp
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info 
                                        best_tabu = tabu
                # move 11
                if act == 2:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip):
                                # intra
                                if point_idx != len_trip - 1:
                                    for next_point_idx in range(point_idx + 1, len_trip):
                                        copy_cur = deepcopy(cur)
                                        tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                        copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][trip_idx][next_point_idx]
                                        copy_cur[drone_idx][trip_idx][next_point_idx] = tmp
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                        tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                            tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                
                                                tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                                copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[next_drone_idx][next_trip_idx][next_point_idx]
                                                copy_cur[next_drone_idx][next_trip_idx][next_point_idx] = tmp
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                                tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                                #tabu_duration = iter + self.tabu_size
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        if copy_cur[self.num_drone + staff_idx][next_point_idx] not in self.inp["C1"]:
                                            copy_cur = deepcopy(cur)
                                            tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                            copy_cur[self.num_drone + staff_idx][next_point_idx] = tmp
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                            tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                        #                        
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip):
                            # intra
                            if point_idx != len_staff_trip - 1:
                                for next_point_idx in range(point_idx + 1, len_staff_trip):
                                    copy_cur = deepcopy(cur)
                                    tmp = copy_cur[self.num_drone + staff_idx][point_idx]
                                    copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                    copy_cur[self.num_drone + staff_idx][next_point_idx] = tmp
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, copy_cur[self.num_drone + staff_idx][point_idx]]
                                    tabu_extra =  [copy_cur[self.num_drone + staff_idx][point_idx], tmp]
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    for next_point_idx in range(len_next_staff):
                                        copy_cur = deepcopy(cur)
                                        tmp = copy_cur[self.num_drone + staff_idx][point_idx]
                                        copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + next_staff_idx][next_point_idx]
                                        copy_cur[self.num_drone + next_staff_idx][next_point_idx] = tmp

                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, copy_cur[self.num_drone + staff_idx][point_idx]]
                                        tabu_extra =  [copy_cur[self.num_drone + staff_idx][point_idx], tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu

                            # inter in drone
                            if cur[self.num_drone + staff_idx][point_idx] not in self.inp["C1"]:
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            tmp = copy_cur[self.num_drone + staff_idx][point_idx]
                                            copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, copy_cur[self.num_drone + staff_idx][point_idx]]
                                            tabu_extra =  [copy_cur[self.num_drone + staff_idx][point_idx], tmp]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                # move 20
                if act == 3:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip - 1):
                                
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                next_tmp = cur[drone_idx][trip_idx][point_idx + 1]
                                # intra
                                for next_point_idx in range(len_trip):
                                    if next_point_idx - point_idx not in [-1, 0, 1]:
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        if next_point_idx > point_idx: 
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx - 1 , next_tmp)
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx - 1, tmp)
                                        else:
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, next_tmp)
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, tmp)
                                        
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        # print("---")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx].pop(point_idx)
                                            copy_cur[drone_idx][trip_idx].pop(point_idx)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                copy_cur[drone_idx].pop(trip_idx)
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("+++")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # create new trip in drone 
                                copy_cur = deepcopy(cur)
                                new_trip = [tmp, next_tmp]
                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                copy_cur[drone_idx].append(new_trip)
                                tabu = [tmp, next_tmp]
                                #tabu_duration = iter + self.tabu_size
                                if fitness - best_fitness < (-1)*0.000001:
                                    local_best_solution = copy_cur
                                    best_fitness =  fitness
                                    best_local_fitness = fitness
                                    best_solution = copy_cur
                                    best_local_fitness_info = fitness_info
                                    best_tabu = tabu
                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                    
                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                    best_local_fitness = fitness
                                    local_best_solution = copy_cur
                                    best_local_fitness_info = fitness_info 
                                    best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                                if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                    copy_cur[drone_idx].pop(trip_idx)   
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp, next_tmp]
                                                #tabu_duration = iter + self.tabu_size
                                                # print("****")
                                                # print(fitness)
                                                # print(copy_cur)
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp, next_tmp]
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[next_drone_idx].append(new_trip)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                                        
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp, next_tmp]
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[next_drone_idx].append(new_trip)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu

                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, tmp)
                                        if len(copy_cur[drone_idx][trip_idx]) == 0:
                                            copy_cur[drone_idx].pop(trip_idx)
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        # print("^^^")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        
                                    if len_staff_trip == 0:
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        # new_trip = [tmp, next_tmp]
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].append(tmp)
                                        copy_cur[self.num_drone + staff_idx].append(next_tmp)
                                        if len(copy_cur[drone_idx][trip_idx]) == 0:
                                            copy_cur[drone_idx].pop(trip_idx)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                    #                        
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip - 1):
                            
                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            next_tmp = cur[self.num_drone + staff_idx][point_idx + 1]
                            # intra
                            for next_point_idx in range(len_staff_trip):
                                if next_point_idx - point_idx not in [-1, 0, 1]:
                                    copy_cur = deepcopy(cur)
                                    
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                    if next_point_idx > point_idx: 
                                        
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx - 1, next_tmp)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx - 1, tmp)
                                    else:
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, tmp)
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, next_tmp]
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    for next_point_idx in range(len_next_staff):
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, next_tmp)
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, tmp)

                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness < (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                    if len_next_staff == 0:
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        # new_trip = [tmp, next_tmp]
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].append(tmp)
                                        copy_cur[self.num_drone + next_staff_idx].append(next_tmp)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                            # inter in drone
                            if tmp not in self.inp["C1"] and next_tmp not in self.inp["C1"] :
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu 
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp, next_tmp]
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[drone_idx].append(new_trip)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu               
                #move 21
                if act == 4:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip - 1):
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                next_tmp = cur[drone_idx][trip_idx][point_idx + 1]
                                # intra
                                for next_point_idx in range(len_trip):
                                    if next_point_idx - point_idx not in [0, 1]:
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][trip_idx][next_point_idx]
                                        copy_cur[drone_idx][trip_idx][next_point_idx] = tmp
                                        copy_cur[drone_idx][trip_idx].pop(point_idx + 1)
                                        if next_point_idx > point_idx: 
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx , next_tmp)
                                        else:
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, next_tmp)
                                            
                                        
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        # print("---")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            copy_cur[drone_idx][trip_idx].pop(point_idx  + 1)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("+++")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                
                                                
                                                copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[next_drone_idx][next_trip_idx][next_point_idx]
                                                copy_cur[next_drone_idx][next_trip_idx][next_point_idx] = tmp
                                                copy_cur[drone_idx][trip_idx].pop(point_idx + 1)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                                  
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp, next_tmp]
                                                #tabu_duration = iter + self.tabu_size
                                                # print("****")
                                                # print(fitness)
                                                # print(copy_cur)
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        if copy_cur[self.num_drone + staff_idx][next_point_idx] not in self.inp["C1"]: 
                                            copy_cur = deepcopy(cur)
                                            
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                            copy_cur[self.num_drone + staff_idx][next_point_idx] = tmp
                                            copy_cur[drone_idx][trip_idx].pop(point_idx + 1)
                                            copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                            
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("^^^")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                    #                      
                    
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip - 1):

                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            next_tmp = cur[self.num_drone + staff_idx][point_idx + 1]
                            # intra
                            for next_point_idx in range(len_staff_trip):
                                if next_point_idx - point_idx not in [ 0, 1]:
                                    copy_cur = deepcopy(cur)
                                    
                                    copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                    copy_cur[self.num_drone + staff_idx][next_point_idx]  = tmp
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx + 1)
                                    if next_point_idx > point_idx: 
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx , next_tmp)
                                    else:
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                        
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, next_tmp]
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    
                                    for next_point_idx in range(len_next_staff):
                                        
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + next_staff_idx][next_point_idx]
                                        copy_cur[self.num_drone + next_staff_idx][next_point_idx]  = tmp
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx + 1)
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, next_tmp)
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness < (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                            # inter in drone
                            if tmp not in self.inp["C1"] and next_tmp not in self.inp["C1"] :
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx + 1) 
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu     
                # move 2opt
                if act == 5:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip - 1):
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                next_tmp = cur[drone_idx][trip_idx][point_idx + 1]
                                # intra
                                if point_idx < len_trip - 3:
                                    for next_point_idx in range(point_idx + 2, len_trip - 1):
                                        copy_cur = deepcopy(cur)

                                        copy_cur[drone_idx][trip_idx][point_idx + 1:next_point_idx + 1] = reversed(copy_cur[drone_idx][trip_idx][point_idx + 1:next_point_idx + 1] )
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        # print("---")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len - 1):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx][point_idx + 1:], copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:] = copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:], copy_cur[drone_idx][trip_idx][point_idx + 1:]
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, cur[drone_idx][next_trip_idx][next_point_idx]]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("+++")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip - 1):
                                                copy_cur = deepcopy(cur)
                                                copy_cur[drone_idx][trip_idx][point_idx + 1:], copy_cur[next_drone_idx][next_trip_idx][next_point_idx + 1:] = copy_cur[next_drone_idx][next_trip_idx][next_point_idx + 1:], copy_cur[drone_idx][trip_idx][point_idx + 1:]                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp,  cur[next_drone_idx][next_trip_idx][next_point_idx]]
                                                #tabu_duration = iter + self.tabu_size
                                                # print("****")
                                                # print(fitness)
                                                # print(copy_cur)
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip - 1):
                                        conclude_c1 = False
                                        for tmp_idx in range(next_point_idx + 1, len_staff_trip):
                                            if cur[self.num_drone + staff_idx][tmp_idx] in self.inp["C1"]: 
                                                conclude_c1 = True
                                        if not conclude_c1:
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx][point_idx + 1:], copy_cur[self.num_drone + staff_idx][next_point_idx + 1:] = copy_cur[self.num_drone + staff_idx][next_point_idx + 1:], copy_cur[drone_idx][trip_idx][point_idx + 1:]
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, cur[self.num_drone + staff_idx][next_point_idx]]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("^^^")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                    #                      
                    
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip - 1):

                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            next_tmp = cur[self.num_drone + staff_idx][point_idx + 1]
                            # intra
                            if point_idx < len_staff_trip - 3:
                                for next_point_idx in range(len_staff_trip - 1):
                                    copy_cur = deepcopy(cur)
                                    copy_cur[self.num_drone + staff_idx][point_idx + 1:next_point_idx + 1]  = reversed(copy_cur[self.num_drone + staff_idx][point_idx + 1:next_point_idx + 1] )
                                    
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, next_tmp]
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    
                                    for next_point_idx in range(len_next_staff - 1):
                                        
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx][point_idx + 1:], copy_cur[self.num_drone + next_staff_idx][next_point_idx + 1:] = copy_cur[self.num_drone + next_staff_idx][next_point_idx + 1:], copy_cur[self.num_drone + staff_idx][point_idx + 1:]
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, cur[self.num_drone + next_staff_idx][next_point_idx]]
                                        # #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur                                                
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness < (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                            # inter in drone
                            conclude_c1 = False
                            for tmp_idx in range(point_idx + 1, len_staff_trip):
                                if cur[self.num_drone + staff_idx][tmp_idx] in self.inp["C1"]:
                                    conclude_c1 = True
                            if not conclude_c1 :
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip - 1):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[self.num_drone + staff_idx][point_idx + 1:], copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:] = copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:], copy_cur[self.num_drone + staff_idx][point_idx + 1:]
                                        
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, cur[drone_idx][next_trip_idx][next_point_idx]]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu 
                        
                if cur != local_best_solution:
                    # print(1)
                    cur = local_best_solution
                    # tabu duration
                    tabu_list[act - 1].append(best_tabu)
                    tabu_duration_list[act - 1].append(iter + self.tabu_size)
                    self.update_penalty_param(best_local_fitness_info[1], best_local_fitness_info[2])
                # print(best_local_fitness)
                print(act)
                print(cur)
                print(best_fitness)
                # print(tabu_list)
                # print(tabu_duration_list)
                # update params
                
                # remove tabu 
                idx = 0
                idx_1 = 0
                while idx < len(tabu_duration_list) - 1:
                    while idx_1 < len(tabu_duration_list[idx]) - 1:
                        if iter >= tabu_duration_list[idx][idx_1]:
                            tabu_list[idx].pop(idx_1)
                            tabu_duration_list[idx].pop(idx_1)
                        else:
                            idx_1 += 1
                    idx += 1
                if iter > self.max_steps:
                    break            
            print(best_fitness)
            if best_fitness - self.best_fitness < (-1)*0.000001:
                self.best_fitness = best_fitness
            # match point
            rs_match = self.match_point(best_solution[self.config.params["num_drone"]:], best_solution[:self.config.params["num_drone"]], score_edge, self.match_percent, self.inp["tau"], self.inp["tau_a"],
                                         self.num_cus, nested_point_dict[level], nested_tau_dict[level], nested_tau_a_dict[level], self.pure_inp["C1"])
            
            result_by_level[level] = {'best_sol': str(best_solution), 'best_fitness': str(best_fitness), 'score_edge': str(rs_match['sorted_score_edge']), 'nested_point': str(rs_match["nested_point"]),
                                       'ori_best_sol': str(self.get_ori_solution(rs_match["solution"][self.config.params["num_drone"]:], rs_match["solution"][:self.config.params["num_drone"]], rs_match["nested_point"]))}     
            print("**")
            
            # print(nested_point)
            # print(new_tau)
            # print(self.tabu.best)
            # print(rs_match["solution"])
            # 
            # (rs_match["next_level_nested"])
            # print(best_score)
            
            print(self.ori_score(rs_match["solution"][self.config.params["num_drone"]:], rs_match["solution"][:self.config.params["num_drone"]]
                                 , rs_match["nested_point"], self.pure_inp["tau"], self.pure_inp["tau_a"], self.pure_inp["num_cus"], nested_tau, nested_tau_a))
            
            # print(rs_match["nested_point"])
            # print(rs_match["tau"])
            # print(self.pure_inp["tau"])
            # update new inp config
            new_config = self.config
            new_inp = self.inp
            new_config["num_cus"] = rs_match["num_cus"]
            new_inp["num_cus"] = rs_match["num_cus"]
            new_inp["C1"] = rs_match["C1"]
            new_inp["tau"] = rs_match["tau"]
            new_inp["tau_a"] = rs_match["tau_a"]
            new_inp["nested_tau"] = rs_match["nested_tau"]
            new_inp["nested_tau_a"] = rs_match["nested_tau_a"]
            nested_point_dict[level + 1] = rs_match["nested_point"]
            nested_tau_dict[level + 1] = rs_match["nested_tau"]
            nested_tau_a_dict[level + 1] = rs_match["nested_tau_a"]
            level_nested_point[level + 1] = rs_match["next_level_nested"]
            level_num_cus[level + 1] = rs_match["num_cus"]
            level_c1[level + 1] = rs_match["C1"]
            level_tau[level + 1] = rs_match["tau"]
            level_tau_a[level + 1] = rs_match["tau_a"]
            cur = rs_match["solution"]
            self._update_config(new_config, new_inp)
            # self.tabu.update(new_config, new_inp)
            self.mt_utils = MTUtils(new_config, new_inp)
            self.tabu = TabuSearch(new_inp, new_config, rs_match["solution"],  self.tabu_size, self.max_steps, self.ext)

        # seperate point and tabu search
        for level in range(self.num_level, -1, -1):

            r = {}
            # not_improve_iter = 0
            score_edge = np.zeros((self.num_cus, self.num_cus), int)
            tabu_list = [[], [], [], [], [], [], []]
            tabu_duration_list = [[], [], [], [], [], [], []]
            best_fitness = self.mt_utils.get_score(cur, self.penalty_params)[0]
            best_solution = cur
            local_best_solution = cur
            best_local_fitness_info = self.mt_utils.get_score(cur, self.penalty_params)
            score_edge = np.zeros((self.num_cus, self.num_cus), int)
            if level != 0:
                num_iter = self.config.multilevel_params["tabu_max_iter"]
            else:
                num_iter = 2*self.config.multilevel_params["tabu_max_iter"]
            for iter in range(num_iter):
                # variables'
                best_local_fitness = 100000000000
                # parse solution
                drone_path = []
                staff_path = []
                for i in range(self.num_drone):
                    drone_path.append(cur[i])
                for i in range(self.num_drone, len(cur)):
                    staff_path.append(cur[i])
                act = random.randrange(1,6)
                # act = 5
                #move 10
                if act == 1:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip):
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                # intra
                                for next_point_idx in range(len_trip):
                                    if point_idx != next_point_idx:
                                        copy_cur = deepcopy(cur)
                                        
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        if next_point_idx > point_idx: 
                                            if next_point_idx == point_idx + 1:
                                                continue
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx, tmp)
                                        else:
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, tmp)
                                        
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx].pop(point_idx)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                copy_cur[drone_idx].pop(trip_idx)
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = tmp
                                            #tabu_duration = iter + self.tabu_size
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # create new trip in drone 
                                copy_cur = deepcopy(cur)
                                new_trip = [tmp]
                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                copy_cur[drone_idx].append(new_trip)
                                tabu = tmp
                                #tabu_duration = iter + self.tabu_size
                                if fitness - best_fitness < (-1)*0.000001:
                                    local_best_solution = copy_cur
                                    best_fitness =  fitness
                                    best_local_fitness = fitness
                                    best_solution = copy_cur
                                    best_local_fitness_info = fitness_info
                                    best_tabu = tabu
                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                    
                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                    best_local_fitness = fitness
                                    local_best_solution = copy_cur
                                    best_local_fitness_info = fitness_info 
                                    best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                                if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                    copy_cur[drone_idx].pop(trip_idx)   
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = tmp
                                                #tabu_duration = iter + self.tabu_size
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp]
                                        copy_cur[next_drone_idx].append(new_trip)
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].insert(  + 1, tmp)
                                        if len(copy_cur[drone_idx][trip_idx]) == 0:
                                            copy_cur[drone_idx].pop(trip_idx)
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu

                                    if len_staff_trip == 0:    
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].append(tmp)
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                    #                        
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip):
                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            # intra
                            for next_point_idx in range(len_staff_trip):
                                if point_idx != next_point_idx:
                                    copy_cur = deepcopy(cur)
                                    
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                    if next_point_idx > point_idx: 
                                        if next_point_idx == point_idx + 1:
                                            continue
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx, tmp)
                                    else:
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, tmp)
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = tmp
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                           
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    for next_point_idx in range(len_next_staff):
                                        copy_cur = deepcopy(cur)
                                        
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, tmp)

                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                    if len_next_staff == 0:    
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].append(tmp)
                                        tabu = tmp
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                            # inter in drone
                            if cur[self.num_drone + staff_idx][point_idx] not in self.inp["C1"]:
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = tmp
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                    # create new trip in drone 
                                    copy_cur = deepcopy(cur)
                                    new_trip = [tmp]
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                    copy_cur[drone_idx].append(new_trip)
                                    tabu = tmp
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info 
                                        best_tabu = tabu
                # move 11
                if act == 2:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip):
                                # intra
                                if point_idx != len_trip - 1:
                                    for next_point_idx in range(point_idx + 1, len_trip):
                                        copy_cur = deepcopy(cur)
                                        tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                        copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][trip_idx][next_point_idx]
                                        copy_cur[drone_idx][trip_idx][next_point_idx] = tmp
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                        tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                            tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                
                                                tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                                copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[next_drone_idx][next_trip_idx][next_point_idx]
                                                copy_cur[next_drone_idx][next_trip_idx][next_point_idx] = tmp
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                                tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                                #tabu_duration = iter + self.tabu_size
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        if copy_cur[self.num_drone + staff_idx][next_point_idx] not in self.inp["C1"]:
                                            copy_cur = deepcopy(cur)
                                            tmp = copy_cur[drone_idx][trip_idx][point_idx]
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                            copy_cur[self.num_drone + staff_idx][next_point_idx] = tmp
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, copy_cur[drone_idx][trip_idx][point_idx]]
                                            tabu_extra =  [copy_cur[drone_idx][trip_idx][point_idx], tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                        #                        
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip):
                            # intra
                            if point_idx != len_staff_trip - 1:
                                for next_point_idx in range(point_idx + 1, len_staff_trip):
                                    copy_cur = deepcopy(cur)
                                    tmp = copy_cur[self.num_drone + staff_idx][point_idx]
                                    copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                    copy_cur[self.num_drone + staff_idx][next_point_idx] = tmp
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, copy_cur[self.num_drone + staff_idx][point_idx]]
                                    tabu_extra =  [copy_cur[self.num_drone + staff_idx][point_idx], tmp]
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    for next_point_idx in range(len_next_staff):
                                        copy_cur = deepcopy(cur)
                                        tmp = copy_cur[self.num_drone + staff_idx][point_idx]
                                        copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + next_staff_idx][next_point_idx]
                                        copy_cur[self.num_drone + next_staff_idx][next_point_idx] = tmp

                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, copy_cur[self.num_drone + staff_idx][point_idx]]
                                        tabu_extra =  [copy_cur[self.num_drone + staff_idx][point_idx], tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu

                            # inter in drone
                            if cur[self.num_drone + staff_idx][point_idx] not in self.inp["C1"]:
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            tmp = copy_cur[self.num_drone + staff_idx][point_idx]
                                            copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, copy_cur[self.num_drone + staff_idx][point_idx]]
                                            tabu_extra =  [copy_cur[self.num_drone + staff_idx][point_idx], tmp]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                # move 20
                if act == 3:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip - 1):
                                
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                next_tmp = cur[drone_idx][trip_idx][point_idx + 1]
                                # intra
                                for next_point_idx in range(len_trip):
                                    if next_point_idx - point_idx not in [-1, 0, 1]:
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        if next_point_idx > point_idx: 
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx - 1 , next_tmp)
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx - 1, tmp)
                                        else:
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, next_tmp)
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, tmp)
                                        
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        # print("---")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx].pop(point_idx)
                                            copy_cur[drone_idx][trip_idx].pop(point_idx)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                copy_cur[drone_idx].pop(trip_idx)
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("+++")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # create new trip in drone 
                                copy_cur = deepcopy(cur)
                                new_trip = [tmp, next_tmp]
                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                copy_cur[drone_idx].append(new_trip)
                                tabu = [tmp, next_tmp]
                                #tabu_duration = iter + self.tabu_size
                                if fitness - best_fitness < (-1)*0.000001:
                                    local_best_solution = copy_cur
                                    best_fitness =  fitness
                                    best_local_fitness = fitness
                                    best_solution = copy_cur
                                    best_local_fitness_info = fitness_info
                                    best_tabu = tabu
                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                    
                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                    best_local_fitness = fitness
                                    local_best_solution = copy_cur
                                    best_local_fitness_info = fitness_info 
                                    best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                                copy_cur[drone_idx][trip_idx].pop(point_idx)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                                if len(copy_cur[drone_idx][trip_idx]) == 0:
                                                    copy_cur[drone_idx].pop(trip_idx)   
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp, next_tmp]
                                                #tabu_duration = iter + self.tabu_size
                                                # print("****")
                                                # print(fitness)
                                                # print(copy_cur)
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp, next_tmp]
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[next_drone_idx].append(new_trip)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                                        
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp, next_tmp]
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[next_drone_idx].append(new_trip)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu

                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, tmp)
                                        if len(copy_cur[drone_idx][trip_idx]) == 0:
                                            copy_cur[drone_idx].pop(trip_idx)
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        # print("^^^")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        
                                    if len_staff_trip == 0:
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        # new_trip = [tmp, next_tmp]
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[drone_idx][trip_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].append(tmp)
                                        copy_cur[self.num_drone + staff_idx].append(next_tmp)
                                        if len(copy_cur[drone_idx][trip_idx]) == 0:
                                            copy_cur[drone_idx].pop(trip_idx)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                    #                        
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip - 1):
                            
                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            next_tmp = cur[self.num_drone + staff_idx][point_idx + 1]
                            # intra
                            for next_point_idx in range(len_staff_trip):
                                if next_point_idx - point_idx not in [-1, 0, 1]:
                                    copy_cur = deepcopy(cur)
                                    
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                    if next_point_idx > point_idx: 
                                        
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx - 1, next_tmp)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx - 1, tmp)
                                    else:
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, tmp)
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, next_tmp]
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    for next_point_idx in range(len_next_staff):
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, next_tmp)
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, tmp)

                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness < (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                    if len_next_staff == 0:
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        # new_trip = [tmp, next_tmp]
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[self.num_drone + next_staff_idx].append(tmp)
                                        copy_cur[self.num_drone + next_staff_idx].append(next_tmp)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu
                            # inter in drone
                            if tmp not in self.inp["C1"] and next_tmp not in self.inp["C1"] :
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, tmp)
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu 
                                        # create new trip in drone 
                                        copy_cur = deepcopy(cur)
                                        new_trip = [tmp, next_tmp]
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx)
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx) 
                                        copy_cur[drone_idx].append(new_trip)
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info 
                                            best_tabu = tabu               
                #move 21
                if act == 4:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip - 1):
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                next_tmp = cur[drone_idx][trip_idx][point_idx + 1]
                                # intra
                                for next_point_idx in range(len_trip):
                                    if next_point_idx - point_idx not in [0, 1]:
                                        copy_cur = deepcopy(cur)
                                        copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][trip_idx][next_point_idx]
                                        copy_cur[drone_idx][trip_idx][next_point_idx] = tmp
                                        copy_cur[drone_idx][trip_idx].pop(point_idx + 1)
                                        if next_point_idx > point_idx: 
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx , next_tmp)
                                        else:
                                            copy_cur[drone_idx][trip_idx].insert(next_point_idx + 1, next_tmp)
                                            
                                        
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        # print("---")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            copy_cur[drone_idx][trip_idx].pop(point_idx  + 1)
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("+++")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip):
                                                copy_cur = deepcopy(cur)
                                                
                                                
                                                copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[next_drone_idx][next_trip_idx][next_point_idx]
                                                copy_cur[next_drone_idx][next_trip_idx][next_point_idx] = tmp
                                                copy_cur[drone_idx][trip_idx].pop(point_idx + 1)
                                                copy_cur[next_drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                                  
                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp, next_tmp]
                                                #tabu_duration = iter + self.tabu_size
                                                # print("****")
                                                # print(fitness)
                                                # print(copy_cur)
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip):
                                        if copy_cur[self.num_drone + staff_idx][next_point_idx] not in self.inp["C1"]: 
                                            copy_cur = deepcopy(cur)
                                            
                                            copy_cur[drone_idx][trip_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                            copy_cur[self.num_drone + staff_idx][next_point_idx] = tmp
                                            copy_cur[drone_idx][trip_idx].pop(point_idx + 1)
                                            copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                            
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("^^^")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                    #                      
                    
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip - 1):

                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            next_tmp = cur[self.num_drone + staff_idx][point_idx + 1]
                            # intra
                            for next_point_idx in range(len_staff_trip):
                                if next_point_idx - point_idx not in [ 0, 1]:
                                    copy_cur = deepcopy(cur)
                                    
                                    copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + staff_idx][next_point_idx]
                                    copy_cur[self.num_drone + staff_idx][next_point_idx]  = tmp
                                    copy_cur[self.num_drone + staff_idx].pop(point_idx + 1)
                                    if next_point_idx > point_idx: 
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx , next_tmp)
                                    else:
                                        copy_cur[self.num_drone + staff_idx].insert(next_point_idx + 1, next_tmp)
                                        
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, next_tmp]
                                    #tabu_duration = iter + self.tabu_size
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    
                                    for next_point_idx in range(len_next_staff):
                                        
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[self.num_drone + next_staff_idx][next_point_idx]
                                        copy_cur[self.num_drone + next_staff_idx][next_point_idx]  = tmp
                                        copy_cur[self.num_drone + staff_idx].pop(point_idx + 1)
                                        copy_cur[self.num_drone + next_staff_idx].insert(next_point_idx + 1, next_tmp)
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness < (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                            # inter in drone
                            if tmp not in self.inp["C1"] and next_tmp not in self.inp["C1"] :
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[self.num_drone + staff_idx][point_idx] = copy_cur[drone_idx][next_trip_idx][next_point_idx]
                                            copy_cur[drone_idx][next_trip_idx][next_point_idx] = tmp
                                            copy_cur[self.num_drone + staff_idx].pop(point_idx + 1) 
                                            copy_cur[drone_idx][next_trip_idx].insert(next_point_idx + 1, next_tmp)
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, next_tmp]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu     
                # move 2opt
                if act == 5:
                    for drone_idx in range(self.num_drone):
                        drone = drone_path[drone_idx]
                        num_trip_in_drone = len(drone)
                        for trip_idx in range(num_trip_in_drone):
                            trip = drone[trip_idx]
                            len_trip = len(trip)
                            for point_idx in range(len_trip - 1):
                                tmp = cur[drone_idx][trip_idx][point_idx]
                                next_tmp = cur[drone_idx][trip_idx][point_idx + 1]
                                # intra
                                if point_idx < len_trip - 3:
                                    for next_point_idx in range(point_idx + 2, len_trip - 1):
                                        copy_cur = deepcopy(cur)

                                        copy_cur[drone_idx][trip_idx][point_idx + 1:next_point_idx + 1] = reversed(copy_cur[drone_idx][trip_idx][point_idx + 1:next_point_idx + 1] )
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, next_tmp]
                                        # print("---")
                                        # print(fitness)
                                        # print(copy_cur)
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                        

                                        
                                # inter within same drone
                                for next_trip_idx in range(num_trip_in_drone):
                                    if next_trip_idx != trip_idx:
                                        next_trip = drone[next_trip_idx]
                                        next_trip_len = len(next_trip)
                                        for next_point_idx in range(next_trip_len - 1):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx][point_idx + 1:], copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:] = copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:], copy_cur[drone_idx][trip_idx][point_idx + 1:]
                                            
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, cur[drone_idx][next_trip_idx][next_point_idx]]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("+++")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info 
                                                best_tabu = tabu
                                # inter in other drone
                                for next_drone_idx in range(self.num_drone):
                                    if next_drone_idx != drone_idx:
                                        next_drone = drone_path[next_drone_idx]
                                        num_trip_in_next_drone = len(next_drone)
                                        for next_trip_idx in range(num_trip_in_next_drone):
                                            next_trip = next_drone[next_trip_idx]
                                            len_next_trip = len(next_trip)
                                            for next_point_idx in range(len_next_trip - 1):
                                                copy_cur = deepcopy(cur)
                                                copy_cur[drone_idx][trip_idx][point_idx + 1:], copy_cur[next_drone_idx][next_trip_idx][next_point_idx + 1:] = copy_cur[next_drone_idx][next_trip_idx][next_point_idx + 1:], copy_cur[drone_idx][trip_idx][point_idx + 1:]                                                
                                                #caculate fitness
                                                fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                                fitness = fitness_info[0]
                                                tabu = [tmp,  cur[next_drone_idx][next_trip_idx][next_point_idx]]
                                                #tabu_duration = iter + self.tabu_size
                                                # print("****")
                                                # print(fitness)
                                                # print(copy_cur)
                                                if fitness - best_fitness < (-1)*0.000001:
                                                    local_best_solution = copy_cur
                                                    best_fitness =  fitness
                                                    best_local_fitness = fitness
                                                    best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                                    score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                    
                                                elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                    best_local_fitness = fitness
                                                    local_best_solution = copy_cur
                                                    best_local_fitness_info = fitness_info
                                                    best_tabu = tabu
                                
                                # inter in  staff
                                for staff_idx in range(self.num_staff):
                                    staff = staff_path[staff_idx]
                                    len_staff_trip = len(staff)
                                    for next_point_idx in range(len_staff_trip - 1):
                                        conclude_c1 = False
                                        for tmp_idx in range(next_point_idx + 1, len_staff_trip):
                                            if cur[self.num_drone + staff_idx][tmp_idx] in self.inp["C1"]: 
                                                conclude_c1 = True
                                        if not conclude_c1:
                                            copy_cur = deepcopy(cur)
                                            copy_cur[drone_idx][trip_idx][point_idx + 1:], copy_cur[self.num_drone + staff_idx][next_point_idx + 1:] = copy_cur[self.num_drone + staff_idx][next_point_idx + 1:], copy_cur[drone_idx][trip_idx][point_idx + 1:]
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, cur[self.num_drone + staff_idx][next_point_idx]]
                                            #tabu_duration = iter + self.tabu_size
                                            # print("^^^")
                                            # print(fitness)
                                            # print(copy_cur)
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                    #                      
                    
                    for staff_idx in range(self.num_staff):
                        staff = staff_path[staff_idx]
                        len_staff_trip = len(staff)
                        
                        for point_idx in range(len_staff_trip - 1):

                            tmp = cur[self.num_drone + staff_idx][point_idx]
                            next_tmp = cur[self.num_drone + staff_idx][point_idx + 1]
                            # intra
                            if point_idx < len_staff_trip - 3:
                                for next_point_idx in range(len_staff_trip - 1):
                                    copy_cur = deepcopy(cur)
                                    copy_cur[self.num_drone + staff_idx][point_idx + 1:next_point_idx + 1]  = reversed(copy_cur[self.num_drone + staff_idx][point_idx + 1:next_point_idx + 1] )
                                    
                                    
                                    #caculate fitness
                                    fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                    fitness = fitness_info[0]
                                    tabu = [tmp, next_tmp]
                                    if fitness - best_fitness < (-1)*0.000001:
                                        local_best_solution = copy_cur
                                        best_fitness =  fitness
                                        best_local_fitness = fitness
                                        best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                                        score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                        
                                    elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                        best_local_fitness = fitness
                                        local_best_solution = copy_cur
                                        best_local_fitness_info = fitness_info
                                        best_tabu = tabu
                            
                            # inter in other 
                            for next_staff_idx in range(self.num_staff):
                                if staff_idx != next_staff_idx:
                                    next_staff = staff_path[next_staff_idx]
                                    len_next_staff = len(next_staff)
                                    
                                    for next_point_idx in range(len_next_staff - 1):
                                        
                                        copy_cur = deepcopy(cur)
                                        copy_cur[self.num_drone + staff_idx][point_idx + 1:], copy_cur[self.num_drone + next_staff_idx][next_point_idx + 1:] = copy_cur[self.num_drone + next_staff_idx][next_point_idx + 1:], copy_cur[self.num_drone + staff_idx][point_idx + 1:]
                                        #caculate fitness
                                        fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                        fitness = fitness_info[0]
                                        tabu = [tmp, cur[self.num_drone + next_staff_idx][next_point_idx]]
                                        # #tabu_duration = iter + self.tabu_size
                                        if fitness - best_fitness < (-1)*0.000001:
                                            local_best_solution = copy_cur
                                            best_fitness =  fitness
                                            best_local_fitness = fitness
                                            best_solution = copy_cur                                                
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                                            score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                            
                                        elif fitness - best_local_fitness < (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                            best_local_fitness = fitness
                                            local_best_solution = copy_cur
                                            best_local_fitness_info = fitness_info
                                            best_tabu = tabu
                            # inter in drone
                            conclude_c1 = False
                            for tmp_idx in range(point_idx + 1, len_staff_trip):
                                if cur[self.num_drone + staff_idx][tmp_idx] in self.inp["C1"]:
                                    conclude_c1 = True
                            if not conclude_c1 :
                                for drone_idx in range(self.num_drone):
                                    drone = drone_path[drone_idx]
                                    len_drone = len(drone)
                                    for next_trip_idx in range(len_drone):
                                        next_trip = drone[next_trip_idx]
                                        len_next_trip = len(next_trip)
                                        for next_point_idx in range(len_next_trip - 1):
                                            copy_cur = deepcopy(cur)
                                            copy_cur[self.num_drone + staff_idx][point_idx + 1:], copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:] = copy_cur[drone_idx][next_trip_idx][next_point_idx + 1:], copy_cur[self.num_drone + staff_idx][point_idx + 1:]
                                        
                                            #caculate fitness
                                            fitness_info = self.mt_utils.get_score(copy_cur, self.penalty_params)
                                            fitness = fitness_info[0]
                                            tabu = [tmp, cur[drone_idx][next_trip_idx][next_point_idx]]
                                            if fitness - best_fitness < (-1)*0.000001:
                                                local_best_solution = copy_cur
                                                best_fitness =  fitness
                                                best_local_fitness = fitness
                                                best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu
                                                score_edge = self.mt_utils.update_score_edge(score_edge, best_solution[self.num_drone:], best_solution[:self.num_drone])
                                                
                                            elif fitness - best_local_fitness< (-1)*0.000001 and tabu not in tabu_list[act - 1]:
                                                best_local_fitness = fitness
                                                local_best_solution = copy_cur
                                                best_local_fitness_info = fitness_info
                                                best_tabu = tabu 
                        
                if cur != local_best_solution:
                    # print(1)
                    cur = local_best_solution
                    # tabu duration
                    tabu_list[act - 1].append(best_tabu)
                    tabu_duration_list[act - 1].append(iter + self.tabu_size)
                    self.update_penalty_param(best_local_fitness_info[1], best_local_fitness_info[2])
                # print(best_local_fitness)
                print(act)
                print(cur)
                print(best_fitness)
                # print(tabu_list)
                # print(tabu_duration_list)
                # update params
                
                # remove tabu 
                idx = 0
                idx_1 = 0
                while idx < len(tabu_duration_list) - 1:
                    while idx_1 < len(tabu_duration_list[idx]) - 1:
                        if iter >= tabu_duration_list[idx][idx_1]:
                            tabu_list[idx].pop(idx_1)
                            tabu_duration_list[idx].pop(idx_1)
                        else:
                            idx_1 += 1
                    idx += 1
                if iter > self.max_steps:
                    break      
            if best_fitness - self.best_fitness < (-1)*0.000001:
                self.best_fitness = best_fitness
            result_by_level[level + self.num_level] = {'best_sol': str(best_solution), 'best_fitness': str(best_fitness), 'score_edge': [], 'nested_point': str(nested_point_dict[level]),
                                       'ori_best_sol': str(self.get_ori_solution(best_solution[self.config.params["num_drone"]:], best_solution[:self.config.params["num_drone"]], nested_point_dict[level]))}
            if level != 0:
                level_nested = level_nested_point[level]
                cur = self.seperate_point(best_solution[self.config.params["num_drone"]:],best_solution[:self.config.params["num_drone"]], level_nested)
                nested_point = nested_point_dict[level - 1 ]
                nested_tau = nested_tau_dict[level - 1]
                nested_tau_a = nested_tau_a_dict[level - 1]
                new_num_cus = level_num_cus[level - 1]
                new_c1 = level_c1[level - 1]
                new_tau = level_tau[level - 1]
                new_tau_a = level_tau_a[level - 1]
                # print(nested_point)
                # print(new_tau)
                # update config and inp
                new_config = self.config
                new_inp = self.inp
                new_config["num_cus"] = new_num_cus
                new_inp["num_cus"] = new_num_cus
                new_inp["C1"] = new_c1
                new_inp["tau"] = new_tau
                new_inp["tau_a"] = new_tau_a
                new_inp["nested_tau"] = nested_tau
                new_inp["nested_tau_a"] = nested_tau_a

                self._update_config(new_config, new_inp)
                # self.tabu.update(new_config, new_inp)
                self.mt_utils= MTUtils(new_config, new_inp)
        
        return result_by_level 

    def _clear(self):
        """
        Resets the variables that are altered on a per-run basis of the algorithm

        :return:
        """
        self.score_dict = {}

    def _score(self, state, nested_tau, nested_tau_a, return_all=False):
        """
        Returns objective function value of a state

        :param state:
        :return:
        """
        if return_all:
            return self.mt_utils.get_score(state, nested_tau, nested_tau_a, self.penalty_params)
        return self.mt_utils.get_score(state, nested_tau, nested_tau_a, self.penalty_params)[0]
    
    def seperate_point(self, staff_list_path, drone_list_path, level_nested):
        solution = []
        
        for drone in drone_list_path:
            tmp_drone = []
            for trip in drone:
                tmp_trip = []
                for i in trip:
                    for point in level_nested[i]:
                        tmp_trip.append(point)  
                tmp_drone.append(tmp_trip)
            solution.append(tmp_drone)
        for trip in staff_list_path:
            tmp_trip = []
            for i in trip:
                for point in level_nested[i]:
                    tmp_trip.append(point)
            solution.append(tmp_trip)
        return solution
    
    def ori_score(self, staff_list_path, drone_list_path, nested_point, ori_tau, ori_tau_a, num_cus, nested_tau, nested_tau_a):
        solution = []
        staff_path = []
        drone_path = []
        for drone in drone_list_path:
            tmp_drone = []
            for trip in drone:
                tmp_trip = []
                for i in trip:
                    for point in nested_point[i]:
                        tmp_trip.append(point)  
                tmp_drone.append(tmp_trip)
            drone_path.append(tmp_drone)
        for trip in staff_list_path:
            tmp_trip = []
            for i in trip:
                for point in nested_point[i]:
                    tmp_trip.append(point)
            staff_path.append(tmp_trip)
        
        score = cal(staff_path, drone_path, ori_tau, ori_tau_a, num_cus, self.config, nested_tau, nested_tau_a)
        return score[0]
    
    def get_ori_solution(self,  staff_list_path, drone_list_path, nested_point):
        solution = []
        
        for drone in drone_list_path:
            tmp_drone = []
            for trip in drone:
                tmp_trip = []
                for i in trip:
                    for point in nested_point[i]:
                        tmp_trip.append(point)  
                tmp_drone.append(tmp_trip)
            solution.append(tmp_drone)
        for trip in staff_list_path:
            tmp_trip = []
            for i in trip:
                for point in nested_point[i]:
                    tmp_trip.append(point)
            solution.append(tmp_trip)
        return solution
    
    def update_penalty_param(self, dz, cz):
        alpha1 = self.penalty_params.get("alpha1", 0)
        alpha2 = self.penalty_params.get("alpha2", 0)
        beta = self.penalty_params.get("beta", 0)

        if dz > 0:
            self.penalty_params["alpha1"] = alpha1 * (1 + beta)
        else:
            self.penalty_params["alpha1"] = alpha1 / (1 + beta)

        if cz > 0:
            self.penalty_params["alpha2"] = alpha2 * (1 + beta)
        else:
            self.penalty_params["alpha2"] = alpha2 / (1 + beta)
    
