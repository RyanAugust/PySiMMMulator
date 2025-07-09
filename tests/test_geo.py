from pysimmmulator import load_parameters, simmm, geos

def test_random_geo_create():
    geo_maker = geos(total_population=330_000_000)
    geo_details = geo_maker(count=200)
    assert 1 == 1

def test_geo_create():
    geo_specs = {"ABC": {"loc":1.0, "scale": 2.0}}
    geo_maker = geos(total_population=330_000_000)
    geo_details = geo_maker(geo_specs=geo_specs, universal_scale=1.0)
    assert 1 == 1
