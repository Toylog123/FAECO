"""Patch candidate representation."""

from dataclasses import dataclass

from .cut import CutBoundary
from .equivalence import EquivalenceResult


@dataclass(frozen=True)
class PatchCandidate:
    case_id: str
    patch_id: str
    source_cone: str
    cut_method: str
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    gates: list[str]
    patch_size: int
    equivalence_result: str
    equivalence_method: str
    status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "patch_id": self.patch_id,
            "source_cone": self.source_cone,
            "cut_method": self.cut_method,
            "boundary_inputs": self.boundary_inputs,
            "boundary_outputs": self.boundary_outputs,
            "gates": self.gates,
            "patch_size": self.patch_size,
            "equivalence_result": self.equivalence_result,
            "equivalence_method": self.equivalence_method,
            "status": self.status,
        }


def make_patch_candidate(
    *,
    case_id: str,
    boundary: CutBoundary,
    equivalence: EquivalenceResult,
) -> PatchCandidate:
    root = boundary.boundary_outputs[0]
    status = "structural_checked" if equivalence.status == "pass" else "equivalence_failed"
    return PatchCandidate(
        case_id=case_id,
        patch_id=f"patch_{root}_{boundary.method}",
        source_cone=f"cone_{root}",
        cut_method=boundary.method,
        boundary_inputs=boundary.boundary_inputs,
        boundary_outputs=boundary.boundary_outputs,
        gates=boundary.gates,
        patch_size=boundary.patch_size,
        equivalence_result=equivalence.status,
        equivalence_method=equivalence.method,
        status=status,
    )
