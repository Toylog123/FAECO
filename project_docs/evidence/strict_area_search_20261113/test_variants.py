"""Pure variant-recipe admission tests; no EDA."""
import copy
import pytest
from run_variants import variant_recipe


def original():
    return {'applied':[{'instance':'_054_','old_cell':'sky130_fd_sc_hd__or3b_1','new_cell':'sky130_fd_sc_hd__or3b_4'},
                       {'instance':'_096_','old_cell':'sky130_fd_sc_hd__nor4_1','new_cell':'sky130_fd_sc_hd__nor4_2'}]}


def test_changes_exactly_one_target_preserves_input():
    source=original(); before=copy.deepcopy(source)
    result=variant_recipe(source)
    expected=copy.deepcopy(before);expected['applied'][0]['old_cell']='sky130_fd_sc_hd__or3b_2'
    assert result==expected and source==before


@pytest.mark.parametrize('bad',['source','target','missing','duplicate'])
def test_unexpected_recipe_rejected(bad):
    source=original()
    if bad=='source':source['applied'][0]['new_cell']='sky130_fd_sc_hd__or3b_2'
    if bad=='target':source['applied'][0]['old_cell']='sky130_fd_sc_hd__or3b_2'
    if bad=='missing':source['applied'].pop(0)
    if bad=='duplicate':source['applied'].append(copy.deepcopy(source['applied'][0]))
    with pytest.raises(ValueError):variant_recipe(source)
