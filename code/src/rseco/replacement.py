"""Internal patch replacement representation for early FAECO flow."""

from dataclasses import dataclass

from .graph import FaninCone
from .patch import PatchCandidate


@dataclass(frozen=True)
class PatchReplacementResult:
    case_id: str
    method: str
    status: str
    patch_id: str
    source_cone: str
    original_roots: list[str]
    replaced_gates: list[str]
    preserved_gates: list[str]
    boundary_inputs: list[str]
    boundary_outputs: list[str]
    patched_outputs: list[str]
    patch_size: int

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "method": self.method,
            "status": self.status,
            "patch_id": self.patch_id,
            "source_cone": self.source_cone,
            "original_roots": self.original_roots,
            "replaced_gates": self.replaced_gates,
            "preserved_gates": self.preserved_gates,
            "boundary_inputs": self.boundary_inputs,
            "boundary_outputs": self.boundary_outputs,
            "patched_outputs": self.patched_outputs,
            "patch_size": self.patch_size,
        }


def apply_patch_replacement(
    *,
    case_id: str,
    cone: FaninCone,
    patch: PatchCandidate,
) -> PatchReplacementResult:
    """Apply a selected patch to the cone-level internal representation."""
    cone_gate_set = set(cone.gates)
    missing_gates = [gate for gate in patch.gates if gate not in cone_gate_set]
    if missing_gates:
        raise ValueError(f"patch gates are outside source cone: {', '.join(missing_gates)}")

    replaced_gate_set = set(patch.gates)
    return PatchReplacementResult(
        case_id=case_id,
        method="internal_cone_replacement_v0",
        status="applied",
        patch_id=patch.patch_id,
        source_cone=patch.source_cone,
        original_roots=list(cone.roots),
        replaced_gates=list(patch.gates),
        preserved_gates=[gate for gate in cone.gates if gate not in replaced_gate_set],
        boundary_inputs=list(patch.boundary_inputs),
        boundary_outputs=list(patch.boundary_outputs),
        patched_outputs=list(patch.boundary_outputs),
        patch_size=patch.patch_size,
    )
