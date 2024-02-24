from dataclasses import dataclass
import datetime


@dataclass
class basic_parameters:
    """Handler for loading in basic parameters used by simmmulate class.
    After init, this class will also preform logic checks for the values of the
    parameters.

    Args:
        years (int): Number of years you want to generate data for.
        channels_impressions (list[int]): names of media channels that use impressions as their metric of activity (Examples: Amazon, TV, etc)
        channels_clicks (list[int]): names of media channels that use clicks as their metric of activity (Examples: Search)
        frequency_of_campaigns (int): how often campaigns occur (for example, frequency of 1 would yield a new campaign every 1 day with each campaign lasting 1 day).
        start_date (str): format yyyy/mm/dd that determines when your daily data set starts on
        true_cvr (list): what the underlying conversion rates of all the channels are, statistical noise will be added on top of this.
        revenue_per_conv (float): How much money we make from a conversion (i.e. profit from a unit of sale).
    """

    years: int
    channels_impressions: list[str]
    channels_clicks: list[str]
    frequency_of_campaigns: int
    start_date: str
    true_cvr: list = None
    revenue_per_conv: float = None

    def __post_init__(self):
        self.all_channels = self.channels_clicks + self.channels_impressions
        self.start_date = datetime.datetime.strptime(self.start_date, "%Y/%m/%d")
        self.end_date = self.start_date + datetime.timedelta(days=(self.years * 365))
        self.evaluate_params()

    def evaluate_params(self):
        assert (
            self.years > 0
        ), "You entered less than 1 year. Must generate more than a years worth of data"
        if self.true_cvr is not None:
            assert len(self.true_cvr.keys()) == len(
                self.all_channels
            ), "True CVR must have equal number of entries as channel impressions and channel clicks"
            for cvr in self.true_cvr.values():
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
            if self.true_cvr is not None
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
    """Handler for loading in parameters used by simmmulate class to generate a baseline of sales.
    After init, this class will also preform logic checks for the values of the
    parameters.

    Args:
        basic_params (basic_parameters): Number of years you want to generate data for.
        base_p (int): Amount of baseline sales we get in a day (sales not due to ads)
        trend_p (int): How much baseline sales is going to grow over the whole period of our data.
        temp_var (int): How big the height of the sine function is for temperature -- i.e. how much temperature varies (used to inject seasonality into our data)
        temp_coef_mean (int): The average of how important seasonality is in our data (the larger this number, the more important seasonality is for sales)
        temp_coef_sd (int): The standard deviation of how important seasonality is in our data (the larger this number, the more variable the importance of seasonality is for sales)
        error_std (int): Amount of statistical noise added to baseline sales (the larger this number, the noisier baseline sales will be).
    """

    basic_params: basic_parameters
    base_p: int
    trend_p: int
    temp_var: int
    temp_coef_mean: int
    temp_coef_sd: int
    error_std: int

    def __post_init__(self):
        assert self.error_std < self.base_p, "Error std can not exceed base sales value"


@dataclass
class ad_spend_parameters:
    """Handler for loading in parameters used by simmmulate class to generate ad spend approximation.
    After init, this class will also preform logic checks for the values of the
    parameters. Also provided is a check function that when passed basic_params
    from input to simmmulate, will provide futher validation checks.

    Args:
        campaign_spend_mean (int): The average amount of money spent on a campaign.
        campaign_spend_std (int): The standard deviation of money spent on a campaign
        max_min_proportion_on_each_channel (dict): Specifies the minimum and maximum percentages of total spend allocated to each channel.
    """

    campaign_spend_mean: int
    campaign_spend_std: int
    max_min_proportion_on_each_channel: dict

    def __post_init__(self):
        assert (
            self.campaign_spend_mean > 0
        ), "You entered a negative average campaign spend. Enter a positive number."
        assert (
            self.campaign_spend_std < self.campaign_spend_mean
        ), "You've entered a campaign spend standard deviation larger than the mean."
        for k, v in self.max_min_proportion_on_each_channel.items():
            assert (
                0 < v["min"] <= 1
            ), "Min spend must be between 0 and 1 for each channel"
            assert (
                0 < v["max"] <= 1
            ), "Max spend must be between 0 and 1 for each channel"

    def check(self, basic_params: basic_parameters):
        """Validates ad_spend parameters agianst previously constructed basic
        parameter values.

        Args:
            basic_params (basic_parameters): Previously submitted parameters as required by the simmmulate class
        """
        assert len(self.max_min_proportion_on_each_channel.keys()) - 1 == len(
            basic_params.all_channels
        ), "You did not input in enough numbers or put in too many numbers for proportion of spends on each channel. Must have a maximum and minimum percentage specified for all channels except the last channel, which will be auto calculated as any remaining amount."


