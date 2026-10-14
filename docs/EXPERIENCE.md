# 开发经验库（踩坑记录）

> 解决问题后当天登记。历史坑位自 work_log 摘录高频项，完整记录见 `project_docs/LOGS.md`。

## 2026-10-14 r22 回归时不可并行修改被测源码/fixture

- **现象**：第二次全回归628passed/1fail，batch输入锁stub失败；同一会话pytest已经载入旧fixture，但主线又加入LIB/mapped锁并修改production脚本，发生旧fixture与新脚本组合。
- **归因**：测试对象跨版本，不是这个结果已推翻实验设计。新输入锁与Path(m.LIB)统一必须在稳定组合中重测。
- **处理**：停止core编辑，重启session14951全回归，测试期间保持production源码、fixture与输入锁不变；若必须接纳修改，废弃旧验收对象并重新启动，不边测边改。
- **验证**：稳定最终源码实际629passed/4skipped/156subtests、99.79s，timeout包装102s/exit0。前两次回归只作历史，不合并为当前门；正式EDA未启动。

## 2026-10-14 r22 静态mincut探针：先检验预期，保留无作用与tie

- **现象**：P2原断言uniform与高size权重应选不同门，实际两者都选g1，断言失败。
- **归因**：实际求解确认uniform为确定tie，高size也选择g1；测试预期不能从“权重改变”自动推出“这个输入割必改变”。这不是已经证明实现错误或方法无效。
- **修复**：以高size与默认配置（g2）检验代码具备改变割的能力，同时保留uniform确定tie与根退化场景；不删零差异例，不为了pilot好看换真实实验臂。
- **验证**：主线TDD先失败后通过，candidate十二项与批运行器共15passed/0.21s，无EDA。静态可辨识能力不等于实际电路时序贡献，正式C′按预锁正负判据报告。

## 2026-10-14 r22 历史来源恢复：JSON缺字段可用独有报告交叉验证

- **现象**：r21仅依旧JSON判断b17新STA数量不可识别；该判断不能证明仓库其他档案也没有来源。r22先查既往/原始报告，而非重跑或补造schema。
- **恢复**：b17的104条trial按iteration与组内序号精确对应104独有STA日志/Tcl，所有日志有限WNS与trial相同，候选mapped输入路径一一绑定；当前可报告104个有独有来源的候选STA结果，结合另18实例2890得到2994。它不含基线/刷新/重试/SEC的所有工具执行。
- **验证**：只读历史审计300s超时包装、51s/exit0，输入清单及两个结果JSON哈希回验；证据为r22_historical_audit_20261014包。主线确认B/D计数可闭合；没有改原始档案、没有新EDA。
- **边界**：C的输出目录跨pass覆盖，缺base hash与实际revision；重复candidate描述不等于缓存，现存报告数不等于历史总调用。flags恢复分recovered/launcher_recovered/inferred/missing，launcher模板不能当实际argv证书。s382 v3的数值/输入匹配不证明发布身份，不自动借入主表。
- **复用**：先用独有报告/Tcl/输入哈希寻找可审计来源；无法恢复的身份/执行数明确保留，不猜参数、不套其他族缓存规则，也不把档案审计拖成无期限等待。

## 2026-10-14 STA 台账：来源字段不证明新执行，缺失 schema 不等于零

- **现象**：D 的归档 B(k) 含 `skipped_duplicate`，缓存字典保留旧 STA provenance；旧 runtime 把全部评估记录当测量。B 的 3363/664/104 也恰等于全部 trials，含前置拒绝/缓存，不能称新增 OpenSTA 次数。
- **根因**：逻辑评估记录、带来源记录、新 STA 执行、预算计数是不同事件；字段名 `n_candidate_sta_runs` 和有 provenance 不足以证明新测量。
- **修复**：D 从原始 trials 筛有效来源/WNS 并剔缓存，逐运行与唯一报告路径和 sta_used 对齐；实际图轴/表列使用重建数，旧记录列与墙钟保持。B 的指标名改为评估记录；18 实例可确认新 STA 2890，b17 缺来源/缓存 schema，保留未知，不能补 0 或把 104 全当新执行。
- **验证**：独立 `methodology_verification.md`、`sta_count_followup.md` 与当前主稿一致；D Fixed/EMA 新 STA 1947/2003，随机均值 2480.7；本轮全稿质量门零错误/溢出/未引用。只做已有台账重算，没有新 EDA。其它族审计继续留 OI-034。
- **复用规则**：计数单位先落到真实事件、原始记录和独有报告路径；同族缓存标记规则不能套给缺字段的历史 schema。曲线按各臂停止位置结束，不在停止后外推收益。

