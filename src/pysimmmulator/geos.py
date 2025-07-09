from typing import Optional
import numpy as np

class geos:
    def __init__(self, total_population:int, random_seed:int=42):
        self.total_population = total_population
        self.rng = self._create_random_factory(seed=random_seed)

    def __call__(self, geo_specs:Optional[dict]=None, universal_scale:Optional[float]=1.0, count:int=250):
        if geo_specs is not None: return self.create_geos(geo_specs=geo_specs, universal_scale=universal_scale)
        return self.create_random_geos(count=count)

    def _create_random_factory(self, seed: int) -> np.random.Generator:
        """Internal helper that serves as a central random number generator, 
        and can be initialized with a seed to enable testing.
        Args:
    		seed (int): Optional seed value for random number generation
        Returns:
    		rng (np.random.Generator): random number generator"""
        rng = np.random.default_rng(seed=seed)
        return rng

    def _invent_geos(self, name_length:int=12, count:int=250):
        geo_specs = {}
        pop_pcts = self.rng.beta(1.069, 20.0, size=count)
        pop_pcts = pop_pcts * (1/pop_pcts.sum())
        pop_pcts[0] = pop_pcts[0] + (1 - pop_pcts.sum())
        pop_pcts_list = pop_pcts.tolist()
        while len(geo_specs) < count: geo_specs.update({self._namer(length=name_length):{"pop_pct":pop_pcts_list.pop()}})
        return geo_specs
    
    def _namer(self, length:int=10, source:str="ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
        name = ""
        for i in self.rng.integers(0, len(source) - 1, size=length):
            name += source[i]
        return name

    def create_geos(self, geo_specs: dict, universal_scale:float=1.0):
        geo_details = {}
        for geo_name, geo_mod in geo_specs.items():
            bias = geo_mod.get("loc", 0.0)
            scale = geo_mod.get("scale", universal_scale)
            geo_details.update({geo_name: {"pop_pct": (1/len(geo_specs) * abs(self.rng.normal(bias, scale, size=1)[0]))*self.total_population}})
        return geo_details

    def create_random_geos(self, count:int=250):
        geo_details = self._invent_geos(name_length=12, count=count)
        for geo in geo_details.keys(): geo_details[geo] = int(geo_details[geo]["pop_pct"] * self.total_population)
        return geo_details


def distribute_to_geos(mmm_inputs: 'pd.Dataframe', geo_details: dict, random_seed:int=42, dist_spec: tuple[float, float]=(0.0, 0.25), cost_spec: tuple[float, float]=(0.0, 0.25), perf_spec: tuple[float, float]=(0.0, 0.15)) -> 'pd.DataFrame':
    """Distributes MMM data to supplied geographies. Allows randomization in the scale of the distributon"""
    geo_dataframes = []
    total_population: int = sum(values(geo_details))
    rng = np.random.default_rng(seed=random_seed)
    for geo_name, geo_pop in geo_details.items():
        pop_pct = geo_pop / total_population
        geo_prop = pop_pct * rng.normal(loc=pop_pct * dist_spec[0], scale=dist_spec[1])
        geo_dataframe = mmm_inputs.copy()
        geo_dataframe["geo_name"] = geo_name
        geo_dataframe *= geo_prop
        if any(cost_spec) != 0.0: geo_dataframe[[col for col in geo_data.columns if 'impressions' or 'clicks' in col]] *= rng.normal(loc=pop_pct * cost_spec[0], scale=cost_spec[1])
        if any(perf_spec) != 0.0: geo_dataframe["total_revenue"] *= rng.normal(loc=pop_pct * cost_spec[0], scale=cost_spec[1])
        geo_dataframes.append(geo_dataframe)
    final = pd.concat(geo_dataframes, axis=0)
    final[[col for col in final.columns if 'impressions' or 'clicks' in col]] *= mmm_inputs[[col for col in mmm_inputs.columns if 'impressions' or 'clicks' in col]].sum() / final[[col for col in final.columns if 'impressions' or 'clicks' in col]].sum()
    final["total_revenue"] *= mmm_inputs[[col for col in mmm_inputs.columns if 'impressions' or 'clicks' in col]].sum() / final[[col for col in final.columns if 'impressions' or 'clicks' in col]].sum()
    return final

