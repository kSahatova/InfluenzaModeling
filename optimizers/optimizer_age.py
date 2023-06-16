from .base_optimizer import BaseOptimizer


class AgeModelOptimizer(BaseOptimizer):
    def __init__(self, model, data_obj, model_detail):
        super().__init__(model, data_obj, model_detail)
        self.groups = self.age_groups if model_detail else ['Все']
        self.age_group_ind = 1

    def fit_function(self, k):
        age_groups_num = len(self.age_groups)
        exposed_list = []  # list(k[:age_groups_num])

        for item in k[:age_groups_num]:
            exposed_list.append([item, 1 - item])

        '''for item in k[:age_groups_num]:
            exposed_list.append(item)
            exposed_list.append(1-item)
        '''
        '''
        for item in k[:age_groups_num]:
            exposed_list.append(1-item)
        '''
        lam_list = [k[age_groups_num]]

        if self.a_detail:
            a = [k[age_groups_num + 1 + i] for i in range(age_groups_num)]
        else:
            a = [k[age_groups_num + 1]]  # Default position for a value

        dist2_list = self.find_model_fit(exposed_list, lam_list, a)
        dist2 = sum(dist2_list)

        return dist2

    def calculate_population_immunity(self, exposed_list, a):
        pass

    '''def update_delta(self):
        peak_indices_real, _ = dtf.max_elem_indices(self.df_data_weekly, self.groups)
        peak_indices_model, peak_values_model = dtf.max_elem_indices(self.df_simul_weekly, self.groups)

        peak_indices_model = [(peak_index + self.tpeak_bias_aux) for peak_index in peak_indices_model]
        delta_list_prelim = [peak_index_model - peak_index_real
                             for peak_index_model, peak_index_real in
                             zip(peak_indices_model, peak_indices_real)]
        self.delta = delta_list_prelim[self.age_group_ind]

    def fit_one_outbreak(self, predict=False, sample_size=None, bootstrap_mode=False):
        """
        An outbreak fitting function
        """
        self.calib_data_weekly = self.df_data_weekly[:sample_size]
        self.bootstrap_mode = bootstrap_mode

        self.data_weights = self._get_data_weights(self.df_data_weekly)
        self.res2_list = dtf.find_residuals_weighted_list(self.df_data_weekly, self.groups, self.data_weights)

        opt_params = []
        min_distance = 10e11

        for i in range(len(self.age_groups)):
            self.age_group_ind = i
            if predict:
                opt_result_cur, opt_params_cur = self.run_prediction()
                opt_result_fun = opt_result_cur[1].fun
                opt_peak = self.tpeak_bias_aux
                print("Optimal predicted peak index: ", opt_peak)
            else:
                opt_result_cur, opt_params_cur = self.run_calibration()
                opt_result_fun = opt_result_cur.fun

            if opt_result_fun < min_distance:
                min_distance = opt_result_fun
                opt_params = opt_params_cur

        print("Values of optimized fit function: ", min_distance)

        exposed_opt_list, lambda_opt_list, a_opt = param_rangef.get_opt_params(opt_params,
                                                                               self.incidence_type,
                                                                               self.age_groups,
                                                                               self.strains,
                                                                               self.a_detail)
        epid_params = {'exposed': exposed_opt_list,
                       'lambda': lambda_opt_list,
                       'a': a_opt,
                       'delta': self.delta,
                       'total_recovered': self.model.total_recovered,
                       'R2': self.R_square_list}

        print("Final optimal parameters: ")
        print("exposed: ", exposed_opt_list)
        print("lambda: ", lambda_opt_list)
        print("a: ", a_opt)
        print("R2: ", self.R_square_list)
        print("Recovered: ", self.model.total_recovered)

        return epid_params'''

