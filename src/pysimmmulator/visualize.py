import pandas as pd
import matplotlib.pyplot as plt

class Visualize:
  def __init__(self):
    self._viz_available = True
    self._valid_agg_levels = ['daily', 'weekly', 'monthly', 'yearly']

  def plot_spend(self, df: pd.DataFrame, agg: str = None):
    """Plot simulated spend data based on a passed date-wise aggregation

    Args:
      df (pd.DataFrame): DataFrame containing simulated data
      agg (str): pick from ['daily', 'weekly', 'monthly', 'yearly'] to aggregate simulated data by"""
    assert agg in self._valid_agg_levels, f"""Please select [{', '.join(self._valid_agg_levels)}] for your aggregation level.
      {agg} is an invalid selection."""
    plot_frame = self._plot_frame_overhead(df, agg_level=agg)
    plot_cols = self._filter_columns(columns=plot_frame.columns.tolist(), filter_string='_spend')
    return self._plot_majors(plot_frame, columns=plot_cols)

  def plot_impressions(self, df: pd.DataFrame, agg: str = None):
    """Plot simulated impressions data based on a passed date-wise aggregation

    Args:
      df (pd.DataFrame): DataFrame containing simulated data
      agg (str): pick from ['daily', 'weekly', 'monthly', 'yearly'] to aggregate simulated data by"""
    assert agg in self._valid_agg_levels, f"""Please select [{', '.join(self._valid_agg_levels)}] for your aggregation level.
      {agg} is an invalid selection."""
    plot_frame = self._plot_frame_overhead(df, agg_level=agg)
    plot_cols = self._filter_columns(columns=plot_frame.columns.tolist(), filter_string='_impressions')
    return self._plot_majors(plot_frame, columns=plot_cols)

  def plot_clicks(self, df: pd.DataFrame, agg: str = None):
    """Plot simulated clicks data based on a passed date-wise aggregation

    Args:
      df (pd.DataFrame): DataFrame containing simulated data
      agg (str): pick from ['daily', 'weekly', 'monthly', 'yearly'] to aggregate simulated data by"""
    assert agg in self._valid_agg_levels, f"""Please select [{', '.join(self._valid_agg_levels)}] for your aggregation level.
      {agg} is an invalid selection."""
    plot_frame = self._plot_frame_overhead(df, agg_level=agg)
    plot_cols = self._filter_columns(columns=plot_frame.columns.tolist(), filter_string='_clicks')
    return self._plot_majors(plot_frame, columns=plot_cols)

  def plot_revenue(self, df: pd.DataFrame, agg: str = None):
    """Plot simulated revenue data based on a passed date-wise aggregation

    Args:
      df (pd.DataFrame): DataFrame containing simulated data
      agg (str): pick from ['daily', 'weekly', 'monthly', 'yearly'] to aggregate simulated data by"""
    assert agg in self._valid_agg_levels, f"""Please select ["{', '.join(self._valid_agg_levels)}] for your aggregation level.
      {agg} is an invalid selection."""
    plot_frame = self._plot_frame_overhead(df, agg_level=agg)
    plot_cols = self._filter_columns(columns=plot_frame.columns.tolist(), filter_string='total_revenue')
    return self._plot_majors(plot_frame, columns=plot_cols)

  def _filter_columns(self, columns: list, filter_string: str) -> list:
    filtered_cols = []
    [filtered_cols.append(col) for col in columns if filter_string in col]
    return filtered_cols

  def _plot_frame_overhead(self, df: pd.DataFrame, agg_level: str = None) -> pd.DataFrame:
    plot_frame = df.copy()
    if 'date' in (plot_frame.index.names or [plot_frame.index.name]):
      plot_frame.reset_index(inplace=True)

    if agg_level is not None:
      plot_frame = self._aggregator(plot_frame, agg_level)

    return plot_frame

  def _aggregator(self, plot_frame: pd.DataFrame, agg_level: str) -> pd.DataFrame:
    if agg_level == 'daily':
      plot_frame = plot_frame.groupby("date").sum()

    elif agg_level == 'weekly':
      plot_frame["week_start"] = plot_frame["date"] - pd.to_timedelta(plot_frame["date"].dt.weekday, unit="D")
      if "date" in plot_frame.columns:
        del plot_frame["date"]
      plot_frame = plot_frame.groupby("week_start").sum()

    elif agg_level == 'monthly':
      plot_frame["month_start"] = plot_frame["date"] - pd.to_timedelta(
        plot_frame["date"].dt.day - 1, unit="D")
      if "date" in plot_frame.columns:
        del plot_frame["date"]
      plot_frame = plot_frame.groupby("month_start").sum()

    elif agg_level == 'yearly':
      plot_frame["year_start"] = plot_frame["date"] - pd.to_timedelta(
        plot_frame["date"].dt.dayofyear - 1, unit="D")
      if "date" in plot_frame.columns:
        del plot_frame["date"]
      plot_frame = plot_frame.groupby("year_start").sum()

    return plot_frame

  def _plot_majors(self, plot_frame: pd.DataFrame, columns: list):
    if not columns:
      return
    plot_subject = columns[-1].split('_')[1] if '_' in columns[-1] else columns[-1]
    plot_subject = plot_subject[0].upper() + plot_subject[1:]

    fig, ax = plt.subplots(1, 1, figsize=(9, 6), dpi=200)
    for col in columns: ax.plot(plot_frame.index, plot_frame[col], label=col.split('_')[0])
    ax.set_xlabel("Date")
    ax.set_ylabel(f"{plot_subject}")
    ax.set_title(f"{plot_subject} by Channel")
    fig.legend(loc="upper right")
    plt.savefig(f'{plot_subject}_by_channel.png')
