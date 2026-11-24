"""Build a frozen-input area priority penalized by the capacitance touched by a swap."""
import math
import re
from statistics import median

import compare_ibex as comparison


def spef_net_caps_pf(path):
    names, capacitance = {}, {}
    in_names, unit = False, None
    with path.open(encoding="utf-8") as stream:
        for row in stream:
            if row.startswith("*C_UNIT "):
                _, scale, unit_name = row.split()
                unit = float(scale) * {"FF": 0.001, "PF": 1.0, "NF": 1000.0}[unit_name]
            elif row.startswith("*NAME_MAP"):
                in_names = True
            elif row.startswith("*D_NET "):
                in_names = False
                _, token, value = row.split()
                name = comparison.canonical_odb_name(names.get(token, token))
                if name in capacitance or unit is None:
                    raise ValueError(f"duplicate SPEF net or missing capacitance unit: {name}")
                cap = float(value) * unit
                if not math.isfinite(cap) or cap < 0:
                    raise ValueError(f"invalid SPEF capacitance: {name}")
                capacitance[name] = cap
            elif in_names:
                match = re.match(r"^(\*\d+)\s+(\S+)", row)
                if match:
                    names[match[1]] = match[2]
    return capacitance


def build_incident_priority(def_path, spef_path, actions):
    """Read each candidate's directly incident original signal nets and their RCX C."""
    caps = spef_net_caps_pf(spef_path)
    routes = comparison.def_section(def_path, "NETS")
    instances = {
        comparison.canonical_odb_name(action.instance.removeprefix("\\")): action for action in actions
    }
    if len(instances) != len(actions) or not instances:
        raise ValueError("expected a nonempty pool of distinct editable instances")
    incident = {name: set() for name in instances}
    for net, record in routes.items():
        if re.search(r"\+ USE (POWER|GROUND)\b", record):
            continue
        endpoints = {
            comparison.canonical_odb_name(instance)
            for instance in re.findall(r"\( (\S+) \S+ \)", record.partition(" + ")[0])
        }
        for instance in endpoints.intersection(instances):
            incident[instance].add(comparison.canonical_odb_name(net))
    sums = {}
    for instance, nets in incident.items():
        if not nets or not nets <= caps.keys():
            raise ValueError(f"missing incident SPEF data for {instance}: {sorted(nets - caps.keys())}")
        sums[instance] = math.fsum(caps[net] for net in sorted(nets))
    divisor = median(sums.values())
    if divisor <= 0:
        raise ValueError("incident capacitance median must be positive")
    return {
        "median_incident_pf": divisor,
        "actions": {
            action.action_id: {
                "incident_nets": {net: caps[net] for net in sorted(incident[instance])},
                "incident_pf": sums[instance],
                "estimated_save": action.estimated_area_saving,
                "priority": action.estimated_area_saving / (1 + sums[instance] / divisor),
            }
            for instance, action in instances.items()
        },
    }
