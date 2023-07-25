from typing import List
from pandas import DataFrame
from dataclasses import dataclass

from models.BR_model import BRModel

from optimizers.optimizer_age import AgeModelOptimizer
from optimizers.optimizer_strain import StrainModelOptimizer


@dataclass
class ExperimentalSetup:
    incidence_type: str
    age_groups: List[str]
    strains: List[str]
    contact_matrix: object
    pop_size: float
    mu: float

    def get_model_and_optimizer(self):
        model, optimizer = BRModel, None
        if self.incidence_type in ['age-group', 'total']:
            optimizer = AgeModelOptimizer
        elif self.incidence_type in ['strain_age-group', 'strain']:
            optimizer = StrainModelOptimizer

        return model, optimizer

    def setup_model(self, model):
        return model(self.contact_matrix, self.pop_size, self.mu,
                     self.incidence_type, self.age_groups, self.strains)

    def setup_optimizer(self, optimizer, model, data, model_detailed):
        return optimizer(model, data, model_detailed)

    def setup_experiment(self, data: DataFrame, model_detailed: bool):
        model, optimizer = self.get_model_and_optimizer()
        model_obj = self.setup_model(model)
        optimizer_obj = self.setup_optimizer(optimizer, model_obj, data, model_detailed)
        return optimizer_obj
