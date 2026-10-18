# r22 correctness repair and evidence recovery — 当前LOG-44

2026-10-18当前覆盖注：C′v3全72、八包ROOT_POST和图v3独立验收已齐；适配器/证据/稿图941files已随阶段7231e02 commit/push。下文旧“ADAPTER WIP不纳本次commit”只属10-16阶段记录，当前适配器已入库但同族科学EDA仍待。当前源码修复依 `R22_S_SPEF_REPAIR_PLAN_20261018.md`，先红后绿、整体回归/独立review/新sourcecommit与clean pin后才正式EDA；C′原3ea身份保历史。

用户10-16恢复。当前代码完整v8=969pass/4skip/156subtests、155.12s/wrapper157.969exit0、170SHA稳定/PYTHONUTF8=1；原始精确V3正确拒reset→set/合法Gpass/R0/parsed1/1。勾选只表示所述实现/证据阶段完成，不等整篇科学ready。

## 已完成

- [x] K1–K6与namespace/required-input/多输出物理身份等代码门，独立审查范围/source绑定。
- [x] OI040顺序语义：LR禁seq组合R，F1完整raw seq组/角色，合法同族G保持；旧源码多行反证与原单行混合归因均保真。
- [x] OI041语句解析/物理↔parsed覆盖，精确原例V3与公共唯一性opt-in兼容、当前完整v8=969通过；OI040/041实现门关闭，失败receipt/v7等不覆盖。
- [x] 正式9控制预期全部符合（3正/3负/2unsupported/1input_error），不是9个等价证明或三态支持已证；Z伪pass/二态cut反例保留。
- [x] A6、B2、B17确切raw新proof及后验已恢复，各守原source/model pin；九份models重生成字节保持验证非新外部proof。旧runtime/state字段缺失不补造。
- [x] C′v3准备器已审/20控制通过，QA原件逐hash保真；不是RTL→mapped证明。
- [x] D56真实CLI内存预飞56/56；B3/C只读恢复设计已完但execution_ready=false，未知参数不默用defaults。ADAPTER仍WIP不纳本次commit。

## 当前执行顺序

- [x] 当前代码/QA/docs阶段3ea0f75已commit/push，code/preparer clean；raw60新包index字节校验通过。
- [x] 同一HEAD3ea0f75正式注册C′v3 72jobs/manifest72dfbef9…，纯dryrun8would_map成功。
- [x] 真map8/静态域prep completed，wrapper46s/exit0，8/8artifact/F1/F2/domain后验匹配；RTL→mapped等价not_run、STAfalse。
- [x] 18pilot运行completed/1028s exit0，PILOT_AUDIT_18独立18/18全验收，source/argv/STA账本/commit链/finalSEC全匹配。
- [x] 同HEAD3ea0f75余54已wrapper3728s/exit0结束；10-18最终72独立验收通过（a34da9c3…），8458评估/6930实际STA/192提交，原件stage72保真。归档/出图/提交审查齐前暂保持pin。
- [ ] D先14pilot后56同族复验；B3/C明确新重建配置/保持原调度后恢复，不用C′代替旧族。
- [ ] 四态实际语义支持恢复：显式四态编码与强soundness控制；准确writer保留，临时unsupported不等已证。6statetable原不支持failclosed，不扩模型支持。
- [ ] 科学证据闭合后两版稿图/声明一致回填/最终QA；A6+B2+B17恢复不等整篇ready。

当前C′v3已注册、8例准备完成、18pilot与最终全72已独立验收，运行已结束，v1失败与v2仅注册禁执行原件保留。范围外未解决问题保持open，不阻碍本已验证域。新运行前锁source/model/LIB/输入/工具与超时；运行中监测，输入变化停止；评估、真实STA launch、缓存/前拒与提交分账。完整回归期间冻结production/tests。

当前接受协议为严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不意味着关闭setup_tns预算。W0/s27首候选WNS -.27→-.26但TNS -.49→-.50，被setup_tns硬门拒。零提交/零WNS收益如实保留，不为正结果调参。最终审计分开理想候选、baseline/refresh/physical STA与提交。

全72运行期HEAD保持3ea0f75，不仅18pilot期间；18全通过后同pin扩余54，避免新run_config.git_head偏离manifest。B3/C适配器可继续独立review/QA（不占STA），提交须等72全部验收。
