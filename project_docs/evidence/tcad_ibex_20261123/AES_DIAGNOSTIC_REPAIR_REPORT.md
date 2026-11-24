# 已有诊断的定向 ECO 邻线释放

2026-11-24。上一轮 AES 固定与定向臂用了不同的六门组合。本轮固定为完全相同的动作：原 V3 第五次的六门。在同机上交替运行原初试／标记重试流程和已有诊断预放线流程，测量相同待修目标的验证开销。候选产生、DRC 诊断产生，以及全池搜索收益与这个组件实验分开记账。 [上一轮六门报告](AES_MARKER_REPAIR_REPORT.md)

## 输入与行为

入口从给定的 `request.json` 取得候选动作，按当前冻结候选池和直连信号网复核。已有诊断还必须提供该动作的实际布线收据、独立全块 DRC 输入清单和完成收据。审核输入的候选 ODB、DEF、冻结矩阵与 SDC 需要和相应收据一致，实际文件逐项核对摘要。驱动以现有标记解析器识别与编辑实例或直连网同属标记的原有已布线信号邻网。时钟和无关邻网保持保护。若有任何标记无法归属到可释放的原信号邻网，保留已解析证据并按原初试／重试流程处理。若预放线后产生新标记，仍至多做一次由新标记证明的额外邻线重试。代码中没有指定电路内的网名、单元号、候选排名或旧报告目录。

正式输入来自冻结 AES 和同一组六门。原失败候选的恢复 `ROUTED` 独立检查有 8 处标记，程序仅由绑定证据推得 20 条直连网之外的 `_08784_`、`net4840`、`net8148`、`net8407` 四条邻网。给两种方法相同的待修动作和已有诊断清单。原流程在首次布线后读这次运行实际产生的标记再重试。预放线流程在首次布线前消费给定诊断，计入核对及提取时间。已有诊断这一输入的生成成本不在四臂运行内，已在此前实际记录。若从零开始获取标记，首轮失败布局和诊断的成本也要纳入端到端评估。 [运行入口](run_aes_diagnostic_repair.py)

## 实测规约

顺序为原流程、已有诊断预放线、已有诊断预放线、原流程，同机串行固定 CPU 0–5，OpenROAD 四线程。每臂一个完全相同的逻辑请求、720 RAW s 硬截止、0.01% 面积目标，统一计入此前同一实测筛选 113.363032440 s。每一物理尝试从相同冻结 CONTROL 重新 DRT/RCX 和三角 STA。FF／TT／SS 绝对和相对 hold、setup WNS/TNS、原 IO、电气、恢复 ROUTED 后独立全块 DRC、天线及非空 SEC 使用原门。任何一臂物理、时序或证明输出都不能充当另一臂的端点收据。比较首达时间、实际物理次数及最终端点身份。 [独立核验](verify_aes_diagnostic_repair.py)

## 复现

从 WSL 仓库根目录运行，输出使用尚未存在的目录。

```bash
raw=/home/toylog/faeco_tcad_sky_holdout_20261123
e=project_docs/evidence/tcad_ibex_20261123
case_dir="$raw/aes_retry_triage_v3/faeco/05"
bash code/scripts/run_with_timeout.sh 2530 taskset -c 0-5 python3 -B "$e/run_aes_diagnostic_repair.py" \
  "$raw/aes_matrix_v1" "$raw/aes_incident_priority_preflight_v1/preflight/result.json" \
  "$case_dir/request.json" "$case_dir/initial/receipt.json" \
  "$raw/aes_retry_triage_v3_cutoff_completion_v1/restored_checks" "$raw/aes_diagnostic_repair_replay"
python3 -B "$e/verify_aes_diagnostic_repair.py" "$raw/aes_diagnostic_repair_replay"
```

## 同动作四臂结果

| 实跑顺序 | 达到 0.01% 目标 / RAW s | 面积回收 / µm² | 实测 DRT/RCX／独立 DRC／视图 STA／SEC |
|---|---:|---:|---:|
| 原流程 1 | 335.523258 | 65.0624 | 2／2／6／1 |
| 已有诊断预放线 1 | 231.616129 | 65.0624 | 1／1／3／1 |
| 已有诊断预放线 2 | 231.123264 | 65.0624 | 1／1／3／1 |
| 原流程 2 | 333.166168 | 65.0624 | 2／2／6／1 |

依实际顺序配成两对，首达各省 **103.907129 s（30.97%）**、**102.042905 s（30.63%）**。已有诊断的核对和邻网计算分别为 0.066997／0.067225 RAW s，已包含在时间里。原流程的首次布局都独立重现历史 8 处 DRC 标记及规范化 DEF，随后在线选出同四条邻网。四个最终端点的实际 ODB、DEF、网表字节相同，去日期 SPEF 及全部三角视图收据一致。每臂新做的独立全块 DRC 和天线均为 0，各自 SEC 11,089/0。最终实际改动 24 条允许对象，其余 15,633 条保护网几何保持。三角 hold WNS 改善约 +0.059／+0.093／+0.937 ps，TT、SS 各新增一个负 setup 端点，原 WNS/TNS 预算通过。

这组对照验证了已有诊断时跳过已知失败初试的收益。分开看输入来源，旧六门布局的那次独立 DRC 已实测花 15.075220 RAW s，且其前面还需要产生初次布局。冷启动的端到端收益须以纳入诊断获取成本的在线实验确定。下一轮从没有候选专用报告的冻结起点开始，把在线诊断或低成本几何预检也计入 720 s。

另对三个既有包做只读验证。V2 固定第二批 4 个标记推得 `net4840`、`net8407`，V2 FAECO 第二批 6 个标记推得 `_03615_`、`net8222`，严格预检中没有 DRC 标记的首批给出空邻网。读回邻网属于诊断规则验证。V2 FAECO 对应的历史物理重试清除 DRC 后仍未过 FF/TT 相对 hold，保留其原拒因。五项新专项用例覆盖报错候选、错几何、时钟保护、不完整标记回退和只补放行新邻网。核心回归 115 项和 AES WSL 专项 16 项全部通过。

正式 WSL 原件根 `aes_diagnostic_repair_abba_20261124_v1`。配置 SHA-256 `74b711f7052a2a271efa581d05eae22f583c945639bca2a412f1dccae5a74e2a`，结果 SHA-256 `95e896f71d36576a9e3af8912a1602dba5e789a56c8729a1e128a59066e90412`，追加只读核验 SHA-256 `678311dd893a13bd0bb68bbfb94e0c17b74a4d9e66d403dc140006a519713aa1`。 [独立核验收据](AES_DIAGNOSTIC_REPAIR_VERIFIED.json) · [专项测试](test_aes_diagnostic_repair.py)

四臂原件、只读验证和核验源码封存于 `scratch/tcad_ibex_20261123/aes_diagnostic_repair_20261124.tar.gz`。归档 170,375,901 字节、280 个成员，253 个普通文件与 WSL 原件逐项核对 SHA-256。包 SHA-256 `1f65491a614ba7610562418aca979746f82a1ec296d7348f7f01ab91c309e926`。
