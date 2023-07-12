import json
import os
import random
from collections import deque
from copy import deepcopy

from src.ts.init_solution import init_by_distance, init_by_angle
from src.ts.ts_utils import TSUtils
from src.utils import make_dirs_if_not_present


class TabuSearch:
    """
    Conducts tabu search
    """
    cur_steps = None

    tabu_size = None
    tabu_dict = None

    initial_state = None
    current = None
    best = None

    max_steps = None

    cache = {}

    def __init__(self, inp, config, initial_state, tabu_size, max_steps, ext=0):
        """

        :param initial_state:
        :param tabu_size:
        :param max_steps:
        """
        self.init_info = "random"
        self.config = config
        self.inp = inp
        self.penalty_params = self.config.tabu_params
        self.ext = ext
        try:
            self.nested_tau = inp["nested_tau"]
            self.nested_tau_a = inp["nested_tau_a"]
        except:
            nested = {}
            for i in range(1, self.inp["num_cus"] + 1):
                nested[i] = 0
            self.nested_tau = nested
            self.nested_tau_a = nested
        self.utils = TSUtils(config, inp)
        self.actions = list(self.utils.action.keys())
        self.action_weights = None
        if self.config.tabu_params.use_weights:
            self.action_weights = []
            for a in self.actions:
                self.action_weights.append(self.config.tabu_params.action_weights[a])

        if initial_state is None:
            initial_state = self.init_solution_heuristic()
        self.initial_state = initial_state

        if isinstance(tabu_size, int) and tabu_size > 0:
            self.tabu_size = tabu_size
        else:
            raise TypeError('Tabu size must be a positive integer')

        if isinstance(max_steps, int) and max_steps > 0:
            self.max_steps = max_steps
        else:
            raise TypeError('Maximum steps must be a positive integer')

    def init_solution_heuristic(self):
        solution = self.init_solution_random()
        for reverse in [True, False]:
            s = init_by_distance(self.inp, self.config, reverse=reverse)
            if s is not None and self._score(s) < self._score(solution):
                solution = s
                self.init_info = f"distance-reversed: {reverse}"

            s = init_by_angle(self.inp, self.config, reverse=reverse, direction=1)
            if s is not None and self._score(s) < self._score(solution):
                solution = s
                self.init_info = f"angle-reversed: {reverse}-direction: 1"

            s = init_by_angle(self.inp, self.config, reverse=reverse, direction=-1)
            if s is not None and self._score(s) < self._score(solution):
                solution = s
                self.init_info = f"angle-reversed: {reverse}-direction: -1"

        return solution
    
    def update(self, config, inp):
        self.config = config 
        self.inp = inp 
        self.utils.update_config(config, inp)
    
    def init_solution_random(self):
        num_cus = self.inp["num_cus"]
        num_staff = self.config.params["num_staff"]
        num_drone = self.config.params["num_drone"]
        L_w = self.config.params["L_w"]
        L_d = self.config.params["L_d"]

        tau_a = self.inp["tau_a"]

        C1 = self.inp["C1"]
        tmp = [i for i in range(1, num_cus + 1) if i not in C1]

        random.shuffle(tmp)
        solution = []

        for i in range(num_drone + num_staff - 1):
            tmp.insert(random.randint(0, len(tmp) + 1), 0)

        indices = [i for i, x in enumerate(tmp) if x == 0]

        for i in C1:
            tmp.insert(random.randint(indices[num_drone - 1] + 1, len(tmp) + 1), i)

        trip = []
        for i in tmp:
            if i != 0:
                trip.append(i)
            else:
                solution.append(trip)
                trip = []

        solution.append(trip)
        for i in range(num_drone):
            if len(solution[i]) == 0:
                continue
            t_d = 0
            t_w = -tau_a[0, solution[i][0]]
            prev = 0
            new_trip = []
            sub_trip = []
            for ind, cus in enumerate(solution[i]):
                if t_d + tau_a[prev, cus] + tau_a[cus, num_cus + 1] > L_d \
                        or t_w + tau_a[prev, cus] + tau_a[cus, num_cus + 1] > L_w:
                    t_d = 0
                    t_w = -tau_a[0, solution[i][ind]]
                    prev = 0
                    new_trip.append(sub_trip)
                    sub_trip = [cus]
                else:
                    t_d += tau_a[prev, cus]
                    t_w += tau_a[prev, cus]
                    prev = cus
                    sub_trip.append(cus)
            new_trip.append(sub_trip)
            solution[i] = new_trip

        return solution

    def __str__(self):
        return ('TABU SEARCH: \n' +
                'CURRENT STEPS: %d \n' +
                'BEST SCORE: %f \n' +
                'BEST MEMBER: %s \n\n') % \
               (self.cur_steps, self._score(self.best), str(self.best))

    def __repr__(self):
        return self.__str__()

    def _clear(self):
        """
        Resets the variables that are altered on a per-run basis of the algorithm

        :return:
        """
        self.cur_steps = 0
        self.tabu_dict = {}
        for act in self.actions:
            self.tabu_dict[act] = deque(maxlen=self.tabu_size)
        self.current = self.initial_state
        self.best = self.initial_state
        self.cache["order_neighbor"] = []

    def _score(self, state, return_all=False):
        """
        Returns objective function value of a state

        :param state:
        :return:
        """
        if return_all:
            return self.utils.get_score(state, self.penalty_params)
        return self.utils.get_score(state, self.penalty_params)[0]

    def _neighborhood(self):
        """
        Returns list of all members of neighborhood of current state, given self.current

        :return:
        """
        result = {}
        act = None
        while len(result) == 0:
            act = random.choices(self.actions, weights=self.action_weights)[0]
            # print(f"act - {act}")
            # print(self.current)
            result = self.utils.get_all_neighbors(self.current, act)
            

        return act, result

    def _best(self, neighborhood, reset=False):
        """
        Finds the best member of a neighborhood

        :param neighborhood:
        :return:
        """

        if reset:
            self.cache["order_neighbor"] = sorted(neighborhood.items(), key=lambda x: self._score(x[1]))

        if len(self.cache["order_neighbor"]) > 0:
            return self.cache["order_neighbor"].pop(0)
        return None, None

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

    def run_tabu(self, verbose=True):
        """
        Conducts tabu search

        :param verbose:
        :return:
        """

        r = {}
        self._clear()
        not_improve_iter = 0
        for _ in range(self.max_steps):
            previous_best = self.best
            self.cache["order_neighbor"] = []
            self.cur_steps += 1
            if verbose:
                print(
                    f"Step: {self.cur_steps} - Best: {self._score(self.best, True)} "
                    f"- Step Best: {self._score(self.current, True)}")

                print(f"{self.current}")
            act, neighborhood = self._neighborhood()
            print(f"{act} - {len(neighborhood)}")
            ext, neighborhood_best = self._best(neighborhood, True)
            tabu_list = self.tabu_dict[act]

            cur = self.current

            while True:
                if all([self.get_tabu(act, x) in tabu_list for x in neighborhood]):
                    # print("TERMINATING - NO SUITABLE NEIGHBORS")
                    # return {"tabu-sol": str(self.best), "tabu-score": str(self._score(self.best)), "tabu-log": r}
                    break

                step_best_info = self._score(neighborhood_best, True)
                best_score = self._score(self.best)

                if self.get_tabu(act, ext) in tabu_list:
                    if step_best_info[0] < best_score:
                        self.current = neighborhood_best
                        self.update_penalty_param(step_best_info[1], step_best_info[2])
                        self.best = deepcopy(neighborhood_best)
                        tabu_list.append(self.get_tabu(act, ext))
                        r[self.cur_steps] = {"best": f"{self._score(self.best)} - {self.best}",
                                             "old_current": f"{self._score(cur)} - {cur}",
                                             "current": f"{self._score(self.current)} - {self.current}",
                                             "action": act,
                                             "ext": str(self.get_tabu(act, ext)),
                                             "t": "in tabu"}
                        break
                    else:
                        ext, neighborhood_best = self._best(neighborhood)
                        if ext is None:
                            break
                elif abs(step_best_info[0] - self._score(cur)) < self.config.tabu_params.epsilon:
                    if len(neighborhood) > 0:
                        ext, neighborhood_best = self._best(neighborhood)
                        if ext is None:
                            break
                    else:
                        break
                else:
                    self.current = neighborhood_best
                    current_info = self._score(self.current, True)
                    tabu_list.append(self.get_tabu(act, ext))
                    if current_info[0] < best_score:
                        self.best = deepcopy(self.current)
                        self.update_penalty_param(current_info[1], current_info[2])
                    r[self.cur_steps] = {"best": f"{self._score(self.best)} - {self.best}",
                                         "old_current": f"{self._score(cur)} - {cur}",
                                         "current": f"{self._score(self.current)} - {self.current}",
                                         "action": act,
                                         "ext": str(self.get_tabu(act, ext)),
                                         "t": "not in tabu"}
                    break

            if self.best == previous_best:
                not_improve_iter += 1

            if not_improve_iter > self.config.tabu_params.terminate_iter:
                print("TERMINATING TABU - REACHED MAXIMUM NOT IMPROVE STEPS")
                break

        print("TERMINATING TABU - REACHED MAXIMUM STEPS")
        if verbose:
            print(self)
        print(self.initial_state)

        # with open('result.json', 'w') as json_file:
        #     json.dump(r, json_file, indent=2)

        return {"tabu-sol": str(self.best), "tabu-score": str(self._score(self.best)), "tabu-log": r}

    def run_post_optimization(self, verbose=True):
        r = {}

        if self.config.params.use_ejection:
            ejection_log = self.utils.run_ejection(solution=self.best)
            r["ejection"] = {"ejection-sol": str(self.best), "ejection-score": str(self._score(self.best)),
                             "ejection-log": ejection_log}
        if self.config.params.use_inter:
            self.utils.run_inter_route(solution=self.best)
            r["inter"] = {"inter-sol": str(self.best), "inter-score": str(self._score(self.best)), "inter-log": {}}

        if self.config.params.use_inter:
            self.utils.run_intra_route(solution=self.best)
            r["intra"] = {"intra-sol": str(self.best), "intra-score": str(self._score(self.best)), "intra-log": {}}

        return r

    def run(self, verbose=True):
        r = {"init_info": {"method": self.init_info, "init": str(self.initial_state)}}

        tabu_info = self.run_tabu(verbose)
        r["tabu"] = tabu_info
        post_optimization_info = self.run_post_optimization(verbose)
        r.update(post_optimization_info)

        make_dirs_if_not_present(self.config.result_folder)

        with open(os.path.join(self.config.result_folder,
                               'result_' + self.inp['data_set'] + '_' + str(self.ext) + '.json'), 'w') as json_file:
            json.dump(r, json_file, indent=2)

    @staticmethod
    def get_tabu(act, ext):
        if act == "move01":
            return ext[0]
        elif act == "move02":
            return ext[1]
        elif act == "move10":
            return ext[0]
        elif act == "move11":
            return ext
        elif act == "move20":
            return ext[:2]
        elif act == "move21":
            return ext
        else:
            return [ext[0], ext[2]]
