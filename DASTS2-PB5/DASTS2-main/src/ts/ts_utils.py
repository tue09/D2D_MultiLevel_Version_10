import copy
import random

from src.utils import cal


class TSUtils:
    def __init__(self, config, inp):
        """

        :param config:
        :param inp:
        """
        self.config = config
        self.inp = inp
        try:
            self.nested_tau = inp["nested_tau"]
            self.nested_tau_a = inp["nested_tau_a"]
        except:
            nested = {}
            for i in range(1, self.inp["num_cus"] + 1):
                nested[i] = 0
            self.nested_tau = nested
            self.nested_tau_a = nested
        self.num_cus = self.inp["num_cus"]
        self.num_staff = self.config.params["num_staff"]
        self.num_drone = self.config.params["num_drone"]
        self.action = {"move10": self.move10, "move11": self.move11,
                       "move20": self.move20, "move21": self.move21,
                       "move2opt": self.move2opt, "move01": self.move01, "move02": self.move02}

        self.cache = {"index": {}, "score": {}}

    def update_config(self, config, inp):
        self.config = config
        self.inp = inp
        self.num_cus = self.inp["num_cus"]
        
    def get_score(self, solution, penalty=None):
        """

        :param solution:
        :param penalty:
        :return:
        """
        if penalty is None:
            penalty = {}
        if str(solution) not in self.cache["score"]:
            self.cache["score"][str(solution)] = cal(solution[self.config.params["num_drone"]:],
                                                     solution[:self.config.params["num_drone"]], self.inp['tau'],
                                                     self.inp['tau_a'], self.inp['num_cus'], self.config, self.nested_tau, self.nested_tau_a)
        c = self.cache["score"][str(solution)][0]
        cz = self.cache["score"][str(solution)][1]
        dz = self.cache["score"][str(solution)][2]

        alpha1 = penalty.get("alpha1", 0) if penalty is not None else 0
        alpha2 = penalty.get("alpha2", 0) if penalty is not None else 0

        return c + alpha1 * dz + alpha2 * cz, dz, cz

    def get_score_some_trip(self, solution, trip, penalty=None):
        """

        :param trip:
        :param solution:
        :param penalty:
        :return:
        """

        if penalty is None:
            penalty = {}
        drone_trip_cal = [i for i in trip if i < self.num_drone]
        staff_trip_cal = [i - self.num_drone for i in trip if i >= self.num_drone]

        c, cz, dz = cal(solution[self.config.params["num_drone"]:],
                        solution[:self.config.params["num_drone"]], self.inp['tau'],
                        self.inp['tau_a'], self.inp['num_cus'], self.config, drone_trip_cal, staff_trip_cal)

        alpha1 = penalty.get("alpha1", 0) if penalty is not None else 0
        alpha2 = penalty.get("alpha2", 0) if penalty is not None else 0

        return c + alpha1 * dz + alpha2 * cz, dz, cz

    def get_all_neighbors(self, solution, act):
        """

        :param solution:
        :param act:
        :return:
        """
        # print(solution)
        return self.action[act](solution)

    def find_index(self, solution, val):
        """

        :param solution:
        :param val:
        :return:
        """

        if str(solution) not in self.cache["index"]:
            self.cache['index'][str(solution)] = {}
            for i in range(self.num_drone):
                drone_trip = solution[i]
                for j, trip in enumerate(drone_trip):
                    for k, node in enumerate(trip):
                        self.cache['index'][str(solution)][node] = i, j, k

            for i in range(self.num_drone, self.num_drone + self.num_staff):
                staff_trip = solution[i]
                for j, node in enumerate(staff_trip):
                    self.cache['index'][str(solution)][node] = i, j

        return self.cache['index'][str(solution)].get(val, None)

    def get_predecessor(self, solution, val):
        index = self.find_index(solution, val)
        if len(index) == 2:
            return solution[index[0]][index[1] - 1] if index[1] > 0 else 0
        else:
            return solution[index[0]][index[1]][index[2] - 1] if index[2] > 0 else 0

    def get_successor(self, solution, val):
        index = self.find_index(solution, val)
        if len(index) == 2:
            return solution[index[0]][index[1] + 1] if index[1] < len(solution[index[0]]) - 1 else self.num_cus + 1
        else:
            return solution[index[0]][index[1]][index[2] + 1] if index[2] < len(
                solution[index[0]][index[1]]) - 1 else self.num_cus + 1

    def delete_by_ind(self, solution, index):
        """

        :param solution:
        :param index:
        :return:
        # """
        # print(index)
        if len(index) == 2:
            if index[0] >= self.num_drone:
                solution[index[0]].pop(index[1])

        if len(index) == 3:
            if index[0] < self.num_drone:
                solution[index[0]][index[1]].pop(index[2])

        self.refactor(solution)

    def delete_by_val(self, solution, val):
        """
        :param solution:
        :param val:
        :return:
        """
        if val <= self.num_cus:
            self.delete_by_ind(solution, self.find_index(solution, val))

    def delete_trip(self, solution, ind):
        r = None
        if isinstance(ind, int) and ind < self.num_drone + self.num_staff:
            r = solution[ind]
            solution[ind] = []
        elif ind[0] < self.num_drone and ind[1] < len(solution[ind[0]]):
            r = solution[ind[0]][ind[1]]
            solution[ind[0]].pop(ind[1])
        return r

    def refactor(self, solution):
        for i in range(self.num_drone):
            solution[i] = list(filter(lambda a: a != [], solution[i]))

    def insert_after(self, solution, val1, val2):
        """

        :param solution:
        :param val1:
        :param val2:
        :return:
        """
        index = self.find_index(solution, val2)
        if len(index) == 2:
            if index[0] >= self.num_drone:
                solution[index[0]].insert(index[1] + 1, val1)

        else:
            if index[0] < self.num_drone:
                solution[index[0]][index[1]].insert(index[2] + 1, val1)

    def insert_before(self, solution, val1, val2):
        """

        :param solution:
        :param val1:
        :param val2:
        :return:
        """
        index = self.find_index(solution, val2)

        if len(index) == 2:
            if index[0] >= self.num_drone:
                solution[index[0]].insert(index[1], val1)

        else:
            if index[0] < self.num_drone:
                solution[index[0]][index[1]].insert(index[2], val1)

    def insert_by_index(self, solution, val, index):
        """

        :param solution:
        :param val:
        :param index:
        :return:
        """

        if len(index) == 2:
            if index[0] >= self.num_drone:
                solution[index[0]].insert(index[1], val)

        else:
            if index[0] < self.num_drone:
                if len(solution[index[0]]) == index[1]:
                    solution[index[0]].append([val])
                else:
                    solution[index[0]][index[1]].insert(index[2], val)

    def is_in_drone_route(self, solution, val):
        """

        :param solution:
        :param val:
        :return:
        """
        index = self.find_index(solution, val)
        if index[0] >= self.num_drone:
            return False
        return True

    def is_adj(self, solution, val1, val2):
        """

        :param solution:
        :param val1:
        :param val2:
        :return:
        """
        ind1 = self.find_index(solution, val1)
        ind2 = self.find_index(solution, val2)

        if len(ind1) != len(ind2):
            return False

        if len(ind1) == 2:
            return ind1[0] == ind2[0] and ind2[1] == ind1[1] + 1

        else:
            return ind1[0] == ind2[0] and ind1[1] == ind2[1] and ind2[2] == ind1[2] + 1

    def dis(self, solution, x1, x2):
        """

        :param solution:
        :param x1:
        :param x2:
        :return:
        """
        ind1 = self.find_index(solution, x1)
        ind2 = self.find_index(solution, x2)

        if len(ind1) != len(ind2):
            return float("inf")

        if len(ind1) == 2:
            if ind1[0] == ind2[0]:
                return ind2[1] - ind1[1]

        if len(ind1) == 3:
            if ind1[0] == ind2[0] and ind1[1] == ind2[1]:
                return ind2[2] - ind1[2]

        return float("inf")

    def swap(self, solution, x, y):
        """

        :param solution:
        :param x:
        :param y:
        :return:
        """
        x_ind = self.find_index(solution, x)
        y_ind = self.find_index(solution, y)

        if len(x_ind) == 2:
            solution[x_ind[0]][x_ind[1]] = y
        else:
            solution[x_ind[0]][x_ind[1]][x_ind[2]] = y

        if len(y_ind) == 2:
            solution[y_ind[0]][y_ind[1]] = x
        else:
            solution[y_ind[0]][y_ind[1]][y_ind[2]] = x

    def is_in_same_trip(self, solution, x, y):
        """

        :param solution:
        :param x:
        :param y:
        :return:
        """
        x_ind = self.find_index(solution, x)
        y_ind = self.find_index(solution, y)
        if len(x_ind) != len(y_ind):
            return False
        if len(x_ind) == 2:
            return x_ind[0] == y_ind[0]
        else:
            return x_ind[0] == y_ind[0] and x_ind[1] == y_ind[1]

    @staticmethod
    def eq(val1, val2):
        return val1 == val2

    @staticmethod
    def gt(val1, val2):
        return val1 > val2

    @staticmethod
    def lt(val1, val2):
        return val1 < val2

    @staticmethod
    def ge(val1, val2):
        return val1 >= val2

    @staticmethod
    def le(val1, val2):
        return val1 <= val2

    # ACTION

    def move10(self, solution, route_type="all"):
        """

        :param route_type:
        :param solution:
        :return:
        """
        result = {}

        for x in range(1, self.num_cus + 1):

            for y in range(1, self.num_cus + 1):
                s = self.relocate(solution, x, y, route_type)
                if s is not None:
                    result[x, y] = s

        return result

    def move11(self, solution, route_type="all"):
        """

        :param route_type:
        :param solution:
        :return:
        """
        result = {}

        for x in range(1, self.num_cus + 1):
            for y in range(1, self.num_cus + 1):
                s = self.exchange(solution, x, y, route_type)
                if s is not None:
                    result[x, y] = s
        return result

    def move20(self, solution, route_type="all"):
        """

        :param route_type:
        :param solution:
        :return:
        """
        result = {}

        for x1 in range(1, self.num_cus + 1):
            for x2 in range(1, self.num_cus + 1):
                for y in range(1, self.num_cus + 1):
                    s = self.or_opt(solution, x1, x2, y, compare_operator=self.eq, route_type=route_type)
                    if s is not None:
                        result[x1, x2, y] = s

        return result

    def move21(self, solution):
        """

        :param solution:
        :return:
        """
        result = {}

        C1 = self.inp["C1"]

        for x1 in range(1, self.num_cus + 1):
            for x2 in range(1, self.num_cus + 1):
                if not self.is_adj(solution, x1, x2):
                    continue
                for y in range(1, self.num_cus + 1):
                    if x1 == y or x2 == y:
                        continue

                    if x1 in C1 and self.is_in_drone_route(solution, y):
                        continue

                    if y in C1 and self.is_in_drone_route(solution, x1):
                        continue

                    s = copy.deepcopy(solution)

                    self.swap(s, x1, y)
                    self.delete_by_val(s, x2)
                    self.insert_after(s, x2, x1)

                    result[x1, x2, y] = s
        return result

    def move2opt(self, solution, route_type="all"):
        """

        :param route_type:
        :param solution:
        :return:
        """
        result = {}

        for x1 in range(1, self.num_cus + 1):
            for x2 in range(1, self.num_cus + 1):
                for y1 in range(1, self.num_cus + 1):
                    for y2 in range(1, self.num_cus + 1):
                        s = self.two_opt(solution, x1, x2, y1, y2, route_type)
                        if s is not None:
                            result[x1, x2, y1, y2] = s
        return result

    def move01(self, solution):
        """

        :param solution:
        :return:
        """

        result = {}

        C1 = self.inp["C1"]
 
        for x in range(1, self.num_cus + 1):

            x_ind = self.find_index(solution, x)

            for i in range(self.num_drone + self.num_staff):
                if i < self.num_drone and x in C1:
                    continue

                for j in range(len(solution[i]) + 1):
                    if self.num_drone <= i == x_ind[0] and j == x_ind[1]:
                        continue
                    s = copy.deepcopy(solution)
                    self.delete_by_val(s, x)
                    self.refactor(s)
                    if i < self.num_drone:
                        s[i].insert(j, [x])
                    else:
                        if len(s[i]) == 0:
                            s[i].insert(j, x)
                        else:
                            continue

                    if s != solution:
                        result[x, i, j] = s

        return result

    def move02(self, solution):
        """

        :param solution:
        :return:
        """

        result = {}
        C1 = self.inp["C1"]

        tmp = []
        for i in range(self.num_drone + self.num_staff):
            if i < self.num_drone:
                for j in range(len(solution[i])):
                    tmp.append((i, j))
            else:
                if len(solution[i]) > 0:
                    tmp.append(i)

        for i in tmp:
            for j in tmp:
                if i == j:
                    continue
                s = copy.deepcopy(solution)
                if isinstance(j, int):
                    t2 = solution[j]
                else:
                    t2 = solution[j[0]][j[1]]

                if isinstance(i, tuple):
                    if not all(cus not in C1 for cus in t2):
                        continue
                    s[i[0]][i[1]].extend(t2)
                else:
                    s[i].extend(t2)
                self.delete_trip(s, j)
                if s != solution:
                    result[i, j] = s
        return result

    # POST OPTIMIZATION
    def relocate(self, solution, x, y, route_type="all"):
        C1 = self.inp["C1"]

        if x == y:
            return None

        if x in C1 and self.is_in_drone_route(solution, y):
            return None

        if not self.is_in_same_trip(solution, x, y) and route_type == "intra":
            return None

        if self.is_in_same_trip(solution, x, y) and route_type == "inter":
            return None
        s = copy.deepcopy(solution)
        self.delete_by_val(s, x)
        self.insert_after(s, x, y)
        self.refactor(s)

        if s == solution:
            return None

        return s

    def exchange(self, solution, x, y, route_type="all"):
        C1 = self.inp["C1"]

        if x == y:
            return None

        if x in C1 and self.is_in_drone_route(solution, y):
            return None

        if y in C1 and self.is_in_drone_route(solution, x):
            return None

        if not self.is_in_same_trip(solution, x, y) and route_type == "intra":
            return None

        if self.is_in_same_trip(solution, x, y) and route_type == "inter":
            return None

        s = copy.deepcopy(solution)

        self.swap(s, x, y)
        if s == solution:
            return None

        return s

    def two_opt(self, solution, x1, x2, y1, y2, route_type="all"):
        if not self.is_adj(solution, x1, x2):
            return None
        if y1 == x1 or y1 == x2:
            return None
        if not self.is_adj(solution, y1, y2):
            return None

        C1 = self.inp["C1"]

        if x1 in C1 and self.is_in_drone_route(solution, y2):
            return None

        if y1 in C1 and self.is_in_drone_route(solution, x2):
            return None

        s = copy.deepcopy(solution)

        x1_ind = self.find_index(s, x1)
        x2_ind = self.find_index(s, x2)
        y1_ind = self.find_index(s, y1)
        y2_ind = self.find_index(s, y2)

        if self.is_in_same_trip(s, x1, y1) and route_type != "inter":
            if x1_ind < y1_ind:
                if len(x1_ind) == 2:
                    tmp = s[x2_ind[0]][x2_ind[1]:y2_ind[1]]
                    tmp.reverse()
                    s[x2_ind[0]][x2_ind[1]:y2_ind[1]] = tmp
                else:
                    tmp = s[x2_ind[0]][x2_ind[1]][x2_ind[2]:y2_ind[2]]
                    tmp.reverse()
                    s[x2_ind[0]][x2_ind[1]][x2_ind[2]:y2_ind[2]] = tmp

                return s
        if not self.is_in_same_trip(s, x1, y1) and route_type != "intra":
            if len(x2_ind) == 2:
                tmp1 = s[x2_ind[0]][x2_ind[1]:]
            else:
                tmp1 = s[x2_ind[0]][x2_ind[1]][x2_ind[2]:]

            if len(y2_ind) == 2:
                tmp2 = s[y2_ind[0]][y2_ind[1]:]
                s[y2_ind[0]][y2_ind[1]:] = tmp1
            else:
                tmp2 = s[y2_ind[0]][y2_ind[1]][y2_ind[2]:]
                s[y2_ind[0]][y2_ind[1]][y2_ind[2]:] = tmp1

            if len(x2_ind) == 2:
                s[x2_ind[0]][x2_ind[1]:] = tmp2
            else:
                s[x2_ind[0]][x2_ind[1]][x2_ind[2]:] = tmp2
            return s

        return None

    def or_opt(self, solution, x1, x2, y, b_dis=1, compare_operator=None, route_type="all"):
        if compare_operator is None:
            compare_operator = self.ge

        dis = self.dis(solution, x1, x2)
        if dis == float('inf'):
            return None

        if not compare_operator(dis, b_dis):
            return None

        if not self.is_adj(solution, x1, x2):
            return None

        if x1 == y or x2 == y:
            return None

        if not self.is_in_same_trip(solution, x1, y) and route_type == "intra":
            return None

        if self.is_in_same_trip(solution, x1, y) and route_type == "inter":
            return None

        C1 = self.inp["C1"]

        if x1 in C1 and self.is_in_drone_route(solution, y):
            return None

        s = copy.deepcopy(solution)

        self.delete_by_val(s, x1)
        self.delete_by_val(s, x2)
        self.insert_after(s, x1, y)
        self.insert_after(s, x2, x1)
        self.refactor(s)

        return s

    def inter_cross_exchange(self, solution, x1, x2, y1, y2, b_dis=1, compare_operator=None):
        if compare_operator is None:
            compare_operator = self.ge
        dis1 = self.dis(solution, x1, x2)
        dis2 = self.dis(solution, y1, y2)
        if dis1 == float('inf') or dis2 == float('inf'):
            return None

        if not compare_operator(dis1, b_dis) or not compare_operator(dis2, b_dis):
            return None

        if self.is_in_same_trip(solution, x1, y1):
            return None

        s = copy.deepcopy(solution)

        x1_ind = self.find_index(s, x1)
        x2_ind = self.find_index(s, x2)
        y1_ind = self.find_index(s, y1)
        y2_ind = self.find_index(s, y2)

        if len(x1_ind) == 2:
            tmp1 = s[x1_ind[0]][x1_ind[1] + 1:x2_ind[1]]
        else:
            tmp1 = s[x1_ind[0]][x1_ind[1]][x1_ind[2] + 1:x2_ind[2]]

        if len(y1_ind) == 2:
            tmp2 = s[y1_ind[0]][y1_ind[1] + 1:y2_ind[1]]
            s[y1_ind[0]][y1_ind[1] + 1:y2_ind[1]] = tmp1[:]
        else:
            tmp2 = s[y1_ind[0]][y1_ind[1]][y1_ind[2] + 1:y2_ind[2]]
            s[y1_ind[0]][y1_ind[1]][y1_ind[2] + 1:y2_ind[2]] = tmp1[:]

        if len(x1_ind) == 2:
            s[x1_ind[0]][x1_ind[1] + 1:x2_ind[1]] = tmp2[:]
        else:
            s[x1_ind[0]][x1_ind[1]][x1_ind[2] + 1:x2_ind[2]] = tmp2[:]

        return s

    def run_ejection(self, solution):
        max_level = self.config.ejection.max_level
        best_gain = 0
        best_shift_sequence = []
        current_gain = 0
        current_level = 0
        shift_sequence = []

        def ejection(x, gain, level):
            nonlocal best_gain, max_level, solution, shift_sequence, best_shift_sequence

            scores = []
            for i in range(len(solution)):
                scores.append(self.get_score_some_trip(solution, [i])[0])

            f_score = max(scores)

            x_ind = self.find_index(solution, x)

            predecessor = self.get_predecessor(solution, x)
            successor = self.get_successor(solution, x)

            if len(x_ind) == 2:
                dis = self.inp['tau']
            else:
                dis = self.inp['tau_a']

            scores[x_ind[0]] -= dis[predecessor, x] + dis[x, successor] - dis[predecessor, successor]
            c_score = max(scores)
            g = f_score - c_score

            self.delete_by_val(solution, x)
            gain += g

            for _cus in range(1, self.num_cus + 1):
                if _cus == x:
                    continue
                _cus_ind = self.find_index(solution, _cus)

                if len(_cus_ind) == 2:
                    if _cus_ind[0] == x_ind[0]:
                        continue
                    dis = self.inp['tau']
                    trip = solution[_cus_ind[0]]
                else:
                    if _cus_ind[0] == x_ind[0] and _cus_ind[1] == x_ind[1]:
                        continue
                    dis = self.inp['tau_a']
                    trip = solution[_cus_ind[0]][_cus_ind[1]]

                _cus_predecessor = self.get_predecessor(solution, _cus)

                tmp_score = scores[:]
                tmp_score[_cus_ind[0]] += dis[_cus_predecessor, x] + dis[x, _cus] - dis[_cus_predecessor, _cus]
                d = max(tmp_score) - c_score

                if gain - d > best_gain:
                    self.insert_before(solution, x, _cus)
                    gain -= d
                    shift_sequence.append((x, self.find_index(solution, x)))
                    level += 1

                    _, dz, cz = self.get_score_some_trip(solution, [_cus_ind[0]])

                    if dz == 0 and cz == 0:
                        best_shift_sequence = shift_sequence[:]
                        best_gain = gain
                    elif level + 1 <= max_level:
                        for yr in trip:
                            s = copy.deepcopy(solution)
                            self.delete_by_val(s, yr)
                            _, dz1, cz1 = self.get_score(s)
                            if dz1 == 0 and cz1 == 0:
                                ejection(yr, gain, level)

                    self.delete_by_val(solution, x)
                    gain += d
                    shift_sequence.pop()
                    level -= 1

                _cus_successor = self.get_successor(solution, _cus)
                if _cus_successor == self.num_cus + 1:
                    d = dis[_cus, x] + dis[x, _cus_successor] - dis[_cus, _cus_successor]

                    if gain - d > best_gain:
                        self.insert_after(solution, x, _cus)
                        gain -= d
                        shift_sequence.append((x, self.find_index(solution, x)))
                        level += 1

                        _, dz, cz = self.get_score_some_trip(solution, [_cus_ind[0]])

                        if dz == 0 and cz == 0:
                            best_shift_sequence = shift_sequence[:]
                            # print(best_shift_sequence)
                            best_gain = gain
                            # print(best_gain)
                        elif level + 1 <= max_level:
                            for yr in trip:
                                s = copy.deepcopy(solution)
                                self.delete_by_val(s, yr)
                                _, dz1, cz1 = self.get_score(s)
                                if dz1 == 0 and cz1 == 0:
                                    ejection(yr, gain, level)

                        self.delete_by_val(solution, x)
                        gain += d
                        shift_sequence.pop()
                        level -= 1

            self.insert_by_index(solution, x, x_ind)

        for cus in range(1, self.num_cus + 1):
            # print(cus)
            ejection(cus, current_gain, current_level)

        # print(best_shift_sequence)
        # print(best_gain)

        for cus, index in best_shift_sequence:
            self.delete_by_val(solution, cus)
            self.insert_by_index(solution, cus, index)

        return {"best_shift_sequence": str(best_shift_sequence), "best_gain": str(best_gain)}

    def run_inter_route(self, solution):
        inter = [self.relocate, self.exchange, self.two_opt, self.or_opt,
                 self.inter_cross_exchange]
        route_type = "inter"
        r = {}
        while True:
            random.shuffle(inter)
            has_improve = False
            for op in inter:
                if op == self.relocate or op == self.exchange:
                    for x in range(1, self.num_cus + 1):
                        for y in range(1, self.num_cus + 1):
                            s = op(solution, x, y, route_type)
                            if s is not None and self.get_score(s)[0] < self.get_score(solution)[0]:
                                solution = s
                                has_improve = True

                elif op == self.two_opt:
                    for x1 in range(1, self.num_cus + 1):
                        for x2 in range(1, self.num_cus + 1):
                            for y1 in range(1, self.num_cus + 1):
                                for y2 in range(1, self.num_cus + 1):
                                    s = self.two_opt(solution, x1, x2, y1, y2, route_type)
                                    if s is not None and self.get_score(s)[0] < self.get_score(solution)[0]:
                                        solution = s
                                        has_improve = True
                elif op == self.or_opt:
                    for x1 in range(1, self.num_cus + 1):
                        for x2 in range(1, self.num_cus + 1):
                            for y in range(1, self.num_cus + 1):
                                s = self.or_opt(solution, x1, x2, y, route_type=route_type)
                                if s is not None and self.get_score(s)[0] < self.get_score(solution)[0]:
                                    solution = s
                                    has_improve = True
                else:
                    for x1 in range(1, self.num_cus + 1):
                        for x2 in range(1, self.num_cus + 1):
                            for y1 in range(1, self.num_cus + 1):
                                for y2 in range(1, self.num_cus + 1):
                                    s = self.inter_cross_exchange(solution, x1, x2, y1, y2)
                                    if s is not None and self.get_score(s)[0] < self.get_score(solution)[0]:
                                        solution = s
                                        has_improve = True

            if not has_improve:
                break

    def run_intra_route(self, solution):
        intra = [self.relocate, self.exchange, self.two_opt, self.or_opt]
        route_type = "intra"

        improve_set = set()

        while True:
            random.shuffle(intra)
            has_improve = False
            new_improve_set = set()

            for op in intra:
                if op == self.relocate or op == self.exchange:
                    for x in range(1, self.num_cus + 1):
                        x_ind = self.find_index(solution, x)
                        if x_ind[:-1] in improve_set:
                            continue
                        for y in range(1, self.num_cus + 1):
                            s = op(solution, x, y, route_type)
                            if s is not None and self.get_score(s)[0] < self.get_score(solution)[0]:
                                solution = s
                                has_improve = True
                                new_improve_set.add(x_ind[:-1])

                elif op == self.two_opt:
                    for x1 in range(1, self.num_cus + 1):
                        x_ind = self.find_index(solution, x1)
                        if x_ind[:-1] in improve_set:
                            continue
                        for x2 in range(1, self.num_cus + 1):
                            for y1 in range(1, self.num_cus + 1):
                                for y2 in range(1, self.num_cus + 1):
                                    s = self.two_opt(solution, x1, x2, y1, y2, route_type)
                                    if s is not None and self.get_score(s)[0] < self.get_score(solution)[0]:
                                        solution = s
                                        has_improve = True
                                        new_improve_set.add(x_ind[:-1])
                elif op == self.or_opt:
                    for x1 in range(1, self.num_cus + 1):
                        x_ind = self.find_index(solution, x1)
                        if x_ind[:-1] in improve_set:
                            continue
                        for x2 in range(1, self.num_cus + 1):
                            for y in range(1, self.num_cus + 1):
                                s = self.or_opt(solution, x1, x2, y, route_type=route_type)
                                if s is not None and self.get_score(s)[0] < self.get_score(solution)[0]:
                                    solution = s
                                    has_improve = True
                                    new_improve_set.add(x_ind[:-1])

            if not has_improve:
                break
            improve_set = new_improve_set


if __name__ == '__main__':
    pass