## 2026-10-14 双栏末页 balance 的微小 vbox 溢出

- **现象**：r21 内容与配图集成后仍有末页 0.8534 pt Overfull vbox，hbox 和引用已全通过。
- **归因与修复**：主线单独禁用旧 balance 后溢出归零，定位为末页平衡算法；enlargethispage 引入 Infinite glue shrinkage，已回退。使用本机 `flushend[noshrink,nospread]` 平衡双栏，未缩字体/行距/砍内容。
- **验证**：当前 `.tex` 已使用 flushend，`build_qa.json` 为 12 页、hbox/vbox 全零。该解决只适用于本稿/当前安装的包版本；后续版式变动仍要重编译并看末页，不照搬通过结论。

## 2026-10-14 配图数据读取：零候选 schema 与符号字形

- **现象**：r21 配图首跑读取 s641 的 S 统计时缺少 `tier2`，报 KeyError；部分数学下标/对号未被导出字体覆盖。
- **归因**：原始 `summarize_s_l1.json` 的 s641 确实是零抽窗、零候选、零测量，不提供候选测量汇总层。把每电路都当成非空候选 schema 是读取实现错误，不能据此认定数据丢失；字体中没有对应字形是另一个导出问题。
- **处理**：`paper/zh/figures/data/scripts/review_r21_figures.py` 仅在 `n_candidate == 0` 且 `n_measured == n_extracted == 0` 的断言成立后生成全零分类；其他电路继续直接读取 `tier2`，保留分类总和与总候选数断言。缺字标记改为覆盖可用的字形/字体。
- **验证**：实读零候选原始记录与当前分支，首版图件已导出；最终六新图和整稿逐页视觉/字形审计通过，详见r21 qa_notes。此为既有证据的绘图读取/导出修复，不是新 EDA 实验。
- **复用规则**：零候选可补零分类必须基于明确 schema 与零抽窗/测量断言；对未知缺项直接补零会掩盖证据缺失，不可采用。导出成功后仍要目检字形，不能只看进程 exit code。

## 2026-10-14 预算曲线读取：配置字段层级不能从参数名猜测

- **现象与归因**：新增既有族 D 的 B(k) 备选图时，首次读取把 `sta_budget` 当 `run_config.json` 顶层字段；真实配置保存在 `resolved_args` 中，这是绘图读取实现问题。
- **修复与验证**：改为 `config['resolved_args']['sta_budget']` 并断言为 500；同族全部电路、全部配置分别加载自身数据，按各自自然终止点截断。最终入稿文件为 `fig5_budget_curves_r21`（前期备选名figD），实际轴又按原始台账剔缓存重建，详见上方计数修复；不将族 C 数字接入曲线。
- **复用规则**：先实读原始 JSON 的 schema，再绑定图中计数单位。预约额度不是实际 STA 测量次数，配置字段正确读取也不能将两种计数自动等同。此为既有数据后处理，不是新 EDA 实验。

## 工具链

1. **Windows Yosys 0.9（32 位）映射大电路 OOM**
   - 现象：b18/b19（原型约 7.0 万/23.1 万门；**2026-09-28 更正**：原记「37.6 万/75.5 万门」在任何证据文件中均无法定位，映射后为 7.57 万/15.10 万个 SKY130 单元，见 `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md` §6）read_verilog bad_alloc；$shr 技术映射 OOM。
   - 解决：WSL2 64 位 Yosys 0.33（`run_yosys_mapping` 增加 `yosys_cmd` 参数）。
   - 验证：b18/b19 映射成功（峰值 4.7 GB）。

2. **SKY130 `clkinv_1` 不在 Liberty → CEC unavailable**
   - 解决：从 Liberty boolean function 提取 assign-style `sky130_cells_v2.v` + Yosys `miter -equiv` + `sat -prove-asserts`；8/8 等价证明通过（20260803）。

3. **b19（7.5 万单元）WSL2 STA 输出截断**
   - 解决：`run_opensta()` 3 次重试 + 手工复测校验（WNS=-17.42 一致）。

## 形式验证

4. **顺序 SEC `find_same_wires` 局限（b17 剩 1 个未证明点）**
   - 现象：nor4b_1→nor4b_2 同函数尺寸替换因两侧 wire 命名不一致未匹配。
   - 结论：Liberty function 等价即 effective_pass；论文如实单独报告（12812/12813）。

## 流程 / 工程

