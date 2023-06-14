from typing import List
from dataclasses import dataclass
from typing import Optional,Any
from pandas import DataFrame

from models import BR_model
from models.BR_model import AgeModel

from optimizers.base_optimizer import BaseOptimizer
from optimizers.optimizer_age import AgeModelOptimizer


@dataclass
class ExperimentalSetup:
    incidence_type: str
    age_groups: List[str]
    strains: List[str]
    contact_matrix: object
    suspected_pop_size: float

    def get_model_and_optimizer(self):
        model, optimizer = None, None
        if self.incidence_type == 'age-group':
            model = AgeModel
            optimizer = AgeModelOptimizer

        return model, optimizer

    def setup_model(self, model):
        return model(self.contact_matrix, self.suspected_pop_size, self.incidence_type,
                     self.age_groups, self.strains)

    def setup_optimizer(self, optimizer, model, data, model_detailed):
        return optimizer(model, data, model_detailed)

    def setup_experiment(self, data: DataFrame, model_detailed: bool):
        model, optimizer = self.get_model_and_optimizer()
        model_obj = self.setup_model(model)
        optimizer_obj = self.setup_optimizer(optimizer, model_obj, data, model_detailed)
        return optimizer_obj
