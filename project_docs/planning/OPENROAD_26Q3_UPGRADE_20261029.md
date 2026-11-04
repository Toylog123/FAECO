# 物理验证工具链统一升级到 OpenROAD 26Q3 — 定案

日期：2026-10-29
状态：**已定案，执行中**

---

## 1. 触发问题

ITC'99 `b12`（629 cells / 121 dff）在 `detailed_route` 阶段抛 `DRT-0073` 后 core dump，
util = 35 / 20 / 5 三档全部复现，`Blockages` 恒为 24107（约 38 个/cell），
`yosys check` 对网表无任何告警。ISCAS'89 的 `s382` 卡在 OpenRCX `order_wires` 不终止，
`s713` 同类。三例都记为「未评估」。

根因判断：**工具版本与平台数据错代**。

| 组件 | 现用版本 | 年份 |
|---|---|---|
| OpenROAD | `v2.0`（`a5a56584`） | 2021 |
| sky130hd 平台文件（LEF/TLEF/RCX rules） | ORFS `da8f092a`（26Q3） | 2026-07 |
| yosys | 0.70+255（nightly 20261028） | 2026-10 |

平台文件是 2026 年的，布线引擎是 2021 年的，中间隔了五年。
`DRT-0073` 出现在「处理布线网格/障碍」阶段，正是这五年里改动最频繁的部分。

---

## 2. 决定

**整族一起换，不给 b12 单开一套。**

理由：`same claim ⇒ same revision + same config family`。
若只有 b12 用新版、其余 18 例留旧版，则 `phys17.tsv` / `phys_itc.tsv` 内部即跨栈，
任何跨电路的横向比较（如"规模越大退化越强"）都不成立。这比"b12 缺失"更严重。

因此：**升级后全部 19 例（ISCAS'89 17 + ITC'99 3，含已失败的 s382/b12）在同一新栈上重跑**，
旧结果整份保留为历史修订，不删不改。

---

## 3. 版本锁定

| 组件 | 锁定值 | 来源 |
|---|---|---|
| OpenROAD | tag `26Q3` = `a9147cf3aebe65e058bb3fa89c1f9e524488dbb8`（2026-06-30） | gitcode `gh_mirrors/op/OpenROAD` |
| OpenSTA（`src/sta`） | `8572175ac45c42ce8d3d772f73bbb059786b9c66` | codeload 直连 |
| abc（`third-party/abc`） | `d527cfab4ad731b767ea0a2be2021d920d3afece` | codeload 直连 |
| slang-elab（`third-party/slang-elab`） | `82effc8d9541be69e1ed3ec44759a4449f5d9247` | codeload 直连 |
| slang（嵌套） | `f04e81565793c768b747a8fd058f3e7aeceee1b5` | codeload 直连 |
| fmt（嵌套） | `553ec11ec06fbe0beebfbb45f9dc3c9eabd83d28` | codeload 直连 |
| or-tools | `9.14.6206` 预编译包（`or-tools_amd64_ubuntu-24.04_cpp`） | GitHub release 直连 |
| SWIG | 4.3.1（源码构建，26Q3 要求 >= 4.3） | codeload |

不采用 26Q4：它是 2026-10 刚发的季度版，而本地 ORFS 检出、平台文件、RCX rules 都是 26Q3 同代。
**OpenROAD / ORFS / 平台文件三者同代**才能保证"同配置族"。

---

## 4. 安装布局（不动系统）

全部装在用户目录，不写 `/usr/local`，不覆盖现有 v2.0：

```
/home/toylog/faeco_eda/
├── or26Q3/                  # 新 OpenROAD 安装前缀（cmake --install 目标）
├── build26/
│   ├── OpenROAD-src/        # 26Q3 源码 + 全部子模块
│   ├── or-tools/            # or-tools 9.14 预编译（含自带 abseil）
│   ├── deps/root/usr/       # 19+ 个 dev 包的解包结果（spdlog/fmt/absl/protobuf/tbb/...）
│   └── build/               # ninja 构建目录
└── oss-latest/              # yosys 0.70+255（不变）
```

好处：
- 现有 `v2.0`（`/usr/local/bin/openroad`）与 `sta 3.1.0` 原样保留，可随时对照
- 回滚 = 不调用新前缀，零副作用
- 全程无需 `sudo`（除 SWIG 之外全部本地解包；SWIG 也本地构建）

