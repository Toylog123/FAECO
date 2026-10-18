# r22 审稿与修改证据（2026-10-16）

各报告均为固定快照，不以实时运行计数补写旧报告。最新运行入口见 `project_docs/agent_handoff/README.md`。

- `CLAIM_REPLACEMENT_MAP.md/.json`：17项主张、图4–7、中英各14表与396份实际来源；以MATRIX_AUDIT_24为当时截止，原稿SHA保留。后续完成状态不倒填该快照。
- `TIMING_CONSTRAINT_CHECK.json`：187份Pico保留STA脚本；`TIMING_CONSTRAINT_MAIN27.json`：27份canonical B基线。实际周期分别为Pico 5/2/0.5 ns及ISCAS89/ITC-99 0.5 ns。
- `metadata_correction_01/`：中英设置/图4图注的最小纠错、原稿/改后/旧PDF字节、两遍编译、38页渲染与细查、14数值表/7图引用保持、PDF句回读及中文双副本同步。`FINAL_QA.json`和`SYNC_RECEIPT.json`是验收入口；中稿12页/英稿26页，仅该元数据问题已修。
- `MATRIX_FIGURE_SOURCE_PREFLIGHT*.json`：全矩阵配图的代码预检，v2为18PASS/2WARN/0FAIL。原无anchor版本和预检留档；旋转锚点已修，PNG预览及170mm项目图幅两警告有明确用途。51项不完整审计实际被拒绝且不创建输出目录。全72数据未验收前不生成全矩阵图，不把代码预检当出图/科学验收。

主张与图表的科学回填仍须逐族完成：C′来源/代价对照、D反馈复验、B3与C重建、独立S/SPEF域与对象审计。C′禁用physical/S，不能替代这些证据；中英文均为待科学证据补全的工作稿。

## 2026-10-18 后续快照

全72已由MATRIX_AUDIT_72独立验收并完整归档；最终四面板审查预览为 `../../figures/data/previews/r22_matrix_gain_cost_v3/`，72原始点和64配对差完整保留。图源更新后预检19PASS/2WARN/0FAIL，对齐/碰撞/字形门与实际查看记录见其目录。v1自动碰撞发现6处标签边界重叠，原件及当时人工审查保留，v3修正后0FAIL/0WARN。独立数据/全轨迹及新布局审查在同级 `../r22_20261018/`；旧24项/准备阶段不倒填。未观察到独立权重收益，后续方法设计需依此推进。
