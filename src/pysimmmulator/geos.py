from typing import Optional
import numpy as np
import pandas as pd

class geos:
    """Provides randomized generation of population subsets"""
    def __init__(self, total_population:int, random_seed:Optional[int]=None) -> None:
        self.total_population = total_population
        self.rng = self._create_random_factory(seed=random_seed)

    def __call__(self, geo_specs:Optional[dict]=None, universal_scale:Optional[float]=1.0, count:int=250) -> dict:
        """Distributes the total population to an array of geos, which can be specified or randomly generated

        Args:
            geo_specs (Optional[dict]): Geography names coupled with a dict of parameters for the normal distribution of that geos population (ie {"California":{"loc": 3.0, "scale": 0.5}}). 'loc' in this case is the multiplicative bias relative to an equal apportionment of the total population.
            universal_scale (Optional[flaot]): Scale parameter to be used universally for all geographies. Increased value means increased spread in the distribution of all geos
            count (int): in the absense of specified geographies, this is the number of geos to be created using the `create_random_geos` function.
        Returns:
            (dict[str, int]): Names of geogrphies and their generated population sizes."""
        if geo_specs is not None: return self.create_geos(geo_specs=geo_specs, universal_scale=universal_scale)
        return self.create_random_geos(count=count)

    def _create_random_factory(self, seed: int) -> np.random.Generator:
        """Internal helper that serves as a central random number generator, and can be initialized with a seed to enable testing.

        Args:
            seed (int): Optional seed value for random number generation
        Returns:
            rng (np.random.Generator): random number generator"""
        rng = np.random.default_rng(seed=seed)
        return rng

    def _invent_geos(self, name_length:int=12, count:int=250) -> dict:
        """Generate randomly names geographies with random population distribution using a `beta` distribution. This is the default generation method when no `geo_specs` is supplied to the `create_geos` function.

        Args:
            length (int): Length of the geography name string to be generated
            count (int): Number of geographies to be created
        Returns:
            geo_specs (dict): Dict of named geos and their beta distributed populations"""
        geo_specs: dict = {}
        pop_pcts = self.rng.beta(1.069, 20.0, size=count)
        pop_pcts = pop_pcts * (1/pop_pcts.sum())
        pop_pcts[0] = pop_pcts[0] + (1 - pop_pcts.sum())
        pop_pcts_list = pop_pcts.tolist()
        while len(geo_specs) < count: geo_specs.update({self._namer(length=name_length):{"pop_pct":pop_pcts_list.pop()}})
        return geo_specs
    
    def _namer(self, length:int=10, source:str="ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
        """Creates random names.

        Args:
            length (int): Length of the geography name string to be generated
            source (str): Letter or alphanumeric characters to draw from.
        Returns:
            name (str): Geo names of length `length` drawn from `source` characters"""
        name = ""
        for i in self.rng.integers(0, len(source) - 1, size=length):
            name += source[i]
        return name

    def create_geos(self, geo_specs: dict, universal_scale:float=1.0) -> dict:
        """Evaluates distirbution specification for each geo and returns a finalized mapping of geo names to generated population sizes.
        
        Args:
            geo_specs (Optional[dict]): Geography names coupled with a dict of parameters for the normal distribution of that geos population (ie {"California":{"loc": 3.0, "scale": 0.5}}). 'loc' in this case is the multiplicative bias relative to an equal apportionment of the total population.
            universal_scale (Optional[flaot]): Scale parameter to be used universally for all geographies. Increased value means increased spread in the distribution of all geos
        Returns:
            geo_details (dict): Geo names and their associated populations"""
        geo_details = {}
        for geo_name, geo_mod in geo_specs.items():
            bias = geo_mod.get("loc", 0.0)
            scale = geo_mod.get("scale", universal_scale)
            geo_details.update({geo_name: {"pop_pct": (1/len(geo_specs) * abs(self.rng.normal(bias, scale, size=1)[0]))*self.total_population}})
        return geo_details

    def create_random_geos(self, count:int=250) -> dict:
        """Generate randomly names geographies with random population distribution using a `beta` distribution.

        Args:
            count (int): Number of geographies to be created"""
        geo_details = self._invent_geos(name_length=12, count=count)
        for geo in geo_details.keys(): geo_details[geo] = int(geo_details[geo]["pop_pct"] * self.total_population)
        return geo_details


def distribute_to_geos(mmm_input: 'pd.DataFrame', geo_details: dict, random_seed:Optional[int]=None, dist_spec: tuple[float, float]=(0.0, 0.25), media_cost_spec: tuple[float, float]=(0.0, 0.069), perf_spec: tuple[float, float]=(0.0, 0.069)) -> 'pd.DataFrame':
    """Distributes MMM data to supplied geographies. Allows randomization in the scale of the distributon

    Args:
        mmm_input (pd.DataFrame): simulated MMM data that was generated as part of a prior process
        geo_details (dict): formulated dict or output of the `geos` creation call (ie `geos(count=50)`)
        random_seed (int): random seed for rng--if needed
        dist_spec (tuple[float, float]): Parameters to control the normal distribution function for populations of the geographies
        media_cost_spec (tuple[float, float]): Parameters to control the normal distribution function for allocation of media spend across geographies
        perf_spec (tuple[float, float]): Parameters to control the normal distribution function for allocation of media performance across geographies
    Returns:
        (pd.DataFrame): simulated MMM data divided into geographies as specified"""
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
        if any(perf_spec) != 0.0: geo_dataframe["total_revenue"] *= (1 + abs(rng.normal(loc=pop_pct * perf_spec[0], scale=perf_spec[1])))
        geo_dataframe["geo_name"] = geo_name
        geo_dataframes.append(geo_dataframe)
    final = pd.concat(geo_dataframes, axis=0)
    final = final.reset_index().set_index(["geo_name","date"])
    final[media_cols] *= mmm_input[media_cols].sum() / final[media_cols].fillna(0.0).sum()
    final["total_revenue"] *= mmm_input["total_revenue"].sum() / final["total_revenue"].sum()
    final[["total_revenue"] + media_cols] = final[["total_revenue"] + media_cols].round(0)
    return final.dropna()
