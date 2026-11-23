#!/usr/bin/env python3
"""Replay the AES matrix physical evaluator with zero edits and fresh DRT/RCX."""

import json
from pathlib import Path
import sys

import compare_ibex as comparison
from run_screened_matrix import bind_runtime, CLOCK_NAME


def main():
    parser = comparison.create_parser(description=__doc__)
    parser.add_argument("--routing-config", required=True, type=Path)
    parser.add_argument("--matrix-config", required=True, type=Path)
    args = comparison.prepare_args(parser, parser.parse_args())
    if args.pdk != "sky130hd" or not args.embedded_guides or args.zero_reextract or not args.probe_only:
        parser.error("the zero-edit control requires embedded guides and --probe-only with fresh DRT")
    try:
        matrix = json.loads(args.matrix_config.read_bytes())
        top = matrix["top"]
        if top != "aes_cipher_top" or matrix["route_guide_source"] != "embedded in frozen CONTROL ODB":
            raise ValueError("expected the embedded-guide AES matrix CONTROL")
        setup = (args.threads, args.route_mode, args.droute_iters, args.route_timeout, args.sta_timeout,
                 args.sec_timeout, args.report_setup_endpoints)
        if setup != tuple(matrix[key] for key in (
            "methods_route_threads", "route_mode", "route_drt_iters", "route_timeout_seconds",
            "sta_timeout_seconds_per_view", "sec_timeout_seconds", "report_setup_endpoints",
        )):
            raise ValueError("zero-edit probe settings differ from the AES matrix")
        bindings = matrix["bindings"]
        route = args.routing_config.resolve(strict=True)
        for expected, path in (
            (bindings["qualification_receipt"], args.views_json), (bindings["original_sdc"], args.original_sdc),
            (bindings["control_drc"], args.control_drc), (bindings["tools"]["openroad"], args.openroad),
            (bindings["tools"]["opensta"], args.sta), (bindings["tools"]["sec"], args.sec),
            (bindings["flow"][route.name], route),
            *((item, args.control_dir / f"6_final.{ext}") for ext, item in bindings["control"].items()),
        ):
            if comparison.bind(path) != expected:
                raise ValueError(f"AES matrix input binding mismatch: {path}")
        helper_sources = [Path(item["path"]) for item in bindings["driver_source"].values()]
        with bind_runtime(top, route):
            return comparison.run(args, config_overrides={
                "purpose": "zero-edit diagnostic from the unchanged AES matrix start",
                "clock": CLOCK_NAME, "matrix_config": comparison.bind(args.matrix_config.resolve()),
            }, extra_sources=(Path(__file__), *helper_sources))
    except (comparison.TrialFailure, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
