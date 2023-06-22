from .base_optimizer import BaseOptimizer


class StrainModelOptimizer(BaseOptimizer):
    def __init__(self, model, data_obj, model_detail):
        super().__init__(model, data_obj, model_detail)
        self.groups = self.strains if model_detail else ['Все']

    def fit_function(self, k):
        age_groups_num = len(self.age_groups)
        strains_num = len(self.strains)

        sum_exposed = sum([k[i][j] for i in range(age_groups_num)
                           for j in range(strains_num)])
        exposed_list = []

        for i in range(age_groups_num):
            if sum_exposed < 1:
                temp = [k[i][m] for m in range(strains_num)]
                temp.append(1-sum_exposed)
            else:
                temp = [k[i][m]/sum_exposed for m in range(strains_num)]
                temp.append(0)
            exposed_list.append(temp)

        # todo: finish indexing
        lam_list = [k[i + len(self.strains)] for i in range(0, len(self.strains))]

        a = k[2 * len(self.strains)]  # Default position for a value

        dist2_list = self.find_model_fit(exposed_list, lam_list, a)
        dist2 = sum(dist2_list)

        return dist2

    def calculate_population_immunity(self, exposed_list, a):
        for i in range(0, len(exposed_list)):
            self.population_immunity[i] = [
                (imm + (exposed_list[i] * self.active_population * a[0])) / self.active_population
                for imm in self.population_immunity[i]]

        return self.population_immunity
