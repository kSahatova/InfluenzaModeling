import os.path as osp
from datetime import datetime

from utils.experiment_setup import ExperimentalSetup
from data.data_preprocessing import get_contact_matrix, prepare_calibration_data

from visualization.visualization import plot_fitting
from utils.utils import get_config, save_results


def main():
    config = get_config('config.yaml')

    path = config['data_path']
    exposure_year = config['year']
    contact_matrix_path = config['contact_matrix_path']
    mu = config['percent_protected']
    sigma = config['sigma']

    age_groups = config['age_groups']
    strains = config['strains']

    output_folder = config['output_folder']
    city_eng = config['city']
    city = "_".join(city_eng.lower().split())

    incidence = config['INCIDENCE_TYPE']
    data_detail = config['DATA_DETAIL']
    model_detail = config['MODEL_DETAIL']
    predict = config['PREDICT']

    # data will be grouped if model is grouped (GMDD and DMGD will be run as GMGD)
    if not data_detail or not model_detail:
        incidence = 'total'

    contact_matrix = get_contact_matrix(contact_matrix_path) \
        if incidence not in ['strain', 'total'] else [[6.528]]
    epidemic_data, pop_size = prepare_calibration_data(path, incidence, age_groups, strains, exposure_year)

    experiment_setter = ExperimentalSetup(incidence, age_groups, strains, contact_matrix, pop_size, mu, sigma)
    optimizer = experiment_setter.setup_experiment(epidemic_data, model_detail)

    opt_parameters = optimizer.fit_one_outbreak()

    output_dir = osp.join(output_folder, 'data', incidence)
    model_fit = optimizer.df_simul_weekly.dropna(axis=1)
    incidence_data = optimizer.df_data_weekly.loc[:, model_fit.columns]
    calibration_data = optimizer.calib_data_weekly.loc[:, model_fit.columns]
    r_squared = optimizer.R_square_list

    results_dir = f'{incidence}_{exposure_year}_{datetime.now().strftime("%Y_%m_%d_%H_%M")}_mu_{mu}_sigma_{sigma}'
    full_path = osp.normpath(osp.join(output_dir, 'ysc_paper', results_dir))
    save_results(opt_parameters, model_fit, calibration_data, incidence_data, full_path)

    file_path_fitting = osp.join(full_path, f'fit_{incidence}_{city}_{exposure_year}.png')
    plot_fitting(incidence_data, calibration_data, model_fit, city_eng,
                 exposure_year, file_path_fitting, r_squared=r_squared, predict=predict)


if __name__ == '__main__':
    main()
