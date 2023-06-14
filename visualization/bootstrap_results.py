import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import StrMethodFormatter
from sklearn.metrics import r2_score
import os.path as osp


def get_colormap(n, name='hsv'):
    """Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.
    References https://stackoverflow.com/questions/14720331/how-to-generate-random-colors-in-matplotlib"""
    return plt.cm.get_cmap(name, n)


def get_rand_colors(amount):
    colors_ = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    return colors_(amount)


def plot_95CI_bootstrapped_curves(df_weekly, bootstrapped_curves, output_dir="./"):
    """Plots 95% bootstrapped curves based on the value of determination coefficient"""
    column_titles = df_weekly.columns
    colormap = get_rand_colors(len(column_titles))
    for i_color, title in enumerate(column_titles):
        m, n = df_weekly[title].index.min(), df_weekly[title].index.max()

        r2_values = [r2_score(df_weekly[title], curve[title][m:n + 1]) for curve in bootstrapped_curves]

        lhs, rhs = np.percentile(r2_values, [5, 95])

        for i, curve in enumerate(bootstrapped_curves):
            if lhs <= r2_values[i] <= rhs:
                plt.plot(curve[title][m:n + 1].index, curve[title][m:n + 1], color=colormap[i_color], alpha=0.5)

        plt.plot(df_weekly[title].index, df_weekly[title], 'o', color=colormap[i_color], label=f"{title} data")

    plt.xlabel('Time, weeks', fontsize=13)
    plt.ylabel('Incidence, cases', fontsize=13)
    plt.title("95% CI bootstrapped curves", fontsize=13)

    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    plt.legend()

    if output_dir:
        plt.savefig(osp.join(output_dir, "plot_95CI_bootstrapped_curves.png"), dpi=300)

    plt.show()


class EmpiricalDistributionPlot:
    """Class for plotting empirical distributions of the epidemic parameters"""

    def __init__(self, plt, name, values=None):
        self.name = name
        self.plt = plt
        self.values = [] if values is None else values

    def plot_distribution(self):
        self.plt.hist(self.values)

        plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.2f}'))  # 2 decimal places

        locs, _ = plt.yticks()

        plt.yticks(locs, np.round(locs / len(self.values), 3))

        self.plt.title(
            '\n95% CI: {}\n'.format(np.round(np.percentile(self.values, [5, 95]), 4)) +
            f'CV={np.round(np.std(self.values), 4)}, ' +
            f'mean={np.round(np.mean(self.values), 4)}, ' +
            f'median={np.round(np.median(self.values), 4)}')

        self.plt.xlabel(self.name)
        self.plt.ylabel("Density")

    def draw_mean(self, **kwargs):
        self.plt.axvline(np.mean(self.values), **kwargs)

    def draw_median(self, **kwargs):
        self.plt.axvline(np.median(self.values), **kwargs)

    def save_to(self, path, filetype, **kwargs):
        self.plt.savefig(osp.join(path, f"{self.name}.{filetype}"), **kwargs)


def plot_empirical_distributions(df_samples_mapped, output_dir="./", **keys_titles):
    for name, dataframe in df_samples_mapped.items():
        plot_empirical_distribution(dataframe, name, output_dir, **keys_titles)


def plot_empirical_distribution(df_sample, name, output_dir="./", **keys_titles):
    for key in keys_titles.keys():
        dist_plot = EmpiricalDistributionPlot(plt, f"{name}; parameter: {keys_titles[key]}", np.array([val for val in df_sample[key]]))
        dist_plot.plot_distribution()
        dist_plot.draw_mean(color="black", linestyle="--")
        dist_plot.draw_median(color="grey", linestyle="--")

        if output_dir:
            dist_plot.save_to(output_dir, "png", dpi=300)

        dist_plot.plt.show()


def restructurate_parameters_df(df_samples_raw, columns=None):
    if columns is None:
        columns = ["total"]

    df_mapping = dict()

    def transform_value(obj, index):
        if isinstance(obj, list):
            if len(obj)>index:
                return obj[i]
            return obj[0]
        return obj

    for i, key_column in enumerate(columns):
        df_sample_i = df_samples_raw.copy()
        for column in df_sample_i.columns:
            df_sample_i[column] = df_sample_i[column].map(lambda v: transform_value(v,i))
        df_mapping[key_column] = df_sample_i
        print(df_sample_i)

    return df_mapping