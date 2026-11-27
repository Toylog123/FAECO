# 第四轮 ASAP7 UART 原生提议的同后端物理验证

2026-11-27，实验标识 `TCAD-R4-NATIVE-UART-PROTECTED-16`。使用冻结的原生常规模式 16 条提议，清单 SHA-256 `269d62f05c711c9177d5ad07ebca53b0d33668f110c5ba2ed9cc397dcd24d44c`。16 个同尺寸替换均为 `BUFx3_ASAP7_75t_R` 至 `HB3xp67_ASAP7_75t_R`，各 0.08748 µm²。输入清单、参考、原库和时序约束的字节保持一致；仅在内存补齐 TT 面积字段的语句终止符以恢复绑定。单次重放固定提议直接执行物理验证，沿用 270 ps 参考、2.7 ps 逐角 Setup 容许损失及逐角 TNS 门。

同一保护后端先完成空动作参考的完整资格核验（SEC 567/0），随后调用一行高诊断以验证该提议。候选窗为 720 s，单次 DRT 限时 240 s，4 线程。最终窗口预检 0 标记，详细布线与寄生提取一次完成，独立全块 DRC 和天线为零，32 条直连网中有 12 条发生几何变化，760 条保护网的几何均保持，未进入复修。物理流程完成并给出三工艺角时序用于判定。

| 工艺角 | Setup WNS 变化（ps） | Setup TNS 变化（ps） | Hold WNS 变化（ps） | Hold TNS 变化（ps） |
| --- | ---: | ---: | ---: | ---: |
| FF | −0.001027 | 0 | −0.093082 | 0 |
| TT | 0 | −8.668177 | −0.111293 | 0 |
| SS | +0.000222 | −28.728131 | −0.018138 | 0 |

绝对 Hold WNS 均为正。三工艺角 Hold WNS 下降均超过 0.001 ps 的相对容差，且实测净回收 0 µm²。候选拒因是 `no_area_gain` 及 FF、TT、SS 的 `hold_regression`；按原验收顺序未进入候选 SEC。候选实测 23.188743 s，进程组外层 89 s、rc0，最终合格回收 0 µm²。原生提议旨在回收功耗，这次验证仅回答该冻结提议在共同面积回收后端下能否合格交付。ASAP7 AES 的语法归一化仍仅验证原生动作绑定。

## 原件与执行

[原件压缩包](R4_ASAP7_NATIVE_UART_PROTECTED_ORIGINALS.zip) 含 81 份逐字节原件及成员索引，SHA-256 `1b8af351304902712842ea1a180ccaee8c33c08765201c5b605bba55170e6460`。已核验全部原件的成员集合、字节数与指纹。候选物理收据 SHA-256 `1c3b3ec5798bff6aba482428925f2a34067e39214dc9f0b64fc1b76ada2acc85`；最终运行收据 SHA-256 `f7f885d3548294ff1380d55b64ad05a808f8b2abc2d2dc8e88bf440c8713bfea`。原件包含候选及资格参考的实际 ODB、DEF、网表、提取 SPEF、布局审核、终检、三角时序和工具日志。

恢复相同冻结输入与工具后，从仓库根运行：

```bash
PYTHONPATH=code/src bash code/scripts/run_with_timeout.sh 1200 \
    flock -w 15 /home/toylog/faeco_v5_eda.lock taskset -c 0-5 \
    python3 -B project_docs/evidence/tcad_v5_revision_20261126/replay_r4_asap7_native_uart.py \
    /var/tmp/faeco_r4_native_uart_protected_recheck
```

[执行程序](replay_r4_asap7_native_uart.py) 实跑 SHA-256 `b713d158c3695f5626453be8e36699ef15b1df73945856fa6393161a55317ec6`。
