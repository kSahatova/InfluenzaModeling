from pandas import DataFrame
import numpy as np


import matplotlib.pyplot as plt
from matplotlib.colors import BASE_COLORS, TABLEAU_COLORS
from typing import List
from sklearn.metrics import r2_score


def plot_r0(r0: DataFrame, city: str, year: int, output_file: str):
    colors = list(TABLEAU_COLORS.keys()) + list(BASE_COLORS.keys())

    for i, r in enumerate(r0):
        plt.plot(year, r, 'o', color=colors[i])

    plt.title(f"{city}, {year}$-${year + 1}")
    plt.xlabel('Year')
    plt.ylabel('R0 value')
    plt.legend()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.show()


def plot_immune_population(population_immunity: DataFrame,
                           city: str, year: int, output_file: str):
    """Plots population immunity"""

    # labels = population_immunity.columns
    # for i in range(len(population_immunity)):
    #     plt.plot(population_immunity[i][:300])
    #     # plt.plot(population_immunity[i][:300], label=labels[i])

    colors = list(TABLEAU_COLORS.keys()) + list(BASE_COLORS.keys())

    for i, immun in enumerate(population_immunity):
        plt.plot(year, immun, 'o', color=colors[i])

    plt.title(f"{city}, {year}$-${year + 1}")
    plt.xlabel('Year')
    plt.ylabel('Immune population')
    plt.legend()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.show()


def plot_fitting(original_data: DataFrame,
                 calibration_data: DataFrame,
                 simulated_data: DataFrame,
                 city: str, year: int,
                 file_path: str = 'model_fit.png',
                 r_squared: List[float] = None,
                 predict: bool = False):
    """Plots model fit, data used for calibration and original data"""

    last_point_ind = original_data.index[-1] + 15

    ax = plt.figure(figsize=(10, 7)).add_subplot(111)
    colors = list(TABLEAU_COLORS.keys()) + list(BASE_COLORS.keys())
    labels = [item.replace('15 и ст.', '15+').replace('_', " ")
              for item in list(simulated_data.columns)]

    for i, column in enumerate(simulated_data.columns):
        if predict:
            ax.plot(original_data.loc[:, column], 'o', color='white',
                    markeredgecolor=colors[i], label=f'Original data ({labels[i]})')
            ax.plot(calibration_data.loc[:, column], 'o', color=colors[i],
                    label=f'Calibration data ({labels[i]})')
        else:
            ax.plot(original_data.loc[:, column], 'o', color=colors[i],
                    label=f'Calibration data ({labels[i]})')

        ax.plot(simulated_data.loc[:last_point_ind, column],
                label=f'Model fit ({labels[i]})', color=colors[i])
        if r_squared:
            plt.text(0.05, 0.6 - (i * 0.05), "$R^2$={}".format(round(r_squared[i], 2)),
                     fontsize=16, color=colors[i], horizontalalignment='left',
                     verticalalignment='center', transform=ax.transAxes)

    plt.title(f'{city}, {year}$-${year + 1}')
    plt.xlabel('Weeks')
    plt.ylabel('Incidence, cases')
    plt.legend()
    plt.savefig(file_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_bootstrapped_fitting(calib_data, orig_data, simulated_curve, bootstrapped_curves):

    ax = plt.figure(figsize=(10, 7)).add_subplot(111)
    n = calib_data.index[-1]
    last_point_ind = orig_data.index[-1] + 15

    labels = ['Bootstrapped curves' if i == 0 else None for i in range(len(bootstrapped_curves))]
    for label, bs_curve in zip(labels, bootstrapped_curves):
        ax.plot(bs_curve[:last_point_ind], c='gray', label=label)

    ax.plot(simulated_curve.index[:last_point_ind], simulated_curve[:last_point_ind],
            color='red', linewidth=1, label='Predicted curve')
    ax.plot(simulated_curve.index[:n+1], simulated_curve[:n+1],
            color='cyan', linewidth=1, label='Calibrated curve')

    ax.scatter(orig_data.index, orig_data, color='white', edgecolors='tab:blue', label='Original data')
    ax.scatter(calib_data.index, calib_data, label='Calibration data')
    ax.axvline(n, color='black', linestyle='dashed')
    plt.xlabel('Weeks')
    plt.ylabel('Incidence, cases')
    plt.legend()
    plt.savefig(f'./output/forecast_spb_{len(calib_data)}points.png', dpi=300)
    plt.show()


def plot_bootstrap_curves_w_ci(calibr_data, orig_data, simulated_curve,
                               bootstrapped_curves, output_fpath):

    ax = plt.figure(figsize=(10, 7)).add_subplot(111)

    m, n = orig_data.index[0], orig_data.index[-1]
    k = calibr_data.index[-1]

    r2_values = [r2_score(orig_data, curve[m:n + 1]) for curve in bootstrapped_curves]
    lhs, rhs = np.percentile(r2_values, [5, 95])

    labels = ['Bootstrapped curves' if i == 0 else None
              for i in range(len(bootstrapped_curves))]

    for label, bs_curve, r2_value in zip(labels, bootstrapped_curves, r2_values):
        if lhs <= r2_value <= rhs:
            ax.plot(bs_curve[:n], c='gray', label=label, alpha=0.6)

    ax.plot(simulated_curve.index[:n], simulated_curve[:n],
            color='red', linewidth=1, label='Predicted curve')
    ax.plot(simulated_curve.index[:k+1], simulated_curve[:k+1],
            color='cyan', linewidth=1, label='Calibrated curve')

    ax.scatter(orig_data.index, orig_data, color='white', edgecolors='tab:blue', label='Original data')
    ax.scatter(calibr_data.index, calibr_data, label='Calibration data')
    ax.axvline(k, color='black', linestyle='dashed')
    plt.xlabel('Weeks')
    plt.ylabel('Incidence, cases')
    plt.legend()
    plt.savefig(output_fpath, dpi=300)
    plt.show()
