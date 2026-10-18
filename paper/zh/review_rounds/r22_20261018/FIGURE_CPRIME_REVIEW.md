# C′ 完整矩阵图独立审查（2026-10-18）

结论：**通过数据、解读与视觉审查**。本次只读审查 `r22_matrix_gain_cost_v1`，没有改图源、图件或旧文件，没有 EDA/Git。按 nature-figure 和用户学术写作风格的证据规则检查；它是完整矩阵审查预览，尚非稿件整合或特定期刊格式验收。

## 数据与来源

- `MATRIX_AUDIT_72.json` 实际包含72/72、all_matrix_verified=true、source_stable=true，字节 SHA 与图件 QA 登记一致。
- raw CSV 共72条、8电路×9策略唯一且无缺项。逐行独立核 baseline/final WNS、Decimal `(final−baseline)×1000` ps、candidate/baseline/total STA、提交数、HEAD和completion SHA；72份实际 completion 字节均与审计匹配。
- paired CSV 共64条、8电路×8对照唯一且无缺项。逐行核 `左臂−右臂` 的改善差和实际STA次数差，以及两侧completion SHA。STA总数明确为候选理想线网分析与初始基线过程数；没有把评估记录或缓存当新过程。
- QA所记PDF/PNG/SVG/raw CSV/paired CSV导出 SHA 全部回验；所有本次读取来源前后 SHA 一致。

## 机制解读与不利结果

两个 weighted/uniform 对照在8电路的终点与STA消耗都相等。原 `MATCHED_STATE_PAIRS_16.json` 对重复base只选择最后一条uniform轮作对应；本次从32份实际outerloop结果读取所有trace，穷举每weighted轮的**全部同base uniform轮**，总计5454次交叉比较：子锥割hash列表、ordered pool、dispatch顺序全部一致，无缺失同状态对象；16对终点全文也相同。这些比较没有作为5454个独立统计样本，也不能解释为权重有收益。

s27的W1−UR3实际STA差为+5，说明UR3较W1少5次；s641的W1−C为+8，说明cover-only较W1少8次。两项均在图d、对应CSV和README叙述中保留。图c完整保留零差，图a保留W0/U0零收益；未平均随机种子、未插值或制造误差条。README未将候选来源或排序差异归因权重。

## 视觉核验

实际看过原PNG及由PDF独立 `pdftoppm -scale-to 2000` 渲染的整图。a/b两面板行列、数值和单位清楚；c/d正负差的色标与左右相减解释一致，旋转对照标签完整，未见裁切、遮挡或数值遗漏。最小字体6.8pt/低于5pt为0，来自已回验SHA的既有glyph审计，本环境两套Python均缺PyMuPDF，未冒称独立重测字形。

独立PDF渲染产生三条Poppler nameToUnicode外部资源路径告警，但输出成功且图中文字/数字经实际查看正常。首次Python审查因PyMuPDF缺失在读取科学文件前退出，后改用标准CSV/JSON核验与Poppler渲染；不是图件或实验失败。

| 尚待 | 范围 |
|---|---|
| 正式稿件整合 | 主稿引用、图注、正文对应结果与版式再编译 |
| 其他历史族科学门 | C′完整矩阵与本图不能替代B3/C/D/S/SPEF同族恢复 |

逐文件SHA、每配对交叉比较数与完整检查边界见 `FIGURE_CPRIME_REVIEW.json`。
