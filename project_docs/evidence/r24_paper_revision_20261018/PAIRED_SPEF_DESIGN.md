# r24 fresh 双侧 SPEF 有界后验设计（待root确认，未运行EDA）

选用已验收 C′v3 W1/s382 的完整初始/最终网表，在**当前f761**简化线载模型上进行新的负载敏感性后验。它是新族，不恢复旧scan或旧F6，不是新候选搜索或真实布线/PPA实验。

设计JSON：`PAIRED_SPEF_DESIGN.json`，SHA `f212e78473fc99dcca843aa9ce009b433eb557a8af2f60c858867763b8591465`。静态准备脚本 `prepare_paired_spef_design.py` 已执行纯读取/解析，不启动STA/SEC/ABC；180秒wrapper约25秒内完成。详细逐SHA/模型与输入支持域见 `PAIRED_SPEF_STATIC_PRECHECK.json`（`ed859fb44be171306c5a74d7747e4b8f3fe304c57037b4e3bf4d5bf8b5324408`）与 `PAIRED_SPEF_MODEL_SCOPE.json`（`b98dc3f40db144a061d265d55231df03e8149fb661d8515f8800fc1fcbeefe8a`）。

## 输入选择与现有证明

旧scan exact pair在当前required-input/二态/F2/各侧SPEF静态生成检查均通过；历史SLEEP缺pin由共享baseline SPEF产生，不能据此说网表本身非法。但限定检索未找到这对输入的独立SEC绑定。选择有完整来源和证明绑定的C′pair，避免旧证据缺口污染新后验。

| 角色 | 保留路径（根为 D:/BaiduSyncdisk/01_Papers/03_FAECO/） | bytes SHA256 |
|---|---|---|
| baseline | experiments/20261016_r22_cut_ablation_v3/W1/s382/final_sec/initial_raw.v | 608cf28c7da49b245ec5cb44207552cd112a638275741c3eab74c13be0a06221 |
| final | experiments/20261016_r22_cut_ablation_v3/W1/s382/final_sec/final_raw.v | 5745c7fb0fdcf5654658f41d3e2347f45c1121e694cb1f17d967280f3dce589e |

这两份raw与原completion及SEC result的SHA逐字节相符；completion登记的全部artifact实查一致，completion自身SHA在已验收72矩阵eligible集合内。既有SEC实际90proven/0unproven；最终raw按UTF-8与通用换行解码的SHA `2927efa7fdfd58d786dfc4dee1532c550d1cdd078400169d6c489920359107e8` 与outerloop终点完全相同。原初始/最终理想WNS -0.98/-0.83只用于身份/差异核对，不先当成新测量结果。

当前静态支持域：两侧required-input通过、二态unsupported_reason=null、F2通过；每侧94个网络、端口方向全I/O无inout，各自SPEF可生成。两侧u40生成器文本SHA相同（`23043a55a8105df8237ca9d2fdf926d0db98bd13541e66247fd2432bdcd5f85e`）是允许结果：本pair修改cell而保留连接，不要求SPEF必须不同；**必须分别由各侧输入生成且分别绑定**。静态成功不替代实际工具注入验证。

HEAD固定 `f761ee1996a83fc4f0f3de0999b74d85a8237858`。两输入的来源科学runtime仍 `3ea0f757f5e9bab4a2df75c458b0c665eabcb258`。当前全部rseco Python源、原runner/timeout wrapper、TT库绝对路径与SHA均已锁定，前后稳定；实际使用的Liberty模型metadata和原SEC cells.v模型SHA也已登记。

## 反驳优先的顺序和预算

先运行baseline=final的u40同网表对照，要求理想与SPEF两种delta均为0、两侧SPEF bytes相同、真实注入完整；任一不满足即停，不执行后续扫描。随后依次u10/u40/u160对同一baseline/final pair，所有不利结果保留，不按结果改权重或更换输入。

| job | 相对本evidence目录的新输出 | baseline/final | API STA上限 | annotation replay上限 |
|---|---|---|---:|---:|
| control_same_u40 | paired_spef_runs/control_same_u40 | baseline/baseline | 4 | 2 |
| pair_u10 | paired_spef_runs/pair_u10 | baseline/final | 4 | 2 |
| pair_u40 | paired_spef_runs/pair_u40 | baseline/final | 4 | 2 |
| pair_u160 | paired_spef_runs/pair_u160 | baseline/final | 4 | 2 |

总上限16次API STA+8次真实annotation replay=24次科学工具启动，不含两次read-only工具version/binary SHA身份查询。串行，原runner每次STA内层600秒保持不改；外层每case600秒，全实验1800秒；annotation每次60秒并受剩余全局deadline约束。每次实际launch、returncode、elapsed及原双流和receipt单独留存；外层超时立即停止启动后续case，检查日志与仍存活进程，不盲重试。

u0被原CLI的正值校验拒绝，故使用10/40/160μm/unit；每job另行测量ideal模式，不把u10冒充零线载。设定：TT25℃1.8V、CK周期0.5ns、无额外显式I/O delay，两个网表同设置。L=unit×max(1,sqrt(fanout))，r=0.09Ω/μm，c=0.21fF/μm，fanout/depth penalty均1；没有几何位置或标定主张。

## 实际执行argv与验收

JSON `jobs_in_order` 已给4个完整绝对argv数组，Python解释器绝对路径亦已登记。执行将复用未改动 `code/scripts/run_parasitic_aware_check.py`。示意（真实绝对路径见JSON）：

```text
<registered-python> <root>/code/scripts/run_parasitic_aware_check.py --baseline <registered-initial_raw.v> --repaired <registered-final_raw.v> --period 0.5 --top s382 --clock-port CK --unit-len-um 40 --output-dir <evidence>/paired_spef_runs/pair_u40
```

每个API结果必须valid、returncode0、有限WNS，实际Tcl中read_spef位于所有timing report之前。再复制每侧寄生测量Tcl并只追加 `report_parasitic_annotation -report_unannotated`，按JSON已登记的8个WSL argv真实重放（不修改API原Tcl）。每侧要求零unannotated、零partially unannotated drivers；任何missing pin/unknown instance/injection error/日志错误即不采该WNS。重放WNS与原API日志打印精度一致；缺报告即失败，不以rc0代替注入证明。

实际工具预计为已验收tiny绑定pilot的OpenSTA3.1.0、binary SHA `96833cf69282803fc44fc8cc343bfe03ad8279bab9fb276d84a6d4532e15b468`；执行前须实际查询并匹配。复用入口是 `project_docs/evidence/r22_spef_topology_repair_20261018/actual_tool_binding/`，其40/4000μm tiny控制只证明真实注入与失败拒绝，不提供本pair的科学结果。

最终只报告此pair在该简化模型下的理想收益/每个线载点收益及保持比例，并列逐侧WNS、候选/基线/回放身份。不利或零收益照报；若负载改变未造成可辨识WNS/slack变化，结论为注入敏感性不足而非“收益稳健”。不得把本结果覆盖到旧s382_big、b18_light或历史scan；不碰b18真实三态/inout，不改源码、HEAD和旧产物。

当前阶段停在设计与静态核验，等待root确认后才运行。
