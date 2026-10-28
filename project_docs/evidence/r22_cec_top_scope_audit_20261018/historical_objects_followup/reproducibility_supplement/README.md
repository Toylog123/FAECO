# 原件恢复补充

本目录仅恢复仍在 scratch 的原字节，未重审、未运行EDA、未改code/HEAD或旧收据。

`original_inventory.txt`为2268字节，SHA与旧`FINAL_READ_SHA_MANIFEST.json`引用完全相同。原`LOG_PATH_DISCOVERY.txt`为2290字节，来自splitlines后重新join，不是原字节副本；两件均保留，差异未覆盖。

`original_audit_script_v1.py`及`original_audit_run_v1.log`从实际scratch原件逐字节复制。记录的v1调用命令见`RECOVERY_RECEIPT.json`。

最终适配prep-top-equiv的执行通过PowerShell here-string输入`.venv/Scripts/python.exe -`。当时没有落盘脚本，也没有保存stdin原字节或本地stdout日志。对话保有工具调用代码，但无法据此证明当时stdin的序列化字节；**最终执行脚本原件/完整重跑性仍unknown**。本补充没有重建脚本并冒称原件，也没有倒签新执行为当时执行。

旧`FINAL_RECEIPT.json`保持不变；本收据仅恢复清单/首版脚本日志，并明确保留最终脚本原件缺失。
