# 后续 D case 完整归档 v2（仅准备）

`archive_d_cases_v2.py` 从已实跑首两包的 v1 适配，仅新增显式 `--acceptance` 和通用冻结集合准入。原 v1、s27/s382 包、producer 和 root post 收据均不改。v2 只完成语法检查，尚未执行或压缩新 case。

根接受收据的接口沿用 pilot：`accepted=true`、`completion_set`（key→completion SHA）、`parent_root_audit_sha256`（实际 root audit SHA）、`review_artifacts`（仓库相对路径→SHA）。completion_set 必须全等所传 root audit 的冻结集合；manifest/source pin 与 root audit 相同。所选电路的全部七臂必须出现在这个已接受集合中，且当前 completion SHA 逐个相同。不能仅因 producer 文件出现而归档。

每包收集所选 case 全七 job 原件、45 份固定执行源、实际 Lib、RTL、完整 manifest 与全部 provenance 输入，以及所传 root audit、独立审查根接受及其绑定 review 原件。包同时保留已结束的 pilot 注册/调用/收据；不把仍在写的 remaining stdout 或未接受 case runtime 目录加入来源。归档根目录中压缩器脚本、调用和工具日志独立保留。

继续沿用 solid LZMA2、80 MiB 分卷、每档 2 threads、来源前后完整 SHA/size、exact 成员/size、7z t、新 scratch 完整恢复逐 SHA。新 case 目录必须不存在，不更新或覆盖任何包。最多两档并发，每档外层 900 秒 wrapper、父进程 930 秒；各 7z 阶段仍有内部 timeout 和每十秒进度。失败保留原件，不自动 resume。

只在根正式逐 case 准入后运行，替换所有占位符并保存准确调用与 raw log：

```text
C:/Program Files/Git/bin/bash.exe code/scripts/run_with_timeout.sh 900 .venv/Scripts/python.exe -X utf8 -u project_docs/evidence/r22_D_revalidation_20261018/full_artifact_archives/archive_d_cases_v2.py --circuit <CASE> --output-dir project_docs/evidence/r22_D_revalidation_20261018/full_artifact_archives/<CASE> --audit <ROOT_COMPLETION_AUDIT_N.json> --acceptance <INDEPENDENT_REVIEW_ROOT_ACCEPTANCE.json>
```

完整恢复只证明证据字节可恢复；历史脚本内的绝对路径不改写，不声称恢复后可以不重新绑定环境就执行 EDA。完成后给根独立 post 验收，再由记录员更新入口。本说明不构成新 case 已归档的结论。
