from pysimmmulator.helpers import basic_parameters

import numpy as np
import pandas as pd

import logging
import logging.config
logging.config.fileConfig("./logging.conf")
logger = logging.getLogger("pysimmmulator")


class simulate:
    """Takes input of basic params and provies either piece meal  of 
    MMM data generation tasks or using a config file, """
    def __init__(self, basic_params: basic_parameters):
        self.basic_params = basic_params
        self.channels = basic_params.channels_clicks + basic_params.channels_impressions
        self.channel_count = len(self.channels)
        

    def simulate_ad_spend(self, campaign_spend_mean: int, campaign_spend_std: int, max_min_proportion_on_each_channel: dict) -> None:
        assert campaign_spend_mean > 0, "You entered a negative average campaign spend. Enter a positive number."
        assert campaign_spend_std < campaign_spend_mean, "You've entered a campaign spend standard deviation larger than the mean."
        assert len(max_min_proportion_on_each_channel.keys()) - 1 == self.channel_count, "You did not input in enough numbers or put in too many numbers for proportion of spends on each channel. Must have a maximum and minimum percentage specified for all channels except the last channel, which will be auto calculated as any remaining amount."
        for k,v in max_min_proportion_on_each_channel.items():
            assert 0 < v['min'] <= 1, "Min spend must be between 0 and 1 for each channel"
            assert 0 < v['max'] <= 1, "Max spend must be between 0 and 1 for each channel"
        
        campaign_count = self.basic_params.years*365 / self.basic_params.frequency_of_campaigns
        
        # specify amount spent on each campaign according to a normal distribution
        campaign_spends = np.random.normal(loc = campaign_spend_mean, shape = campaign_spend_std, size=campaign_count)
        # if campaign spend number is negative, automatically make it 0
        campaign_spends[campaign_spends < 0] = 0
        campaign_channel_spend_proportions = {}
        for channel, proportions in max_min_proportion_on_each_channel.items():
            campaign_channel_spend_proportions[channel] = np.random.uniform(min=proportions['min'], max=proportions['max'], shape=campaign_count)

        spend_df = pd.DataFrame({"campaign_id": np.arange(campaign_count),
                           "total_campaign_spend":campaign_spends})
        
        for channel in max_min_proportion_on_each_channel.keys():
            spend_df[channel] = campaign_spends * campaign_channel_spend_proportions[channel]
        
        self.spend_df = spend_df.melt(
            id_vars=['campaign_id','total_campaign_spend'],
            value_vars=self.channels,
            var_name='channel',
            value_name='spend_channel'
        )
        logging.info("You have completed running step 2: Simulating ad spend.")


    def run_with_config(self):
        import pysimmmulator.load_parameters as load_params
        
        self.simulate_ad_spend(**load_params.cfg['ad_spend'])