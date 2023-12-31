from typing import List

# Msk 2017
# exposed_range = [(0.21, 0.27), (0.32, 0.37), (0.37, 0.42)]
# lam_range = [(0.07, 0.08), (0.07, 0.09), (0.07, 0.09)]
# a_range = (0.05, 0.3)


def set_parameters_range(incidence, a_detail=False):
    exposed_range = lam_range = a_range = None

    if incidence == "age-group":
        exposed_range = {
            "0-14": (0.004, 0.0055),  # (0.137,  0.139),
            "15 и ст.": (0.7828, 0.784)  # (0.84, 0.86)
        }
        lam_range = (0.29, 0.31)  # (0.290, 0.292)  # (0.03, 0.24)
        a_range = (0.1759, 0.177)  # (0.234, 0.236)
    elif incidence == "strain_age-group":
        exposed_range = {
            "0-14": {
                "A(H1N1)pdm09": (0.005, 0.9),
                "A(H3N2)": (0.005, 0.9),
                "B": (0.005, 0.9)
            },
            "15 и ст.": {
                "A(H1N1)pdm09": (0.005, 0.9),
                "A(H3N2)": (0.005, 0.9),
                "B": (0.005, 0.9)
            }
        }
        lam_range = {
            "A(H1N1)pdm09": (0.01, 0.3),
            "A(H3N2)": (0.01, 0.3),
            "B": (0.01, 0.3)
        }
        a_range = {
            "0-14": (0.0, 1.0),
            "15 и ст.": (0.0, 1.0)
        }
    elif incidence == "strain":
        exposed_range = {
            # 2010 
            "A(H1N1)pdm09": (0.005, 0.9),  # 2015 (0.3517, 0.3526),  # 2010 (0.82, 0.834),  # (0.54, 0.56),
            "A(H3N2)": (0.005, 0.9), # (0.8428, 0.844),  # (0.44,  0.459),   # (0.21, 0.22),
            "B": (0.005, 0.9), # (0.8912, 0.89135)  # (0.115, 0.116) # (0.6, 0.62),
            # 2015
            # "A(H1N1)pdm09": (0.05, 0.9),
            # "A(H3N2)": (0.05, 0.9),
            # "B": (0.05, 0.9)
        }
        lam_range = {
            '''"A(H1N1)pdm09": (0.01, 0.3),
            "A(H3N2)": (0.01, 0.3),
            "B": (0.01, 0.3)'''
            
            # 2010
            "A(H1N1)pdm09": (0.001, 0.3),  # (0.0809, 0.081),  # (0.13, 0.139), #  (0.189, 0.191),
            "A(H3N2)": (0.001, 0.3),  # (0.0041, 0.0042),  # (0.09, 0.1),  # (0.049, 0.051),
            "B": (0.001, 0.3),  # (0.00563, 0.005645)  # (0.07, 0.079)  # (0.196, 0.198)
            # 2015
            #"A(H1N1)pdm09": (0.005, 0.3),
            #"A(H3N2)": (0.001 , 0.3),
            #"B": (0.005, 0.3)

        }
        a_range = (0.0, 1.0)  # (0.43986, 0.44)  # (0.23, 0.238) #  (0.0, 1.0)  # 2010 - (0.11, 0.13)
    elif incidence == 'total':
        exposed_range = (0.005, 0.9)
        lam_range = (0.03, 0.3)  # (0.03, 0.24)
        a_range = (0.0, 1.0)
    params_range = []
    for item in [exposed_range, lam_range, a_range]:
        for param in unpack_parameter_values(item):
            params_range.append(param)
    return params_range


def unpack_parameter_values(parameter):
    if isinstance(parameter, tuple):
        yield parameter

    elif isinstance(parameter, dict):
        temp_list = []
        for item in list(parameter.values()):
            if isinstance(item, tuple):
                yield item
            elif isinstance(item, dict):  # nested dictionary
                for value in list(item.values()):
                    yield value
        return temp_list


def get_opt_params(K, incidence, age_groups, strains, a_detail=False):
    """
    Unpacks found parameters according to the given incidence type
    param K:

    """
    m, n = len(strains), len(age_groups)
    params = []

    if incidence == 'strain':
        params = [K[:m], K[m:2*m], [K[-1]]]
    elif incidence == 'age-group':
        params = [K[:n], [K[n]], K[n+1:] if a_detail else [K[-1]]]
    elif incidence == 'strain_age-group':
        params = [K[:m*n], K[m*n:m*n+m], K[-n:]]
    elif incidence == 'total':
        params = [[K[0]], [K[1]], [K[2]]]

    for i, item in enumerate(params):
        if not isinstance(item, List):
            params[i] = list(item)
    return params
