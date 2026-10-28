# D 冻结完成集合独立审查 v2（仅准备）

沿用 `checker_v2.py` SHA `59e51ed56d72fafc3b2dd611bf62028e4491991d6d07ca8bebc4b31ddd9e4250` 与 `--audit` 参数。已做内存 compile 语法检查，尚未执行。原 D14 checker、收据和归档 v1 保持冻结。未读取正在写的 job 原件。

输入是根指定的 `ROOT_COMPLETION_AUDIT_N.json`、同一个固定 manifest/source/Lib 和各 completion 已完成 job。开始时，实际存在的 completion key 集合必须与根冻结集合完全相同，且其逐份 SHA 一致；若开始前又增加 completion，需要根更新审计集合后重新派发。审查开始后新增的 completion 仅在输出中列为未覆盖，绝不计入已验收数量。

checker 独立复用已实跑 D14 的原件级逻辑：逐配置/预登记/输入 SHA；actual candidate event 与 trial/hash/Tcl/log/mapped 的绑定及 WNS/TNS；baseline 与 candidate/cache/前置拒绝分开；观测/有效曲线与 budget；最终 state 和实际 SEC raw/gold/gate/helpers、明确 top 命令、实际日志非零 proven/0 unproven。45 源、HEAD、Lib、manifest/provenance 和所有读取原件前后 SHA 均重新核验。只使用 stdlib，不调用生产验证器、EDA、测试或 Git 命令。

输出 `full_56_registered_keys_reviewed` 只有根冻结集合确为全部 56 个注册 key 且所有检查通过才为 true。中间 N 项成功只接受这些 key；未完成或未审查对象继续开放。不是物理 RC 或四态支持验收。

主线正式派发后，在仓库根目录使用 900 秒 wrapper（父进程上限 930 秒）；运行前把实际 argv、脚本 SHA、根审计 SHA、cwd、日期和日志路径保存到新的调用收据。以下占位符必须替换成实际路径：

```text
C:/Program Files/Git/bin/bash.exe code/scripts/run_with_timeout.sh 900 .venv/Scripts/python.exe -X utf8 -u project_docs/evidence/r22_D_revalidation_20261018/independent_completed_review/checker_v2.py --audit <ROOT_COMPLETION_AUDIT_N.json> --output <NEW_EXCLUSIVE_ATTEMPT_DIRECTORY>
```

stdout/stderr 保存到新的独占 raw log，运行中检查逐 job 进度，失败/超时原件保留；成功后补 final receipt/报告，由根核对后签接受收据。此文件不是运行或成功收据。
