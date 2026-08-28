# FAECO 脏 main 资产只读清单（P0.1）

日期：2026-08-28
性质：只读盘点。下列文件/目录一律不修改、不恢复、不删除、不移动，也不并入任何合并。

## 1. `git -C D:\BaiduSyncdisk\03_FAECO status --short --branch` 原样输出

```text
## main...origin/main
 M .codex-handoff.json
 M docs/engineering/toolchain_setup.md
 M docs/project_management/decision_log.md
 M docs/project_management/future_task_backlog.md
 M docs/project_management/work_log.md
 M docs/task_board.md
 M paper/zh/README.md
 D paper/zh/faeco_paper.pdf
 M paper/zh/figures/fig3_method_flow_new.png
 M paper/zh/figures/fig_cut_generation_new.png
 M paper/zh/figures/fig_feedback_loop_new.png
 M paper/zh/figures/fig_spef_gate_new.png
 D paper/zh/manuscript/faeco_paper_jcad.pdf
 D paper/zh/manuscript/faeco_paper_jcad.tex
 M scripts/run_outerloop_real_wns.py
 M scripts/run_sequential_timing_check.py
?? .superpowers/
?? docs/engineering/sequential_sec.md
?? docs/project_management/handoff_20260828.md
?? experiments/20260826_b14_old_logs.txt
?? experiments/crossbench_pr_manifest.json
?? "paper/zh/FAECO_\351\235\242\345\220\221\351\242\204\345\270\203\345\261\200\351\227\250\347\272\247\346\227\266\345\272\217ECO\347\232\204\345\244\261\346\225\210\351\251\261\345\212\250\345\200\231\351\200\211\346\220\234\347\264\242.pdf"
?? "paper/zh/FAECO_\351\235\242\345\220\221\351\242\204\345\270\203\345\261\200\351\227\250\347\272\247\346\227\266\345\272\217ECO\347\232\204\345\244\261\346\225\210\351\251\261\345\212\250\345\200\231\351\200\211\346\220\234\347\264\242.txt"
?? paper/zh/figures/_backup_fig3_20260813_154003.png
?? paper/zh/figures/_backup_fig3_20260813_161140.png
?? paper/zh/figures/fig_cross_physical_nature.pdf
?? paper/zh/figures/fig_cross_physical_nature.png
?? paper/zh/figures/fig_cross_physical_nature.svg
?? paper/zh/figures/fig_cross_physical_nature.tiff
?? paper/zh/figures/fig_cut_generation_mechanism_imagegen.png
?? paper/zh/figures/fig_cut_generation_mechanism_nature.pdf
?? paper/zh/figures/fig_cut_generation_mechanism_nature.png
?? paper/zh/figures/fig_cut_generation_mechanism_nature.svg
?? paper/zh/figures/fig_cut_generation_mechanism_nature.tiff
?? paper/zh/figures/fig_cut_generation_redraw_20260814.png
?? paper/zh/figures/fig_feedback_loop_redraw_20260814.png
?? paper/zh/figures/fig_method_flow_redraw_20260814.png
?? paper/zh/figures/gen_cross_physical_nature.py
?? paper/zh/figures/gen_cut_generation_mechanism.py
?? paper/zh/figures/mechanism_figure_redraw_prompts_20260813.md
?? paper/zh/figures/mechanism_figure_redraw_prompts_20260813_simplified.md
?? paper/zh/manuscript/$build/
?? "paper/zh/manuscript/FAECO_\351\235\242\345\220\221\351\242\204\345\270\203\345\261\200\351\227\250\347\272\247\346\227\266\345\272\217ECO\347\232\204\345\244\261\346\225\210\351\251\261\345\212\250\345\200\231\351\200\211\346\220\234\347\264\242.pdf"
?? "paper/zh/manuscript/FAECO_\351\235\242\345\220\221\351\242\204\345\270\203\345\261\200\351\227\250\347\272\247\346\227\266\345\272\217ECO\347\232\204\345\244\261\346\225\210\351\251\261\345\212\250\345\200\231\351\200\211\346\220\234\347\264\242.tex"
?? paper/zh/manuscript/faeco_after_appendix_removal-08.png
?? paper/zh/manuscript/faeco_after_appendix_removal-09.png
?? paper/zh/manuscript/faeco_after_appendix_removal-10.png
?? paper/zh/manuscript/faeco_conclusioncheck-07.png
?? paper/zh/manuscript/faeco_conclusioncheck-08.png
?? paper/zh/manuscript/faeco_conclusioncheck-09.png
?? paper/zh/manuscript/faeco_conclusioncheck-10.png
?? paper/zh/manuscript/faeco_figordercheck-03.png
?? paper/zh/manuscript/faeco_figordercheck-04.png
?? paper/zh/manuscript/faeco_figordercheck-05.png
?? paper/zh/manuscript/faeco_finalall-01.png
?? paper/zh/manuscript/faeco_finalall-02.png
?? paper/zh/manuscript/faeco_finalall-03.png
?? paper/zh/manuscript/faeco_finalall-04.png
?? paper/zh/manuscript/faeco_finalall-05.png
?? paper/zh/manuscript/faeco_finalall-06.png
?? paper/zh/manuscript/faeco_finalall-07.png
?? paper/zh/manuscript/faeco_finalall-08.png
?? paper/zh/manuscript/faeco_finalall-09.png
?? paper/zh/manuscript/faeco_finalall-10.png
?? paper/zh/manuscript/faeco_finalcheck-01.png
?? paper/zh/manuscript/faeco_finalcheck-02.png
?? paper/zh/manuscript/faeco_finalcheck-03.png
?? paper/zh/manuscript/faeco_finalcheck-04.png
?? paper/zh/manuscript/faeco_finalcheck-05.png
?? paper/zh/manuscript/faeco_finalcheck-06.png
?? paper/zh/manuscript/faeco_finalcheck-07.png
?? paper/zh/manuscript/faeco_finalcheck-08.png
?? paper/zh/manuscript/faeco_finalcheck-09.png
?? paper/zh/manuscript/faeco_finalcheck-10.png
?? paper/zh/manuscript/faeco_finalcheck-11.png
?? paper/zh/manuscript/faeco_finalreview-06.png
?? paper/zh/manuscript/faeco_finalreview-07.png
?? paper/zh/manuscript/faeco_finalreview-08.png
?? paper/zh/manuscript/faeco_fullreview_final-1.png
?? paper/zh/manuscript/faeco_fullreview_final-2.png
?? paper/zh/manuscript/faeco_fullreview_final-3.png
?? paper/zh/manuscript/faeco_fullreview_final-4.png
?? paper/zh/manuscript/faeco_fullreview_final-5.png
?? paper/zh/manuscript/faeco_fullreview_final-6.png
?? paper/zh/manuscript/faeco_fullreview_final-7.png
?? paper/zh/manuscript/faeco_fullreview_final-8.png
?? paper/zh/manuscript/faeco_fullreview_final-9.png
?? paper/zh/manuscript/faeco_methodcompact-03.png
?? paper/zh/manuscript/faeco_methodcompact-04.png
?? paper/zh/manuscript/faeco_methodcompact-05.png
?? paper/zh/manuscript/faeco_methodcompact-06.png
?? paper/zh/manuscript/faeco_methodcompact-07.png
?? paper/zh/manuscript/faeco_methodcompact_edges-01.png
?? paper/zh/manuscript/faeco_methodcompact_edges-02.png
?? paper/zh/manuscript/faeco_methodcompact_edges-08.png
?? paper/zh/manuscript/faeco_methodcompact_edges-09.png
?? paper/zh/manuscript/faeco_methodcompact_edges-10.png
?? paper/zh/manuscript/faeco_methodreview2-01.png
?? paper/zh/manuscript/faeco_methodreview2-02.png
?? paper/zh/manuscript/faeco_methodreview2-03.png
?? paper/zh/manuscript/faeco_methodreview2-04.png
?? paper/zh/manuscript/faeco_methodreview2-05.png
?? paper/zh/manuscript/faeco_methodreview2-06.png
?? paper/zh/manuscript/faeco_methodreview2-07.png
?? paper/zh/manuscript/faeco_methodreview2-08.png
?? paper/zh/manuscript/faeco_methodreview2-09.png
?? paper/zh/manuscript/faeco_methodreview2-10.png
?? paper/zh/manuscript/faeco_methodreview2-11.png
?? paper/zh/manuscript/faeco_methodreview2-12.png
?? paper/zh/manuscript/faeco_methodreview3-03.png
?? paper/zh/manuscript/faeco_methodreview3-04.png
?? paper/zh/manuscript/faeco_methodreview3-05.png
?? paper/zh/manuscript/faeco_methodreview4-03.png
?? paper/zh/manuscript/faeco_methodreview4-04.png
?? paper/zh/manuscript/faeco_methodreview4-05.png
?? paper/zh/manuscript/faeco_sec_check_a-04.png
?? paper/zh/manuscript/faeco_sec_check_a-05.png
?? paper/zh/manuscript/faeco_sec_check_b-09.png
?? scripts/build_crossbench_pr_manifest.py
?? scripts/verify_crossbench_sequential_sec.py
?? scripts/verify_iscas89_sequential_sec.py
?? tmp_debug_2dff.tcl
?? tmp_debug_dffmod.tcl
?? tmp_debug_dfxtp.tcl
?? tmp_debug_edfxtp.tcl
?? tmp_debug_regs.tcl
?? tmp_min_2dff.v
?? tmp_min_dffmod.v
?? tmp_min_dfxtp.v
?? tmp_min_edfxtp.v
```

