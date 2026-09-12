# 论文字体（随项目分发，避免换电脑重装）

按《计算机辅助设计与图形学学报》投稿要求，本目录集中放置论文所需字体。
**编译时 compile.ps1 自动设置 `OSFONTDIR` 指向本目录**（LuaLaTeX + luaotfload），
换电脑无需重装系统字体即可编译。

| 字体 | 文件 | 族名（LaTeX 中用） | 状态 |
|------|------|------|------|
| 方正书宋_GBK（中文正文） | `FangZhengShuSong-GBK/FangZhengShuSong-GBK-1.ttf` | `FZShuSong-Z01` | ✅ 已含 |
| 黑体（标题 / 摘要标签） | `simhei.ttf` | `SimHei` | ✅ 已含 |
| 方正仿宋_GBK（作者名） | `FangZhengFangSong-GBK/…/方正仿宋GBK（正文三号）.ttf` | `FZFangSong-Z02` | ✅ 已含 |
| Times New Roman（英文 / 公式） | `times.ttf` `timesbd.ttf` `timesi.ttf` `timesbi.ttf` | `Times New Roman` | ✅ 已含 |

## 编译

```powershell
# 在 paper/zh/ 下执行
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/compile.bat                    # 编译 template
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/compile.ps1 -Name example_paper  # 编译示例
```

## 跨电脑移植

- 本目录字体随项目分发，编译脚本自动设 `OSFONTDIR`——**新电脑无需安装字体**。
- 只需安装 **TeX Live（默认）**（含 LuaLaTeX 与字体库）即可编译。
- 手动 lualatex 编译时先设字体路径：`export OSFONTDIR="<项目绝对路径>/paper/zh/fonts"`。
