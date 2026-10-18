# OI048：ABC错选顶层的证据域影响审计

本轮只读审查生产调用边界、已归档运行源码及实际proof脚本/日志/收据；没有新EDA、Git或修改生产/旧证据。这里“未受此反例影响”只表示没有落入这次top=None、ABC选中首个库单元的证明对象错误，不替代模型、X/Z、状态初始化或历史对象绑定等其他证据门。

## 逐域结论

| 域 | 本次实查 | 判定 |
|---|---|---|
| C′完整矩阵 finalSEC | 72份实际sec.ys/result/log，逐收据与原输入/输出SHA核对；非零proven、0unproven | **未受此反例影响** |
| A6新证明 | 6份实际proof、receipt全部artifact SHA匹配 | **未受此反例影响** |
| B2新证明 | core与mul两份实际proof及manifest artifacts逐SHA匹配 | **未受此反例影响**；core孤立X证书范围不变 |
| B17新证明 | 确切新proof及全部final_sec artifact SHA匹配，12879/0 | **未受此反例影响**；不把旧partial proof升级 |
| 3ea运行期full-netlist ABC checker | 实读runtime_inputs.zip里的原real_wns/共享helper源 | caller显式传circuit top，helper执行对应hierarchy；**未落入top=None分支** |
| S现存86份可精确对应的局部post CEC | 每份左右BLIF都是单一、同名win顶层；原factory显式推断窗口top并传入 | **未受此错选库model反例影响**；40条缺局部对应仍unknown，其余S缺口不关闭 |
| native ztop反例 | Y=A与Y=B，A0/B1输出不同；ABC日志明确选首个sky130 buf库model却pass | **已确认受影响：真实假pass** |
| legacy flow.py、ABC baseline、EPFL mapped-check的省略top调用边界 | 实际调用缺top，历史helper默认None | **存在受影响调用边界；具体旧proof为unknown**，须看每个实际脚本/BLIF/日志 |
| A另两份复用旧proof、其他仅写method/pass的记录 | 不在本次81份新证明的逐对象复核内 | **unknown/本轮未审**；不能由新proof或方法名替代 |

## 为什么81份新证明没有用错ABC对象

逐件打开的实际 `sec.ys` 均包含：

```
rename <circuit> gold
rename <circuit> gate
equiv_make gold gate equiv
hierarchy -top equiv
flatten
equiv_simple
equiv_induct -seq 10
equiv_status -assert
```

实际result命令为Yosys执行该sec.ys，日志含非零已证点、0未证点和成功标记；不是调用共享 `check_yosys_abc_equivalence(top_module=None)`。对应raw输入、helpers及已有artifact收据均实查SHA，而非只读取status=pass。本轮没有把81个对象的已证点相加当统计结果，逐对象值保存在REPORT.json。

## 来源与调用边界

- `code/scripts/run_r22_cut_ablation.py:102` 的 `final_sec` 明确构造gold/gate；归档3ea源码与实际72份脚本相符。A6/B2/B17复用了该独立流程，实际脚本已逐份查看。
- `code/src/rseco/real_wns.py:608` 的full checker传 `top_module=top_module`。这一点同时在3ea原字节ZIP内确认，不能用今天修后的代码反推过去。
- S `structure_resynthesis._normalize_any` 从原窗口Verilog/BLIF取top，Verilog分支明确传sharednormalizer，BLIF分支明确 `hierarchy -check -top`。现存86份左右实际BLIF各只有同名win模型，因此没有native反例的“多个root、首个library model”条件。
- `flow.py:104` 的generic formal checker、`run_yosys_abc_resynthesis_baseline` 的归一化及 `verify_epfl_mapping_cec.py:131`→`check_mapped_blif_equivalence` 省略显式top。历史实现在省略时不会做层次选择，具备该反例暴露的风险。**调用点风险不等于每个旧proof都已证明是假pass**；旧对象需独立源top和BLIF根模型交叉核验。

当前主线正修共享helper的唯一源top推断；本审计保存所读当前源码SHA和3ea原字节，未将正在开发的修复当作已验收，更不倒签旧proof。

## 验证记录与保留限制

实际完整读取：72+6+2+1=81份新proof；300秒超时包装实际约5秒退出0，审计Python约1.407秒，所读来源前后SHA稳定。最初脚本误把B17 manifest的`model_preflight.v`当成final_sec目录内文件，产生FileNotFound；旧脚本/log保留，v2按实际`final_sec/`前缀分层后完整通过。这是审计路径schema错误，不是B17证明失败。

后续S局部86份双侧BLIF检查同样是只读源内容/哈希，不是新CEC。所有结论分别落在REPORT.json、S_RETAINED_LOCAL_TOP_SCOPE.json、SCOPE_MATRIX.json。未检查的旧证明继续保留unknown，不以“总数未变”“方法名相同”或历史pass字段宣告恢复。
