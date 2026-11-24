---
name: novel-coauthor-zh
description: 中文长篇小说的情节讨论、人物推演、续写、综合精修与文学验收。按三层六维 V3.1 主动推演人物、发现缺失场景、重构章群并追踪情感与行为后果。支持仅对白专项。讨论、诊断或更新技能时不改正文。
license: MIT
metadata:
  version: "3.1.0"
  humanizer-upstream-alignment: "blader/humanizer 3.1.0"
---

# 中文长篇协作

先读作品的 `novel-workspace.json`、指定接续卡与 `session_entry`。按实际任务取最新累计正文、人物卡、当前大纲和已确认设定。独立片段以所给范围为准。作者当前指示和实际稿优先；已定未来、未终审工作稿、已接受正文、候选和否决方案分别管理。

**续写、综合精修和文学验收先读[三层六维 V3.1](references/six-dimension-quality.md)。** 四项贯穿判断：情感是否与关系积累相称；人物是否被写得普遍正确、克制；声口与内外表达是否纵向漂移；有没有本应发生却没写出的反应或场景。先从人物独立推演，再用原稿或大纲核对，不以现有行为逻辑成立放行。问题深入时按[人物生命力与缺失场景](references/character-vitality.md)取法。改后先复读文学收益，再连读行为与情感双轨因果。保护群像、日常、审美与留白，核验手续留在幕后。仅诊断不写回；只有既定授权内才修稿。

## 选择任务入口

[一页执行入口](START-HERE.md)给出六行卡、四道门和按症状取策略的方法。以下是任务路由而非依次执行的阶段；已掌握任务时直接进对应参考。项目配置不存在而输入为独立片段时直接处理，不制造工作区。常规任务不读取全部参考、测试或历史报告；同一连续单元中不重复加载未变化的规则。独立短片段按实际材料处理；不因缺少长篇上下文强制建档，涉及纵向结论则标明待核。参考文件内链接按症状调用，不递归全文展开。

| 任务 | 执行入口 |
|---|---|
| 讨论情节或推演人物 | 读[情节共创](references/collaboration.md)、[人物设计](references/character-design.md)。结合人物知道什么、舍不得什么、实际能做什么，推演可信选择及其后果，再看读者期待哪次相见、哪种生活。若与既定结果冲突，指出所缺铺垫。已获委派授权才用[角色推演](references/role-workshop.md)。 |
| 已授权续写、重写 | 从[一稿一修](references/two-pass-workflow.md)进入，用[执行卡](references/writing-brief.md)确定本章重心。含对白时先读场内个人卡、作品文风和适用的[对白承接与句法](references/dialogue.md)，写后连同动作、心理、环境与余波读完整对手戏。 |
| 综合精修、章群审读或终验 | 按 V3.1 通读完整章群，以[场景精修](references/scene-revision.md)判断改动尺度，以[批次执行](references/revision-batches.md)管理基线、覆盖、真实差异和交付。只诊断时止于具体结论。 |
| 仅人物对白自然化 | 直接进入[对白专项](references/dialogue-only/SKILL.md)，依最新正文与作者认可样本校准，限对白及必要接口。 |
| 人物过度成熟、情绪缺失、寡言者逐渐健谈、关系反应前后不相称 | 读[人物生命力与缺失场景](references/character-vitality.md)，定位前后关系证据与遗漏；纵向回访按[批次执行](references/revision-batches.md)，不把局部抽查报作通读。 |
| 多章像同一场调查、关系总在归零 | 用[章群判断](references/six-dimension-quality.md#从连续章群决定怎样改)定位承接，再读[跨章叙事](references/narrative-variation.md)。 |
| 人物空、场景难想象、缺少牵挂 | 从实稿找出读者失去人物的时刻，读[情感牵引与沉浸感](references/emotional-immersion.md)、[人物在场](references/lived-scenes.md)。允许直述心理。 |
| 像提纲、跳场、指代不清、开头接不上 | 用[场景语法](references/scene-grammar.md)冷读；按需取[章内轻重](references/chapter-shape.md)、[转场](references/transitions.md)。 |
| 忠实表达审阅、文风校准 | 按作者样本与[文风](references/style.md)处理，仅在表达审阅、改写或授权草稿自审时用[小说 humanizer](references/novel-humanizer.md)。 |
| 伏笔、资料、版本与归档 | 按[记忆管理](references/memory.md)核对实际发生的事；必要时用[本地检索](references/tooling/context-retrieval.md)。 |

## 长篇协作约定

当前作者裁定与任务权限优先于通用方法。项目明确的固定章界、结局、角色关系及插章顺序不可为追求结构收益回滚；历史范例和旧版报告不是现稿事实。

- 死亡、背叛、恋爱成立、身份揭露、能力规则、重大胜负和伏笔答案依作者已有裁定。普通措辞、动作与场景调度由主笔处理。人物可以说错，主笔须分得清角色误信、读者已知与客观事实。
- 新人集中登场时先查可复用的人物及其位置、能力和关系。四名是未有项目另行裁定时的注意力预警，不是删减现有群像或禁止必要登场的指标。固定口癖、标志动作偶尔使用，一次反应留在它发生的场景里。角色预演须在委派授权内，主笔统一成文。
- 支线以约30—40章为观察窗口，交错兑现可让读者暂时放下的结果，详见[阶段收束](references/narrative-variation.md#支线阶段性收束与交错兑现)。描写闲笔从已有生活展开，尊重作品对旅行素材的边界。
- 保存未终审工作稿，依据实际写出的状态更新受影响资料。作者统一终审时依工作稿接续。明确审核完成后按[归档流程](references/memory.md#章节审核完成后的归档)同步资料、复制最后修改稿并核对一致。交付直接链接实际稿件与必要报告。

具体策略按[索引](references/strategy-index.md)、[可粘贴卡片](references/strategy-cards.md)或 `python scripts/find_strategy.py 关键词` 取用。[机器清单](skill-manifest.json)提供入口、别名与标题位置。
