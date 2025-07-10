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


def distribute_to_geos(mmm_input: 'pd.Dataframe', geo_details: dict, random_seed:int=42, dist_spec: tuple[float, float]=(0.0, 0.25), media_cost_spec: tuple[float, float]=(0.0, 0.069), perf_spec: tuple[float, float]=(0.0, 0.069)) -> 'pd.DataFrame':
    """Distributes MMM data to supplied geographies. Allows randomization in the scale of the distributon"""
    mmm_input = mmm_input.dropna()
    geo_dataframes = []
    total_population: int = sum(geo_details.values())
    rng = np.random.default_rng(seed=random_seed)
    media_cols = [w for w in mmm_input.columns if "impressions" in w or "clicks"in w]
    for geo_name, geo_pop in geo_details.items():
        pop_pct = geo_pop / total_population
        geo_prop = pop_pct * (1 + abs(rng.normal(loc=pop_pct * dist_spec[0], scale=dist_spec[1])))
        geo_dataframe = mmm_input.copy()
        geo_dataframe *= geo_prop
        if any(media_cost_spec) != 0.0: geo_dataframe[media_cols] *= (1 + abs(rng.normal(loc=pop_pct * media_cost_spec[0], scale=media_cost_spec[1])))
        if any(perf_spec) != 0.0: geo_dataframe["total_revenue"] *= (1 + abs(rng.normal(loc=pop_pct * media_cost_spec[0], scale=media_cost_spec[1])))
        geo_dataframe["geo_name"] = geo_name
        geo_dataframes.append(geo_dataframe)
    final = pd.concat(geo_dataframes, axis=0)
    final = final.reset_index().set_index(["geo_name","date"])
    final[media_cols] *= mmm_input[media_cols].sum() / final[media_cols].fillna(0.0).sum()
    final["total_revenue"] *= mmm_input["total_revenue"].sum() / final["total_revenue"].sum()
    final[["total_revenue"] + media_cols] = final[["total_revenue"] + media_cols].round(0)
    return final
