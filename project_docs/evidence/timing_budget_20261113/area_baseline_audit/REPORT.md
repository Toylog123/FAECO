# s382 Resizer 净新增面积分母正式审计

2026-11-13。静态审计通过，无新EDA、STA、布线或SEC。主指标按用户关注的 **Resizer 净新增面积回收比例** 定义：

\[
R_{\mathrm{added}}=(A_R-A_F)/(A_R-A_0).
\]

这里 (A_0) 是同次原流程中 `repair_timing -setup` 前的CTS完成快照，(A_R) 是该流程Resizer后最终导出端点，(A_F) 是既有 `RESTORE__074_` 物理端点。完整面积按固定Liberty中的所有功能单元计数，含层级展开/转义FF与时钟单元；同一组3,026个无普通信号引脚连接的physical taps明确排除。它不是core/die面积，也不把不同阶段的面积混为一项。

| 固定阶段 | 功能实例数 | 完整mapped-cell面积 |
|---|---:|---:|
| 综合输入，按s382顶层展开dff层级（仅用于区分阶段） | 90 | 809.5264 |
| (A_0)：修复前CTS快照 `cts.def` | 94 | 892.1056 |
| (A_R)：Resizer最终 `routed.def` / `routed.v` / CONTROL | 102 | 1052.2592 |
| (A_F)：`RESTORE__074_` 最终 `routed.def` / `routed.v` | 102 | 1005.9648 |

因此：

- Resizer阶段净新增面积 `A_R-A_0` = **160.1536**。
- 最终回收面积 `A_R-A_F` = **46.2944**。
- **净新增面积回收比例 = 28.90625%。**
- 相对Resizer总面积下降比例另报为 **4.399524375743%**。两个百分比使用不同分母，不可互换。

该分母已在s382绑定的快照上完整重算，不能据此恢复其它13设计的旧分母或宣称旧全族14%已经成立。28.90625%也不表示“28.90625%的Resizer操作无效”。

## 阶段与身份链

原始目录为 `experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382/`。复制的 `inputs/resizer_flow.tcl` 明确显示：

1. `clock_tree_synthesis`、`repair_clock_nets`（L28）和一次合法化先完成。
2. L30写出 `cts.def`，作为 (A_0)。
3. 其后只有 `set_propagated_clock`、`source $ORFS/setRC.tcl`、`set_routing_layers`，再于L38调用 `repair_timing -setup`。已核验所绑定 `setRC.tcl` 只有RC参数设置命令。
4. L38之后执行合法化、pin access、global/detailed route，于L44写出 `routed.def`，随后写Verilog与提取SPEF。

所以综合→CTS/前处理的面积增量 **82.5792** 已包含在 (A_0)，不归入Resizer分母。该段端点差分为新增3个 `clkbuf_16` 与1个 `clkbuf_4`（`clkload0`），无功能单元移除或换master。其面积和CTS/clock repair后的快照对应；不从最终快照反推这四个实例各自的精确创建命令。

(A_R) 是repair之后经过合法化/布线的固定阶段快照，未存立即repair结束而尚未合法化的独立快照。因此本审计测量的是 **该受控流程repair前后最终单元master净差**，不是每次瞬态resize操作的历史累计面积。脚本与日志没有插入第二轮综合、CTS或显式其它cell-repair阶段；完整最终netlist/DEF身份已逐实例对齐。

## 完整计数和差分

`audit_denominator.py` 读取DEF完整COMPONENTS段，检查声明计数、所有记录、重复名和未解析文本，并检查physical taps没有普通NETS连接。A0为3,120个component，AR/AF为3,128个；唯一不在固定Liberty内的master是上述相同3,026个tap。AR完整instance→master映射与其Verilog完全相同，AR的完整canonical结构与现CONTROL相同；AF完整DEF/V一致，并精确等于原13动作配方去掉 `_074_` 后的目标，保留完整ports、assigns、pin bindings。

| (A_0\to A_R) 差分 | 数量 | 面积增量 |
|---|---:|---:|
| 新增buffer实例 | 8（5个buf_4、3个buf_6） | 71.3184 |
| 已有FF换master | 8（4个dfxtp_1→2、4个dfxtp_1→4） | 20.0192 |
| 已有其他逻辑换master | 16 | 68.8160 |
| 移除功能实例 | 0 | 0 |
| 合计净新增 | 8新增、24已有实例最终master改变 | 160.1536 |

原日志记录“Inserted 8 buffers”和“Resized 34 instances”。前者与净新增实例吻合；后者是工具运行过程统计，不等于24个最终master不同的实例，不能硬写成24或据此声称工具日志错误。完整按instance与master分类的有符号面积账见 `RECEIPT.json/A0_to_AR`，两种加总都精确等于端点面积差。

AR→AF没有新增/移除实例，仅12个已有master改变，合计−46.2944；其中 `_077_`、`_081_` 的o21ai_1→0是同面积变化，仍保留在结构账中。`_074_` 留在CONTROL型号，因此AF与原完整13动作回收面积相同，逻辑/物理端点却不同。不能把相同面积当作相同网表或相同timing。

## 层级与旧分母问题

原综合输入为 `experiments/20261016_r22_cut_ablation_v3/W1/s382/mapped.v`（头部Yosys0.67+146）。它定义一个含dfxtp_1的 `dff` helper，并在s382顶层调用21次。审计使用完整Reader分别解析每个module，再递归按实例展开叶master，不把helper定义只计一次，也不遗漏带 `/` 的展开FF身份。展开后90个Liberty叶实例、809.5264面积。

旧409.14的综合面积统计、旧611.84的Resizer面积统计与上述完整值均不一致；尤其旧Resizer计数遗漏了转义FF。即使完整修正综合分母，综合→Resizer也包含CTS/前处理增量，不能叫纯Resizer新增。当前采用修复前CTS快照直接避免了该阶段混用，并单列综合值供复核。

## 来源、复现与边界

`SOURCE_COPIES.json` 绑定16个原始来源的路径、SHA-256和复制件字节数。`structure_reader.py` 与 `liberty_signature_reader.py` 是既有sealed审计器的逐字节副本，未改源文件；新脚本仅调用后者的保守Liberty解析函数。固定TT库SHA为 `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`，与复制的已归档platform-library检查身份相同。本次不重新访问或运行安装工具。

`RECEIPT.json` 保存每阶段全部instance/master清单、physical tap全ID、master计数、Decimal面积、层级结果、两个方向的差分账、Tcl阶段顺序、源文件身份与审计器SHA。审计前后核对原始来源和复制件均未变；AF/CONTROL还与父包COPY_MANIFEST对齐。重复DEF实例的反例检查会拒绝而非合并计数。

复现命令（只重写本子目录RECEIPT，不运行EDA）：

```powershell
.venv/Scripts/python.exe project_docs/evidence/timing_budget_20261113/area_baseline_audit/audit_denominator.py
```

面积分母验收不替代10ps预算下的端点时序/hold/DRV、完整SEC或IO约束资格，亦不证明新优化算法的贡献。正式主结果须把本面积口径与该精确AF端点的物理报告及最终proof绑定。
