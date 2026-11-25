import pytest

from run_qualified_wallclock import comparison, rank_qualified_actions


def action(name, area):
    return comparison.PhysicalAction(name, name, "large", "small", area)


def test_all_inf_actions_stay_in_frozen_tail_and_finite_pins_keep_the_existing_score():
    pool = [action("untimed_large", 10), action("mixed", 3), action("untimed_small", 1), action("timed", 4)]
    log = "\n".join(("RANK_WNS_PS -10", "RANK_PIN untimed_large Y Inf", "RANK_PIN mixed Y 30",
                     "RANK_PIN mixed X Inf", "RANK_PIN untimed_small Y Inf", "RANK_PIN timed Y 0"))

    result = rank_qualified_actions(pool, log, -10)

    assert result["ordered_action_ids"] == ["mixed", "timed", "untimed_large", "untimed_small"]
    assert result["rows"]["mixed"]["pins_without_finite_setup_slack"] == ["X"]
    assert result["rows"]["untimed_large"]["score"] is None
    assert result["unconstrained_tail_action_ids"] == ["untimed_large", "untimed_small"]


@pytest.mark.parametrize("observations", ("", "RANK_PIN g Y NaN", "RANK_PIN g Y -Inf",
                                           "RANK_PIN g Y 0\nRANK_PIN g Y Inf", "RANK_PIN unknown Y Inf"))
def test_unexpected_or_missing_rank_observations_still_fail(observations):
    with pytest.raises(ValueError):
        rank_qualified_actions([action("g", 1)], "RANK_WNS_PS -10\n" + observations, -10)
