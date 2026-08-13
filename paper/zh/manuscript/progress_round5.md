# FAECO 审稿—实验对齐推进记录（round 5）

更新时间：2026-08-11

## 已完成

1. 核对既有实验来源：20 轮混合/纯 G/纯 B、8 电路真实外层 27 次、110 次 full-candidate、SPEF 扫描、hold、ITC-99/PicoRV32 和 8 电路 P&R 均能在 `experiments/` 找到对应产物；因此没有把已有数据误判为“尚未做过”。
2. 建立 `experiment_data_dictionary_round5.md`，绑定主要数字、配置、口径和证据边界。
3. 从 WSL `/home/toylog/pr_iscas8` 找回并归档 16 份 `pr_run.log` 与 16 份 `final.odb`；确认 P&R 表可做布线后时序复核，但该批次没有 DRC 报告。
4. 修正论文：删除失效的 `eq:score` 引用；把 27/110 改成描述性调用数对比，不再写成已证明的同候选空间无损加速；补充 P&R 日志/ODB 来源和 DRC 限定；说明历史主批次未使用代理特征。
5. 增加 opt-in `--proxy-ranking` 审计开关和逐候选 proxy 字段；focused tests 通过（当前 CLI/proxy/real-STA/batch 共 30 项）。
6. 运行代理审计 smoke 与部分 8 电路批次：smoke 29/29 候选有代理字段；大批次 7 个电路完整落盘，s420 在父批次超时前不完整。该批次未被写入主结果。
7. 对 P&R 表的 16 个 baseline/fixed 网表补做同约束预布局 OpenSTA 审计；16 个 WNS 与表 5 预布局两列逐项一致，生成 `experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json`。
8. 核验 ITC-99 0.67 复验的 19 个 `outerloop_result.json`：候选 STA 调用次数加总为 1693，18/19 改善，b06 失败；主图脚本已改为直接读取 ISCAS89 审计汇总和 ITC-99 逐电路 JSON，移除主结果图的手填数组。
9. 修正 b18/b19 被误写入 ITC-99 19 电路大规模名单的事实错配；补充 Nature 风格数据可得性审计和 round-5 综合复审报告。

## 关键判断

- 旧主实验的 27/110 数字来自历史 runner，旧 JSON 没有代理特征字段；不能事后把代理评分归因到这些数字。
- 新代理默认改为关闭，只有显式 `--proxy-ranking` 才改变候选顺序，避免无声改变历史实验口径。
- 新代理审计批次改变了搜索轨迹，且未复现旧 27 次批次的逐电路行为；目前只能证明记录链路可审计，不能声称代理带来质量或效率提升。

## 下一步

1. 已完成重新编译、渲染与摘要/ITC-99/27/110/P&R/表格布局检查。
2. 已完成全量 pytest 和 PDF 文本/版面审计。
3. 已完成 Nature/academic/user-style 三视角复审；未发现“代理已验证”“同空间无损”“DRC signoff”“SEC 已完成”等越界表述。
4. 当前不新增 proxy/legacy 实验；只有在投稿前需要公开候选全集或外部 artifact DOI 时再做发布打包，不替换已有主结果。
