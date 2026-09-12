# Changelog

本项目变更日志（按时间倒序；格式参考 Keep a Changelog）。

## [Unreleased]

- 待记录（本版本之后的变更在此累积）

## [v2.0] - 2026-08-11

### 新增
- 科研技能库：安装 nature-skills（19 个科研技能，覆盖检索/写作/绘图/审稿/统计）
- 中文论文模板：按《计算机辅助设计与图形学学报》格式重写（A4、LuaLaTeX、字体入项目 `paper/zh/fonts/`）
- 论文示例：`example_paper.tex`（完整演示期刊格式）
- 审稿轮次归档：`paper/zh/review_rounds/`（每轮意见+回复+修改前论文）
- 审稿工作流：多智能体并行审稿（5 个审稿 skill）+ 讨论综合
- 机制图提示词：`drawing_prompts/MECHANISM_FIGURE_PROMPT_TEMPLATE.md`（结构示意，草图后用户手绘）
- 归档规范：`project_docs/ARCHIVE_POLICY.md`（全对象版本迭代归档）
- 多智能体监控：派发后监控子智能体是否有实际进展（防空转卡死）

### 变更
- 论文编译从 XeLaTeX 改为 **LuaLaTeX + OSFONTDIR**（项目内字体，跨电脑免装）
- 写作规范通用化：`chinese-paper-style` 适用于论文/技术说明/报告/设计文档
- 文档更新清单：按触发时机更新所有相关文档（不只 LOGS/进度/未决）

## [v1.0] - 2026-08-06

### 新增
- 通用工程模板框架初始版本：立项（创新评估+自杀式测试）→ 开发 → 实验 → 证据 → 论文 → 版本 → 交接 全流程
- 交接体系：`agent_handoff/` 6 件套 + 推送检查清单
- 记录机制：进度 / 日志 / 状态 / 周报 / 未决问题 / 经验库
- 版本管理：`versions/` 冻结快照 + 具名基线 + git 纪律
- 学术技能：ARS 技能包（deep-research / academic-paper / reviewer / pipeline）
- 工具：check_record / check_project / make_manifest / Makefile / CI
- 协作规范 CONTRIBUTING / 安全 SECURITY / 立项评估 PROPOSAL
