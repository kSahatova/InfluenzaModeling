import numpy as np
import pandas as pd


def f(h, m, a):
    """
    Function to imitate that the individual was exposed to the same virus strain as in the previous season
    :param h: exposure history state
    :param m: virus strain m
    :param a: susceptible fraction of individuals in (0;1] range
    """
    if h == m:
        return a
    else:
        return 1


class BRModel:
    """
    Age-structured Baroyan-Rvachev model with comparison for the averaged model without age groups
    """
    def __init__(self, M, pop_size, mu, incidence_type, age_groups, strains):
        """
        :param M: contact matrix
        :param pop_size (float): susceptible population size
        :param incidence_type (str): experiment setup
        :param age_group (list[str]): list of age groups
        :param strains (list[str]): list of strain names
        """
        self.q = [0.0, 0.0, 1, 0.9, 0.55, 0.3, 0.15, 0.05]  # infectivity
        self.N = 1800  # in days

        self.M = M
        self.pop_size = pop_size  # A scalar in absence of separate age groups
        self.mu = mu

        self.incidence_type = incidence_type
        self.a_detail = False  # flag whether to set individual a_value per age group (a - susceptible fraction)
        self.age_groups = age_groups
        self.strains = strains

        self.history_states = []
        self.exposed_fraction_h = []  # fractions with different exposure history
        self.lam_m = []
        self.I0 = []  # TODO: put out to the config file to tweak initially infected persons
        self.a = []  # Waning immunity level

        self.total_recovered = []  # Recovered from different strains

    def sum_ill(self, y, t):
        """
        Accumulation of number of the infected people by the strain m up to the moment t
        """
        sum = 0
        T = len(self.q)  # disease duration for a single person

        # cummul_y = sum([y[t-epid_day] * self.q[epid_day] if t-epid_day >= 0 else 0 for epid_day in range(T)])
        for epid_day in range(0, T):
            if t - epid_day < 0:
                y_cur = 0
            else:
                y_cur = y[t - epid_day]

            sum += y_cur * self.q[epid_day]

        return sum

    def init_simul_params(self, exposed_list, lam_list, a):
        if not isinstance(exposed_list, list):
            exposed_list = [exposed_list]

        if not isinstance(lam_list, list):
            lam_list = [lam_list]

        if not isinstance(a, list):
            a = [a]
        self.exposed_fraction_h = exposed_list
        self.lam_m = lam_list
        self.a = a

    def get_recovery_time(self):
        return len(self.q) + 1

    def make_simulation(self):
        raise NotImplementedError


class AgeModel(BRModel):
    def __init__(self, M, pop_size, mu, incidence_type, age_groups, strains):
        super().__init__(M, pop_size, mu, incidence_type, age_groups, strains)

        self.I0 = np.ones(len(self.age_groups))
        self.history_states = ['Exposed', 'Not exposed']
        self.total_recovered = [0 for _ in range(len(self.age_groups))]
        self.a_detail = False  # [legacy] change manually if needed
        self.strains = ['Generic']

    def make_simulation(self):
        age_groups_num = len(self.age_groups)
        history_states_num = len(self.history_states)

        y = np.zeros((age_groups_num, self.N + 1))
        y_daily = np.zeros((age_groups_num, self.N + 1 + 8))  # 2 x (1801 + 8) | strains x N
        y[:, 0] = self.I0

        x = np.zeros((age_groups_num, history_states_num, self.N + 1))
        rho = np.asarray(self.pop_size) - self.I0

        r0 = np.zeros(age_groups_num)
        rt = np.zeros((age_groups_num, self.N + 1))

        total_pop_size = rho.sum()
        for i in range(age_groups_num):
            x[i, :, 0] = np.asarray(self.exposed_fraction_h)[i, :] * (1-self.mu) * rho[i]  # (1-self.mu) *

        population_immunity = np.zeros((age_groups_num, self.N + 1))
        recovery_days_num = self.get_recovery_time()

        for t in range(self.N):
            for i, age in enumerate(self.age_groups):
                for h, state in enumerate(self.history_states):
                    x[i, h, t + 1] = x[i, h, t]

                    infect_force_list = []

                    for j in range(age_groups_num):
                        if self.a_detail:
                            a = self.a[i]   # [legacy] deprecated
                        else:
                            a = self.a[0]

                        if state == 'Not exposed':
                            m = self.strains.index(self.strains[h-1])  # m is strain index
                        else:
                            m = self.strains.index(self.strains[h])

                        f_value = f(h, m, a)

                        if t == 0:
                            r0[i] = (self.lam_m[0] * self.M[i][j] / (1 / 6))  # 1/6

                        infect_force = self.lam_m[0] * self.M[i][j] * self.sum_ill(y[j], t) * f_value / rho[i]
                        infect_force_list.append(infect_force)

                    infect_force_total = sum(infect_force_list)
                    real_infected = min(infect_force_total, 1.0) * x[i, h, t]
                    x[i, h, t + 1] -= real_infected
                    y[i, t+1] += real_infected

                    y_daily[i, t + 8] = real_infected
                    if y_daily[i, t] != 0:
                        rt[i, t + 1] = real_infected / y_daily[i, t]
                        # rt[i, m, t + 1] = r0[i, m] * (x[i, h, t+1] / x[i, h, 0])
                    self.total_recovered[i] += real_infected

                    if t > recovery_days_num - 1:
                        if isinstance(real_infected, np.ndarray):
                            population_immunity[i][t + 1] = population_immunity[i][t] + real_infected[0]
                        else:
                            population_immunity[i][t + 1] = population_immunity[i][t] + real_infected

        return y, population_immunity, rho, r0, rt


