import csv
import numpy as np


def time_string(seconds):
    """Returns time in seconds as a string formatted HHHH:MM:SS."""
    s = int(round(seconds))  # round to the nearest second
    h, s = divmod(s, 3600)  # get hours and remainder
    m, s = divmod(s, 60)  # split remainder into minutes and seconds
    return '%4i:%02i:%02i' % (h, m, s)


def max_elem_index(my_list):
    # returns the index of a highest incidence
    max_value = max(my_list)
    max_index = my_list.index(max_value)
    return max_index


def max_elem_indices(df, groups):
    # returns the index of a highest incidence
    max_values_list = []
    max_indices_list = []

    for group in groups:
        my_list = list(df[group])
        max_value = max(my_list)
        max_values_list.append(max_value)
        max_indices_list.append(my_list.index(max_value))

    return max_indices_list, max_values_list


def calculate_dist_squared_weighted_list(df_data, df_simul, groups, delta, w):
    # x is real data, y is modeled curve
    # delta is the difference between the epidemic starts in real data and modeled curve

    sum_list = []
    sum_ww_list = []
    for group in groups:
        x = list(df_data[group])
        y = list(df_simul[group])

        sum = 0
        sum_ww = 0
        for i in range(delta, delta + len(x)):
            try:
                sum = sum + w[group][i - delta] * pow(x[i - delta] - y[i], 2)
                sum_ww = sum_ww + pow(x[i - delta] - y[i], 2)
            except IndexError as e:
                print(e)

        sum_list.append(sum)
        sum_ww_list.append(sum_ww)

    return sum_list, sum_ww_list


def find_residuals_weighted_list(df, groups, w):
    res_list = []
    for group in groups:
        res = 0
        data = list(df[group])
        mean = np.mean(data)
        for i in range(0, len(data)):
            res += w[group][i] * pow(data[i] - mean, 2)
        res_list.append(res)

    return res_list


def calculate_r_square(df_data_weekly, df_simul_weekly, groups, delta, weights):
    res2_list = find_residuals_weighted_list(df_data_weekly, groups, weights)

    dist2_list, dist2_ww_list = calculate_dist_squared_weighted_list(df_data_weekly,
                                                                     df_simul_weekly,
                                                                     groups,
                                                                     delta,
                                                                     weights)

    R_square_list = [1 - fun_val / res2 for fun_val, res2 in zip(dist2_list, res2_list)]

    return R_square_list