5. **多轮 ablation 被 early-stop 截断（假阴性）**
   - 原因：flow.py 接受分支无条件 return True。
   - 解决：仅 `early_stop` 开启时提前返回（flow.py:471）；264 测试全绿；备份 `project_docs/archive/superpowers_backup/T19_20260908/`。

6. **论文数字与实验产物混源（2026-09-11 审计）**
   - 教训：同一小节混用两轮运行数字（1012 次 STA、b21 +2.16、JOINT-12 均无产物支持）。
   - 规则：先更新聚合 summary 再动论文；审计记录 `project_docs/review_history/paper_audit/consistency_audit_20260911.md`。

7. **仓库迁移（2026-09-12）**
   - 目录 rename 被 BaiduSync 客户端句柄阻塞（Device or resource busy）→ robocopy 复制（316,765 文件/117.7 GB，0 失败）+ 源目录留作归档。
   - `.venv` 可编辑安装路径失效 → 重新 `pip install -e .`；硬编码绝对路径脚本改为 `__file__` 锚定。

8. **LaTeX 双栏 `figure*` 独占整页造成版面塌陷（2026-09-28）**
   - 现象：第 5 页仅 7 行、约 80% 空白；且 §3.3 正文在上一页末被截断，跨过图页才续上，阅读流断裂。
   - 根因三重叠加：① 图为 1254×1254 正方形、宽度 `0.85\textwidth`（14.4×14.4 cm）过高；② 位置参数 `[!htbp]` 含 `p`，允许 LaTeX 生成"只含浮动体"的浮动页；③ 图前 `\FloatBarrier`（`placeins` 包）强制立即输出，与图后屏障形成夹逼。
   - 解决：改 `[!tb]` 禁用浮动页 + 宽度降到 `0.55\textwidth` + 删除图前屏障 + 合并相邻重复 `\FloatBarrier`（全文 20 处，其中 2 组为连续重复，功能等价无意义）。
   - 结果：10 页 → **9 页**；第 5 页 7→43 行（图 + 正文 + 表 3 同页共存），末页结论与参考文献同页、不再孤立成页；0 Error / 0 Overfull / 0 Underfull。
   - 规则：双栏文档慎用 `figure*` + `p` 位置 + `\FloatBarrier` 三者叠加；`\FloatBarrier` 只在节边界保留 1 个，禁止连续重复（重复调用无额外作用，却让版面僵硬）。

9. **PDF SHA256 不能作为"内容一致"的判据（2026-09-28）**
   - 现象：同一 `.tex` 一字未改，重编译后 PDF SHA256 由 `5c98b77d…` 变为 `611741c5…`，看似"内容变了"。
   - 根因：PDF 内嵌编译时间戳（CreationDate / ModDate）元数据，每次编译字节必变。
   - 解决：判定内容是否真一致改用 **`pdftotext -layout` 全文的 SHA256**（本次 `856fac5b…`），并配合页数与质量门；实测两次编译文本指纹完全相同、`diff` 无差异，确认仅元数据变化。
   - 规则：冻结记录须同时给出「PDF 字节 SHA256」（标识该文件副本）与「文本指纹」（标识内容）；不可只用前者断言内容一致，也不可因前者变化就判内容被改。

10. **`\FloatBarrier` 在双栏下退化为 `\clearpage` → 孤儿参考文献页（2026-09-29）**
   - 现象：论文改完正文后编译多出 1 页，第 10 页仅 8 条参考文献、约 80% 空白；上一页左栏亦有约 28% 留白。
   - 根因：`placeins` 的 `\FloatBarrier` 在**双栏模式下遇到待排浮动体会退化为 `\clearpage`**（须把两栏都清空）。§3.4 表 `tab:failures` 之后、§3.5 之前那处屏障前方有表未排出，于是强制结束该页 → 正文整体后移 → 参考文献被挤成独立末页。
   - 解决：**只删掉那一处多余 `\FloatBarrier`**（除该行外 `.tex` 与上一版逐字节相同，`diff` 输出仅 `311d310`）。10 页 → **9 页**；第 5 页 = 图 2 + §3.3 正文 + 表 3 + §3.5 开头，第 9 页 = §5 结论 + 参考文献 [1]–[19]（约 95% 满）。
   - 规则：**页数异常 / 末页孤儿 / 大面积留白，第一优先是逐个试删（或下移）`\FloatBarrier`，而不是缩字体、行距或砍内容。** 排查方法：数出全文所有 `\FloatBarrier` 位置（`grep -n '\\FloatBarrier'`），每次只删一处后重编译，看页数与每页有效行数（`pdftotext` + 按 `\f` 切页统计）。

