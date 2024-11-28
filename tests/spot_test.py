import pandas as pd
import numpy as np
from pysimmmulator import load_parameters, simmm

cfg = load_parameters.load_config(config_path="./example_config.yaml")
my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
sim = simmm(my_basic_params)
sim.simulate_baseline(**cfg["baseline_params"])
sim.simulate_ad_spend(**cfg["ad_spend_params"])
sim.simulate_media(**cfg["media_params"])
sim.simulate_cvr(**cfg["cvr_params"])

date_backbone = pd.date_range(
    start=sim.basic_params.start_date, end=sim.basic_params.end_date, freq="D"
)
campaigns_in_period = (
    date_backbone.shape[0] / sim.basic_params.frequency_of_campaigns
)
campaign_id_to_date_map = np.trunc(
    np.linspace(
        start=0, stop=campaigns_in_period - 1, num=date_backbone.shape[0]
    )
).astype(int)
sim.mmm_df = pd.DataFrame(
    {"date": date_backbone, "id_map": campaign_id_to_date_map}
)
sim.mmm_df.set_index("id_map", inplace=True)


agg_media_df = sim.spend_df.groupby(["channel", "campaign_id"]).sum()[
    ["daily_impressions", "daily_clicks", "daily_spend", "noisy_cvr"]
]
agg_media_df = agg_media_df.unstack(level=0)
joined_columns = []
for _metric, _channel in agg_media_df.columns:
    # we'll just name everything channel_metric from here. No need for daily/lifetime
    col_name = f"{_channel}_{_metric.split('_')[1]}"
    joined_columns.append(col_name)
agg_media_df.columns = joined_columns

print(sim.mmm_df)

print(agg_media_df)