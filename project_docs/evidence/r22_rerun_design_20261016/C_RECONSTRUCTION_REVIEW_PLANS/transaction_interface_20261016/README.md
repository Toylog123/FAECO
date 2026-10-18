# C 重建执行接口：审查预览，未登记、未执行

本包交付 `C_RECONSTRUCTION_ADAPTER/register_run.py` 和限定 `test_register_run.py`。它只把冻结 C `run_frozen` 包在事务中，不实现另一搜索器，不调用 outerloop/C′，不调用 mapper。48 个 job 的完整 recipe、配置、保留 mapped 路径/SHA、精确子进程 argv 已写入 `plan_preview.json`。历史 runtime argv/source 继续为 null；明示的新重建选择不能倒填为历史事实。

当前预览 HEAD 为 `3ea0f757f5e9bab4a2df75c458b0c665eabcb258`，源码干净标志为 false，**不能注册**。source_manifest 共 57 项，包括生产 common 来源、旧 hybrid helper、适配器/限定 QA/历史预览/恢复依据和 timeout wrapper。工具二进制、启动器 SHA 和版本在明确正式 register 时采集；build-preview 不启动任何 EDA 或工具版本进程。Python、bash、wsl.exe、Ubuntu STA/Yosys 的身份在正式执行前后重核。

正式操作须等 C′72 验收后，由 root 审查、提交本工具，再用新 clean HEAD 重建外置 preview。示例仅说明接口，不授权现在执行：

```powershell
.venv/Scripts/python.exe project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER/register_run.py build-preview --output-dir project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_RUNS/<new-id> --plan project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_REVIEW_PLANS/<new-review-id>/plan.json
.venv/Scripts/python.exe project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER/register_run.py register --output-dir project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_RUNS/<new-id> --plan project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_REVIEW_PLANS/<new-review-id>/plan.json
.venv/Scripts/python.exe project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER/register_run.py run --manifest project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_RUNS/<new-id>/manifest.json --arm hybrid --circuit s27
.venv/Scripts/python.exe project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER/register_run.py verify --manifest project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_RUNS/<new-id>/manifest.json --arm hybrid --circuit s27
```

register 要求全新专属 `C_RECONSTRUCTION_RUNS` 子目录、clean source 和逐字相同的当前 recipe/source/input/Lib；manifest 和 registration.json 都 exclusive 写入。后者固定 manifest 的原始 SHA，因此在 job 之间只改空白也拒绝。每个 job 独占新目录，保存 preregistered.json、原始 retained_mapped.v、完整 actual_run.json 关联、stdout/stderr、native run 全产物。外层命令使用既有 timeout wrapper 3900 秒和父 subprocess 3930 秒监测，超时保存部分输出并失败。

`guarded-run` 是 run 自动调用的内部入口；单独调用不能跳过 preregistration。它以 FunctionType 复制 `run_frozen` 的函数作用域，仅替换该局部视图的 PinGuard 构造器，使原有内部 guard 同时核 manifest 字节、registration anchor、preregistered/actual 关联及 staged input，不改冻结模块 global 或搜索调度。实际配置仍由冻结 recipe 解析，不能从 CLI 偷加覆盖参数。

完成验收重新核 native 与事务两层完整 artifact inventory/SHA、实际配置、raw/text 输入身份、按 measured trial 绑定的连续 commit chain、终点网表、STA reservation/launch/failed 计数、有限 WNS、实际 SEC raw/results/splits/helpers、当前 actual Liberty 独立静态生成的 cells 模型，以及非零 proven/零 unproven/success 且无 NoSAT 的证明日志。QA 或 simulated=true 不能升级为 scientific complete。失败只留新 failure.json 和当时完整 artifact hashes，不覆盖，不自动 resume；verify 不会重跑或修复失败任务。

本接口没有增加矩阵调度器。正式工具/EDA 整合仍未运行，无法据此声称 C48 已重验；旧 F2 支持域和 Boolean SEC 限制继续有效。

## OI-042 最小补修及保留原证据

独立审查的原始 `C_ADAPTER_REVIEW/REVIEW.json`、原 probe 和适配器旧 `QA_REPORT.json` 均保持原字节。六个冻结原件事前备份在 `scratch/r22_C_adapter_pre_OI042_fix_20261016/`，含 before_sha256.json。

精确原 probe 红重放仍得到 1 commit、qa_complete，captured Tcl 与 live Tcl SHA 不同，证实此前 README 的 finally 描述超过当时实现。随后仅修改 adapter.py/test_adapter.py：每次调用 finally 和 helper 返回时重新核同一 input_snapshot；actual read_liberty 必须唯一且指向注册 common.LIB，并前后核真实 bytes/SHA。不更改 STA 命令、重试/选优/JOINT 调度，也不修改 immutable 历史 snapshot。

新增 8 控制先 8 fail 后 8 pass，精确旧 probe 补修后返回 1/PinDrift，0 commit 且无 completion。完整限定验证为 **84 passed / 81.73 秒**：原 38 + OI-042 新 8 + 注册事务 38。QA 所有 STA/SEC 外部边界均为 stub；八份真实 retained C 输入仅接受静态门检查，未执行 EDA。

日志、当前八文件 SHA、57 项 source manifest、与独立审查比对的 production SHA、精确红/绿证据和限制均见同目录新 `QA_REPORT.json`。本预览输出目标目录仍不存在，没有正式 manifest 或正式 job。
