# FAECO 决策记录

更新时间：2026-07-20

| 日期 | 决策 | 理由 | 影响 |
|---|---|---|---|
| 2026-07-07 | 主线不再执着恢复旧代码 | 旧代码找不到或可能存在大问题 | 以旧论文思想为基础重做新工作 |
| 2026-07-07 | 第一篇先冲中文工程类论文 | 当前目标是稳妥发表，中文更适合快速落地 | 写作和实验标准按工程类论文组织 |
| 2026-07-07 | 新方法暂定名 FAECO，不沿用 RSECO | 避免被认为只是整理学长工作 | 论文叙事变成继承思想后的新方法 |
| 2026-07-07 | 第一阶段先做 combinational cone | 降低实现复杂度，先验证核心机制 | 第二阶段必须补 sequential cone 以贴近真实场景 |
| 2026-07-07 | 第一版 ranking 不用 GNN/RL | 避免工程复杂度过高，保证可解释性 | 使用确定性 scoring |
| 2026-07-07 | 核心创新放在 failure-aware cut refinement | 比 benchmark flow 更像算法贡献 | 论文贡献顺序以算法为先 |
| 2026-07-07 | 原始材料保留原位，另建归纳索引 | 保证可追溯且避免破坏历史材料 | `docs/materials/` 作为派生索引 |
| 2026-07-14 | 旧稿不按原样投稿 | 旧代码、工业数据、baseline 和公式证据链不足 | 旧稿转为 FAECO 的问题来源和历史证据 |
| 2026-07-14 | 第一批 benchmark 优先 ISCAS85 与 EPFL | 二者公开、规模可控，适合验证 combinational cone 机制 | 该初步决策已被 2026-07-19 许可审计收窄：ISCAS85 当前文件仅作 smoke，EPFL 作为论文主来源 |
| 2026-07-14 | 每个 ECO case 采用统一 schema | 后续代码、实验和论文表格需要可追溯数据结构 | 以 `docs/experiment_design/case_schema.md` 作为实验数据约束 |
| 2026-07-14 | Git 分支使用 `main` | 避免后续从默认 `master` 再迁移 | `.git` 已初始化，尚未创建首次提交 |
| 2026-07-14 | 第一版测试使用 Python `unittest` | 不引入额外测试依赖，先保证最小骨架可验证 | 测试命令为 `python -m unittest discover -s tests` |
| 2026-07-19 | Stage A 论文主数据源固定为 EPFL `v2025.1` | 官方仓库提供固定版本和 MIT license；当前第三方 ISCAS85 文件的 license 未声明 | EPFL 待规范化和 formal 验证后进入主实验；c432/c499/c880 仅保留本地 smoke，不进入可再分发包 |
| 2026-07-20 | X18 formal scope 采用门级网表对比 | 先比较经 Yosys 规范化后的 gate-level full-netlist 全部主输出，避免把结构签名、candidate boundary 或未接入 runner 的探针混作正式 formal | 正式 runner 需要记录 normalized gate-level artifacts、ABC `cec` scope、命令、版本、日志和 runtime；candidate/boundary-level formal 留作后续扩展 |
| 2026-07-20 | X21 权威内部格式采用 Yosys JSON | EPFL 原始 Verilog 和 `write_verilog -noexpr` 均不适配当前轻量 parser；Yosys JSON 能保留结构、端口、cell 和 escaped identifier 信息，适合作为 FAECO 的可追溯 normalized representation | 第一波 EPFL 导入转为实现 Yosys JSON importer、gate/level 统计、source blob/notice 记录和对官方 BLIF 的 formal 回验 |
