# r21 图件与整稿验收

本轮重画图1/2，增加图4–7；正文共7图14表。PDF/SVG保留可编辑文字，PNG为600 dpi预览。旧两张PNG仍保留，稿件通过新引用使用矢量图。

- 六张新图源预检：18 PASS，0 FAIL；PDF字形最低7 pt。正文全宽为170 mm，单栏约79.5 mm，单栏图源80 mm，实际最小字形约6.95 pt，高于5 pt下限。
- 两项静态WARN已逐项复核：宽度检测器误把动态毫米参数170读为英寸，实际PDF MediaBox按170/80 mm导出；PNG为预览、未导TIFF，论文引用矢量PDF，当前不作为最终期刊上传包。
- 数据图CSV与来源SHA256随图保存；全样本保留，regs标N/A、s641零候选、物理退化、s953随机更优均未删去。
- D族40运行真实STA账本复核通过：剔前置拒绝及缓存命中后，计数等于唯一报告路径数与sta_used，终点与原归档一致；缓存均能追溯到更早实测，不漏首次发现。曲线自然终止，无插值或外推，三个随机种子分别绘制。
- 新STA表列为1947 / 2003 / 随机均值2480.7；4146 / 4883 / 5624保留为全部候选评估记录。B族3363 / b06 664 / b17 104按评估记录称呼，b17旧schema实际STA不可恢复。
- 整稿LuaLaTeX两次：12页，Error/Overfull hbox/Underfull hbox/Overfull vbox均0，未定义引用0；21个图表标签全部有正文引用。完整页渲染及图5逐板检查，无图件落在参考文献之后。
- 末页0.8534 pt溢出经隔离确认由旧balance机制引起；关闭balance则消失，enlargethispage与balance组合产生无限胶缩错误，已回退。使用本机已安装flushend的noshrink/nospread选项平衡末页，未缩字体、行距或内容。

机器证据：`figure_qa.json`、`build_qa.json`、`sta_ledger_audit.json`；独立复核：`methodology_verification.md`、`domain_verification.md`、`sta_count_followup.md`。

验收范围是本轮图件和修订稿。论文仍为Major Revision工作稿，双割机制独立因果证据与历史配置档案缺口保留，不因版式及绘图通过而宣布投稿就绪。
