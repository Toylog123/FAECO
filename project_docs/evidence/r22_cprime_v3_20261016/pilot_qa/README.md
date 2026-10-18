# 首18 pilot与独立审计原件归档

ARCHIVE_MANIFEST.json保存两版audit、原pilot.log、05/07/18独立报告以及18例completion/最终SEC receipt/log，共60份原件；每份来源/目标/字节数/SHA逐项匹配。完整raw/models/STA artifacts保留在experiments/20261016_r22_cut_ablation_v3相应目录，由manifest的full_artifact_bindings及原PILOT_AUDIT_18逐对象绑定；此处不制造第二套实验原始数据。

v1原调用scratch/audit_cprime_v3.py，后另存_v1.py，SHA e6d9f0a0…对应05；v2调用同原路径，SHA d932d974…对应07/18。归档副本命名含v1/v2，不冒充同一source SHA。初版更早schema误期待未序列化epoch字段KeyError没有输出receipt，不是生产失败；有效v1及v2保留完整实际commit hash链。脚本保原路径依赖；复跑使用原调用位置，或新副本显式适配路径后另锁SHA，勿修改原件。

18独立核验通过不等全72科学结论。剩余54运行期HEAD固定3ea0f75；全部72验收后再由root提交此新包/ZIP，当前无Git动作。
