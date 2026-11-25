# ASAP7 UART 原约束下的在线面积回收对照

2026-11-25。冻结物理起点来自原生 ORFS UART。原周期 270 ps，非时钟 I/O 延迟 54 ps，虚拟时钟延迟 66.270 ps。FF／TT／SS hold WNS 为 +50.315／+67.502／+54.053 ps。TT 和 SS 已存在负 setup 裕量。 [原始起点](UART_CONTROL_RUN.md)

## 适配与预检

原生资格收据以 `view_liberty_groups` 保存 Liberty 绑定，筛选驱动另读 `library_paths`。适配器核对原 15 个文件的尺寸和 SHA-256 后只补路径表，并记录原始收据身份。ASAP7 的部分库名是符号链接，实际内容身份以原尺寸和 SHA-256 核验。首次未适配入口因缺字段退出，候选为零。

筛选固定原布局、原 SDC 和原 SPEF，以单线程顺序完成 18 次 TT 候选 STA，18 项通过，耗时 81.563830427 RAW s。它提供统一的候选池，按相同成本计入每一臂。池 SHA-256 `73bc816db40e5ca76e4a1dd34392dc1ab9bfeba3a7b9c0cff196ce2188b8fdff`，筛选收据 SHA-256 `e3f6003fd6a0c97c8132798c75282308d02550e24eeec26999c58fb104419f56`。

首次零编辑驱动把物理工作目录设在资格清单目录之外，在发起候选物理子进程前退出。v2 将资格清单留在 `seed/`，物理评估根绑定到整个新运行目录。共享零编辑完成保护布线 DRT/RCX、三角时序和独立全块 DRC，原网表保持同一哈希，SEC 为 567/0，耗时 16.773417292 RAW s。面积口径为 TT Liberty 的功能单元面积，参考为 79.00902 µm²。原生 105.107 µm² 为流程报告的标准单元统计口径。

## 对照规约

正序为原顺序单门、固定批次、FAECO，反序为 FAECO、固定批次、单门。三者都使用当前候选的实时布线前诊断和同一保护路由后端。CPU 0–5，详细布线四线程，诊断一线程。每臂采用 720 RAW s（含筛选）、至多六个逻辑请求、按 0.01% 参考功能单元面积（0.007900902 µm²）记录首达。固定批次和 FAECO 的初始批宽为三。每个端点须通过原三角 WNS 和 TNS 的相对门、绝对且相对 hold 门、电气门、布线、独立 DRC、天线和两态 SEC。WNS 的预算为原周期 1%（2.7 ps），FF／TT／SS 的 TNS 损失上限为 27／27／136.9736502 ps。FF 现有裕量远大于 WNS 预算。

v2 原件在 `/home/toylog/faeco_tcad_uart_online_20261125_matrix_v2`。规约 SHA-256 `90bf70bb080d5544d51265e575c3ec94ff72f6342fe6b9aaf452c5476d374a4f`，共享零编辑动作收据 SHA-256 `8ea78b314aa9ec130f37cf138421047e115c05c1cf477cc05afcdadee8a22b85`。

## 已核验的六臂结果

| 调度 | 原面积回收 | 最大合格回收（µm²） | 首达目标正序／反序（RAW s） | 最优端点完成正序／反序（RAW s） |
|---|---:|---:|---:|---:|
| 原顺序单门 | 0.22144% | 0.17496 | 152.165／151.161 | 199.708／198.261 |
| 固定批次 | 0.29526% | 0.23328 | 152.778／152.067 | 223.566／221.947 |
| FAECO | 0.18454% | 0.14580 | 151.795／152.289 | 222.513／222.660 |

三法均在第三次评估首达。单门和 FAECO 首达实收 0.08748 µm²，固定批次为 0.17496 µm²，均高于同一面积下限。首达时间差在两个顺序间变号。每臂均完成六次物理请求，六臂共有 36 次 DRT/RCX、108 次逐角 STA、36 次独立全块 DRC、12 次 SEC。36 次实时预诊断均为零标记，未开放邻线或发生布线重试，因而这个试验提供后端可运行与无触发场景的证据。

