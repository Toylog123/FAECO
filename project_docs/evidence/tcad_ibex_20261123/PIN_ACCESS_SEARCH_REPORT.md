# 单次 pin access 的完整搜索对照

单个候选的前一轮反序对照已经观察到 GCD 和 Ibex 的布线耗时下降。完整的原起点在线搜索仍需检查每一次派发、拒收和验收，尤其是首次达到同一面积目标的费用。保存 ODB 后继续 ECO 是另一个独立验证。 [单候选基线](PIN_ACCESS_AB_REPORT.md) · [保存 ODB 重入](PIN_ACCESS_REENTRY_REPORT.md)

## 配方

GCD 使用已有的冻结 CONTROL、筛选池、三门整批、六次物理评估、720 RAW s 窗口和 0.01% 面积目标。四臂使用同一 hold-aware 调度、原 SDC/IO、三视图联合门、DRC、电气与非空 SEC；每次候选均从共同冻结起点新做物理评估。A 保留外部和 DRT 内部两次 pin access。B 使用 `--single-pin-access`，仅省掉嵌入 SKY130 guides 场景中的外部调用。原默认仍是 A。外部 guide 及重新全局布线路径无法启用此开关。

WSL CPU 6–11 上串行运行 A→B→B→A，候选四线程。每臂外层超时 2400 s，单次 DRT/RCX、每视图 STA、SEC 分别为 1500、180、210 s。四臂都加上原冻结筛选的同一实测成本，搜索过程全新运行。CPU 0–5 上的 ODB 重入试验可能重叠。首达时间配对和保存 ODB 后重入时间分别报告。 [启动器](run_hold_aware_sky130.sh) · [逐臂物理核验](verify_pin_access_search.py)

## 结果

| 顺序 | A 首达含筛选 / RAW s | B 首达含筛选 / RAW s | B 省时 / RAW s | A、B 搜完六次不含筛选 / RAW s |
|---|---:|---:|---:|---:|
| A→B | 122.989 | 118.740 | 4.249 | 84.989／80.463 |
| B→A | 118.933 | 113.860 | 5.073 | 82.730／75.670 |

四臂都在第五次回收 11.2608 µm²（0.234742%），SEC 262/0。每次的动作元组、接受和拒收理由、DEF、Verilog、DRC、去日期 SPEF、逐角 setup/hold 和电气读数、实际改线以及证明点逐项匹配。候选 Tcl 的归一化差异只有外部 `pin_access` 一行。日志验证 A 的 12 次候选各执行两次，B 的 12 次候选各执行一次。四臂共 24 次 DRT/RCX、72 次 STA、4 次候选 SEC，候选缓存为零。首达前五次 DRT/RCX 在两对分别省 4.927 和 7.134 RAW s，非布线阶段抵消部分节省。 [核验收据](PIN_ACCESS_SEARCH_VERIFIED.json)

同一筛选时间 52.520673 RAW s 计入每个首达端点。此次是重复顺序的 GCD 搜索级对照和原 DRT 路径的加速证据，未把已计时的历史矩阵重新贴上这个配方。后续公平比较时，在同一工艺和原始约束下为所有方法一起固定该开关和共同物理起点。

## 下轮配方

后续 SKY130 嵌入 guides 的冻结起点正式对照，在所有方法统一显式启用 `--single-pin-access`。保存 ODB 重入的两个用例在不同 pin access 模式下均作出一致决定。GCD 重入候选合格，Ibex 重入候选都因 TT 电气和 TNS 门拒收。冻结起点与提交后重入属于不同物理路径，下轮的冻结起点对照继续用原共同起点执行每个候选。 [重入报告](PIN_ACCESS_REENTRY_REPORT.md)

原件 `scratch/tcad_ibex_20261123/pin_access_search_20261124.tar.gz`，27,401,310 字节，SHA-256 `6df7e677640aa27488ca8cdd80acf7ced0a996854e3a4d17d10fcfda2c364b1c`，713 个成员，其中 640 个文件与原件逐个 SHA-256 一致。
