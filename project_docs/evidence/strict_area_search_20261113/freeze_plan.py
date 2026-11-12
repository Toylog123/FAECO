"""One-time local-history plan builder. Refuses an existing plan or run outputs."""
import json
import analyze_repair as audit
import local_data as data
import selection


def main():
    here = data.HERE
    audit.require(not (here/'PLAN.json').exists() and not (here/'runs').exists(), 'Plan/run already exists; no refreeze')
    dataset = data.history()
    plan = data.proposal(dataset)
    control = dataset[1]
    sources = ['PREREGISTRATION.md','selection.py','test_selection.py','local_data.py','run_search.py','freeze_plan.py',
               'physical_probe.py','analyze_repair.py','structure_reader.py','COPY_MANIFEST.json','LOCAL_INPUT_MAP.json',
               'TOOLCHAIN_PRECHECK.json']
    shared = ['code/scripts/recover_area.py','code/scripts/run_sequential_timing_check.py','code/src/rseco/opensta.py',
              'code/src/rseco/routed_sta.py',str(audit.LIB.relative_to(audit.ROOT)).replace('\\','/')]
    plan.update(schema=1,scope='s382 fixed 096 seed, complete nine positive-area pair star; no production optimizer',
                tolerance_ns=selection.TOL,norms_ns=selection.NORMS,measurement_order=sorted(plan['singletons']),
                seed=dataset[4],control={key:control[key] for key in ('area','metrics','hashes')},
                source_sha256={name:audit.sha(here/name) for name in sources},
                shared_dependency_sha256={name:audit.sha(audit.ROOT/name) for name in shared},
                timeouts_s={'route':900,'sta':300,'child':1530,'batch':1800},
                reused_history_cost={'isolated_observation_routes':13,'isolated_observation_sta':26,
                                     'broader_seed_discovery_routes':41,'note':'13 is a subset of 41; not additive; seed proof reused'},
                primary_budget=3,secondary_budgets=[1,6,9],max_new_routes=9,max_new_sta=18)
    with (here/'PLAN.json').open('x',encoding='utf-8') as stream:
        json.dump(plan,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({'plan_sha256':audit.sha(here/'PLAN.json'),'orders':plan['orders']}))


if __name__ == '__main__':
    main()
