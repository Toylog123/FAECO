#!/usr/bin/env bash
# Linux input capture and private-namespace reconstruction of the Stage 5 reference.
set -euo pipefail

readonly paper_commit=c4ede33ddcb4400184a115f4718fe8adeabd6935
readonly orfs_commit=da8f092a02a8e75658cc3100691aabff05f35629
readonly historical_home=/home/toylog
readonly historical_repo=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
readonly historical_run=$historical_home/faeco_v5_step5_riscv32i_tc40ns_mmmc_drv_20261127_v1
readonly openroad_bin=$historical_home/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped
readonly openroad_alias=$historical_home/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad
readonly source_protocol_sha=7654c67b777694a0b8f0697912e920ce572f63bb29768cfc1c25bdf3397167cd
readonly source_receipt_sha=05c29db7ab321a9b38a9fae0f0094ff280047ad10801886371267399755e75dd
readonly source_qualification_sha=ce7b57b58e1d9968ce07876fe36911293ca32d66de090c9b975eee478350d9d7
readonly source_directive=project_docs/evidence/tcad_v5_revision_20261126/run_v5_stage5_reference.py

record_links() {
    find project home local-bin -type l -printf '%p\t%l\n' | LC_ALL=C sort
}

record_files() {
    find project home local-bin comparison driver.sh -type f -print0 | LC_ALL=C sort -z
}

