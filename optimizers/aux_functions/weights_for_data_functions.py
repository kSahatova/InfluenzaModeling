from . import data_functions as dtf


def getWeights4Data(df, model_group):
    weights = {}

    for subgroup in model_group:
        y = list(df[subgroup])
        w_general_list = [1]
        for i in range(len(y)):
            w_general_list.append(w_general_list[-1] / 1.0)  # 1.3

        peak_index = dtf.max_elem_index(y)

        w = []
        for i in range(len(y)):  # assigning values of w based on the distance from the peak
            w.append(w_general_list[abs(peak_index - i)])

        weights[subgroup] = w

    return weights
