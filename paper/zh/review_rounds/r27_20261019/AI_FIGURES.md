# 黑白灰示意图与生成提示

图1和图2均用内置 `image_gen.imagegen` 编辑r26原图；未使用CLI/API备用路线，未手工改动模型输出像素。定量数据图由原Python流程复用生成。

| 图 | 工作区保存路径 | 最终提示 |
|---|---|---|
| 图1 | paper/zh/figures/manual/figures/r27_mono_overview/r27_mono_overview.png | FIG1_MONOCHROME_PROMPT.txt |
| 图2 | paper/zh/figures/manual/figures/r27_mono_regions/r27_mono_regions.png | FIG2_MONOCHROME_PROMPT.txt |

每个图目录包含SOURCE_PROVENANCE.json和提示副本。科学核对见FIG1_MONOCHROME_QA.md与FIG2_MONOCHROME_QA.md。原生PNG呈黑白灰，但数学上仍有微小RGB通道差；最终主文/补充PDF通过文档层DeviceGray输出并逐页检验，原生PNG保持原字节。图像API未披露provider/model/version，未声称已核验投稿资格。

完整PDF、源文件、七数据图、数据一致性及当前未决事项见FINAL_DELIVERY.json和DELIVERY_AND_REPRODUCE.md。
