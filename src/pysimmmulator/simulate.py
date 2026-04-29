from pysimmmulator.param_handlers import (
  BasicParameters,
  BaselineParameters,
  AdSpendParameters,
  MediaParameters,
  CVRParameters,
  AdstockParameters,
  OutputParameters,
  GeoParameters,
)

from .visualize import Visualize
from .geos import Geos, distribute_to_geos

import numpy as np
import pandas as pd

import logging

logger = logging.getLogger(__name__)

class Simulate(Visualize):
  """Takes input of basic params and provies either piece meal or single shot creation of MMM data using a config file"""
  def __init__(self, basic_params: BasicParameters = None, random_seed=None):
    self.basic_params = basic_params
    self.rng = self._create_random_factory(seed=random_seed)
    super().__init__()

  def _create_random_factory(self, seed: int) -> np.random.Generator:
    """Internal helper that serves as a central random number generator, and can be initialized with a seed to enable testing.

    Args:
  		seed (int): Optional seed value for random number generation
    Returns:
  		rng (np.random.Generator): random number generator"""
    rng = np.random.default_rng(seed=seed)
    return rng

  def _truncated_normal(self, loc, scale, size, low=0):
    """Samples from a truncated normal distribution.
    Uses rejection sampling to ensure all values are >= low, preserving the
    distribution's shape above the threshold rather than clamping to zero.
    """
    samples = self.rng.normal(loc=loc, scale=scale, size=size)
    mask = samples < low
    while np.any(mask):
      resample_count = np.sum(mask)
      samples[mask] = self.rng.normal(loc=loc, scale=scale, size=resample_count)
      mask = samples < low
    return samples

  def _report_random_state(self) -> int:
    """Gives the generators bit signature

    Args:
    	None
    Returns:
      (int)
    """
    return self.rng.bit_generator

  def simulate_baseline(self, params: BaselineParameters) -> pd.DataFrame:
    """Simulation of baseline sales and revenue for the subject business.

    The simulation calculates daily baseline sales as a sum of:
    - Base sales: A constant value (base_p)
    - Trend: Linear growth over the period (total growth of trend_p)
    - Seasonality: Modeled via a sine function (height temp_var) scaled by a random
      importance coefficient (mean temp_coef_mean, std temp_coef_sd)
    - Error: Gaussian noise (std error_std)

    If the combined terms result in negative sales, they are clamped to zero.

    Args:
      params (BaselineParameters): Parameters for baseline simulation.
    Returns:
      pd.DataFrame: Daily baseline sales components."""
    self.baseline_params = params

    days = np.arange(0, self.basic_params.years * 365)
    base = (np.zeros(shape=self.basic_params.years * 365) + self.baseline_params.base_p)

    trend_cal = (self.baseline_params.trend_p / (self.basic_params.years * 365))
    trend = trend_cal * days

    temp = self.baseline_params.temp_var * np.sin(days * 3.14 / 182.5)
    seasonality = self.rng.normal(loc=self.baseline_params.temp_coef_mean, scale=self.baseline_params.temp_coef_sd, size=1) * temp

    error = self._truncated_normal(loc=0, scale=self.baseline_params.error_std, size=self.basic_params.years * 365, low=-np.inf)

    baseline_sales = base + trend + seasonality + error
    if np.any(baseline_sales < 0):
        baseline_sales = np.where(baseline_sales < 0, 0, baseline_sales)

    return pd.DataFrame({
      "days": days,
      "baseline_sales": baseline_sales,
      "base": base,
      "trend": trend,
      "temp": temp,
      "seasonality": seasonality,
      "error": error,
    })
  def simulate_ad_spend( self, baseline_sales_df: pd.DataFrame, params: AdSpendParameters) -> pd.DataFrame:
    """Simulation of ad spend based on normal distribution parameters for campaign spend.
    Overall campaign spend is then divided amongst each channel based on passed
    min-max proportionality.

    Args:
      baseline_sales_df (pd.DataFrame): DataFrame containing baseline sales
      params (AdSpendParameters): Parameters for ad spend simulation.
    Returns:
      pd.DataFrame: DataFrame containing ad spend data"""
    campaign_count = int(self.basic_params.years * 365 / self.basic_params.frequency_of_campaigns)

    # specify amount spent on each campaign according to a normal distribution
    campaign_spends = np.round(
      self._truncated_normal(
        loc=params.campaign_spend_mean,
        scale=params.campaign_spend_std,
        size=campaign_count,
      ),
      2,
    )
    campaign_channel_spend_proportions = {}
    total_proportions = np.zeros(campaign_count)
    for (channel, proportions,) in params.max_min_proportion_on_each_channel.items():
      campaign_channel_spend_proportions[channel] = self.rng.uniform(low=proportions["min"], high=proportions["max"], size=campaign_count,)
      total_proportions += campaign_channel_spend_proportions[channel]

    remaining_channels = [c for c in self.basic_params.all_channels if c not in params.max_min_proportion_on_each_channel.keys()]
    if remaining_channels:
      remaining_channel = remaining_channels[0]
      campaign_channel_spend_proportions[remaining_channel] = np.maximum(0, 1.0 - total_proportions)

    spend_df = pd.DataFrame({"campaign_id": np.arange(campaign_count), "total_campaign_spend": campaign_spends, })

    for channel in self.basic_params.all_channels:
      spend_df[channel] = np.round(campaign_spends * campaign_channel_spend_proportions[channel], 2)
      # Apply random trend to the spend of each of the platforms. This creates the alignemnt to revenue trend and spend trend
      spend_df[channel] *= (
        ((baseline_sales_df["trend"] / baseline_sales_df["base"]) + 1
        )  # multiplies by the existing trend vector normalized by baseline sales
        * self.rng.normal(loc=1.0, scale=0.05, size=1)
        [0]  # Applies a normaly distributed multiplier to the trend to create unique channel effects
      )
    spend_df = spend_df.melt(
      id_vars=["campaign_id", "total_campaign_spend"],
      value_vars=self.basic_params.all_channels,
      var_name="channel",
      value_name="spend_channel",
    )
    logger.info("You have completed running step 2: Simulating ad spend.")
    return spend_df

  def _negative_check(self, df: pd.DataFrame, column: str, channel: str) -> None:
    """Checks each column of the dataframe for negative values. Negative values are seen as errors
    in the case of this simulation, given that values produced typically reflect investment or media metrics.

    Args:
      df (DataFrame): Dataframe containing columns of metrics with rows of date wise values
      column (str): specified column to search for negativ values.
      channel (str): context passed to the function for sake of error logging when negative values are detected
    Returns:
      None"""
    if df[column].min() < 0:
      sub_zero_count = (df[column] < 0).sum()
      logger.warning(
        f"""There are {sub_zero_count} negative values for {channel} in {column.split('_')[1]}.
        Consider adjusting your distribution parameters. For now those values will be set to 0"""
      )

  def _negative_replace(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Replaces negative velues within a passed column.
    For spend based metrics (cost per click and impression) <=0 is replaced with 1st percentile of positive values (minimum 1e-6).

    Args:
      df (DataFrame): Dataframe containing columns of metrics with rows of date wise values
      column (str): specified column to search for negativ values
    Returns:
      df (DataFrame): Treated dataframe with replacement"""
    col_lower = column.lower()
    is_cost_metric = ("cpc" in col_lower) or ("cpm" in col_lower)

    if is_cost_metric:
      positives = df.loc[df[column] > 0, column]
      epsilon = 1e-6
      if len(positives) > 0:
        replacement = max(positives.quantile(0.01), epsilon)
      else:
        replacement = epsilon
      df.loc[df[column] <= 0, column] = replacement
    else:
      df.loc[df[column] < 0, column] = 0
    return df

  def simulate_media(self, spend_df: pd.DataFrame, params: MediaParameters) -> pd.DataFrame:
    """Simulation of relevant media metrics for each channel.
    True values are passed and noise is applied in accordance with a normal distribution described within the noisy dict.
    Media metrics are checked for 0 values stemming from the random noise applied and will be flagged with logger when found.
    It is generally understood that negativ evalues should not arrise for media metrics.

    Args:
      spend_df (pd.DataFrame): DataFrame containing ad spend data
      params (MediaParameters): Parameters for media simulation.
    Returns:
      pd.DataFrame: Updated spend DataFrame"""
    for channel in params.noise_channels:
      channel_idx = spend_df[spend_df["channel"] == channel].index

      channel_noise = self._truncated_normal(
        size=len(channel_idx),
        **params.noisy_cpm_cpc[channel],
        low=-min(params.true_cpm.get(channel, np.inf), params.true_cpc.get(channel, np.inf)))

      channel_true_cpm_value = (params.true_cpm[channel] if channel in params.true_cpm.keys() else np.nan)
      channel_noisy_cpm_value = (params.true_cpm[channel] + channel_noise if channel in params.true_cpm.keys() else np.nan)
      spend_df.loc[channel_idx, "true_cpm"] = channel_true_cpm_value
      spend_df.loc[channel_idx, "noisy_cpm"] = channel_noisy_cpm_value

      channel_true_cpc_value = (params.true_cpc[channel] if channel in params.true_cpc.keys() else np.nan)
      channel_noisy_cpc_value = (params.true_cpc[channel] + channel_noise if channel in params.true_cpc.keys() else np.nan)
      spend_df.loc[channel_idx, "true_cpc"] = channel_true_cpc_value
      spend_df.loc[channel_idx, "noisy_cpc"] = channel_noisy_cpc_value

      self._negative_check(spend_df.loc[channel_idx], column="noisy_cpm", channel=channel)
      self._negative_check(spend_df.loc[channel_idx], column="noisy_cpc", channel=channel)

    spend_df = self._negative_replace(df=spend_df, column="noisy_cpm")
    spend_df = self._negative_replace(df=spend_df, column="noisy_cpc")

    spend_df["lifetime_impressions"] = np.round( spend_df["spend_channel"] / spend_df["noisy_cpm"] * 1000, 0)
    spend_df["lifetime_clicks"] = np.round( spend_df["spend_channel"] / spend_df["noisy_cpc"], 0)

    spend_df["daily_spend"] = np.round( spend_df["spend_channel"] / self.basic_params.frequency_of_campaigns, 2)
    spend_df["daily_impressions"] = np.round( spend_df["lifetime_impressions"] / self.basic_params.frequency_of_campaigns, 0,)
    spend_df["daily_clicks"] = np.round( spend_df["lifetime_clicks"] / self.basic_params.frequency_of_campaigns, 0,)

    logger.info("You have completed running step 3: Simulating media.")
    return spend_df

  def simulate_cvr(self, spend_df: pd.DataFrame, params: CVRParameters) -> pd.DataFrame:
    """Generate Conversion Rate using the true conversion rates passed in the basic params with noise parameters passed in this function.

    Args:
      spend_df (pd.DataFrame): DataFrame containing ad spend data
      params (CVRParameters): Parameters for CVR simulation.
    Returns:
      pd.DataFrame: Updated spend DataFrame"""
    for channel in params.noise_channels:
      channel_idx = spend_df[spend_df["channel"] == channel].index

      channel_noise = self.rng.weibull((1 / params.noisy_cvr[channel]["scale"]) / 10 + 1, size=len(channel_idx))
      spend_df.loc[channel_idx, "noisy_cvr"] = (channel_noise * self.basic_params.true_cvr[channel])

      self._negative_check(spend_df.loc[channel_idx], column="noisy_cvr", channel=channel)
    spend_df = self._negative_replace(df=spend_df, column="noisy_cvr")
    # Daily CVR == campaign CVR, no reason to duplicate
    logger.info("You have completed running step 4: Simulating CVR.")
    return spend_df

  def _reformat_for_mmm(self, spend_df: pd.DataFrame) -> pd.DataFrame:
    """Establishes a date based index which previously generated spend, media metric, and conversion data is then mapped to.
    This begins to form the structure of a dataframe that can function as an MMM input.

    Args:
      spend_df (pd.DataFrame): DataFrame containing ad spend data
    Returns:
      pd.DataFrame: MMM input DataFrame
    """
    date_backbone = pd.date_range(start=self.basic_params.start_date, end=self.basic_params.end_date, freq="D")
    campaigns_in_period = (date_backbone.shape[0] / self.basic_params.frequency_of_campaigns)
    campaign_id_to_date_map = np.trunc(np.linspace(start=0, stop=campaigns_in_period - 1, num=date_backbone.shape[0])).astype(int)
    mmm_df = pd.DataFrame({"date": date_backbone, "id_map": campaign_id_to_date_map})
    mmm_df.set_index("id_map", inplace=True)

    agg_media_df = spend_df.groupby(["channel", "campaign_id"]).sum()[["daily_impressions", "daily_clicks", "daily_spend", "noisy_cvr" ]]
    agg_media_df = agg_media_df.unstack(level=0)
    joined_columns = []
    for _metric, _channel in agg_media_df.columns:
      # we'll just name everything channel_metric from here. No need for daily/lifetime
      col_name = f"{_channel}_{_metric.split('_')[1]}"
      joined_columns.append(col_name)
    agg_media_df.columns = joined_columns

    mmm_df = mmm_df.join(agg_media_df)

    logger.info("You have completed running step 5a: pivoting the data frame to an MMM format.")
    return mmm_df

  def _simulate_decay(self, mmm_df: pd.DataFrame, adstock_config: dict) -> pd.DataFrame:
    """Helper function for the simulation of adstocking.
    Ad stocking is the idea that an ad has a lasting effect for some amount of time in the future.
    """
    from .transforms import geometric_adstock, weibull_adstock
    for channel, config in adstock_config.items():
      metric = ("impressions" if channel in self.basic_params.channels_impressions else "clicks")
      vector = mmm_df[f"{channel}_{metric}"]

      if config["type"] == "geometric":
        params = config["params"].copy()
        if 'lambda' in params:
          params['lambda_'] = params.pop('lambda')
        mmm_df[f"{channel}_{metric}_adstocked"] = geometric_adstock(vector, **params)
      elif config["type"] == "weibull":
        mmm_df[f"{channel}_{metric}_adstocked"] = weibull_adstock(vector, **config["params"])
      else:
        logger.warning(f"Unknown adstock type {config['type']} for channel {channel}. Using raw values.")
        mmm_df[f"{channel}_{metric}_adstocked"] = vector

    logger.info("You have completed running step 5b: applying adstock decay.")
    return mmm_df

  def _simulate_diminishing_returns(self, mmm_df: pd.DataFrame, saturation_config: dict) -> pd.DataFrame:
    """Helper function for the simulation of diminishing returns."""
    from .transforms import scurve_saturation, hill_saturation
    for channel, config in saturation_config.items():
      metric = ("impressions" if channel in self.basic_params.channels_impressions else "clicks")
      target = mmm_df[f"{channel}_{metric}_adstocked"]

      if config["type"] == "scurve":
        mmm_df[f"{channel}_{metric}_adstocked_decay_diminishing"] = scurve_saturation(target, **config["params"])
      elif config["type"] == "hill":
        mmm_df[f"{channel}_{metric}_adstocked_decay_diminishing"] = hill_saturation(target, **config["params"])
      else:
        logger.warning(f"Unknown saturation type {config['type']} for channel {channel}. Using adstocked values.")
        mmm_df[f"{channel}_{metric}_adstocked_decay_diminishing"] = target

    logger.info("You have completed running step 5c: apply diminishing marginal returns.")
    return mmm_df

  def simulate_decay_returns(self, spend_df: pd.DataFrame, params: AdstockParameters) -> pd.DataFrame:
    """Generates the decay and returns values associated with ad stocking and diminishing returns.

    Args:
      spend_df (pd.DataFrame): DataFrame containing ad spend data
      params (AdstockParameters): Parameters for adstock and saturation.
    Returns:
      pd.DataFrame: MMM input DataFrame with decay and returns applied"""
    mmm_df = self._reformat_for_mmm(spend_df=spend_df)
    mmm_df = self._simulate_decay(mmm_df=mmm_df, adstock_config=params.adstock)
    mmm_df = self._simulate_diminishing_returns(
      mmm_df=mmm_df,
      saturation_config=params.saturation,
    )

    logger.info("You have completed running step 5: Simulating adstock.")
    return mmm_df

  def simulate_geos(self, mmm_df: pd.DataFrame, params: GeoParameters) -> pd.DataFrame:
    """Distributes the consolidated MMM dataframe into geographies.

    Args:
      mmm_df (pd.DataFrame): Consolidated MMM DataFrame
      params (GeoParameters): Parameters for geographic distribution.
    Returns:
      pd.DataFrame: MMM DataFrame with geographic distribution"""
    geos = Geos(total_population=params.total_population, random_seed=None)
    geo_details = geos(geo_specs=params.geo_specs, universal_scale=params.universal_scale, count=params.count)

    mmm_df = distribute_to_geos(
        mmm_input=mmm_df,
        geo_details=geo_details,
        dist_spec=params.dist_spec,
        media_cost_spec=params.media_cost_spec,
        perf_spec=params.perf_spec
    )
    logger.info("You have completed running step 8: Distributing data to geographies.")
    return mmm_df

  def calculate_conversions(self, mmm_df: pd.DataFrame) -> pd.DataFrame:
    """Calculates row wise values for conversions based on the noisy cvr and the adstocked media metric associated with each channel.

    Args:
      mmm_df (pd.DataFrame): MMM input DataFrame
    Returns:
      pd.DataFrame: Updated mmm_df"""
    for channel in self.basic_params.all_channels:
      metric = ("impressions"
            if channel in self.basic_params.channels_impressions else "clicks")
      mmm_df[f"{channel}_conversions"] = (
        mmm_df[f"{channel}_{metric}_adstocked_decay_diminishing"] *
        mmm_df[f"{channel}_cvr"])

    logger.info("You have completed running step 6: Calculating the number of conversions.")
    return mmm_df

  def consolidate_dataframe(self, mmm_df: pd.DataFrame, baseline_sales_df: pd.DataFrame) -> pd.DataFrame:
    """Filters and formats internal data into uniform output.

    Args:
      mmm_df (pd.DataFrame): MMM input DataFrame
      baseline_sales_df (pd.DataFrame): Baseline sales DataFrame
    Returns:
      pd.DataFrame: Consolidated MMM DataFrame"""
    metric_cols = [
      f"{channel}_impressions"
      for channel in self.basic_params.channels_impressions
    ]
    [metric_cols.append(f"{channel}_clicks") for channel in self.basic_params.channels_clicks]
    spend_cols = []
    [spend_cols.append(f"{channel}_spend") for channel in self.basic_params.all_channels]
    conv_cols = []
    [conv_cols.append(f"{channel}_conversions") for channel in self.basic_params.all_channels]
    mmm_df = mmm_df[["date"] + metric_cols + spend_cols + conv_cols]
    mmm_df["total_conversions_from_ads"] = mmm_df[conv_cols].sum(axis=1)
    mmm_df["total_revenue_from_ads"] = (mmm_df["total_conversions_from_ads"] * self.basic_params.revenue_per_conv)
    mmm_df["baseline_revenue"] = (round(baseline_sales_df["baseline_sales"]) * self.basic_params.revenue_per_conv)
    mmm_df["total_revenue"] = mmm_df[["total_revenue_from_ads", "baseline_revenue"]].sum(axis=1)

    logger.info("You have completed running step 7: Expanding to maximum data frame.")
    return mmm_df

  def calculate_channel_roi(self, mmm_df: pd.DataFrame) -> dict:
    """Calculates the ROI for all channels, based on pre-generated spend and conversions data

    Args:
      mmm_df (pd.DataFrame): Consolidated MMM DataFrame
    Returns:
      dict: Channel ROI mapping"""
    channel_roi = {}
    for channel in self.basic_params.all_channels:
      total_cpa = (mmm_df[f"{channel}_spend"].sum() / mmm_df[f"{channel}_conversions"].sum())
      total_roi = (self.basic_params.revenue_per_conv - total_cpa) / total_cpa
      channel_roi[channel] = total_roi
    return channel_roi

  def finalize_output(self, mmm_df: pd.DataFrame, params: OutputParameters) -> pd.DataFrame:
    """Provide aggregation (daily, weekly) and column filtering for final output

    Args:
      mmm_df (pd.DataFrame): Consolidated MMM DataFrame
      params (OutputParameters): Parameters for output finalization.
    Returns:
      pd.DataFrame: Finalized output DataFrame"""
    metric_cols = [f"{channel}_impressions" for channel in self.basic_params.channels_impressions]
    [metric_cols.append(f"{channel}_clicks") for channel in self.basic_params.channels_clicks]
    spend_cols = []
    [spend_cols.append(f"{channel}_spend") for channel in self.basic_params.all_channels]

    if params.aggregation_level == "daily":
      if "geo_name" in mmm_df.index.names:
        final_df = mmm_df[metric_cols + spend_cols + ["total_revenue"]]
      else:
        mmm_df = mmm_df.set_index("date")
        final_df = mmm_df[metric_cols + spend_cols + ["total_revenue"]]
    else:
      if "geo_name" in mmm_df.index.names:
        mmm_df = mmm_df.reset_index()

      mmm_df["week_start"] = mmm_df["date"] - pd.to_timedelta(
        mmm_df["date"].dt.weekday, unit="D")

      group_cols = ["week_start"]
      if "geo_name" in mmm_df.columns:
        group_cols = ["geo_name", "week_start"]

      final_df = (mmm_df[metric_cols + spend_cols + ["total_revenue"] +
                     group_cols].groupby(group_cols).sum())

    logger.info(f"You have completed running step 9: Finalization of output dataframe at the {params.aggregation_level} level")
    return final_df

  def run_with_config(self, config: dict) -> tuple[pd.DataFrame, dict]:
    from .load_parameters import create_all_parameters
    params = create_all_parameters(config)
    self.basic_params = params["basic_params"]

    baseline_sales_df = self.simulate_baseline(params["baseline_params"])
    spend_df = self.simulate_ad_spend(baseline_sales_df=baseline_sales_df, params=params["ad_spend_params"])
    spend_df = self.simulate_media(spend_df=spend_df, params=params["media_params"])
    spend_df = self.simulate_cvr(spend_df=spend_df, params=params["cvr_params"])
    mmm_df = self.simulate_decay_returns(spend_df=spend_df, params=params["adstock_params"])
    mmm_df = self.calculate_conversions(mmm_df=mmm_df)
    mmm_df = self.consolidate_dataframe(mmm_df=mmm_df, baseline_sales_df=baseline_sales_df)

    if "geo_params" in params:
      mmm_df = self.simulate_geos(mmm_df=mmm_df, params=params["geo_params"])

    channel_roi = self.calculate_channel_roi(mmm_df=mmm_df)
    final_df = self.finalize_output(mmm_df=mmm_df, params=params["output_params"])

    return (final_df, channel_roi)

class Multisim(Simulate):
  """Provides capability to generate multiple runs on a single configuration"""
  def __init__(self):
    super(Multisim, self).__init__()
    self.final_frames = []
    self.rois = []

  def stash_outputs(self, final_df: pd.DataFrame, channel_roi: dict):
    """Stores the final simulation dataframe as well as the ground truth channel ROI values
    for each run of the multiple simulations.
    """
    self.final_frames.append(final_df)
    self.rois.append(channel_roi)

  @property
  def get_data(self):
    """Provies the iterable generator for simulaton final dataframes and channel ground truth ROI values

    Args:
    	None
    Returns:
    	data (iterable): iterable of final sim dataframes and channel ROI values"""
    return self.data

  def run(self, config: dict, runs: int) -> None:
    for run in range(runs):
      frame, roi = self.run_with_config(config=config)
      self.stash_outputs(final_df=frame, channel_roi=roi)
      logger.info(f"{run + 1}/{runs} completed")
    self.data = zip(self.final_frames, self.rois)
    logger.info(f"{runs} runs complete and stored")