@dataclass
class media_parameters:
    """Handler for loading in parameters used by simmmulate class to generate media data.
    After init, this class will also preform logic checks for the values of the
    parameters. Also provided is a check function that when passed basic_params
    from input to simmmulate, will provide futher validation checks.

    Args:
        true_cpm (dict): Specifies the true Cost per Impression (CPM) of each channel (noise will be added to this to simulate number of impressions)
        true_cpc (dict): Specifies the true Cost per Click (CPC) of each channel (noise will be added to this to simulate number of clicks)
        noisy_cpm_cpc (dict): Specifies the bias and scale of noise added to the true value CPM or CPC for each channel.
    """

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
            assert isinstance(val, float), "cpm values must be of type float"
            assert val > 0, "CPM values must be greater than 0"
        for val in self.true_cpc.values():
            assert isinstance(val, float), "cpc values must be of type float"
            assert val > 0, "CPC values must be greater than 0"

        assert sorted(self.noise_channels) == sorted(
            basic_params.all_channels
        ), "Channels declared within noisy_cpm_cpc must be the same as original base channel input"


@dataclass
class cvr_parameters:
    """Handler for loading in parameters used by simmmulate class to generate cvr data.
    Provided is a check function that when passed basic_params
    from input to simmmulate, will provide validation checks.

    Args:
        noisy_cpm_cpc (dict): Specifies the bias and scale of noise added to the true value CVR for each channel.
    """

    noisy_cvr: dict

    def __post_init__(self):
        self.noise_channels = list(self.noisy_cvr.keys())

        for channel in self.noisy_cvr.keys():
            channel_spec = self.noisy_cvr[channel]
            assert isinstance(
                channel_spec["loc"], float
            ), "noisy loc value must be of type float"
            assert isinstance(
                channel_spec["scale"], float
            ), "noisy scale value must be of type float"

    def check(self, basic_params: basic_parameters):
        assert sorted(self.noise_channels) == sorted(
            basic_params.all_channels
        ), "Channels declared within noisy_cpm_cpc must be the same as original base channel input"


@dataclass
class adstock_parameters:
    """Handler for loading in parameters used by simmmulate class to augment adstock data.
    Provided is a check function that when passed basic_params
    from input to simmmulate, will provide validation checks.

    Args:
        true_lambda_decay (dict): Numbers between 0 and 1 specifying the lambda parameters for a geometric distribution for adstocking media variables.
        alpha_saturation (dict): Specifying alpha parameter of geometric distribution for applying diminishing returns to media variables
        gamma_saturation (dict): Between 0 and 1 specifying gamma parameter of geometric distribution for applying diminishing returns to media variables
    """

    true_lambda_decay: dict
    alpha_saturation: dict
    gamma_saturation: dict

    def __post_init__(self):
        for channel, value in self.true_lambda_decay.items():
            assert isinstance(value, float), "lambda decay value must be of type float"
            assert 0 <= value <= 1, "lambda decay value must be between 0 and 1"
        for channel, value in self.alpha_saturation.items():
            assert isinstance(
                value, float
            ), "alpha saturation value must be of type float"
        for channel, value in self.gamma_saturation.items():
            assert isinstance(
                value, float
            ), "gamma saturation value must be of type float"
            assert 0 <= value <= 1, "gamma saturation value must be between 0 and 1"

    def check(self, basic_params: basic_parameters):
        for input_dict in [
            self.true_lambda_decay,
            self.alpha_saturation,
            self.gamma_saturation,
        ]:
            assert sorted(list(input_dict.keys())) == sorted(
                basic_params.all_channels
            ), f"Channels declared within {input_dict.__name__} must be the same as original base channel input"


@dataclass
class output_parameters:
    """Handler for loading in parameters used by simmmulate class to generate final output data.

    Args:
        aggregation_level (str): Specifies the aggregation level of final output data. choose between [daily, weekly].
    """

    aggregation_level: str

    def __post_init__(self):
        assert self.aggregation_level in [
            "daily",
            "weekly",
        ], "{self.aggregation_level} is invalid. Aggregation level must be in [daily, weekly]"