class StrainModel(BRModel):
    def __init__(self, M, pop_size, mu, incidence_type, age_groups, strains):
        super().__init__(M, pop_size, mu, incidence_type, age_groups, strains)

        self.history_states = self.strains.copy() + ["No exposure"]
        self.total_recovered = [0 for _ in range(len(self.strains))]
        self.age_groups = self.age_groups if self.incidence_type != 'strain' else ['total']
        self.I0 = np.ones((len(self.age_groups), len(self.strains)))

    def make_simulation(self):
        strains_num = len(self.strains)
        age_groups_num = len(self.age_groups)
        history_states_num = len(self.history_states)

        y = np.zeros((age_groups_num, strains_num, self.N + 1))
        y_daily = np.zeros((age_groups_num, strains_num, self.N + 1 + 8))  # 3 x (1801 + 8) | strains x N
        for i in range(age_groups_num):
            y[i, :, 0] = self.I0[i, :]

        x = np.zeros((age_groups_num, history_states_num, self.N + 1))
        rho = np.asarray([self.pop_size]).T - self.I0.sum(axis=1).reshape(age_groups_num, 1)

        r0 = np.zeros((age_groups_num, strains_num))
        rt = np.zeros((age_groups_num, strains_num, self.N + 1))

        for i in range(age_groups_num):
            exp_list = np.asarray(self.exposed_fraction_h)
            if len(exp_list.shape) == 1:
                exp_list = exp_list.reshape(1, -1)
            x[i, :, 0] = exp_list[i, :] * (1 - self.mu) * rho[i]

        population_immunity = np.zeros((strains_num, self.N + 1))

        for t in range(self.N):
            for i in range(age_groups_num):
                for h, state in enumerate(self.history_states):
                    x[i, h, t+1] = x[i, h, t]

                    inf_force_list = []

                    for m in range(strains_num):
                        infection_force = 0
                        for j in range(age_groups_num):
                            betta = self.lam_m[m] * self.M[i][j]
                            cum_y = self.sum_ill(y[j, m, :], t)
                            f_value = f(h, m, self.a[0])

                            if t == 0:
                                r0[i, m] = (self.lam_m[m] * self.M[i][j] / (1 / 6))  # 1/6
                            infection_force += betta * cum_y * f_value / rho[i]
                        inf_force_list.append(infection_force)

                    infection_force_total = sum(inf_force_list)
                    real_infected = min(infection_force_total, 1) * x[i, h, t]
                    x[i, h, t + 1] -= real_infected
                    if infection_force_total > 0:
                        for m in range(strains_num):
                            y[i, m, t+1] += inf_force_list[m] / infection_force_total * real_infected
                            y_daily[i, m, t + 8] = (real_infected * (inf_force_list[m] / infection_force_total))
                            if y_daily[i, m, t] != 0:
                                rt[i, m, t + 1] = (real_infected * (inf_force_list[m] / infection_force_total)) / y_daily[i, m, t]
                                # rt[i, m, t + 1] = r0[i, m] * (x[i, h, t+1] / x[i, h, 0])

        return y, population_immunity, rho, r0, rt