各调度的最优端点跨序复现。单门、固定批次、FAECO 最差逐角 setup WNS 损失分别为 0.0428、1.3380、0.0251 ps，SS TNS 分别变化 +0.565、+10.113、−0.332 ps，各角均无新增负 setup 端点。最优端点逐角 hold 门和电气门均通过，独立 DRC 与天线违例为零，SEC 均为 567/0。固定批次两序均取得最大面积，FAECO 的面积极值在本设计低于两种基线。

同一批日志的探索性目标扫描检验门槛敏感度，0.01% 仍为主目标。目标为 0.10% 时六臂读数与主目标一致。为 0.15% 时固定批次正反序首达 152.778／152.067 s，单门为 199.708／198.261 s，FAECO 为 222.513／222.660 s。为 0.20% 时 FAECO 两臂未达，另两种调度保持 0.15% 的首达读数。0.25% 时只有固定批次达到，首达 223.566／221.947 s。三法在原六次评估上限下均未达到 0.30%。这些读数只使用原始验收前缀，未调整调度或追加物理评估。

正反序中 FAECO 的第 2 次均因 FF setup 拒绝 `_0814_`、`_0893_`、`_1027_` 三门组合，FF WNS 仍为 +19.252 ps，相对于 +25.853 ps 起点损失 6.601 ps，超过 2.7 ps 门。二分先接受 `_1027_`，其余两门与已接受集合合并后在第 4 次复原同一候选。两次详细布线输出的 ODB、DEF、网表与去日期 SPEF 一致，三视图读数一致。第 4 次含诊断分别消耗 23.221／23.318 RAW s，各占一次物理评估。后续 opt-in 变体按同一冻结评价身份复用完整的确定拒收，继续拆分，在原六次实际物理评估上限内验证回收是否改善。

生产退出码为 0，原 `results.json` SHA-256 `1bc709c4a2429e2ed0276a0c37f4c0b2ba0e830cb8ea0350371c3e82ee843da8`。独立审计复核已发布的全部 6 臂，重建物理范围、在线诊断、候选顺序、时限和已验收端点。 [独立核验收据](UART_ONLINE_VERIFIED.json)

## 复现入口

从 WSL 项目根运行，输出路径须采用新的目录和文件名。

```bash
e=project_docs/evidence/tcad_ibex_20261123
h=project_docs/evidence/tcad_holdout_20261123
u=/home/toylog/faeco_tcad_holdout_qualification_20261124_v1/asap7/uart
src=/home/toylog/faeco_eda/orfs/flow/designs/asap7/uart/constraint.sdc
raw=/home/toylog/faeco_tcad_uart_online_reproduction
python3 -B "$h/adapt_uart_qualification.py" "$h/UART_CONTROL.json" "${raw}_views.json"
base=(--pdk asap7 --control-dir "$u/results/asap7/uart/base" --original-sdc "$src"
      --control-drc "$u/reports/asap7/uart/base/5_route_drc.rpt" --views-json "${raw}_views.json"
      --sec "$h/prove_holdout.py" --embedded-guides)
bash code/scripts/run_with_timeout.sh 500 taskset -c 0-5 \
  python3 -B "$e/run_holdout_screened.py" screen "${base[@]}" --top uart --screen-workers 1 --out "${raw}_screen"
bash code/scripts/run_with_timeout.sh 4700 taskset -c 0-5 \
  python3 -B "$h/run_uart_online.py" "${base[@]}" --out "${raw}_matrix" \
  --screen-pool "${raw}_screen/screen_pool.json" --screen-receipt "${raw}_screen/screen_receipt.json" \
  --route-timeout 240 --sec-timeout 210
python3 -B "$h/verify_uart_online.py" "${raw}_matrix" "${raw}_verified.json"
```
