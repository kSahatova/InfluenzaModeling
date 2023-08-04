import os.path as osp
from datetime import datetime
from sklearn.metrics import r2_score

from utils.experiment_setup import ExperimentalSetup
from data.data_preprocessing import get_contact_matrix, prepare_calibration_data

from visualization.visualization import plot_fitting
from utils.utils import get_config, restore_fit_from_params


def main(output_dir):
    config = get_config('config.yaml')

    path = config['data_path']
    exposure_year = config['year']
    contact_matrix_path = config['contact_matrix_path']
    mu = config['percent_protected']
    sigma = config['sigma']

    age_groups = config['age_groups']
    strains = config['strains']

    city_eng = config['city']
    city = "_".join(city_eng.lower().split())

    incidence = config['INCIDENCE_TYPE']
    predict = config['PREDICT']

    contact_matrix = get_contact_matrix(contact_matrix_path) \
        if incidence not in ['strain', 'total'] else [[6.528]]
    _, pop_size = prepare_calibration_data(path, incidence, age_groups, strains, exposure_year)

    calib_data, simul_data, orig_data, r_squared = \
        restore_fit_from_params(contact_matrix, pop_size, incidence,
                                age_groups, strains, mu, sigma, output_dir)

    r2_plain = r2_score(calib_data, simul_data.iloc[calib_data.index], multioutput='raw_values').tolist()

    file_path_fitting = osp.join(output_dir, f'fit_{incidence}_{city}_{exposure_year}_regenerated.png')
    plot_fitting(orig_data, calib_data, simul_data, city_eng, exposure_year,
                 file_path_fitting, r_squared=None, r_squared_plain=r2_plain, predict=predict)


if __name__ == '__main__':
    data_dir = 'output/data/strain/ysc_paper/strain_2015_2023_07_24_12_05_mu_0.2_sigma_2.5'
    main(data_dir)
