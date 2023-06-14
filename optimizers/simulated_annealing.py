import sys, time
import numpy as np
from simanneal import Annealer

from .aux_functions import data_functions as datf


class InitValueFinder(Annealer):
    """Test annealer
    """
    ranges = []
    history_states = []
    age_groups = []
    incidence_type = ""
    a_detail = False
    energy_func = None

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, ranges, history_states, age_groups, incidence_type, a_detail,
                 optimum_func):
        self.ranges = ranges
        self.history_states = history_states
        self.age_groups = age_groups
        self.incidence_type = incidence_type
        self.energy_func = optimum_func
        self.a_detail = a_detail
        self.steps = 500  # 10000
        self.updates = 100  # 1000
        self.copy_strategy = "slice"
        self.state = state
        super(InitValueFinder, self).__init__(state)  # important!

    def move(self):
        """Moves to different argument"""

        state_list = []
        for i in range(0, len(self.state)):
            state_list.append(np.random.uniform(self.ranges[i][0], self.ranges[i][1]))
        state_array = np.array(state_list)

        self.state = state_array

    def energy(self):
        """Calculates the optimization function value"""

        exposed_list = lam_list = a_list = None

        if self.incidence_type == "age-group":
            exposed_list = [0] * len(self.history_states)
            for i, history_state in enumerate(self.history_states):
                if history_state[1] == "Not exposed":
                    exposed_list[i] = 1.0 - self.state[i - 1]
                else:
                    exposed_list[i] = self.state[i]

            lam_idx = len(self.age_groups)
            lam_list = [self.state[lam_idx]]

            if self.a_detail:
                a_list = [0] * len(self.age_groups)
                a_idx = lam_idx + 1
                for idx_j, age_group in enumerate(self.age_groups):  # 4 groups
                    a_list[idx_j] = self.state[a_idx + idx_j]
            else:
                a_idx = lam_idx + 1
                a_list = [self.state[a_idx]]

        '''exposed_list = lam_list = a_list = None

        if self.incidence_type == "age-group":
            exposed_list = [0] * len(self.history_states)
            for i, history_state in enumerate(self.history_states):
                if history_state[1] == "Not exposed":
                    exposed_list[i] = 1.0 - self.state[i-1]
                else:
                    exposed_list[i] = self.state[i]

            lam_idx = len(self.age_groups)
            lam_list = [self.state[lam_idx]]

            if self.a_detail:
                a_list = [0] * len(self.age_groups)
                a_idx = lam_idx + 1
                for idx_j, age_group in enumerate(self.age_groups):  # 4 groups
                    a_list[idx_j] = self.state[a_idx + idx_j]
            else:
                a_idx = lam_idx + 1
                a_list = [self.state[a_idx]]'''
        '''
        if self.incidence_type == "age-group":
            exposed_list = []
            not_exposed = []
            for i, item in enumerate(self.state[:len(self.age_groups)]):
                exposed_list.append(item)
                not_exposed.append(1-item)

            exposed_list = exposed_list + not_exposed

            lam_idx = len(self.age_groups)
            lam_list = [self.state[lam_idx]]

            if self.a_detail:
                a_list = [0] * len(self.age_groups)
                a_idx = lam_idx + 1
                for idx_j, age_group in enumerate(self.age_groups):  # 4 groups
                    a_list[idx_j] = self.state[a_idx + idx_j]
            else:
                a_idx = lam_idx + 1
                a_list = [self.state[a_idx]]
        '''
        dist2_list = self.energy_func(exposed_list, lam_list, a_list)
        dist2 = sum(dist2_list)

        return dist2

    def update(self, step, T, E, acceptance, improvement):
        elapsed = time.time() - self.start
        if step == 0:
            print(' Temperature        Energy    Accept   Improve     Elapsed   Remaining',
                  file=sys.stderr)
            print('\r%12.5f  %12.2f                      %s            ' %
                  (T, E, datf.time_string(elapsed)), file=sys.stderr)
            sys.stderr.flush()
        else:
            remain = (self.steps - step) * (elapsed / step)
            print('\r%12.5f  %12.2f  %7.2f%%  %7.2f%%  %s  %s\r' %
                  (T, E, 100.0 * acceptance, 100.0 * improvement,
                   datf.time_string(elapsed), datf.time_string(remain)), file=sys.stderr)
            sys.stderr.flush()