## 5. 国内可达性（实测）

| 资源 | 路径 | 实测 |
|---|---|---|
| OpenROAD 源码 | gitcode `gh_mirrors/op/OpenROAD` | 1.8 GB，57 秒 |
| or-tools 预编译 | `github.com/google/or-tools/releases/...` | 54 MB，12.6 MB/s |
| 子模块 | `codeload.github.com/<repo>/tar.gz/<commit>` | 全部 200（92 MB 也可） |
| dev 包 | USTC apt 源 + `dpkg -x` | 21 个 deb，41 MB |

**修正旧记录**：此前 `EXPERIENCE.md` 第 66 条称"codeload 直连被截断在 ~7 MB"，本次实测
92 MB 的 OpenSTA 一次成功，该结论对当前网络已不成立，需更新。
另：`api.github.com` 可用（可精确取子模块 commit），`github.com` 主站仍不通。

---

## 6. 验收口径（升级后必须逐条过）

1. **编译**：`openroad -version` 报 26Q3 对应 commit。
2. **最小例**：ISCAS'89 `s27` 完整走通 布局→CTS→布线→SPEF→双档 STA。
3. **同网表双档**：理想档与布线后档**都读 `routed.v`**，差异只来自 `read_spef`。
4. **SDC 不变**：`create_clock -name clk -period 0.5 [get_ports CK]`，禁自拟。
5. **理想档守门**：新栈重算 s27 理想档，须与主实验 `sta.log` 逐位相同；
   对不上则该例后续 Δ 全部不可用。
6. **触发器守门**：`dfxtp` 数量与源网表 `dff` 数量比对，差值必须能解释。
7. **失败也报**：仍跑不通的例记「未评估」+ 原因，不记 0、不删行。

---

## 7. 已知风险

| 风险 | 说明 | 应对 |
|---|---|---|
| Tcl 命令语义变化 | `define_process_corner` / `extract_parasitics` / `detailed_route` 参数在 2.0→26Q3 间有改动 | 先单例试跑，按报错逐个改脚本 |
| abseil 双版本 | or-tools 自带 88 个 absl `.so`，deps 里另有系统版 | 链接优先级以 or-tools 目录为先；出现符号冲突则统一用 or-tools 版 |
| WNS 数值全变 | 换引擎后绝对 WNS 必然不同 | 明确声明"换栈即换数字"，不与旧表并列 |
| b12 仍可能挂 | DRT-0073 也许不是版本问题 | 若 26Q3 仍崩，则确认为数据规模/几何边界，如实记录 |
| 编译时间 | 12 核，Release | 预计 30–60 分钟，后台跑 |

---

## 8. 产物登记（完成后补）

- 安装前缀：`/home/toylog/faeco_eda/or26Q3`
- 版本指纹：`openroad -version` / `sta -version` / `yosys -V` 三项写入 manifest
- 新实验目录：`experiments/20261029_openroad26q3/`
- 文档：`docs/EXPERIENCE.md` 增补、`project_docs/LOGS.md` 增补
---

## 9. 编译期事故：fmt 9.1 / spdlog 1.12 版本错配（2026-10-29 补记）

**现象**：首次 `ninja` 跑到 1573/2810 时失败，
`src/odb/src/db/dbJournal.cpp` 报
`static assertion failed: Cannot format an argument`（`fmt/core.h:1757`），
失败类型 `odb::Rect`。

**根因**：Ubuntu 24.04 apt 的 `libfmt-dev` 是 **9.1.0**、`libspdlog-dev` 是 **1.12.0**，
而 26Q3 的 `utl/Logger.h` 用 `#if !SWIG && FMT_VERSION >= 100000` 守卫 `utl::format_as`，
`fmt < 10` 时该函数退化为「不可调用的空类」，`odb::Rect` 因此不可格式化。
编译命令里的 `-isystem deps/root/usr/include` 又排在 `-isystem fc/fmt/include` **之前**，
所以即使 FetchContent 备了 fmt 12.1.0，实际命中的仍是 9.1.0。

**官方配对**：`etc/DependencyInstaller.sh` 里 `SPDLOG_VERSION="1.15.0"`，走源码构建
（`git clone -b v1.15.0` + cmake install），**不用 apt 版**。

**走过的弯路（记录以免重犯）**：

