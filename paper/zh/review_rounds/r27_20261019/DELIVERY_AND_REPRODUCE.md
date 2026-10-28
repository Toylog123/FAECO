# r27 黑白灰交付

主文10页7图6表，补充9页5图12表。主线和完整论文保持，逆替换证明仅图路径及两处颜色描述改变。两稿各3份PDF同步，详见FINAL_DELIVERY.json。

两示意图沿内置图片模型定向编辑，原生PNG和prompt/provenance保留；7数据图复用既有数据和Python绘图逻辑。AI PNG有细微RGB残留，最终PDF通过Ghostscript文档层DeviceGray导出而非手工改图像素。全部19页实看contact，主3/4/7/9与补7/8实看整页，量化7图逐面板实看。

复现顺序：在仓库根用.venv/Scripts/python.exe -X utf8运行WORKFLOW_COMPILE.py，参数为新的build子目录和显式TeX文件名；随后WORKFLOW_EXPORT_MONOCHROME.py用相同两参数及新的export子目录；最后WORKFLOW_RENDER_QA.py同两参数。脚本在本round，必须显式选主文或补充；不能把LuaLaTeX原始RGB编译稿冒充最终严格灰度稿。本机Ghostscript10.04.0的Resource/Init、kanji和MSYS路径转换已在快照中配置，换主机需核实运行时路径。最终稿保留原生图像尺寸、文字非空白字形及链接；宽度舍入0.00403pt，主9页提取器一处自动空格有差异，详见MONOCHROME_EXPORT。

无新EDA/production修改或HEAD变化，不提交。4个科学partial及D28/56、raw3/8、原SPEF OI051与既有其它未决不因样式交付关闭。既有字体提示/图片投稿资格和模型身份未知保留。
