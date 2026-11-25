from verify_rank_alignment import first_area_hit, same_realized_areas


def test_equal_area_and_equal_threshold_are_reported_independently():
    accepted = [
        {"request_id": 1, "elapsed_seconds": 150.0, "area_saved": 26.27520000001},
        {"request_id": 2, "elapsed_seconds": 220.0, "area_saved": 48.7968},
        {"request_id": 3, "elapsed_seconds": 720.01, "area_saved": 57.5552},
    ]
    assert first_area_hit(accepted, 26.2752, exact=True)["request_id"] == 1
    assert first_area_hit(accepted, 45.0432, exact=False)["request_id"] == 2
    assert first_area_hit(accepted, 45.0432, exact=True) is None
    assert first_area_hit(accepted, 57.5552, exact=False) is None


def test_pairwise_comparison_requires_the_same_delivered_area():
    fixed = [{"request_id": 1, "elapsed_seconds": 140.0, "area_saved": 26.2752},
             {"request_id": 2, "elapsed_seconds": 213.0, "area_saved": 48.7968}]
    adaptive = [{"request_id": 1, "elapsed_seconds": 139.0, "area_saved": 26.27520000001},
                {"request_id": 2, "elapsed_seconds": 215.0, "area_saved": 50.048}]
    result = same_realized_areas(fixed, adaptive)
    assert len(result) == 1
    assert result[0]["area_um2"] == 26.2752
    assert result[0]["first_minus_second_raw_s"] == 1.0
