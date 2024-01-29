from dataclasses import dataclass
import numpy as np


@dataclass
class basic_parameters:
    years: int
    channels_impressions: list[str]
    channels_clicks: list[str]
    frequency_of_campaigns: int
    start_date: str
    true_cvr: list = None
    revenue_per_conv: str = None

    def __post_init__(self):
        self.all_channels = self.channels_clicks + self.channels_impressions
        self.evaluate_params()

    def evaluate_params(self):
        assert (
            self.years > 0
        ), "You entered less than 1 year. Must generate more than a years worth of data"
        if self.true_cvr != None:
            assert len(self.true_cvr) == len(self.channel_clicks) + len(
                self.channel_clicks
            ), "True CVR must have equal number of entries as channel impressions and channel clicks"
            for cvr in self.true_cvr:
                assert (
                    0 < cvr <= 1
                ), "You've entered an invalid True CVR value. CVR values must be greater than 0 and less than or equal to 1"
        assert (
            self.frequency_of_campaigns >= 1
        ), "You entered a frequency of campaigns less than 1. You must enter a number greater than 1"

    def __repr__(self):
        channel_use_impressions = ", ".join(self.channels_impressions)
        channel_use_clicks = ", ".join(self.channels_clicks)
        cvr_values = (
            ", ".join([str(cvr) for cvr in self.true_cvr])
            if self.true_cvr != None
            else ""
        )

        slug = f"""Years of Data to generate : {self.years}
Channel that use impressions : {channel_use_impressions}
Channel that use clicks : {channel_use_clicks}
How frequently campaigns occur : {self.frequency_of_campaigns}
True CVRs of a channel (in order of channels you specified) : {cvr_values}
Revenue per conversion : {self.revenue_per_conv}
Date the data set will start with : {self.start_date}"""

        return slug


@dataclass
class baseline_parameters:
    basic_params: basic_parameters
    base_p: int
    trend_p: int
    temp_var: int
    temp_coef_mean: int
    temp_coef_sd: int
    error_std: int

    def __post_init__(self):
        assert (
            self.error_std < self.base_p
        ), "Error std can not exceed base sales value"


@dataclass
class ad_spend_parameters:
    campaign_spend_mean: int
    campaign_spend_std: int
    max_min_proportion_on_each_channel: dict

    def __post_init__(self):
        assert (self.campaign_spend_mean > 0), "You entered a negative average campaign spend. Enter a positive number."
        assert (
            self.campaign_spend_std < self.campaign_spend_mean
        ), "You've entered a campaign spend standard deviation larger than the mean."
        assert (
            len(self.max_min_proportion_on_each_channel.keys()) - 1
            == self.channel_count
        ), "You did not input in enough numbers or put in too many numbers for proportion of spends on each channel. Must have a maximum and minimum percentage specified for all channels except the last channel, which will be auto calculated as any remaining amount."
        for k, v in self.max_min_proportion_on_each_channel.items():
            assert (
                0 < v["min"] <= 1
            ), "Min spend must be between 0 and 1 for each channel"
            assert (
                0 < v["max"] <= 1
            ), "Max spend must be between 0 and 1 for each channel"


@dataclass
class media_parameters:
    true_cpm: dict
    true_cpc: dict
    noisy_cpm_cpc: dict

    def __post_init__(self):
        self.true_cpmcpc_channels = list(self.true_cpm.keys()) + list(
            self.true_cpc.keys()
        )
        self.noise_channels = list(self.noisy_cpm_cpc.keys())

    def check(self, basic_params: basic_parameters):
        assert sorted(self.true_cpmcpc_channels) == sorted(
            basic_params.all_channels
        ), "Channels declared within true_cpm & true_cpc must be the same as original base channel input"
        for val in self.true_cpm.values():
            assert type(val) == float, "cpm values must be of type float"
            assert val > 0, "CPM values must be greater than 0"
        for val in self.true_cpc.values():
            assert type(val) == float, "cpc values must be of type float"
            assert val > 0, "CPC values must be greater than 0"

        assert sorted(self.noise_channels) == sorted(
            basic_params.all_channels
        ), "Channels declared within noisy_cpm_cpc must be the same as original base channel input"
