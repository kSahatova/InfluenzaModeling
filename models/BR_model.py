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
    Age-sctructured Baroyan-Rvachev model with comparison for the averaged model without age groups
    """
    def __init__(self, M, pop_size, incidence_type, age_groups, strains):
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
        self.rho = pop_size  # A scalar in absence of separate age groups

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
    def __init__(self, M, pop_size, incidence_type, age_groups, strains):
        super().__init__(M, pop_size, incidence_type, age_groups, strains)
        #self.history_states = [(age, state) for age in self.age_groups for state in ['Exposed', 'Not exposed']]
        #self.history_states = self.age_groups + ['Not exposed'] * len(self.age_groups)
        self.history_states = self.age_groups
        self.I0 = np.ones(len(self.age_groups))
        self.rho += np.sum(self.I0)
        self.total_recovered = [0 for _ in range(len(self.age_groups))]
        self.a_detail = False  # [legacy] change manually if needed

    def make_simulation(self):
        age_groups_num = len(self.age_groups)
        history_states_num = len(self.history_states)

        '''y = pd.DataFrame(0, index=self.age_groups, columns=range(self.N+1))  # strains x N
        y.iloc[:, 0] = self.I0
        x = pd.DataFrame(0, index=self.history_states, columns=range(self.N+1))  # history_states x N
        x.iloc[:, 0] = [(exp_fraction * self.rho).item() for exp_fraction in self.exposed_fraction_h]
        print(x.loc[('0-14', 'Exposed'), :])'''
        y = np.zeros((age_groups_num, self.N + 1))
        y[:, 0] = self.I0
        x = np.zeros((history_states_num, self.N + 1))
        x[:, 0] = [(exp_fraction * self.rho).item() for exp_fraction in self.exposed_fraction_h]
        population_immunity = np.zeros((age_groups_num, self.N + 1))
        recovery_days_num = self.get_recovery_time()

        for t in range(0, self.N):
            for h in range(0, history_states_num):
                x[h][t + 1] = x[h][t]

                infect_force_total = 0  # Infection from all strains per group
                infect_force_list = []

                for m, age_group in enumerate(self.age_groups):  # Calculating y_m
                    if self.a_detail:
                        a = self.a[m]
                    else:
                        a = self.a[0]

                    # todo: self.M[m][h]
                    inf_force = self.lam_m[0] * 6.528 * self.sum_ill(y[m], t) * f(h, m, a) / self.rho
                    infect_force_list.append(inf_force)
                    infect_force_total += inf_force  # Considering the overall strength of the infection

                real_infected = min(infect_force_total, 1.0) * x[h][t]
                x[h][t + 1] -= real_infected

                if infect_force_total > 0:
                    for m, age_group in enumerate(self.age_groups):  # Calculating y_m
                        real_infected_m = real_infected * (infect_force_list[m] / infect_force_total)

                        y[m][t + 1] += real_infected_m
                        self.total_recovered[m] += real_infected_m  # They will get cured (no mortality)

                        if t > recovery_days_num - 1:
                            if isinstance(real_infected_m, np.ndarray):
                                population_immunity[m][t + 1] = population_immunity[m][t] + real_infected_m[0]
                            else:
                                population_immunity[m][t + 1] = population_immunity[m][t] + real_infected_m

        return y, population_immunity, self.rho, []
