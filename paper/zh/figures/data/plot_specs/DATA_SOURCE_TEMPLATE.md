# 图表数据来源记录：fig<N>_<名称>

> 每张**数据图**必须填写本记录（放 `plot_specs/<figN>_<名称>_data.md`），
> 写清数据来源，**防止弄混版本 / 配置**。

## 基本信息

- 图号 / 名称：`fig<N>_<名称>`
- 图类型：数据图（定量折线 / 统计 / 曲线）
- 论文位置：§ / 表 / 图

## 数据来源

- 数据文件：`project_docs/evidence/<域>/<实验>/<日期>/<文件>`
- 证据包 README：`project_docs/evidence/<域>/<实验>/<日期>/README.md`
- 数据版本 / 基线：`[基线ID]` 或 commit
- **配置**（参数 / 输入 / 口径）：……

## 生成

- 生成脚本：`figures/scripts/<脚本>.py`
- 命令：`python figures/scripts/<脚本>.py`
- 运行日期 / 环境：

## 防混淆核对

- 数据来自**当前版本**（非旧版 / 其他配置）？是 / 否
- 口径（估测 / 实测）：
- 与论文中数字一致（对照 `project_docs/evidence/CROSSWALK_TEMPLATE.md`）？是 / 否
- 配置变更时是否新建记录（不覆盖旧数据）？
