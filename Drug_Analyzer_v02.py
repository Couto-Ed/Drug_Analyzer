import collections.abc as c  # these are _classes_, not _types_.
from dataclasses import dataclass
from numbers import Real  # again, a class, for typing we'll use float.
from typing import Any, Iterable, Sequence  # these are _types_.
#    You can just use List for everything; I like to split hairs.
import sys

sys.tracebacklimit = 0  # handling error message


@dataclass(frozen=True)  # I think they should be frozen by default.
class PillRow:
    pill_id: str
    series: str
    weight: float
    active: float
    impure: float

    @staticmethod
    def from_data(data: Any) -> "PillRow":
        if isinstance(data, PillRow):
            return data
        try:
            if not isinstance(data, c.Sized) and isinstance(data, c.Iterable):
                raise ValueError("Could not parse data.")
            if len(data) != 4:
                raise ValueError(f"Four columns needed; found {len(data)}.")
            pill_id, pill_weight, active_substance, impurities = data
            if not isinstance(pill_id, str):
                raise ValueError(f"Column One must be the pill id. Not {pill_id}")
            series_id = pill_id.split('-')[0]
            if len(series_id) != 3:
                raise ValueError(f"Could not parse series id from the pill id. {pill_id}")
            if not isinstance(pill_weight, Real):
                raise ValueError("Invalid pill weight.")
            if not isinstance(active_substance, Real):
                raise ValueError("Invalid active-substance weight.")
            if not isinstance(impurities, Real):
                raise ValueError("Invalid impurities weight.")
            if pill_weight <= 0 or active_substance <= 0 or impurities <= 0:
                raise ValueError("The values of pill weight, active substance or impurities must not be zero")
            return PillRow(pill_id=pill_id,
                           series=series_id,
                           weight=float(pill_weight),
                           active=float(active_substance),
                           impure=float(impurities))
        except AssertionError as ae:
            raise ValueError(ae)

    def to_list(self) -> list:
        return [self.pill_id, self.weight, self.active, self.impure]


class DrugAnalyzer:
    def __init__(self, *datas: Iterable[Sequence]):  # taking *args will make __add__ easier to write.
        self._data = [PillRow.from_data(pill)
                      for data in datas
                      for pill in data]
        self.data = [pill.to_list() for pill in self._data]

    def __add__(self, data):
        return DrugAnalyzer(self._data, [data])  # that's what all the above work was for!

    def verify_series(self,
                      series_id: str,
                      act_subst_wgt: float,
                      act_subst_rate: float,
                      allowed_imp: float) -> bool:
        pills = [p for p in self._data if p.series == series_id]
        if not pills:
            raise ValueError(f'There is no {series_id} series in database')
        else:
            num_pills = len(pills)
            target_active = act_subst_wgt * num_pills
            margin_active = target_active * act_subst_rate
            actual_active = sum(p.active for p in pills)
            max_impure = allowed_imp * sum(p.weight for p in pills)
            actual_impure = sum(p.impure for p in pills)
            return (abs(target_active - actual_active) <= margin_active) and (actual_impure <= max_impure)


my_drug_data = [
    ['L01-10', 1007.67, 102.88, 1.00100],
    ['L01-06', 996.42, 99.68, 2.00087],
    ['G02-03', 1111.95, 125.04, 3.00100],
    ['G03-06', 989.01, 119.00, 4.00004]
]
# my_drug_data = [0,0,0]

my_analyzer = DrugAnalyzer(my_drug_data)
print(my_analyzer.data)

my_new_analyzer = my_analyzer + ['G03-01', 789.01, 129.00, 0.00008]
print(my_new_analyzer.data)

print(my_analyzer.verify_series(series_id='L01', act_subst_wgt=100, act_subst_rate=0.05, allowed_imp=0.001))
