# C′ v3 输入准备与静态门

新输出目录为 `experiments/20261016_r22_cut_ablation_v3`。旧 v1 失败原件、v2 仅登记原件保留，均不复用为本轮输入。

`prepare_inputs.py` 只接受 common runner 已登记的 manifest。正式执行要求 HEAD、production 与准备器已提交且洁净，逐例首次映射并冻结完整字节；existing/orphan/partial 输出不覆盖。真实 required-input、模型支持域、实例唯一及 F2 identity 均需通过，并在每次映射及收尾复核所有已验输入与 artifact 哈希。此处**不是 RTL→mapped 等价证明**，未运行该项也不宣称完成。

准备器 SHA256：`22a3254cbe6b93d3a23e877b07f7097fd46a92b85c0b6430a1eb178d3b5f481a`。限定 TDD：先红，跨例漂移再红，最终 20 passed / 0.78 s。QA 原件按来源与哈希归档；production/tests 仍与完整回归 v5 的 166 文件一致。

执行顺序：锁新 HEAD → common `--dry-run` 登记 72 jobs → 本工具 `--dry-run` 纯静态检查 → 真实准备八份 mapped 与 `preflight.json` → 复核静态门与实际 input receipt → common 仅 `s27,s382` 的 18 项 pilot → 全部最终 SEC/真实计数验收后才扩余下 54 项。每阶段实际状态以 manifest/preflight/独立运行收据与当前交接为准，不按本说明预填成功。

## QA重跑路径

qa/是来源字节保真的原件，不是改过根路径的便携测试包。测试的R=parents[2]依赖原scratch/r22_cprime_v3_20261016位置；直接运行qa副本曾20例FileNotFoundError，均未触生产代码。应在原scratch位置重跑，或在新副本显式适配路径/另锁SHA，不修改归档原件。root在最终源码原scratch位置已再测20pass/1.10s；该回显不替代当前完整v7结果。
