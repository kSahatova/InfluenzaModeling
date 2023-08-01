from itertools import product

from .base_optimizer import BaseOptimizer


class StrainModelOptimizer(BaseOptimizer):
    def __init__(self, model, data_obj, model_detail, sigma):
        super().__init__(model, data_obj, model_detail, sigma)
        self.age_groups = model.age_groups if self.incidence_type != 'strain' else ['total']
        self.groups = [i[1] + '_' + i[0] if i[0] != 'total' else i[1]
                       for i in list(product(self.age_groups, self.strains))] \
            if model_detail else ['Все']
        # groups are following: ['A(H1N1)pdm09_0-14', 'A(H3N2)_0-14', 'B_0-14',
        # 'A(H1N1)pdm09_15 и ст.', 'A(H3N2)_15 и ст.', 'B_15 и ст.'] [order of groups matters]

    def fit_function(self, k):
        age_groups_num = len(self.age_groups)
        strains_num = len(self.strains)
        n = strains_num * age_groups_num

        exposed_list = []

        for i in range(age_groups_num):
            sum_exposed = sum(k[i * strains_num:i * strains_num + strains_num])

            if sum_exposed < 1:
                temp = [k[i * strains_num + m] for m in range(strains_num)]
                temp.append(1 - sum_exposed)
            else:
                temp = [k[i * strains_num + m] / sum_exposed for m in range(strains_num)]
                temp.append(0)
            exposed_list.append(temp)

        lam_list = list(k[n:n + strains_num])
        a = list(k[-age_groups_num:])

        dist2_list = self.find_model_fit(exposed_list, lam_list, a)
        dist2 = sum(dist2_list)

        return dist2

    def calculate_population_immunity(self, exposed_list, a):
        for i in range(0, len(exposed_list)):
            self.population_immunity[i] = [
                (imm + (exposed_list[i] * self.active_population * a[0])) / self.active_population
                for imm in self.population_immunity[i]]

        return self.population_immunity
