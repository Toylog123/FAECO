# SKY130HD GCD 同提议的窗口与全块预检

2026-11-27 对同一固定三门提议实跑常规、窗口预检、全块预检三臂。两种预检均无标记。三臂首轮详细布线后的独立全块 DRC 都检出同三处 met1 短路，其位置全在原诊断窗口内。三臂复修清零，仍因 TT 相对 Hold 门拒收，合格回收均为 0。

## 冻结协议

沿用[原 GCD 对照](GCD_MARKER_MECHANISM_REPORT.md)的 SKY130HD 控制点、18 项池和固定排名 13–15。将 `_092_`、`_093_`、`_094_` 的 `mux2_4` 同时替换为 `mux2_1`。共清除 10 条直连旧线，首轮保护 476 条其余有线网。使用 1.1 ns 周期、220 ps I/O、290 ps 虚时钟延迟、嵌入导引、四线程详细布线、一次显式 pin access 和 64 轮上限。采用 11 ps 相对 Setup WNS、原逐角 Setup TNS 门、绝对及相对 Hold 门。共享零编辑起点实跑通过独立 DRC 与 SEC 262/0。

每臂只派发一次固定提议，允许一次按独立 DRC 标记放行的复修。720 RAW s 含 39.206442669 s 共用预筛。预检在换门并清除直连旧线后执行，使用一线程。窗口预检用单元换门后包围盒向外扩一行高，共三个互不相交的裁剪盒。全块预检使用同一诊断前状态和同一 DRC 引擎。按预登记顺序串行运行，CPU 亲和性为 6–11，观察期间有轻量日志与只读审计。

## 原始结果

| 臂 | 预检时长（RAW s） | 预检标记 | 首轮独立 DRC | 复修独立 DRC | 首轮／复修 DRT+RCX（RAW s） | 含预筛总计（RAW s） |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 常规 | — | — | 3 | 0 | 324.721／6.752 | 376.551 |
| 窗口预检 | 0.658 | 0 | 3 | 0 | 350.495／7.102 | 403.299 |
| 全块预检 | 0.861 | 0 | 3 | 0 | 308.403／6.608 | 360.655 |

首次布线均无预放行。独立检查在 `net242` 与 `net266` 之间报告三个相同的 `Short`，类型、层、关联网络和位置框均一致。`net266` 属直连网，`net242` 首轮保持原走线。由冻结 DEF、实际导入的 LEF 与换门后 DEF 重建，三个短路的包围盒都完整落在 `_093_` 的 `[60760,10880,70340,19040]` DBU 窗口内。独立 DRC 首次记录这些短路时，布线状态已改变。两种原位预检的结果只覆盖重布前状态。

三臂均按标记放行 `net242`，保持其他保护线，复修后独立 DRC 清零。TT Hold WNS 仍为 +430.704083509 ps，相对共享参考下降 0.022620794 ps，超过登记的 0.001 ps 容差。三臂各自完成 2 次 DRT/RCX、2 次独立全块 DRC 和 6 次逐角 STA，均止于相对 Hold 门，候选 SEC 阶段未触发。提议的物理面积差均为 11.2608 µm²，交付回到共同参考，合格回收为 0。

分别比较首轮和复修，三个臂之间及与原 ABBA 四臂的对应 ODB、DEF、网表、统一 `*DATE` 行后的 SPEF 及独立 DRC 原件一致。本轮每种方法只运行一次，表中计时用于核对预算与工序，速度差需要配对重复观测。几何邻网预放行和不同保护范围对可行性的影响仍待验证。 [原 ABBA 规约](GCD_MARKER_MECHANISM_PREFLIGHT.md) · [未决项](../../OPEN_ISSUES.md#oi-1072026-11-25open-gcd-固定提议在布线前预检无标记但正式布线后出现短路)

## 复算与原始配置

运行于原 WSL 主机，源码基点 `00b0bc591ddcb8e0d7fb8f3ae06307b7018ae531`，生产驱动及 1.0 行高窗口实现的指纹由 `protocol.json` 记录。正式结果 SHA-256 为 `02b44e2774fe87ae93eae269842817bb92a5fdeca7a330a35d8a125f416d106d`，所在目录为 `gcd_window_diagnosis_20261127_v1`。生产作业返回 0，共经过 1038 s。离线检查不依赖原始绝对路径、EDA 安装或工作目录。

[原件包](GCD_WINDOW_DIAGNOSIS_ORIGINALS.zip)包含 321 份索引原件和 SHA-256 清单，共 9,207,546 字节，SHA-256 `a6ed1f30f01232d67079974c916a5337a46bbfa7f9c95fffb074fe2ee3eae705`。包内 `independent/` 保留独立核验脚本、现场回执 `8ecdc94c043f76d51e654e11c91196d4d4cf9fb383a4fdc376f7df184c91a580` 和几何回执 `b0747104db866b2f3114102220530a91d720cb47433f57ec26970dbb941204a3`。相同 ZIP 在 Windows 原生 Python 与 WSL 离线复算逐字段一致。几何回执同时绑定实际导入的 LEF 指纹和路径，供现场检查重新推算窗口。

```bash
python3 -I -B project_docs/evidence/tcad_ibex_20261123/verify_gcd_window_archive.py
```

原机运行需要冻结 seed、先前 ABBA 协议与结果，以及配置指纹绑定的 EDA 安装和工艺输入。生成新输出前，先在 Python 3.12 下运行冻结输入检查。`results.json`、`protocol.json`、控制点工件和三臂原件见归档。

```bash
base=/home/toylog/faeco_tcad_sky_holdout_20261123
driver=project_docs/evidence/tcad_ibex_20261123/run_gcd_window_diagnosis.py
seed="$base/gcd_incident_cap_pair_20261124_v1"
history="$base/gcd_marker_mechanism_20261125_v1"
out="$base/gcd_window_diagnosis_replay"
taskset -c 6-11 python3 "$driver" "$seed" "$history" "$out" --check-inputs
timeout --signal=TERM --kill-after=8s 2550s bash code/scripts/run_with_timeout.sh 2520 \
  flock -w 8 /home/toylog/faeco_v5_eda.lock taskset -c 6-11 \
  python3 -u "$driver" "$seed" "$history" "$out"
```
