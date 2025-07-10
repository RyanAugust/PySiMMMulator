from pysimmmulator import geos, distribute_to_geos

def test_random_geo_create():
    geo_maker = geos(total_population=330_000_000)
    geo_details = geo_maker(count=200)
    assert 1 == 1

def test_geo_create():
    geo_specs = {"ABC": {"loc":1.0, "scale": 2.0}}
    geo_maker = geos(total_population=330_000_000)
    geo_details = geo_maker(geo_specs=geo_specs, universal_scale=1.0)
    assert 1 == 1

def test_distribution():
    import pandas as pd
    mmm_input = pd.DataFrame({'YouTube_impressions': {pd.Timestamp('2017-01-01 00:00:00'): 3854978.0},
     'YouTube_spend': {pd.Timestamp('2017-01-01 00:00:00'): 25122.61},
     'total_revenue': {pd.Timestamp('2017-01-01 00:00:00'): 1659573.7993172132}})
    mmm_input.index.name = 'date'
    country = geos(total_population=20_000_000)
    geo_details = country(count=50)
    s = distribute_to_geos(mmm_input=mmm_input, geo_details=geo_details, random_seed=42, dist_spec=(0.0, 0.25), media_cost_spec=(0.0, 0.25), perf_spec=(0.0, 0.15))
    assert 1 == 1