| 尝试 | 结果 |
|---|---|
| spdlog 1.15.0 + fmt 11.2 | 失败：fmt 11 删除了 `fmt::basic_format_string`（仅 `xchar.h` 残留宽字符版），spdlog 1.15.0 仍引用它 |
| spdlog 1.15.0 + fmt 12.1 | 同样失败，同一符号 |
| spdlog 1.15.0 默认 C++11 编译 | 失败：`inline` 变量需 C++17，须显式 `-DCMAKE_CXX_STANDARD=17` |
| **spdlog 1.15.3 + fmt 12.1.0** | **通过**（1.15.1 起修好 fmt 11/12 兼容） |

**最终口径（单一 fmt，禁双版本共存）**：

- fmt = **12.1.0**，来自 `FETCHCONTENT_SOURCE_DIR_FMT=fc/fmt`（slang 需要，OpenROAD 一并沿用）
- spdlog = **1.15.3**，源码编译，`-DSPDLOG_FMT_EXTERNAL=ON`，静态库装到 `build26/spdlog115b`
- `tweakme.h` 里把 `// #define SPDLOG_FMT_EXTERNAL` 改为生效（防止只靠 target 接口宏传播）
- apt 的 fmt 9.1 / spdlog 1.12（`include` + `lib` + `cmake` 全套）**整体移入**
  `build26/quarantine_fmt_spdlog/`，从 `-isystem deps/root/usr/include` 中彻底消失

配置复核输出：`{fmt} version: 12.1.0` / `spdlog: 1.15.3` / `SPDLOG_FMT_EXTERNAL=ON`。
---

## 10. 编译期事故（二）：yaml-cpp 目标名 / LEMON C++20 兼容

### 10.1 yaml-cpp：裸名目标不存在

`src/odb/src/3dblox/CMakeLists.txt` 底部写的是
`target_link_libraries(3dblox PUBLIC ... yaml-cpp ...)`。
但 yaml-cpp 0.8 的 CMake 包只导出**带命名空间**的 `yaml-cpp::yaml-cpp`，
裸名 `yaml-cpp` 被 CMake 当成「库文件名字符串」→ 只加 `-lyaml-cpp`，
**不带任何 include 目录**，于是 `#include "yaml-cpp/yaml.h"` 直接 fatal error。

处置：本地打一行补丁（`src/odb/src/3dblox/CMakeLists.txt:24`）：

```
-    yaml-cpp
+    yaml-cpp::yaml-cpp
```

备份在同目录 `CMakeLists.txt.orig`。补丁只影响 3dblox（3D-IC 版图读写），
不进入任何时序路径，对本项目实验无功能影响。

### 10.2 LEMON：系统 1.3.1 在 C++20 下不可编译

报错 `std::allocator<odb::Point> has no member named 'construct'`。
C++20 按 P0619 删除了 `std::allocator::construct/destroy`，而 LEMON 1.3.1 的
`lemon/bits/array_map.h` 仍在调用。

**关键事实**：OpenROAD 官方不用上游 LEMON，而是在
`etc/DependencyInstaller.sh` 里 `LEMON_VERSION="1.3.1"` +
`git clone -b 1.3.1 https://github.com/The-OpenROAD-Project/lemon-graph.git`
——用的是**他们自己的分支**。该分支的差异恰好就是
`third-party/lemon/patches/allocator-patch.patch`（2021-11，修 C++20 兼容）。

处置（不动系统文件）：

1. `cp -r /usr/include/lemon build26/lemon-local/include/lemon`（同版本 1.3.1）
2. 应用 `allocator-patch.patch`。**只保留 `array_map.h` 部分**：
   `path.h` 的 15 个 hunk 里有 6 个因 Debian 版行号差异失败（内容是
   `len` → `_len` 重命名 + 自定义 Allocator），只应用一半会造成类内不一致，
   故 `path.h` 还原为原始版本。
3. `-DCMAKE_CXX_FLAGS="-I<build26>/lemon-local/include"` 让本地头优先于
   `/usr/include`（`-I` 天然先于系统目录）。
4. 冒烟测试：`c++ -std=c++20` 同时包含 `list_graph/smart_graph/path/
   network_simplex/maps/bfs/dijkstra` 全部通过。

结论：**只有 `array_map.h` 一处需要修**，`path.h` 在 C++20 下原本可编译。
