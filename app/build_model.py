import os.path as osp
from typing import Dict, Any, List


from utils.experiment_setup import ExperimentalSetup
from data.data_preprocessing import prepare_calibration_data

from utils.utils import get_config


def get_data_and_model(mu):
    config = get_config('../config.yaml')

    path = config['data_path']
    exposure_year = config['year']
    contact_matrix_path = config['contact_matrix_path']

    age_groups = config['age_groups']
    strains = config['strains']
    incidence = config['INCIDENCE_TYPE']

    contact_matrix = [[6.528]]
    epid_data, pop_size = prepare_calibration_data('../'+path, incidence, age_groups, strains, exposure_year)

    factory = ExperimentalSetup(incidence, age_groups, strains, contact_matrix, pop_size, mu)
    model, _ = factory.get_model_and_optimizer()
    model_obj = factory.setup_model(model)

    return epid_data, model_obj


def make_simulation():
    return


if __name__ == '__main__':
    get_data_and_model()
