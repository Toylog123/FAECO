# 待A8实际结果填充的最小双语草稿

本目录是待填充草稿，不是已修改主稿，也不是可直接编译的终稿。A8由根亲自正式登记/执行，本agent不启动SEC。根已接受A8_INPUT_PROPOSAL的八对输入设计；旧FINAL_RECEIPT及失败v1文件冻结保留。

仅两处修改：效率优先A段的功能句，以及tab:sec_iscas8完整表。SENTENCE_REPLACEMENTS.json给精确before/after；两份tex.in保留原表label和四列，不改WNS、接受动作或其它结果。学术表述没有修订过程口吻。

填充必须读取新A8真实result.json/sec.log/receipt，八项均经独立验收后，逐项填PROVEN/UNPROVEN/WALLTIME_3DP：PROVEN取最终实际log点数，UNPROVEN取真实0值，WALLTIME取同批final_sec runtime_s四舍五入到3位小数。完整精度和实际工具/源码/对象/模型SHA保存在证据，不用表中显示精度回填来源。不预置旧137/146，也不混入A6/A2计时。

脚注明确同批prover墙钟时间，排除映射、候选STA和模型准备。新表仅功能证明元数据，不推断搜索效率、不重新测WNS。若任一证明unsupported/fail/timeout/unproven/drift，停止填表并归因，不用旧proof拼齐。

实际patch与中文/英文编译须待根给新真实结果并授权；之后检查该表列宽、分页、正文引用和双语一致性，并核主稿/副本同步。此时其它B3/C/D未完成总体数字保持隔离。