## 2. 分类

| 类别 | 示例/说明 | 处理约束 |
|---|---|---|
| code_modified | scripts/run_outerloop_real_wns.py、scripts/run_sequential_timing_check.py、src 相关改动 | 只读；不并入 Phase 0 实现分支 |
| doc_modified | .codex-handoff.json、docs/engineering/toolchain_setup.md、docs/project_management/*、docs/task_board.md | 只读；由治理分支后续同步 |
| paper_deleted | paper/zh/faeco_paper.pdf、paper/zh/manuscript/faeco_paper_jcad.{pdf,tex} | 只读；删除状态保留，待用户决策 |
| paper_untracked | paper/zh/manuscript/FAECO_*.{tex,pdf}、figures/*new*、$build/ | 只读；未跟踪资产不得删除 |
| experiment_untracked | experiments/20260826_b14_old_logs.txt、experiments/crossbench_pr_manifest.json | 只读；不得删除或改写 |
| scratch_tmp | tmp_debug_*.tcl、tmp_min_*.v、tmp_*.v 等 | 只读；如需清理须用户逐路径批准 |

## 3. 结论

- 本清单与 `baseline-audit.json` 配套；refs 与规格一致（`refs_match_spec=true`）。
- 任何后续批次若需要触碰上述资产，必须先形成独立任务并经用户批准。
