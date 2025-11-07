from pysimmmulator import study, batch_study

def test_single_channel_study():
    google = study("search", 1.600)
    assert 0.0 < google.generate()[0] < 3.20

def test_dynamic_single_channel_study():
    google = study("search", 1.600)
    results = google.generate_dynamic([i/10.0 for i in range(5)], [i/10.0 for i in range(5)])
    assert len(results) == 5 

def test_multiple_channel_study():
    channel_spec = {"google_search": 1.600, "youtube": 9.01}
    batch = batch_study(channel_spec)
    assert 0.0 < batch.generate()["youtube"][0] < 20.06

def test_dynamic_multiple_channel_universal_study():
    channel_spec = {"google_search": 1.600, "youtube": 9.01}
    batch = batch_study(channel_spec)
    results = batch.generate_dynamic(universal_bias=[i/10.0 for i in range(5)], universal_stdev=[i/10.0 for i in range(5)])
    assert 0.0 < results["youtube"][0] < 20.06

def test_dynamic_multiple_channel_study():
    channel_spec = {"google_search": 1.600, "youtube": 9.01}
    batch = batch_study(channel_spec)
    results = batch.generate_dynamic(channel_bias={"google_search":[i/10.0 for i in range(5)],
                                                   "youtube":[i/10.0 for i in range(5)]},
                                     channel_stdev={"google_search":[i/10.0 for i in range(5)],
                                                    "youtube":[i/10.0 for i in range(5)]})
    assert 0.0 < results["youtube"][0] < 20.06
