---
name: novel-coauthor-zh
description: 中文长篇小说的情节讨论、人物推演、续写、综合精修与文学验收。按三层六维 V3.0 连读章群、重构场景、核对跨章后果。支持仅对白专项。讨论、诊断或更新技能时不改正文。
license: MIT
metadata:
  version: "3.0.0"
  humanizer-upstream-alignment: "blader/humanizer 3.1.0"
---

# 中文长篇协作

先读作品的 `novel-workspace.json`、指定接续卡与 `session_entry`。按实际任务取最新累计正文、人物卡、当前大纲和已确认设定。独立片段以所给范围为准。作者当前指示和实际稿优先；已定未来、未终审工作稿、已接受正文、候选和否决方案分别管理。

**续写、综合精修和文学验收都先读[三层六维 V3.0](references/six-dimension-quality.md)。** 从连续章群判断读者已经知道什么、在乎谁、愿意在哪里停留。重复调查先删并；普通生活有独立的阅读价值。重大行动在幕后核实可行性，正文写出读者理解选择所需的部分。改后先复读文学收益，再连读跨章因果与节奏。仅诊断按相同口径给出证据，写回正文须在授权范围内。

## 选择任务入口

[一页执行入口](START-HERE.md)给出六行卡、四道门和按症状取策略的方法。已掌握任务时直接进入对应参考。

| 任务 | 执行入口 |
|---|---|
| 讨论情节或推演人物 | 读[情节共创](references/collaboration.md)、[人物设计](references/character-design.md)。结合人物知道什么、舍不得什么、实际能做什么，推演可信选择及其后果，再看读者期待哪次相见、哪种生活。若与既定结果冲突，指出所缺铺垫。已获委派授权才用[角色推演](references/role-workshop.md)。 |
| 已授权续写、重写 | 从[一稿一修](references/two-pass-workflow.md)进入，用[执行卡](references/writing-brief.md)确定本章重心。含对白时先读场内个人卡、作品文风和适用的[对白承接与句法](references/dialogue.md)，写后连同动作、心理、环境与余波读完整对手戏。 |
| 综合精修、章群审读或终验 | 按 V3.0 通读完整章群，以[场景精修](references/scene-revision.md)判断改动尺度，以[批次执行](references/revision-batches.md)管理基线、覆盖、真实差异和交付。只诊断时止于具体结论。 |
| 仅人物对白自然化 | 直接进入[对白专项](references/dialogue-only/SKILL.md)，依最新正文与作者认可样本校准，限对白及必要接口。 |
| 多章像同一场调查、关系总在归零 | 用[章群判断](references/six-dimension-quality.md#从连续章群决定怎样改)定位承接，再读[跨章叙事](references/narrative-variation.md)。 |
| 人物空、场景难想象、缺少牵挂 | 从实稿找出读者失去人物的时刻，读[情感牵引与沉浸感](references/emotional-immersion.md)、[人物在场](references/lived-scenes.md)。允许直述心理。 |
| 像提纲、跳场、指代不清、开头接不上 | 用[场景语法](references/scene-grammar.md)冷读；按需取[章内轻重](references/chapter-shape.md)、[转场](references/transitions.md)。 |
| 忠实表达审阅、文风校准 | 按作者样本与[文风](references/style.md)处理，仅在表达审阅、改写或授权草稿自审时用[小说 humanizer](references/novel-humanizer.md)。 |
| 伏笔、资料、版本与归档 | 按[记忆管理](references/memory.md)核对实际发生的事；必要时用[本地检索](references/tooling/context-retrieval.md)。 |

## 长篇协作约定

- 死亡、背叛、恋爱成立、身份揭露、能力规则、重大胜负和伏笔答案依作者已有裁定。普通措辞、动作与场景调度由主笔处理。人物可以说错，主笔须分得清角色误信、读者已知与客观事实。
- 同一段相连情节集中引入新人不超过四名，先查可复用的人物及其位置、能力和关系。固定口癖、标志动作偶尔使用，一次反应留在它发生的场景里。角色预演须在委派授权内，主笔统一成文。
- 支线以约30—40章为观察窗口，交错兑现可让读者暂时放下的结果，详见[阶段收束](references/narrative-variation.md#支线阶段性收束与交错兑现)。描写闲笔从已有生活展开，尊重作品对旅行素材的边界。
- 保存未终审工作稿，依据实际写出的状态更新受影响资料。作者统一终审时依工作稿接续。明确审核完成后按[归档流程](references/memory.md#章节审核完成后的归档)同步资料、复制最后修改稿并核对一致。交付直接链接实际稿件与必要报告。

具体策略按[索引](references/strategy-index.md)、[可粘贴卡片](references/strategy-cards.md)或 `python scripts/find_strategy.py 关键词` 取用。[机器清单](skill-manifest.json)提供入口、别名与标题位置。
