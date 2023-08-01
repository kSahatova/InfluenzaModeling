import os
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from scipy.optimize import minimize
from scipy.stats import qmc
from sklearn.metrics import r2_score

from functools import partial
from multiprocessing import Pool

from .simulated_annealing import InitValueFinder
from .aux_functions import data_functions as dtf
from .aux_functions import weekly_functions as weeklyf
from .aux_functions import weights_for_data_functions as weights_for_data
from .aux_functions import param_range_functions as pr


class BaseOptimizer:
    """
    Parent class optimizer
    """
    def __init__(self, model, data, model_detailed, sigma):
        """
        An optimizer class constructor
        :param model (BR_model): Baroyan-Rvachev model (check models.BR_model)
        :param data_obj (EpiData): EpiData object
        :param model_detail (bool): model aggregation flag
        :param grouping (bool): calibrated model results aggregation flag
        :param predict (bool): flag to set prediction mode
        """
        self.model = model

        self.incidence_type = self.model.incidence_type
        self.a_detail = self.model.a_detail  # [legacy] should be changed in BR model manually for age-group case
        self.grouping = False

        self.age_groups = model.age_groups
        self.strains = model.strains
        self.groups = [] if model_detailed else ['Все']

        self.df_data_weekly: DataFrame = data
        self.calib_data_weekly: Optional[DataFrame] = None

        self.df_simul_daily: Optional[DataFrame] = None
        self.df_simul_weekly: Optional[DataFrame] = None

        self.general_main_peak = []
        self.strains_num_opt = 0
        self.delta = 0
        self.data_weights = {}

        self.R_square_list = []
        self.dist2_ww_list = []
        self.res2_list = []

        self.population_immunity = 0
        self.active_population = 0
        self.tpeak_bias_aux = 0

        self.r0 = []
        self.bootstrap_mode = False
        self.sigma = sigma

    def _set_general_peak(self):
        """Calculates the greatest number of incidence cases and its index in the data set"""
        general_main_peak, _ = dtf.max_elem_indices(self.df_data_weekly, self.groups)
        return general_main_peak

    def _set_weekly_inc(self):
        """Converts data points of the model curve presented in days to weeks"""
        self.df_simul_weekly = weeklyf.getDays2Weeks(self.df_simul_daily, self.groups)

    def _get_data_weights(self, df, sigma):  # df, strains, age_group, incidence_type
        """Puts bigger weights to the data points that are closer to the peak"""
        return weights_for_data.getWeights4Data(df, self.groups, sigma)

    def update_delta(self):
        peak_indices_real, _ = dtf.max_elem_indices(self.df_data_weekly, self.groups)
        peak_indices_model, peak_values_model = dtf.max_elem_indices(self.df_simul_weekly, self.groups)

        peak_indices_model = [(peak_index + self.tpeak_bias_aux) for peak_index in peak_indices_model]
        delta_list_prelim = [peak_index_model - peak_index_real
                             for peak_index_model, peak_index_real in
                             zip(peak_indices_model, peak_indices_real)]
        self.delta = delta_list_prelim[dtf.max_elem_index(peak_values_model)]

    def update_data_alignment(self):
        """Updates index of the original data"""
        self.df_data_weekly.index = [item + self.delta for item in range(len(self.df_data_weekly))]
        self.calib_data_weekly.index = [item + self.delta for item in range(len(self.calib_data_weekly))]

    def update_bootstrapped_data_alignment(self):
        # todo : rewrite index update
        self.df_data_weekly.index = [item - list(self.df_data_weekly.index)[0] for item in
                                     list(self.df_data_weekly.index)]
        self.calib_data_weekly.index = [item - list(self.calib_data_weekly.index)[0] for item in
                                        list(self.calib_data_weekly.index)]

    def find_model_fit(self, exposed_list, lam_list, a):
        # Launching the simulation for a given parameter value and aligning the result to model

        self.model.set_attributes()
        self.model.init_simul_params(exposed_list, lam_list, a)
        self.model.set_attributes()
        infected_pop, self.population_immunity, self.active_population, self.r0 = self.model.make_simulation()
        inf_shape = infected_pop.shape
        infected_pop = infected_pop.reshape(inf_shape[0] * inf_shape[1], inf_shape[2])
        self.df_simul_daily = pd.DataFrame(infected_pop.T, columns=self.groups)

        if self.df_simul_daily.max().max() == 1.0:
            print("No epi dynamics")
            return [999999999999] * len(self.groups)

        df_extend = pd.DataFrame(0, index=np.arange(1800), columns=self.df_simul_daily.columns)
        self.df_simul_daily = pd.concat([self.df_simul_daily, df_extend], ignore_index=True)

        self._set_weekly_inc()

        if not self.bootstrap_mode:
            self.update_delta()
            self.update_data_alignment()  # data index update order changed [followed after R2 calc previously]

            dist2_list, self.dist2_ww_list = \
                dtf.calculate_dist_squared_weighted_list(self.calib_data_weekly, self.df_simul_weekly,
                                                         self.groups, self.delta, self.data_weights)
            self.R_square_list = dtf.calculate_r_square(self.calib_data_weekly, self.df_simul_weekly,
                                                        self.groups, self.delta, self.data_weights)
        else:
            self.delta = 0
            self.update_bootstrapped_data_alignment()
            dist2_list, self.dist2_ww_list = \
                dtf.calculate_dist_squared_weighted_list(self.df_data_weekly, self.df_simul_weekly, self.groups,
                                                         self.delta, self.data_weights)

            self.R_square_list = [1 - fun_val / res2 for fun_val, res2 in zip(dist2_list, self.res2_list)]

        print(" R2: ", self.R_square_list)

        '''R_square_plain = dtf.calculate_r_square(self.calib_data_weekly, self.df_simul_weekly,
                                                self.groups, self.delta, self._get_data_weights(self.df_data_weekly,
                                                                                                sigma=1.5))
        print('R2 with weights', R_square_plain)'''

        return dist2_list

    def fit_function(self, k):
        raise NotImplementedError

    def calculate_population_immunity(self, exposed_list, a):
        raise NotImplementedError

    def init_parameters(self):
        param_ranges = pr.set_parameters_range(self.incidence_type)
        init_params = np.zeros(len(param_ranges))
        for i, param_range in enumerate(param_ranges):
            init_params[i] = np.random.uniform(*param_range, 1)
        return init_params, param_ranges

    def optimize(self, param_init, param_range, tpeak_bias_aux_cur):
        self.tpeak_bias_aux = tpeak_bias_aux_cur
        initFinderObj = InitValueFinder(param_init,
                                        param_range,
                                        self.model.history_states,
                                        self.age_groups,
                                        self.incidence_type,
                                        self.a_detail,
                                        self.find_model_fit)
        print("Assessing the best initial point, this might take some time...")
        state, e = initFinderObj.anneal()
        print("Initial state: ", state)
        optim_result = minimize(self.fit_function, state, method='Nelder-Mead', bounds=param_range)  # SLSQP, L-BFGS-B

        return self, optim_result

    def optimize_lhs(self):
        sampler = qmc.LatinHypercube(d=7)
        sampled_params = sampler.random(n=10000)
        l_bounds = [0.1, 0.1, 0.1, 0.06, 0.07, 0.06, 0.05]
        u_bounds = [0.4, 0.4, 0.4, 1.0, 1.0, 1.0, 1.0]
        sampled_params = qmc.scale(sampled_params, l_bounds, u_bounds)
        # result = qmc.discrepancy(sampled_params)
        min_distance = 10e30
        opt_params = []
        for params in sampled_params:
            distance = self.fit_function(params)
            if distance < min_distance:
                min_distance = distance
                opt_params = params.tolist()
        return opt_params, min_distance

    def run_prediction(self):
        initial_param_values, param_range = self.init_parameters()
        peak_boundary_left = 0  # manually defined
        peak_boundary_right = 1

        tpeaks = [peak for peak in range(peak_boundary_left, peak_boundary_right)]
        anneal_func_with_params = partial(self.optimize, initial_param_values, param_range)

        with Pool(processes=os.cpu_count() - 1) as pool:
            results = pool.map_async(anneal_func_with_params, tpeaks)
            pool.close()
            pool.join()

        opt_results = list(results.get())

        # getting optimal result from the sorted list of derived results in ascending order
        opt_result = sorted(opt_results, key=lambda x: x[1].fun)[0]
        optimizer_instance = opt_result[0]
        opt_params = opt_result[1].x

        for k, v in optimizer_instance.__dict__.items():
            self.__dict__[k] = v

        return opt_result, opt_params

    def run_calibration(self):
        initial_param_values, param_ranges = self.init_parameters()
        _, opt_result = self.optimize(initial_param_values, param_ranges, self.tpeak_bias_aux)
        opt_params = list(opt_result.x)  # final bunch of optimal values
        return opt_result, opt_params

    def fit_one_outbreak(self, predict=False, sample_size=None, bootstrap_mode=False):
        """
        An outbreak fitting function
        """
        self.calib_data_weekly = self.df_data_weekly[:sample_size]
        self.data_weights = self._get_data_weights(self.df_data_weekly, self.sigma)
        self.res2_list = dtf.find_residuals_weighted_list(self.df_data_weekly, self.groups, self.data_weights)

        if predict:
            opt_result, opt_params = self.run_prediction()
            opt_result_fun = opt_result[1].fun

            print("Values of optimized fit function: ", opt_result_fun)
            print("Optimal predicted peak index: ", self.tpeak_bias_aux)

        else:
            opt_result, opt_params = self.run_calibration()
            # opt_params, opt_distance = self.optimize_lhs()
            # print("Optimal distance: ", opt_distance)

        exposed_opt_list, lambda_opt_list, a_opt = pr.get_opt_params(opt_params,
                                                                     self.incidence_type,
                                                                     self.age_groups,
                                                                     self.strains)
        total_recovered = self.df_simul_weekly.sum().tolist()

        epid_params = {'exposed': exposed_opt_list,
                       'lambda': lambda_opt_list,
                       'a': a_opt,
                       'delta': self.delta,
                       'total_recovered': total_recovered,
                       'R2': self.R_square_list}

        print("Final optimal parameters: ")
        print("exposed: ", exposed_opt_list)
        print("lambda: ", lambda_opt_list)
        print("a: ", a_opt)
        print("R2: ", self.R_square_list)
        print("Recovered: ", total_recovered)

        return epid_params
