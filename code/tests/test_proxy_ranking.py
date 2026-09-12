from rseco.proxy_ranking import ProxyWeights, rank_real_candidates


def test_proxy_ranking_prefers_library_gain_and_critical_coverage():
    candidates = [
        {
            "instance": "_late_",
            "kind": "G",
            "from_type": "sky130_fd_sc_hd__nor2_1",
            "to_type": "sky130_fd_sc_hd__nor2_2",
            "strategy_rank": 1,
            "critical_rank": 1,
            "critical_count": 2,
            "patch_size": 1,
            "boundary_complexity": 2,
        },
        {
            "instance": "_early_",
            "kind": "G",
            "from_type": "sky130_fd_sc_hd__nor2_1",
            "to_type": "sky130_fd_sc_hd__nor2_4",
            "strategy_rank": 1,
            "critical_rank": 0,
            "critical_count": 2,
            "patch_size": 1,
            "boundary_complexity": 2,
        },
    ]

    ranked = rank_real_candidates(candidates)

    assert ranked[0]["instance"] == "_early_"
    assert ranked[0]["proxy_rank"] == 1
    assert ranked[0]["proxy_features"]["timing_gain"] > 0
    assert ranked[0]["proxy_features"]["critical_path_coverage"] == 1.0


def test_proxy_ranking_uses_stable_tie_break():
    candidates = [
        {
            "instance": "_b_",
            "kind": "R",
            "from_type": "sky130_fd_sc_hd__or2_1",
            "to_type": "sky130_fd_sc_hd__or2_1_alt",
            "strategy_rank": 0,
            "critical_rank": 0,
            "critical_count": 1,
            "patch_size": 1,
            "boundary_complexity": 1,
        },
        {
            "instance": "_a_",
            "kind": "R",
            "from_type": "sky130_fd_sc_hd__or2_1",
            "to_type": "sky130_fd_sc_hd__or2_1_alt",
            "strategy_rank": 0,
            "critical_rank": 0,
            "critical_count": 1,
            "patch_size": 1,
            "boundary_complexity": 1,
        },
    ]

    ranked = rank_real_candidates(candidates, weights=ProxyWeights())

    assert [row["instance"] for row in ranked] == ["_a_", "_b_"]
