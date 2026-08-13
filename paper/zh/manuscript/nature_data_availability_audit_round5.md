# Nature-style data and code availability audit (round 5)

更新时间：2026-08-11

## 可追溯的主结果

| 结果 | 归档证据 | 当前状态 |
|---|---|---|
| ISCAS89 主图与表 5 预布局列 | `experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json`、16 份 `pre_layout_audit/sta.log` | 16/16 WNS 数值逐项匹配 |
| ISCAS89 布线后时序 | 16 份 `pr_run.log`、16 份 `final.odb`、`manifest.json` | 8 个电路可追溯；无 DRC 报告，不能写 DRC signoff |
| ITC-99 主表与主图 | 19 个 `outerloop_result.json`、`batch_progress.log` | 19 个电路、1693 次候选 STA、18/19 改善 |
| 20 轮策略收敛 | `experiments/20260807_multiround_8c_067/convergence_summary.json` | 与正文的独立收敛实验绑定 |
| SPEF 扫描与门控 | `experiments/20260805_parasitic_*`、对应 `scan.json`/`summary.json` | 作为估计线载下的筛选/拒绝信号，不作为版图后证明 |
| 代理排序 | `src/rseco/proxy_ranking.py`、`experiments/20260811_proxy_*` | opt-in 审计链路已落地；未作为主结果因果解释 |

## FAIR/复现检查

- 公开基准、工具和 SKY130 PDK 已在论文参考文献与实验设置中注明。
- 主结果图脚本直接读取 ISCAS89 审计汇总和 ITC-99 逐电路 JSON，不再依赖主结果手填数组。
- `experiment_data_dictionary_round5.md` 绑定论文数字、运行配置和原始产物路径；其中明确区分 27/110、20 轮、ITC-99 1693 次以及 b18/b19 独立补充实验。
- 当前归档没有作者数据、人体数据或受限数据，不需要隐私或受限访问说明。

## 投稿前需要完成的外部发布动作

当前工作区尚未分配稳定的公开仓库 URL、版本号或 DOI。正式投稿到要求公开数据/代码的期刊前，应将上述脚本、JSON、STA/P&R 日志、必要的 `final.odb`、图表源文件和数据字典打包上传至机构仓库或认可的数据仓库，再把实际 accession/DOI 写入数据与代码可得性声明；本轮不虚构链接或 DOI。

## Nature 风格图件

`paper/zh/figures/nature/` 已生成同一批主图的 PDF/PNG 版本。当前 JCAD 稿件使用 PNG；若转投 Nature 系列，应优先提交 PDF/SVG 等矢量版本，并按目标期刊的字体、线宽、色彩和分辨率要求再做一次投稿前检查。
