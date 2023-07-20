import os.path as osp
from typing import Dict, Any, List


from utils.experiment_setup import ExperimentalSetup
from data.data_preprocessing import prepare_calibration_data

from utils.utils import get_config
from data.data_preprocessing import get_contact_matrix
from models.BR_model_test import BRModel


def get_data_and_model(mu, incidence):
    config = get_config('../config.yaml')

    path = config['data_path']
    exposure_year = config['year']
    contact_matrix_path = config['contact_matrix_path']

    age_groups = config['age_groups']
    strains = config['strains']

    contact_matrix = get_contact_matrix('../'+contact_matrix_path)
    epid_data, pop_size = prepare_calibration_data('../'+path, incidence, age_groups, strains, exposure_year)

    model = BRModel(contact_matrix, pop_size, mu, incidence, age_groups, strains)

    return epid_data, model, exposure_year


def prepare_exposed_list(incidence, exposed_list):
    if incidence == 'age-group':
        exposed_cor = []
        for item in exposed_list:
            exposed_cor.append([item, 1 - item])

    elif incidence == 'strain':
        sum_exposed = sum(exposed_list)
        if sum_exposed < 1:
            exposed_list.append(1 - sum_exposed)
        else:
            exposed_list = [item / sum_exposed for item in exposed_list]
            exposed_list.append(0)
    return exposed_list


