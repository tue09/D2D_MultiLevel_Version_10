import copy
import random
import numpy as np

class MTUtils:

    def __init__(self, config, inp) -> None:
        self.config = config
        self.inp = inp
        self.num_staff = self.config.params["num_staff"]
        self.num_drone = self.config.params["num_drone"]
        self.cache = {"index": {}, "score": {}}
        try:
            self.nested_tau = inp["nested_tau"]
            self.nested_tau_a = inp["nested_tau_a"]
        except:
            nested = {}
            for i in range(1, self.inp["num_cus"] + 1):
                nested[i] = 0
            self.nested_tau = nested
            self.nested_tau_a = nested

    def _update_config(self, config, inp):
        self.inp = inp 
        self.config = config 
        
    def mt_cal(self,staff_path_list, drone_path_list, tau, tau_a, num_cus, config, nested_tau, nested_tau_a):
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
    
    def update_score_edge(self, score_edge, staff_path_list, drone_path_list):
        for i, staff in enumerate(staff_path_list):
            if len(staff) <= 1:
                continue
            for j in range(len(staff) - 1):
                found_point = staff[j]
                next_point = staff[j + 1]
                score_edge[found_point - 1][next_point - 1] += 1
        
        for i, drone in enumerate(drone_path_list):
            for j, trip in enumerate(drone):
                if len(trip) <= 1:
                    continue
                for k in range(len(trip) - 1):
                    found_point = trip[k]
                    next_point = trip[k + 1]
                    score_edge[found_point - 1][next_point - 1] += 1
        return score_edge

    def get_score(self, solution, penalty=None):
        """

        :param solution:
        :param penalty:
        :return:
        """
        if penalty is None:
            penalty = {}

        # print(solution)
        if str(solution) not in self.cache["score"]:
            self.cache["score"][str(solution)] = self.mt_cal(solution[self.config.params["num_drone"]:],
                                                     solution[:self.config.params["num_drone"]], self.inp['tau'],
                                                     self.inp['tau_a'], self.inp['num_cus'], self.config, self.nested_tau, self.nested_tau_a)
        c = self.cache["score"][str(solution)][0]
        cz = self.cache["score"][str(solution)][1]
        dz = self.cache["score"][str(solution)][2]

        alpha1 = penalty.get("alpha1", 0) if penalty is not None else 0
        alpha2 = penalty.get("alpha2", 0) if penalty is not None else 0
        
        return c + alpha1 * dz + alpha2 * cz, dz, cz
        