11. **内容指纹依赖 pdftotext 实现：Git Bash 的 `pdftotext` ≠ poppler（2026-09-29）**
   - 现象：冻结记录的内容指纹 `7adf0279…` 用"同一条命令"复算得到 `443c5c3a…`，看似内容被改；但 git 工作区干净、PDF 字节 SHA256 与冻结记录一致。
   - 根因：`pdftotext` 在本机有**两个实现**——Git 自带 `C:\Program Files\Git\mingw64\bin\pdftotext.exe`（**xpdf 4.00**，Git Bash 默认解析到它）与 WinGet poppler `…\poppler-25.07.0\Library\bin\pdftotext.exe`。两者对同一 PDF 提取的文本不同（布局/空格处理差异）→ 指纹不同。用 poppler 25.07.0 复算**精确复现** `7adf0279…`，证实内容未变、指纹 oracle 是工具相关的。
   - 规则：**文本指纹必须连同工具版本一起冻结**——记录指纹时注明工具（本仓钉定 poppler 25.07.0：`"$LOCALAPPDATA\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin\pdftotext.exe"`）；复算不一致时**先用 git 干净度 + 字节 SHA 排除文件被改，再换 pdftotext 实现逐一对算**，不得直接判"内容被改"。

12. **双栏稿压页：删掉正文全部 `\FloatBarrier`（2026-10-09）**
   - 现象：文字收敛后末页出现孤儿参考文献页（[13][14] 独占第 9 页、约 93% 空白）。
   - 排查：① 先证"参考文献本身无压缩余地"——`itemsep≈0`、`\linespread{0.95}` 下仍 9 页；② 删约 5 行正文 → 仍 9 页（省下的空间被栏底松动吸收）；③ 按经验 10 的思路**逐处删除 `\FloatBarrier`**（正文原有 11 处，均为节边界）→ 配合 7 处去重编辑。
   - 解决：**只保留图 2（全宽 `figure*`）之后那 1 处**，其余 10 处全删。9 页 → **8 页**，且**图/表的页面分布逐项不变**（先在与主稿逐字节一致的实验副本 `_exp8.tex` 上验证，再落到主稿）。
   - 规则：双栏稿正文**不应放** `\FloatBarrier`；它只在"约束某个全宽浮动体的落点"时才值得保留。压页次序恒为 **调浮动体参数 → 删屏障 → （最后）才考虑改版式**；禁缩字体/行距/砍内容。并在导言区留维护注记，防止后人回插。

13. **Word 转排管线硬编码摘要，只改 OUT 路径会产出旧摘要（2026-10-09）**
   - 现象：v5 轮重建 Word 稿时只改了 `postprocess.py` 的 `OUT` 路径，结果 `…20261009b.docx` 的摘要**实为 v4 文本**（v5 摘要从未进入 Word 稿），而文档却声称"随 v5 重建"。
   - 根因：`scratch/word_convert/postprocess.py` 内 `zh_abs` / `en_abs` / 中英关键词 / 标题 / 作者均为**硬编码字符串**，**不从 `.tex` 读取**；管线各步（preprocess → pandoc → postprocess → Word 导出）对摘要文本无一致性校验。
   - 解决：以 `.tex` 为准重写硬编码块（并核对字数），重跑整条管线产出 `…20261009c.docx`；缺陷归档 `word/superseded/README.md`。
   - 规则：**改摘要/标题/关键词后，必须同步 Word 管线的硬编码块并重跑整条管线**；验收时须从产出的 Word/PDF 反读摘要文本与 `.tex` 逐字比对，`preprocess.py` 的 `N_BIB` 计数守卫也要随参考文献条数变化同步。

14. **内容指纹值会跨文档传播并被误记——必须回验（2026-10-09）**
   - 现象：v6 冻结记录的内容指纹 `91034fee…` 被写入 11 个文件；但用**任何**提取口径都复现不出它。
   - 排查：以 v5 的 PDF（从 git 取回）反推口径——`pdftotext -layout <pdf> - | sha256sum`（**原始输出，不去空白**）精确复现 v5 记录值 `0a2b0723…`；据此口径，规范脚本对 v6 稳定给出 `88b03403…`（连跑两次一致）。
   - 结论：`91034fee…` 为误值（字节 SHA `09197e5f…` 与页数均正常，说明 PDF 未变）。已更正全部 11 处。
   - 规则：**内容指纹必须由脚本按固定命令现算**，不手抄、不跨文档复制粘贴；跨文档引用指纹时回验一次。判内容一致用**指纹**，判文件副本用**字节 SHA**，两者不可混用。
