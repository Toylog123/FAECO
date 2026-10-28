# OI049 独立只读证据审查

接受 red_v3 的限定归因：**非空 bytes 异常注入在公共 `check_yosys_abc_equivalence` 的直接 CEC 超时结果组织路径触发 TypeError；OI049 保持开放，待 D 冻结结束后修复。**这不是 false-pass，也没有证明真实 OS/EDA 超时的输出类型或发生率。

本次 checker 仅使用 stdlib 读取文件、解析 AST 和计算 SHA；没有导入/执行生产模块，没有重跑 probe、pytest、仿真、EDA 或 Git。60 秒 wrapper 约 5 秒结束、退出码 0。72 份已读原件（含 45 源）前后 SHA/size 一致，当前源、HEAD 与生产者 f761/45 pin 相符。

| 原件 | 实际核验 |
| --- | --- |
| red_v3/RESULT.json | SHA `bb5e332b4c2c9994c6546388557c68591d3d0a8c9b3277af1c78f28df42a1b27` 与 wrapper 输出一致。 |
| 三组公共调用 | 每组正好一次被 mock 的 CEC subprocess 调用。工具解析与归一化也被 mock；六侧 BLIF 均是相同的单 model top 身份逻辑。 |
| str control | 返回 status=timeout；partial stdout/stderr 为字符串 tail。 |
| nonempty bytes injection | 不返回结果，捕获 TypeError：`sequence item 0: expected str instance, bytes found`。 |
| empty control | 返回 status=timeout，stdout/stderr tail 为空。 |
| 当前源码及 traceback | 公共直接 CEC 分支 193 行接收注入 TimeoutExpired，215 行把非空 bytes 交给 `_tail`，902 行用字符串 join 拼接 bytes splitlines 时抛错。 |
| 输出保真 | TypeError 前 `_write_text_log` 已写可读 log 和 stdout/stderr .bin；两份 bin 与注入原件逐字节相同。错误在结果 tail 组织阶段，不能误说为 log 文件写入失败。 |
| wrapper exit0 | 表示 probe 成功观察到其预期的注入异常及控制结果，不表示 CEC 证明 pass。 |

最初静态关注的 mapped `_run_abc_cec` 路径也使用共享 `_tail`，但 red_v3 实际没有调用该 helper。其它路径的影响仍属静态待验证，不能称已被本探针覆盖。两次控制返回 timeout、bytes 抛异常，均未形成成功等价 verdict。

red_v1/v2 先验要求实际 OS TimeoutExpired.stdout 为非空 bytes；合取断言失败在公共 API 调用之前，没有 RESULT。v2 保存原始重定向 wrapper，v1 仅保留工具 trace 转写及脚本。该断言失败不能区分类型不符与空值，两个版本的真实 stream type/value 都仍为 unknown。red_v1 原说明里“partial stdout 未到达”的推断过强；根新增 `red_v1/SETUP_FAILURE_CLARIFICATION.md` 已实读并包括在本次72件哈希清单中，明确此限制，旧说明/脚本保留不改。两次 setup 失败既不复现也不反驳 OI049。

完整独立脚本、准确调用、raw log、当前源片段/行号及读取前后 SHA 保存于本目录。仅确认现存注入证据与当前源码的关系，未作生产修复；本目录在最终收据写入后冻结。
