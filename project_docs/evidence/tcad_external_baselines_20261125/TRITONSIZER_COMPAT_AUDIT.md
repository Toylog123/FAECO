# TritonSizer 兼容性实查预检（2026-11-25）

本报告记录对公开仓库 `The-OpenROAD-Project/TritonSizer` 的源码与构建依赖实查，回答其能否接入当前 FAECO 的 OpenROAD 26Q3 / OpenSTA 3.1.0 多角后布线评测后端（关联 [OI-105](../../OPEN_ISSUES.md) 与 [投稿判断](../tcad_publication_assessment_20261125/REPORT.md)）。

## 实查对象与指纹

- 仓库：`https://github.com/The-OpenROAD-Project/TritonSizer.git`（已归档）
- 检出提交：`31c4a04ef232f8a0d386ce962b961ec25bb3d74b`（提交日期 `2018-12-01 16:54:13 -0800`）
- 检出路径（本机 WSL）：`/home/toylog/faeco_tritonsizer_check`

## 兼容性阻塞事实

| 维度 | 实查发现 | 源码证据 |
|---|---|---|
| 构建与计时器 ABI | 强制绑定已淘汰的 Tcl 8.4.20（`core-8-4-20-rc`）与 2018 年私人 fork `https://github.com/mgwoo/OpenSTA.git`，`src/Makefile` 直接静态链接旧版 autotools 产物 `StaApp_wrap.o`、`StaMain.o`、`TclInitVar.o` 及 10 个 `.a` 静态库（`libliberty.a` 等），且硬编码 `ZLIB_HOME = __YOUR_ZLIB_HOME__/lib` 与 `-Wl,-R/liab`，推荐环境为 CentOS 6。与当前 OpenROAD `b511b6a` / OpenSTA 3.1.0 完全不兼容。 | `.gitmodules`、`Makefile`、`src/Makefile`、`README.md` |
| 闭源 Tcl 字节码依赖 | 仓库内包含编译后的 Tcl 字节码 `src/sizer.tbc` 与 2018 年预编译的 64 位共享库 `src/libtbcload1.7.so`，核心控制流未以可读源码提供。 | `src/sizer.tbc`、`src/libtbcload1.7.so` |
| 工艺库与 Liberty 支持 | 自定义 ISPD13 派生解析器（`src/ckt.cpp`）仅列出 TSMC65/45/ST28/16 与 2018 版 ASAP7，明确提示关键字子集有限且部分 Liberty 无法解析；`ckt.cpp` 无 SKY130HD 支持。 | `README.md`、`src/ckt.cpp` |
| 物理闭环接口 | 仅导出 `.sizes` 文本供外部 P&R（如 Cadence Innovus）执行 ECO，不包含 OpenDB 详细重布线、寄生重提取（RCX）及 FF/TT/SS 三角联合验收。 | `README.md`、`src/sizer_os.tcl` |

## 预检结论

TritonSizer 属于 2018 年已归档工具链，依赖 Tcl 8.4、旧版 OpenSTA ABI 与闭源 `sizer.tbc`，无法在保持同工具版本与同 SKY130HD/ASAP7 三角库身份的前提下直接编译接入当前 OpenROAD `b511b6a` 物理评测闭环。同台外部基线以**同版本 OpenROAD 原生 `repair_timing -recover_power`**（标准档与 `-allow_setup_violations` 宽松档）及已有自实现冻结寄生 LR 承担，并在论文相关工作与局限中如实披露 TritonSizer 的归档与工具链兼容边界。
