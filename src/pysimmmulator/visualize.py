import pandas as pd
import matplotlib.pyplot as plt


class visualize:
    def __init__(self):
        self._viz_available = True
        self._valid_agg_levels = ['daily', 'weekly', 'monthly', 'yearly']

    def plot_spend(self, agg: str = None):
        """Plot simulated spend data based on a passed date-wise aggregation
        
        Args:
            agg (str): pick from [{', '.join(self._valid_agg_levels)}] to aggregate simulated data by"""
        assert agg in self._valid_agg_levels, f"Please select [{', '.join(self._valid_agg_levels)}] for your aggregation level. {agg} is an invalid selection."

        # prepare frame and filter columns for plotting
        self._plot_frame_overhead(agg_level=agg)
        plot_cols = self._filter_columns(columns = self.plot_frame.columns.tolist(), filter_string = '_spend')

        return self._plot_majors(columns = plot_cols)

    def plot_impressions(self, agg: str = None):
        """Plot simulated impressions data based on a passed date-wise aggregation
        
        Args:
            agg (str): pick from [{', '.join(self._valid_agg_levels)}] to aggregate simulated data by"""
        assert agg in self._valid_agg_levels, f"Please select [{', '.join(self._valid_agg_levels)}] for your aggregation level. {agg} is an invalid selection."

        # prepare frame and filter columns for plotting
        self._plot_frame_overhead(agg_level=agg)
        plot_cols = self._filter_columns(columns = self.plot_frame.columns.tolist(), filter_string = '_impressions')

        return self._plot_majors(columns = plot_cols)

    def plot_clicks(self, agg: str = None):
        """Plot simulated clicks data based on a passed date-wise aggregation
        
        Args:
            agg (str): pick from [{', '.join(self._valid_agg_levels)}] to aggregate simulated data by"""
        assert agg in self._valid_agg_levels, f"Please select [{', '.join(self._valid_agg_levels)}] for your aggregation level. {agg} is an invalid selection."

        # prepare frame and filter columns for plotting
        self._plot_frame_overhead(agg_level=agg)
        plot_cols = self._filter_columns(columns = self.plot_frame.columns.tolist(), filter_string = '_clicks')

        return self._plot_majors(columns = plot_cols)
    
    def plot_revenue(self, agg: str = None):
        """Plot simulated revenue data based on a passed date-wise aggregation
        
        Args:
            agg (str): pick from [{', '.join(self._valid_agg_levels)}] to aggregate simulated data by"""
        assert agg in self._valid_agg_levels, f"Please select [{', '.join(self._valid_agg_levels)}] for your aggregation level. {agg} is an invalid selection."

        # prepare frame and filter columns for plotting
        self._plot_frame_overhead(agg_level=agg)
        plot_cols = self._filter_columns(columns = self.plot_frame.columns.tolist(), filter_string = 'total_revenue')

        return self._plot_majors(columns = plot_cols)

    def _filter_columns(self, columns: list, filter_string: str) -> list:
        filtered_cols = []
        [filtered_cols.append(col) for col in columns if filter_string in col]
        return filtered_cols
    
    def _plot_frame_overhead(self, agg_level: int = None) -> pd.DataFrame:
        if agg_level is not None:
            self.plot_frame = self.final_df.copy()
            self.plot_frame.reset_index(inplace=True)
            self._aggregator(agg_level)
        else:
            self.plot_frame = self.final_df.copy()
    
    def _aggregator(self, agg_level: str):
        if agg_level == 'daily':
            self.plot_frame = self.plot_frame.groupby("date").sum()

        elif agg_level == 'weekly':
            self.plot_frame["week_start"] = self.plot_frame["date"] - pd.to_timedelta(
                self.plot_frame["date"].apply(lambda x: x.weekday()), unit="d"
            )
            del self.plot_frame["date"]
            self.plot_frame = self.plot_frame.groupby("week_start").sum()
            
        elif agg_level == 'monthly':
            self.plot_frame["month_start"] = self.plot_frame["date"] - pd.to_timedelta(
                self.plot_frame["date"].apply(lambda x: x.day), unit="d"
            )
            del self.plot_frame["date"]
            self.plot_frame = self.plot_frame.groupby("month_start").sum()
        
        elif agg_level == 'yearly':
            self.plot_frame["year_start"] = self.plot_frame["date"] - pd.to_timedelta(
                self.plot_frame["date"].apply(lambda x: x.timetuple()[7]), unit="d"
            )
            del self.plot_frame["date"]
            self.plot_frame = self.plot_frame.groupby("year_start").sum()


    def _plot_majors(self, columns):
        plot_subject = columns[-1].split('_')[1]
        plot_subject = plot_subject[0].upper() + plot_subject[1:]

        fig, ax = plt.subplots(1,1, figsize=(9,6), dpi=200)
        for col in columns:
            ax.plot(self.plot_frame.index, self.plot_frame[col], label=col.split('_')[0])
        ax.set_xlabel("Date")
        ax.set_ylabel(f"{plot_subject}")
        ax.set_title(f"{plot_subject} by Channel")
        fig.legend(loc="upper right")
        plt.savefig(f'{plot_subject}_by_channel.png')