capture() {
    local repo=$1 bundle=$2 path name
    local evidence=project_docs/evidence
    test "$(git -C "$historical_home/faeco_eda/orfs" rev-parse HEAD)" = "$orfs_commit"
    test -z "$(git -C "$historical_home/faeco_eda/orfs" status --porcelain --untracked-files=no)"
    test -z "$(git -C "$historical_home/faeco_eda/orfs" ls-files flow/logs flow/objects flow/reports flow/results)"
    printf '%s  %s\n' "$source_protocol_sha" "$historical_run/build_protocol.json" \
        "$source_receipt_sha" "$historical_run/build_receipt.json" \
        "$source_qualification_sha" "$historical_run/qualification/CONTROL.json" | sha256sum -c --quiet
    mkdir -- "$bundle"
    bundle=$(realpath -e -- "$bundle")
    mkdir -- "$bundle"/{project,home,local-bin,comparison}
    git -C "$repo" archive "$paper_commit" -- code/src \
        "$evidence/tcad_v5_revision_20261126" "$evidence/tcad_boxed_drc_20261126" \
        "$evidence/tcad_external_baselines_20261125" "$evidence/tcad_ibex_20261123" \
        "$evidence/tcad_holdout_20261123" "$evidence/tcad_wallclock_schedule_20261125" \
        "$evidence/tcad_asap7_aes_holdout_20261125" | tar -x -C "$bundle/project"
    mkdir -- "$bundle/home/faeco_eda"
    # The installed ORFS tree is a partial clone. Preserve its checked-out files
    # and local Git metadata so a replay never needs to fetch missing history.
    rsync -a --exclude='/.mirror_used' --exclude='/flow/logs/' --exclude='/flow/objects/' \
        --exclude='/flow/reports/' --exclude='/flow/results/' -- \
        "$historical_home/faeco_eda/orfs/" "$bundle/home/faeco_eda/orfs/"
    test "$(git -C "$bundle/home/faeco_eda/orfs" rev-parse HEAD)" = "$orfs_commit"
    test -z "$(git -C "$bundle/home/faeco_eda/orfs" status --porcelain --untracked-files=no)"
    cp -a --reflink=auto -- "$historical_home/faeco_eda/oss-latest" "$bundle/home/faeco_eda/"
    for path in "$openroad_bin" \
        "$historical_home/faeco_tcad_anytime_holdouts_20261125_v1/sta_native.py" \
        "$historical_home/faeco_tcad_anytime_holdouts_20261125_v1/sec_native.py"; do
        local suffix=${path#"$historical_home"/}
        mkdir -p -- "$bundle/home/$(dirname -- "$suffix")"
        cp -pL --reflink=auto -- "$path" "$bundle/home/$suffix"
    done
    mkdir -p -- "$bundle/home/$(dirname -- "${openroad_alias#"$historical_home"/}")"
    ln -s -- "$openroad_bin" "$bundle/home/${openroad_alias#"$historical_home"/}"
    mkdir -p -- "$bundle/home/rseco_timing/vendor/OpenROAD-b511b6a/test/sky130hd"
    for path in "$historical_home"/rseco_timing/vendor/OpenROAD-b511b6a/test/sky130hd/sky130_fd_sc_hd__{ff,ss}*.lib; do
        cp -pL --reflink=auto -- "$path" "$bundle/home/rseco_timing/vendor/OpenROAD-b511b6a/test/sky130hd/"
    done
    for name in yosys sta sta-3.1.0; do
        cp -a -- "/usr/local/bin/$name" "$bundle/local-bin/"
    done
    cp -p -- "$historical_run"/{build_protocol,build_receipt}.json "$historical_run/qualification/CONTROL.json" \
        "$bundle/comparison/"
    cp -p -- "$0" "$bundle/driver.sh"
    cd -- "$bundle"
    record_files > FILES.list0
    xargs -0 sha256sum < FILES.list0 > FILES.sha256
    record_links > LINKS.tsv
    printf 'Captured %s source files and %s symlinks.\n' "$(wc -l < FILES.sha256)" "$(wc -l < LINKS.tsv)"
}

mount_readonly() {
    mount --bind "$1" "$2"
    mount -o remount,bind,ro "$2"
}

isolated() {
    local bundle=$1 output= script= rebuilt= state uid_start uid_source uid_count
    if [[ $# == 2 ]]; then
        output=$2
    elif [[ $# == 4 ]]; then
        script=$2
        rebuilt=$3
        output=$4
    fi
    read -r uid_start uid_source uid_count < /proc/self/uid_map
    if [[ $uid_start != 0 || $uid_source == 0 || $uid_count != 1 ||
          -z ${FAECO_STAGE5_PARENT_MOUNT_NS:-} ||
          $(readlink /proc/self/ns/mnt) == "$FAECO_STAGE5_PARENT_MOUNT_NS" ]]; then
        echo 'The internal phase requires a private rootless user and mount namespace.' >&2
        exit 2
    fi
    cd /
    mount --make-rprivate /
    mount -t tmpfs -o mode=0755 stage5-home /home
    mount -t tmpfs -o mode=0755 stage5-mnt /mnt
    mount -t tmpfs -o mode=0755 stage5-local-bin /usr/local/bin
    mkdir -p -- "$historical_home" "$historical_repo"
    mount_readonly "$bundle/home" "$historical_home"
    mount_readonly "$bundle/project" "$historical_repo"
    mount_readonly "$bundle/local-bin" /usr/local/bin
    test ! -e "$historical_run"
    test ! -e "$historical_repo/.git"
    for state in logs objects reports results; do
        test ! -e "$historical_home/faeco_eda/orfs/flow/$state"
    done
    test "$(stat -c '%d:%i' "$bundle/project/code/src")" = "$(stat -c '%d:%i' "$historical_repo/code/src")"
    test "$(git -C "$historical_home/faeco_eda/orfs" rev-parse HEAD)" = "$orfs_commit"

    cd -- "$historical_repo"
    PYTHONDONTWRITEBYTECODE=1 python3 -B - "$bundle" <<'PY'
from pathlib import Path
import json
import sys

bundle = Path(sys.argv[1])
stored = json.loads((bundle / "comparison/build_protocol.json").read_bytes())
sys.path.insert(0, str(Path("project_docs/evidence/tcad_v5_revision_20261126").resolve()))
from run_v5_stage5_reference import MMMC_DRV_VARIANT, SOURCE_SDC, cmp, render_source_sdc
from hashlib import sha256

regenerated = render_source_sdc(SOURCE_SDC.read_text(), MMMC_DRV_VARIANT).encode()
paths = [item for item in stored["inputs"] if "/constraint_tc40ns_mmmc_drv.sdc" not in item["path"]]
generated = [item for item in stored["inputs"] if "/constraint_tc40ns_mmmc_drv.sdc" in item["path"]]
if len(generated) != 1 or sha256(regenerated).hexdigest() != generated[0]["sha256"]:
    raise ValueError("generated Stage 5 SDC differs from the frozen constraint")
for item in paths:
    path = Path(item["path"])
    if cmp.bind(path) != item:
        raise ValueError(f"frozen Stage 5 build input differs: {path}")
print(f"Validated {len(paths)} frozen build paths and the independently rendered SDC.")
PY
    /usr/local/bin/yosys -V
    "$openroad_bin" -version
    printf 'Isolated historical input aliases are read-only; prior Stage 5 output is absent.\n'
    if [[ -n $script ]]; then
        exec env -i HOME="$historical_home" USER=toylog LOGNAME=toylog \
            PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TERM=xterm-256color PYTHONDONTWRITEBYTECODE=1 \
            python3 -B "$script" --rebuilt "$rebuilt" --output-root "$output"
    fi
    if [[ -n $output ]]; then
        mkdir -- "$output"
        mkdir -- "$output/tmp" "$output/cache"
        exec env -i HOME="$historical_home" USER=toylog LOGNAME=toylog \
            PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TERM=xterm-256color PYTHONDONTWRITEBYTECODE=1 \
            TMPDIR="$output/tmp" XDG_CACHE_HOME="$output/cache" \
            python3 -B "$source_directive" --variant tc40ns_mmmc_drv --output-root "$output"
    fi
}

require_visible() {
    case "$1/" in
        /home/*|/mnt/*|/usr/local/bin/*) echo "Path would be masked by the isolated roots: $1" >&2; exit 2 ;;
    esac
}

main() {
    local phase=${1:-} bundle output script rebuilt argument_count
    case "$phase" in
        capture) [[ $# == 3 ]] || exit 2; capture "$2" "$3" ;;
        probe|run|candidate)
            case "$phase" in
                probe) argument_count=2 ;;
                run) argument_count=3 ;;
                candidate) argument_count=5 ;;
            esac
            [[ $# == "$argument_count" ]] || exit 2
            bundle=$(realpath -e -- "$2")
            require_visible "$bundle"
            (cd "$bundle"; record_files | cmp - FILES.list0; sha256sum -c --quiet FILES.sha256; record_links | cmp - LINKS.tsv)
            export FAECO_STAGE5_PARENT_MOUNT_NS
            FAECO_STAGE5_PARENT_MOUNT_NS=$(readlink /proc/self/ns/mnt)
            if [[ $phase == probe ]]; then
                exec unshare --user --map-root-user --mount --net -- \
                    bash "$bundle/driver.sh" inside "$bundle"
            fi
            output=$(realpath -m -- "${!argument_count}")
            require_visible "$output"
            case "$output/" in
                "$bundle/"*) echo 'Put the new output outside the input bundle.' >&2; exit 2 ;;
            esac
            test ! -e "$output"
            if [[ $phase == candidate ]]; then
                script=$(realpath -e -- "$3")
                rebuilt=$(realpath -e -- "$4")
                require_visible "$script"
                require_visible "$rebuilt"
                exec unshare --user --map-root-user --mount --net -- \
                    bash "$(realpath -e -- "$0")" inside "$bundle" "$script" "$rebuilt" "$output"
            fi
            exec unshare --user --map-root-user --mount --net -- \
                bash "$bundle/driver.sh" inside "$bundle" "$output"
            ;;
        inside) shift; isolated "$@" ;;
        *) echo 'Usage: capture <repo> <bundle> | probe <bundle> | run <bundle> <output> | candidate <bundle> <script> <rebuilt-root> <output>' >&2; exit 2 ;;
    esac
}

main "$@"
