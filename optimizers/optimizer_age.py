from .base_optimizer import BaseOptimizer


class AgeModelOptimizer(BaseOptimizer):
    def __init__(self, model, data_obj, model_detail):
        super().__init__(model, data_obj, model_detail)
        self.groups = self.age_groups if model_detail else ['Все']
        self.age_group_ind = 1

    def fit_function(self, k):
        age_groups_num = len(self.age_groups)
        exposed_list = []  # k[:age_groups_num]

        for item in k[:age_groups_num]:
            exposed_list.append([item, 1 - item])

        lam_list = [k[age_groups_num]]

        if self.a_detail:
            a = [k[age_groups_num + 1 + i] for i in range(age_groups_num)]
        else:
            a = [k[age_groups_num + 1]]  # Default position for a value

        dist2_list = self.find_model_fit(exposed_list, lam_list, a)
        dist2 = dist2_list[0]  # sum(dist2_list)

        return dist2

    def calculate_population_immunity(self, exposed_list, a):
        pass
