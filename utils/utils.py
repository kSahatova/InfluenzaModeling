import os
import json
import yaml
import os.path as osp

import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Dict, Any, List

import matplotlib.colors as mcolors

from .experiment_setup import ExperimentalSetup


OUTPUT_DIR = r'output/data'
SIMULATED_DATA_FILE = 'model_fit.csv'
INCIDENCE_DATA_FILE = 'original_data.csv'
CALIBRATION_DATA_FILE = 'calibration_data.csv'
PARAMETERS_FILE = 'parameters.json'

COLORS = list(mcolors.TABLEAU_COLORS.keys()) + list(mcolors.BASE_COLORS.keys())


def get_config(config_path):
    with open(config_path, "r", encoding='utf8') as yamlfile:
        return yaml.load(yamlfile, Loader=yaml.FullLoader)


def save_results(parameters: Dict,
                 simulated_data: DataFrame,
                 calibration_data: DataFrame,
                 original_data: DataFrame,
                 full_path: str) -> None:

    os.makedirs(full_path, exist_ok=True)

    json_object = json.dumps(parameters, indent=4)
    with open(osp.join(full_path, PARAMETERS_FILE), 'w') as outfile:
        outfile.write(json_object)

    simulated_data.to_csv(osp.join(full_path, SIMULATED_DATA_FILE))
    original_data.to_csv(osp.join(full_path, INCIDENCE_DATA_FILE))
    calibration_data.to_csv(osp.join(full_path, CALIBRATION_DATA_FILE))

def save_epid_results(result: DataFrame,
                 epid_name: str,
                 age_groups: List[str],
                 strains: List[str],
                 full_path: str) -> None:

    prev_shape = result.shape
    if len(prev_shape) == 3:
        result = result.reshape(prev_shape[0] * prev_shape[1], prev_shape[2])

    if prev_shape[0] == 1 and prev_shape[1] != 1: # strain
        final_epid_data = pd.DataFrame(result.T, columns=strains)
    elif prev_shape[0] != 1 and prev_shape[1] == 1: # age-group
        final_epid_data = pd.DataFrame(result.T, columns=age_groups)
    elif prev_shape[0] != 1 and prev_shape[1] != 1: # total
        final_epid_data = pd.DataFrame(result.T, columns=["Total"])
    else:  # strain_age-group
        final_epid_data = pd.DataFrame(result.T, columns=[strain + "_" + age_group for strain in strains for age_group in age_groups])

    os.makedirs(full_path, exist_ok=True)
    # new_result = pd.DataFrame(result)
    final_epid_data = final_epid_data
    final_epid_data.to_csv(osp.join(full_path, epid_name))


def get_parameters(output_dir):
    with open(osp.join(output_dir, PARAMETERS_FILE), 'r') as f:
        params = json.load(f)

    exposed_list = params['exposed']
    lam_list = params['lambda']
    a_list = params['a']
    delta = params['delta']
    r_squared = params['R2']
    return exposed_list, lam_list, a_list, delta, r_squared


def get_exposed_ready_for_simulation(exposed_list: List[Any], incidence: str,
                                     age_groups: List[str], strains: List[str]):
    exposed_list_cor = []
    if incidence in ['strain_age-group', 'strain']:

        age_groups_num = len(age_groups) if incidence == 'strain_age-group' else 1
        strains_num = len(strains)

        for i in range(age_groups_num):
            sum_exposed = sum(exposed_list[i * strains_num:i * strains_num + strains_num])

            if sum_exposed < 1:
                temp = [exposed_list[i * strains_num + m] for m in range(strains_num)]
                temp.append(1 - sum_exposed)
            else:
                temp = [exposed_list[i * strains_num + m] / sum_exposed for m in range(strains_num)]
                temp.append(0)
            exposed_list_cor.append(temp)

    return exposed_list_cor


# TODO: rewrite the function to accept paths to files
def restore_from_saved_data(incidence: str):
    simul_data_path = f'{OUTPUT_DIR}/{incidence}/{SIMULATED_DATA_FILE}'
    simul_data = pd.read_csv(simul_data_path, index_col=0)

    orig_data_path = f'{OUTPUT_DIR}/{incidence}/{INCIDENCE_DATA_FILE}'
    orig_data = pd.read_csv(orig_data_path, index_col=0)

    calib_data_path = f'{OUTPUT_DIR}/{incidence}/{CALIBRATION_DATA_FILE}'
    calib_data = pd.read_csv(calib_data_path, index_col=0)

    return calib_data, simul_data, orig_data


def restore_fit_from_params(contact_matrix: object, pop_size: float, incidence: str,
                            age_groups: List[str], strains: List[str], mu: float,
                            output_dir: str):

    factory = ExperimentalSetup(incidence, age_groups, strains, contact_matrix, pop_size, mu)
    model, _ = factory.get_model_and_optimizer()
    model_obj = factory.setup_model(model)

    exposed_list, lam_list, a_list, delta, r_squared = get_parameters(output_dir)
    exposed_list_cor = get_exposed_ready_for_simulation(exposed_list, incidence, age_groups, strains)

    calib_data_path = f'{output_dir}/{CALIBRATION_DATA_FILE}'
    calib_data = pd.read_csv(calib_data_path, index_col=0)

    orig_data_path = f'{output_dir}/{INCIDENCE_DATA_FILE}'
    orig_data = pd.read_csv(orig_data_path, index_col=0)

    model_obj.init_simul_params(exposed_list=exposed_list_cor, lam_list=lam_list, a=a_list)
    simul_data, immune_pop, susceptible, _ = model_obj.make_simulation()

    days_num = simul_data.shape[2]
    wks_num = int(days_num / 7.0)
    simul_weekly = [simul_data[0, :, i * 7: i * 7 + 7].sum(axis=1) for i in range(wks_num)]
    simul_data = pd.DataFrame(simul_weekly, columns=calib_data.columns)
    return calib_data, simul_data, orig_data, r_squared


