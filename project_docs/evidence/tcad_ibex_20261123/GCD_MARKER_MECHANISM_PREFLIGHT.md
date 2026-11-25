# SKY130HD GCD 固定提议的在线标记回放

2026-11-25 · 静态预检完成 · 物理计时待跑

## 输入与预检

沿用 `gcd_incident_cap_pair_20261124_v1` 已冻结的嵌入导引 CONTROL、18 项池、39.206442669 RAW s 筛选收据及四线程单次 pin access。原 SDC 保留 1100 ps 周期、220 ps I/O、290 ps 虚拟时钟延迟，传播原物理时钟。原 FF、TT、SS 的 hold WNS 为 +358.948、+430.727、+342.905 ps。逐角 setup WNS 损失门 11 ps，TNS 损失门 134.876、570.255、5344.787 ps。检查逐角 hold 绝对非负且相对不退化，完整评价包括电气、天线、恢复 `ROUTED` 后的独立全块 DRC、保护布线和非空两态 SEC。 [起点收据](../tcad_holdout_20261123/GCD_CONTROL.json) · [历史迁移实验](INCIDENT_CAP_PRIORITY_REPORT.md)

本次共用同一提议，即冻结池排名 13–15 的 `_092_`、`_093_` 和 `_094_`，历史实际面积回收 11.2608 µm²，SEC 262/0。正式输入预检识别 10 条直连网和 486 条原有线网，锁定要求的两条时钟网确实存在。生成的候选诊断 Tcl 包含直连清线及实时 DRC，正式路由 Tcl 保留嵌入导引、64 轮详细布线上限和单次 pin access。静态预检及两项专项测试通过，静态预检没有启动 EDA。 [当前入口](run_gcd_marker_mechanism.py)

## 对照规约

共同严格零动作通过后，常规→实时诊断→实时诊断→常规依次串行。常规臂第一轮只清直连数据网。实时诊断臂从原 `ROUTED` 起点暂存候选并清除直连线，合法关联的原有线数据邻网入选，全部标记都具备可执行匹配时首次放行。两个后端均允许一次由正式 DRC 新标记支持的邻网重试。一个正式提议计入 720 RAW s 窗口，共同筛选成本逐臂计入。实时检查、解析、DRT/RCX、逐角 STA、真实独立 DRC 与 SEC 都由相同硬时钟约束。记录零回收、未完成和实际合格端点。

历史 GCD 触达电容对照的 12 份历史详细布线器 DRC 报告为空。现行保护后的独立解锁全块检查可确认是否仍然如此。若实时预检为空而正式首轮也同时通过，GCD 可量化空诊断净开销。AES 已有低层冲突的正例，旧 DRT 违规数为零，独立全块 DRC 发现 8 处标记，定位了 4 条可释放邻网。 [AES 机制原件](AES_MARKER_REPAIR_REPORT.md)

接下来的机理解耦先用冻结原布线几何，独立生成并固定所有非时钟邻网的距离顺序。配对核验从几何全序拿出恰与标记集合等量的邻网，只比较第一轮清除能力、布线变化和验收状态。可部署基线预先固定最多四条邻网，计算与释放均实计，其正式运行不接触候选标记或由标记导出的数量。配对中 `k=0` 时保留触发与成本读数。

```bash
r=/home/toylog/faeco_tcad_sky_holdout_20261123
e=project_docs/evidence/tcad_ibex_20261123
seed="$r/gcd_incident_cap_pair_20261124_v1"
out="$r/gcd_marker_mechanism_20261125_v1"
taskset -c 6-11 python3 -B "$e/run_gcd_marker_mechanism.py" "$seed" "$out" --check-inputs
bash code/scripts/run_with_timeout.sh 3100 taskset -c 6-11 \
  python3 -B "$e/run_gcd_marker_mechanism.py" "$seed" "$out"
```
