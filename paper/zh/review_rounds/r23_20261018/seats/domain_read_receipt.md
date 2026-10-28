# Domain席读取收据

日期：2026-10-18。审稿文件：seats/domain_phase2.md。本席只评D2；NOT_CALIBRATED；criteria_binding_unavailable。保持peer盲、旧review盲、项目evidence及交接盲。未执行EDA、修改稿件或生产源。本轮根统一执行conformance，本席首次写卡前已检查两H2、六维、唯一role、P1逐字trigger、repairable block、10个独立typed anchors与7个Severity/Confidence。

## 本地输入与SHA256

路径均相对 paper/zh/review_rounds/r23_20261018/。正文从domain_phase2_input.txt及numbered文本读取；manuscript.tex仅核算SHA，未单独重读；PDF未直接打开，视觉只限下列实际查看的PNG。

| 文件 | SHA256 |
|---|---|
| contract.json | 9e8eb029f0fe893b07ffc6a8f74d2e5a4d9c7ebdc3e5f52b08ac2ddaf773620d |
| metadata.json | 69701f593cc9e431e94cb252e82ba11a14b1992ec91722c83b93d7ded55fa0d6 |
| FIELD_AND_PANEL.md | fcd0e2e21da9cf8528ddb77705574d00b74922c669e54484b96ef028bab3e225 |
| seats/domain_phase1.md | d0e2f38c06540f67bdbd292929e8029468c94d265efb7f18d924b3f17e7044e3 |
| seats/domain_phase2_input.txt | 4070117c739b365619f4df132e43466dbe52429d897f6c49d546d98334928c6f |
| inputs/manuscript_numbered.txt | bdedb8be55b7c124f30223586bc1e5d4c3dede9fa325436b2bf893c0c25f8954 |
| inputs/manuscript.tex（仅hash） | c750ff9cad382ff3fdf3c067980016a0ebcc7be7c2fff2a198c5f5396767918b |

## 实际查看图像

| PNG | 实际检查范围 | SHA256 |
|---|---|---|
| inputs/rendered/page-03.png | 相关工作、方法范围、表1–2 | c36fb105e65164e2dbfb291010e82f345f53deb747338ff0eb13010f92df8226 |
| inputs/rendered/page-04.png | 算法1、符号表、方法总览 | 99b49f6fab58b27e4c4e53044b2a20962f56422a20e81eae6f2bda42661782bf |
| inputs/rendered/page-05.png | 图1、图2与融合排序正文 | 6198491dce994253cb0c5d60c6258d586195874e04736017753fc95e843dd71d |
| inputs/rendered/page-06.png | 式2、表4–5及验证正文 | d6a4f9a213f6d7c1abaaFF4149bcc6121c8d4e6ba9a09cb3e6b74bb8063d330b |
| inputs/rendered/A_SEC_full_page_250dpi.png | 第8页图3、表8和SEC声明 | 8d85e32cb1d77536d9bb8eb0d65053b91fc4840f8eb6ff7a52458555f175e8b2 |

未实际查看其余页面PNG、contact sheets或原图PDF；S2/S3表项依据论文文本与表格源码，非额外图像审查。

## 外部原始来源抽核

| 来源URL | 实际查看内容与用途 | 范围限制 |
|---|---|---|
| [Wu2010作者PDF](https://alcom.ee.ntu.edu.tw/assets/publications/iccad10-eco.pdf) | 摘要、§II、FRAIG、MSPM/插值相关段落；核对golden规格等价与FRAIG用途 | 全文可访问，按相关技术段落抽查，未逐页视觉审查 |
| [Cheng2016 DATE官方PDF](https://past.date-conference.com/proceedings-archive/2016/pdf/0946.pdf) | 摘要、§I、资源代价、SAT/resubstitution相关段落；核对metal-only阶段和物理代价 | 不从其全部实验表外推 |
| [Dao2018作者PDF](https://people.eecs.berkeley.edu/~alanmi/publications/2018/dac18_eco.pdf) | 摘要、§3.2–3.6；目标可修复性、结构裁剪、支持集、超时结构补丁 | 原文没有直接支撑稿件所归属的常规扩窗叙述 |
| [Pan作者arXiv v1全文](https://arxiv.org/html/2312.00421v1) | 摘要、§II-C、§III及全文ECO关键词检索；核对SAT-sweeping仿真机制 | DATE官方PDF搜索摘要可见，但open工具解析失败；技术判断以作者全文为准，不猜测正式版额外内容 |
| [Kravets2019 IBM官方摘要](https://research.ibm.com/publications/comprehensive-search-for-eco-rectification-using-symbolic-sampling) | 修订规格、修正点、symbolic sampling与patch circuitry的研究目标 | 未取得全文，不断言其全部技术细节或效率归因 |
| [Ho2010作者机构摘要](https://scholars.lib.ntu.edu.tw/entities/publication/f04d1554-202f-44ef-bb6b-77dec0eccd66) | post-mask、备用单元、B/G后技术重映射的两阶段流程 | 未取得该期刊文全文；不以同题2006学位论文或二手讲义替代 |
| [Yosys0.33官方equiv_induct文档](https://yosyshq.readthedocs.io/projects/yosys/en/0.33/cmd/equiv_induct.html) | 完整命令帮助、条件性等价语义与初始同步说明 | 该语义不等于实际FAECO证明脚本存在漏洞 |
| [Yosys同tag源码](https://raw.githubusercontent.com/YosysHQ/yosys/yosys-0.33/passes/equiv/equiv_induct.cc) | 帮助文本及归纳/一致性约束部分，与官方文档交叉核对 | 未运行该源码或EDA |

抽核不是14条参考文献的完整引用审计；没有仅凭题名陌生判为不相关，也没有用作者/DOI存在性代替技术支持核对。搜索结果中的二手聚合站、讲义和非同版本论文未用作审稿事实依据。

