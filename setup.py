from setuptools import setup, find_packages

setup(name='uq_influenza_modeling',
      version='1.0.0',
      description='A project represents a framework for influenza modeling '
                  'using Baroyan-Rvachev model with simulated annealing and '
                  'L-BFGS-B optimization techniques. Uncertainty quantification '
                  'is also enabled.',
      packages=find_packages(),
      install_requires=['matplotlib',
                        'numpy',
                        'pandas',
                        'PyYAML',
                        'plotly',
                        'dash',
                        'dash_bootstrap_components',
                        'scikit-learn',
                        'scipy',
                        'simanneal>=0.5.0',
                        'statsmodels',
                        'sklearn',
                        'tqdm',
                        'pathos'])
