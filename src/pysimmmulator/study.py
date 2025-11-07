"""Generation of calibration study results"""
from typing import List, Optional, Dict
import numpy as np 

DEFAULT_STUDY_BIAS = 0.0 
DEFAULT_STUDY_SCALE = 0.05

class study:
    """Object for generating study values from a normal distribution around true the true channel roi"""
    def __init__(self, channel_name:str, true_roi:float, random_seed:int=None, bias:float=DEFAULT_STUDY_BIAS, stdev:float=DEFAULT_STUDY_SCALE) -> None:
        self.channel_name = channel_name
        self._true_roi = true_roi
        self.rng = self._create_random_factory(seed=random_seed)
        self._bias = bias
        self._stdev = stdev

    @property
    def roi(self) -> float: 
        """Reports the true ROI of the channel set at initializaiton

        Returns:
            true_roi (float): the true ROI value for the channel."""
        return self._true_roi
    
    def _create_random_factory(self, seed: int) -> np.random.Generator:
        """Internal helper that serves as a central random number generator, 
        and can be initialized with a seed to enable testing.
        
        Args:
            seed (int): Optional seed value for random number generation
        Returns:
            rng (np.random.Generator): random number generator"""
        rng = np.random.default_rng(seed=seed)
        return rng

    def update_bias(self, value:float) -> None:
        """Updates the distribution bias to the passed value

        Args:
            value (float): value to set the distribution bias to
        Returns:
            None"""
        self._bias = value
    
    def update_stdev(self, value:float) -> None:
        """Updates the distribution stdev to the passed value

        Args:
            value (float): value to set the distribution stdev to
        Returns:
            None"""
        self._stdev = value
    
    def update_roi(self, value:float) -> None:
        """Updates the roi assigned to the channel as the passed value

        Args:
            value (float): value to set the channel roi to
        Returns:
            None"""
        self._true_roi = value

    def generate(self, count:int=1) -> 'np.array': 
        """Provides a study 'result'
        
        Args:
            count (int): number of study results to return (default is 1)
        Retuns:
            study_results (iterable[float]): an array of study results """
        return self.rng.normal(loc=self._true_roi + self._bias, scale=self._stdev, size=count)

    def generate_dynamic(self, bias:list[float], stdev:list[float]) -> list:
        """Provides study results with non-stationary distribution

        Args:
            bias (list[float]): iterable of bias values used to update the distribution per results
            stdev (list[float]): iterable of stdev values used to update the distribution per results
        Returns:
            study_results (iterable[float]): an array of study results """
        results = []
        for b, z in zip(bias, stdev):
            self.update_bias(b)
            self.update_stdev(z)
            results.append(self.generate()[0])
        return results

class batch_study:
    """Object for generating study values across all channels"""
    def __init__(self, channel_rois:dict, channel_distributions:dict[str, dict]=dict(), random_seed:int=None, bias:float=DEFAULT_STUDY_BIAS, stdev:float=DEFAULT_STUDY_SCALE) -> None:
        self._study_hold = {k: study(channel_name=k, true_roi=v, random_seed=random_seed, bias=channel_distributions.get(k, {}).get("bias",bias), stdev=channel_distributions.get(k, {}).get("stdev",stdev)) for k, v in channel_rois.items()}

    def generate(self, count:int=1) -> dict[str, 'np.array']:
        """Produces study results for all of the registered channels

        Args:
            count (int): number of study results to return (default is 1)
        Retuns:
            study_results (dict[iterable[float]]): an array of study results"""
        return {k: v.generate(count) for k, v in self._study_hold.items()}

    def generate_dynamic(self, universal_bias: Optional[List[float]] = None, universal_stdev: Optional[List[float]] = None, 
                         channel_bias: Optional[dict[str, list[float]]]=None, channel_stdev: Optional[dict[str, list[float]]]=None) -> dict[str, list[float]]:
        """Produces study results for all of the registered channels

        Args:
            universal_bias (List[float]): iterable of bias values used to update the distribution per results
            universal_stdev (List[float]): iterable of stdev values used to update the distribution per results
            channel_bias (dict[str, list[float]]): lookup of iterable of bias values used to update the distribution per results
            channel_stdev (dict[str, list[float]]): iterable of stdev values used to update the distribution per results
        Returns:
            study_results (iterable[float]): an array of study results """
        assert all(x is not None for x in [universal_bias, universal_stdev]) or all(x is not None for x in [channel_bias, channel_stdev]), "both Universal or both channel specs must be passed"
        results = {channel: [] for channel in self._study_hold.keys()}
        if all(x is not None for x in [universal_bias, universal_stdev]):
            for b, z in zip(universal_bias, universal_stdev):
                for channel, study in self._study_hold.items():
                    study.update_bias(b)
                    study.update_stdev(z)
                    results[channel].append(study.generate()[0])
            return results
        if all(x is not None for x in [channel_bias, channel_stdev]):
            for channel, study in self._study_hold.items():
                for b, z in zip(channel_bias[channel], channel_stdev[channel]):
                    study.update_bias(b)
                    study.update_stdev(z)
                    results[channel].append(study.generate()[0])
            return results

