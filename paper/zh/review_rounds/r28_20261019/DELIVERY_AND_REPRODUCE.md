# r28 图片与正文比例

图1/2由正文满宽缩至82%，实际约139.395×92.930mm，面积减少32.76%，保持原纵横比。六个数据图按原占幅92%显示；ISCAS89配对图保原栏宽以保6pt以上字。实际最小定量字主6.39716bp、补6.11806bp。所有九原图字节、数据、正文和图注不变。

主文最终main_build03为10页7图6表；补充supplement_build01为9页5图12表。仅11处include宽度及图4/5两处浮动约束改变，逆替换与r27逐字同，CONTENT_PRESERVATION_CHECK.json可核。两稿各3PDF同SHA。main01堆图与main02裁底失败原件保留，最终无溢出/欠满/缺字/未定义引用或全浮动页；根实看19页contact及主3/4/7/8、补7/8/9整页，独立原生主6–8页有限复核。末页参考文献留白保持，未删文字或缩正文求页数。

重建在仓库根运行本round的WORKFLOW_COMPILE.py，传新build子目录及显式TeX名；随后WORKFLOW_EXPORT_MONOCHROME.py传同两参数和新export子目录；再WORKFLOW_RENDER_QA.py及WORKFLOW_SIZE_QA.py同两参数。每次保留新回执，检查实际排版再同步PDF；仅编译不足以保证严格灰度。Ghostscript资源/MSYS环境沿r27已验证配置，换主机须核路径。

无新EDA/图生成/production变化，HEADf761及不提交锁保持。四partial/D28/56 raw3/8/OI051和其它科学未决继续保留；字体替代提示及AI原图模型身份/投稿资格边界未变。
