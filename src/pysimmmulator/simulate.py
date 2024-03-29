from pysimmmulator.param_handlers import (
    basic_parameters,
    baseline_parameters,
    ad_spend_parameters,
    media_parameters,
    cvr_parameters,
    adstock_parameters,
    output_parameters,
)

from .visualize import visualize

import numpy as np
import pandas as pd

import logging
logger = logging.getLogger(__name__)


class simmm(visualize):
    """Takes input of basic params and provies either piece meal or single shot
    creation of MMM data using a config file,"""

    def __init__(self, basic_params: basic_parameters = None, random_seed = None):
        self.basic_params = basic_params
        self.rng = self._create_random_factory(seed=random_seed)
        super().__init__()

    def _create_random_factory(self, seed: int) -> np.random.Generator:
        rng = np.random.default_rng(seed=seed)
        return rng
    
    def _report_random_state(self):
        return self.rng.bit_generator

    def simulate_baseline(
        self,
        base_p,
        trend_p: int,
        temp_var: int,
        temp_coef_mean: int,
        temp_coef_sd: int,
        error_std: int,
    ) -> None:
        self.baseline_params = baseline_parameters(
            basic_params=self.basic_params,
            base_p=base_p,
            trend_p=trend_p,
            temp_var=temp_var,
            temp_coef_mean=temp_coef_mean,
            temp_coef_sd=temp_coef_sd,
            error_std=error_std,
        )

        # Number of days to generate data for
        days = np.arange(0, self.basic_params.years * 365)
        # Base sales of base_p units
        base = (
            np.zeros(shape=self.basic_params.years * 365) + self.baseline_params.base_p
        )
        # Trend of trend_p extra units per day
        trend_cal = (
            self.baseline_params.trend_p / (self.basic_params.years * 365)
        ) * self.baseline_params.base_p
        trend = trend_cal * days
        # Temperature generated by a sin function and we can manipulate how much the sin function goes up or down with temp_var
        temp = self.baseline_params.temp_var * np.sin(days * 3.14 / 182.5)
        # coefficient of temperature's effect on sales will be a random variable with normal distribution
        seasonality = (
            self.rng.normal(loc=self.baseline_params.temp_coef_mean, scale=self.baseline_params.temp_coef_sd, size=1)
            * temp
        )
        # add some noise to the trend
        error = self.rng.normal(loc=0, scale=self.baseline_params.error_std, size=self.basic_params.years * 365)
        # Generate series for baseline sales
        baseline_sales = base + trend + seasonality + error
        # if error term makes baseline_sales negative, make it 0
        baseline_sales = np.where(baseline_sales < 0, 0, baseline_sales)

        self.baseline_sales_df = pd.DataFrame(
            {
                "days": days,
                "baseline_sales": baseline_sales,
                "base": base,
                "trend": trend,
                "temp": temp,
                "seasonality": seasonality,
                "error": error,
            }
        )

    def simulate_ad_spend(
        self,
        campaign_spend_mean: int,
        campaign_spend_std: int,
        max_min_proportion_on_each_channel: dict,
    ) -> None:
        ad_spend_params = ad_spend_parameters(
            campaign_spend_mean=campaign_spend_mean,
            campaign_spend_std=campaign_spend_std,
            max_min_proportion_on_each_channel=max_min_proportion_on_each_channel,
        )

        campaign_count = int(
            self.basic_params.years * 365 / self.basic_params.frequency_of_campaigns
        )

        # specify amount spent on each campaign according to a normal distribution
        campaign_spends = np.round(
            self.rng.normal(
                loc=ad_spend_params.campaign_spend_mean,
                scale=ad_spend_params.campaign_spend_std,
                size=campaign_count,
            ),
            2,
        )
        # if campaign spend number is negative, automatically make it 0
        campaign_spends[campaign_spends < 0] = 0
        campaign_channel_spend_proportions = {}
        for (
            channel,
            proportions,
        ) in ad_spend_params.max_min_proportion_on_each_channel.items():
            campaign_channel_spend_proportions[channel] = self.rng.uniform(
                low=proportions["min"],
                high=proportions["max"],
                size=campaign_count,
            )

        spend_df = pd.DataFrame(
            {
                "campaign_id": np.arange(campaign_count),
                "total_campaign_spend": campaign_spends,
            }
        )

        for channel in max_min_proportion_on_each_channel.keys():
            spend_df[channel] = np.round(
                campaign_spends * campaign_channel_spend_proportions[channel], 2
            )

        self.spend_df = spend_df.melt(
            id_vars=["campaign_id", "total_campaign_spend"],
            value_vars=self.basic_params.all_channels,
            var_name="channel",
            value_name="spend_channel",
        )
        logger.info("You have completed running step 2: Simulating ad spend.")

    def _negative_check(self, df: pd.DataFrame, column: str, channel: str) -> None:
        if df[column].min() < 0:
            sub_zero_count = (df[column] < 0).sum()
            logger.warning(
                f"There are {sub_zero_count} negative values for {channel} in {column.split('_')[1]}. Consider adjusting your distribution parameters. For now those values will be set to 0"
            )

    def _negative_replace(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        df.loc[df[column] < 0, column] = 0
        return df

    def simulate_media(
        self, true_cpm: dict, true_cpc: dict, noisy_cpm_cpc: dict
    ) -> None:
        media_params = media_parameters(true_cpm, true_cpc, noisy_cpm_cpc)
        media_params.check(basic_params=self.basic_params)

        for channel in media_params.noise_channels:
            channel_idx = self.spend_df[self.spend_df["channel"] == channel].index

            channel_noise = self.rng.normal(
                size=len(channel_idx), **noisy_cpm_cpc[channel]
            )

            channel_true_cpm_value = (
                true_cpm[channel] if channel in true_cpm.keys() else np.nan
            )
            channel_noisy_cpm_value = (
                true_cpm[channel] + channel_noise
                if channel in true_cpm.keys()
                else np.nan
            )
            self.spend_df.loc[channel_idx, "true_cpm"] = channel_true_cpm_value
            self.spend_df.loc[channel_idx, "noisy_cpm"] = channel_noisy_cpm_value

            channel_true_cpc_value = (
                true_cpc[channel] if channel in true_cpc.keys() else np.nan
            )
            channel_noisy_cpc_value = (
                true_cpc[channel] + channel_noise
                if channel in true_cpc.keys()
                else np.nan
            )
            self.spend_df.loc[channel_idx, "true_cpc"] = channel_true_cpc_value
            self.spend_df.loc[channel_idx, "noisy_cpc"] = channel_noisy_cpc_value

            self._negative_check(
                self.spend_df.loc[channel_idx], column="noisy_cpm", channel=channel
            )
            self._negative_check(
                self.spend_df.loc[channel_idx], column="noisy_cpc", channel=channel
            )

        self.spend_df = self._negative_replace(df=self.spend_df, column="noisy_cpm")
        self.spend_df = self._negative_replace(df=self.spend_df, column="noisy_cpc")

        self.spend_df["lifetime_impressions"] = np.round(
            self.spend_df["spend_channel"] / self.spend_df["noisy_cpm"] * 1000, 0
        )
        self.spend_df["lifetime_clicks"] = np.round(
            self.spend_df["spend_channel"] / self.spend_df["noisy_cpc"], 0
        )

        self.spend_df["daily_spend"] = np.round(
            self.spend_df["spend_channel"] / self.basic_params.frequency_of_campaigns, 2
        )
        self.spend_df["daily_impressions"] = np.round(
            self.spend_df["lifetime_impressions"]
            / self.basic_params.frequency_of_campaigns,
            0,
        )
        self.spend_df["daily_clicks"] = np.round(
            self.spend_df["lifetime_clicks"] / self.basic_params.frequency_of_campaigns,
            0,
        )

        logger.info("You have completed running step 3: Simulating media.")

    def simulate_cvr(self, noisy_cvr: dict) -> None:
        cvr_params = cvr_parameters(noisy_cvr)
        cvr_params.check(basic_params=self.basic_params)

        for channel in cvr_params.noise_channels:
            channel_idx = self.spend_df[self.spend_df["channel"] == channel].index

            channel_noise = self.rng.normal(size=len(channel_idx), **noisy_cvr[channel])
            self.spend_df.loc[channel_idx, "noisy_cvr"] = (
                channel_noise + self.basic_params.true_cvr[channel]
            )

            self._negative_check(
                self.spend_df.loc[channel_idx], column="noisy_cvr", channel=channel
            )
        self.spend_df = self._negative_replace(df=self.spend_df, column="noisy_cvr")
        # Daily CVR == campaign CVR, no reason to duplicate
        logger.info("You have completed running step 4: Simulating CVR.")

    def _reformat_for_mmm(self) -> None:
        date_backbone = pd.date_range(
            start=self.basic_params.start_date, end=self.basic_params.end_date, freq="D"
        )
        campaigns_in_period = (
            date_backbone.shape[0] / self.basic_params.frequency_of_campaigns
        )
        campaign_id_to_date_map = np.trunc(
            np.linspace(
                start=0, stop=campaigns_in_period - 1, num=date_backbone.shape[0]
            )
        ).astype(int)
        self.mmm_df = pd.DataFrame(
            {"date": date_backbone, "id_map": campaign_id_to_date_map}
        )
        self.mmm_df.set_index("id_map", inplace=True)

        agg_media_df = self.spend_df.groupby(["channel", "campaign_id"]).sum()[
            ["daily_impressions", "daily_clicks", "daily_spend", "noisy_cvr"]
        ]
        agg_media_df = agg_media_df.unstack(level=0)
        joined_columns = []
        for _metric, _channel in agg_media_df.columns:
            # we'll just name everything channel_metric from here. No need for daily/lifetime
            col_name = f"{_channel}_{_metric.split('_')[1]}"
            joined_columns.append(col_name)
        agg_media_df.columns = joined_columns

        self.mmm_df = self.mmm_df.join(agg_media_df)

        logger.info(
            "You have completed running step 5a: pivoting the data frame to an MMM format."
        )

    @staticmethod
    def _build_decay_vector(original_vector: pd.Series, decay_value: float) -> pd.Series:
        decayed_vector = [original_vector.values[0]]
        for i, orig_value in enumerate(original_vector.values[1:]):
            decayed_vector.append(orig_value + decay_value * decayed_vector[i])
        return pd.Series(decayed_vector)

    def _simulate_decay(self, true_lambda_decay: dict) -> None:
        for channel in true_lambda_decay.keys():
            metric = (
                "impressions"
                if channel in self.basic_params.channels_impressions
                else "clicks"
            )
            self.mmm_df[f"{channel}_{metric}_adstocked"] = self._build_decay_vector(
                original_vector=self.mmm_df[f"{channel}_{metric}"],
                decay_value=true_lambda_decay[channel],
            )

        logger.info("You have completed running step 5b: applying adstock decay.")
        # Knew I could find a better way, even better now

    def _simulate_diminishing_returns(
        self,
        alpha_saturation: dict,
        gamma_saturation: dict,
        #   , x_marginal: int = None
    ) -> None:
        for channel in alpha_saturation.keys():
            metric = (
                "impressions"
                if channel in self.basic_params.channels_impressions
                else "clicks"
            )
            target = self.mmm_df[f"{channel}_{metric}_adstocked"]
            gamma_trans = np.round(
                np.quantile(
                    np.linspace(min(target), max(target), num=100),
                    gamma_saturation[channel],
                ),
                4,
            )
            x_scurve = target ** alpha_saturation[channel] / (
                target ** alpha_saturation[channel]
                + gamma_trans ** alpha_saturation[channel]
            )
            self.mmm_df[f"{channel}_{metric}_adstocked_decay_diminishing"] = (
                x_scurve * target
            )

        logger.info(
            "You have completed running step 5c: apply diminishing marginal returns."
        )

    def simulate_decay_returns(
        self, true_lambda_decay: dict, alpha_saturation: dict, gamma_saturation: dict
    ) -> None:
        adstock_params = adstock_parameters(
            true_lambda_decay, alpha_saturation, gamma_saturation
        )
        self._reformat_for_mmm()
        self._simulate_decay(adstock_params.true_lambda_decay)
        self._simulate_diminishing_returns(
            alpha_saturation=adstock_params.alpha_saturation,
            gamma_saturation=adstock_params.gamma_saturation,
        )

        logger.info("You have completed running step 5: Simulating adstock.")

    def calculate_conversions(self):
        for channel in self.basic_params.all_channels:
            metric = (
                "impressions"
                if channel in self.basic_params.channels_impressions
                else "clicks"
            )
            self.mmm_df[f"{channel}_conversions"] = (
                self.mmm_df[f"{channel}_{metric}_adstocked_decay_diminishing"]
                * self.mmm_df[f"{channel}_cvr"]
            )

        logger.info(
            "You have completed running step 6: Calculating the number of conversions."
        )

    def consolidate_dataframe(self):
        metric_cols = []
        [metric_cols.append(f"{channel}_impressions") for channel in self.basic_params.channels_impressions]
        [metric_cols.append(f"{channel}_clicks") for channel in self.basic_params.channels_clicks]
        spend_cols = []
        [spend_cols.append(f"{channel}_spend") for channel in self.basic_params.all_channels]
        conv_cols = []
        [conv_cols.append(f"{channel}_conversions") for channel in self.basic_params.all_channels]
        self.mmm_df = self.mmm_df[["date"] + metric_cols + spend_cols + conv_cols]
        self.mmm_df["total_conversions_from_ads"] = self.mmm_df[conv_cols].sum(axis=1)
        self.mmm_df["total_revenue_from_ads"] = (
            self.mmm_df["total_conversions_from_ads"]
            * self.basic_params.revenue_per_conv
        )
        self.mmm_df["baseline_revenue"] = (
            round(self.baseline_sales_df["baseline_sales"])
            * self.basic_params.revenue_per_conv
        )
        self.mmm_df["total_revenue"] = self.mmm_df[
            ["total_revenue_from_ads", "baseline_revenue"]
        ].sum(axis=1)

        logger.info(
            "You have completed running step 7: Expanding to maximum data frame."
        )

    def calculate_channel_roi(self) -> None:
        self.channel_roi = {}
        for channel in self.basic_params.all_channels:
            total_cpa = (
                self.mmm_df[f"{channel}_spend"].sum()
                / self.mmm_df[f"{channel}_conversions"].sum()
            )
            total_roi = (self.basic_params.revenue_per_conv - total_cpa) / total_cpa
            self.channel_roi[channel] = total_roi

    def finalize_output(self, aggregation_level: str) -> None:
        output_params = output_parameters(aggregation_level)
        metric_cols = []
        [metric_cols.append(f"{channel}_impressions") for channel in self.basic_params.channels_impressions]
        [metric_cols.append(f"{channel}_clicks") for channel in self.basic_params.channels_clicks]
        spend_cols = []
        [spend_cols.append(f"{channel}_spend") for channel in self.basic_params.all_channels]

        if output_params.aggregation_level == "daily":
            self.mmm_df.set_index("date", inplace=True)
            self.final_df = self.mmm_df[metric_cols + spend_cols + ["total_revenue"]]
        else:
            self.mmm_df["week_start"] = self.mmm_df["date"] - pd.to_timedelta(
                self.mmm_df["date"].apply(lambda x: x.weekday()), unit="d"
            )
            self.final_df = (
                self.mmm_df[
                    metric_cols + spend_cols + ["total_revenue"] + ["week_start"]
                ]
                .groupby(["week_start"])
                .sum()
            )

        logger.info(
            f"You have completed running step 9: Finalization of output dataframe at the {aggregation_level} level"
        )

    def run_with_config(self, config: dict) -> set[pd.DataFrame, dict]:
        # import pysimmmulator.load_parameters as load_params
        if self.basic_params is None:
            self.basic_params = basic_parameters(**config["basic_params"])
        self.simulate_baseline(**config["baseline_params"])
        self.simulate_ad_spend(**config["ad_spend_params"])
        self.simulate_media(**config["media_params"])
        self.simulate_cvr(**config["cvr_params"])
        self.simulate_decay_returns(**config["adstock_params"])
        self.calculate_conversions()
        self.consolidate_dataframe()
        self.calculate_channel_roi()
        self.finalize_output(**config["output_params"])

        return (self.final_df, self.channel_roi)


class multisimmm(simmm):
    def __init__(self):
        super(multisimmm, self).__init__()
        self.final_frames = []
        self.rois = []

    def store_outputs(self, final_df: pd.DataFrame, channel_roi: dict):
        self.final_frames.append(final_df)
        self.rois.append(channel_roi)

    def run(self, config: dict, runs: int) -> None:
        for run in range(runs):
            frame, roi = self.run_with_config(config=config)
            self.store_outputs(final_df=frame, channel_roi=roi)
        logger.info(f"{runs} runs complete and stored")
