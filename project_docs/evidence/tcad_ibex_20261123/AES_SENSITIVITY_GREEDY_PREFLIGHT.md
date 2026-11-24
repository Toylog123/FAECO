# AES 灵敏度排序单门贪心预检

2026-11-25 · 同在线诊断后端 · 冻结候选排序预检

## 真实起点评分

冻结 CONTROL 的现有 TT／SS／FF 日志保存全局最差裕量、最差路径与负端点清单。完整候选评分使用同一原始 ODB、SDC、SPEF、TT Liberty，在固定四线程详细布线的 CPU 组内以单线程 OpenROAD 读取 18 个候选实例各自的输出引脚 setup slack。脚本逐个核对实例名，缺失、重复或不可用的引脚数据触发失败。读回的 TT setup WNS 为 −380.500520 ps，与原起点一致。

历史灵敏度规则取实例各输出引脚的最小 setup slack 与 CONTROL WNS 的差值 \(m_i\)，先排 \(m_i>5\) ps 的动作，再按 \(\Delta A_i[0.1+\min(\max(m_i,0),200)/200]\) 降序。同分依次按预估面积和动作 ID 排序。此处 18 门的裕量为 297.415–515.914 ps，全部达到 200 ps 截顶。历史公式完整复现了前轮的候选顺序。

为检验候选优先级对单门搜索的影响，预先冻结去掉 200 ps 截顶的线性权重 \(\Delta A_i[0.1+\max(m_i,0)/200]\)，其余排序规则沿用。新顺序前六为 `_20893_`、`_12777_`、`_10992_`、`_11724_`、`_20897_`、`_13695_`。原顺序前三为 `_10814_`、`_10992_`、`_11167_`。该评分以修改前的 TT setup 裕量分配候选验证优先级。实际换门之后的多角 setup WNS/TNS、绝对和相对 hold、电气与物理门、SEC 仍由同一完整评价链验证。

本次保留的冻结 CONTROL TT 预检查询耗时 3.452 s，连同脚本写入和结果解析耗时 3.454 RAW s。实际候选派发、DRT、RCX、候选三角 STA、独立 DRC、天线和候选 SEC 均为零。独立审计由真实日志重算全部输入、18 条输出裕量、两条顺序和饱和数。AES 专项 WSL 测试为 23 项通过。

## 正式比较规约

从共同的原始物理 CONTROL、已验收零动作起点及 18 个冻结候选出发，分别以单门灵敏度顺序和 FAECO 的原调度正反序串行运行。每个单门臂在其 720 RAW s 硬窗内新做一次 TT 排序查询，实际时间进入子进程台账和搜索墙钟。每臂仍计相同的 113.363032440 RAW s 历史筛选、最多六次逻辑请求和固定功能单元面积 0.01%（11.65079904 µm²）的首达下限。单门按初始灵敏度顺序逐个测试，其前序已接受动作持续累积。FAECO 沿用原三门起批及相对 hold 拒绝后的电容重排。正式结果保留两个指标、真实首达面积、端点身份与删失状态。

原 SDC／I/O、3.6 ns 周期、逐角 setup WNS 损失上限 36 ps、FF／TT／SS TNS 损失上限 360／360／27049.177334 ps、逐角非负且相对不退化 hold（0.001 ps 容差）、电气与正面积门、零独立 DRC 和天线及非空两态 SEC 沿用前轮。[同后端原顺序单门对照](AES_ONLINE_GREEDY_REPORT.md)

```bash
r=/home/toylog/faeco_tcad_sky_holdout_20261123
e=project_docs/evidence/tcad_ibex_20261123
out="$r/aes_online_sensitivity_greedy_20261125_v1"
bash code/scripts/run_with_timeout.sh 3100 taskset -c 0-5 \
  python3 -B "$e/run_aes_sensitivity_greedy.py" "$r/aes_matrix_v1" \
  "$r/aes_incident_priority_preflight_v1/preflight/result.json" "$out"
python3 -B "$e/verify_aes_sensitivity_greedy.py" "$out"
```

独立核验入口接受 `--prefix 1` 至 `--prefix 4` 以复核已发布前缀，整轮结束后生成 `independent_verification.json`。预检使用生产入口的 `--preflight-only` 及核验入口的 `--preflight-only`。本次预检原件位于 `$r/aes_online_sensitivity_greedy_preflight_20261125_v1`，其中 `sensitivity/ranking.json` SHA-256 为 `85c7a17252d23ffeb67059c556dd248c871518d99e7fd4f58e92d0faa6340302`，`independent_preflight.json` 为 `81c27918e7cca0c4878fe56b6de16ee881ddffb8ee39ad08c8f67dd2d174403b`。
