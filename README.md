<div align="center">

当前版本 **3.0.0**。围绕作者当前作品讨论情节、推演人物、写作、全章精修与六维文学验收，保留作者声音、人物知情及长篇连续性。讨论、候选、未终审工作稿和已接受正文分别管理。
# novel_skill-CN

**中文长篇小说协作 · 内置小说 humanizer**

[![License: MIT](https://img.shields.io/badge/License-MIT-374151?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)](#本地检索)
![中文](https://img.shields.io/badge/写作语言-中文-9B4444?style=flat-square)

[使用](#使用) · [文件怎样分工](#文件怎样分工) · [小说 humanizer](references/novel-humanizer.md) · [来源和借鉴](#来源和借鉴)

</div>

## 使用

将本目录完整放入技能目录，并命名为`novel-coauthor-zh`，保留内部相对路径。用`$novel-coauthor-zh`调用；在已有作品目录工作时先读其`novel-workspace.json`和指定接续卡。不需要模型密钥、外部写作平台或联网服务。Python 3.10+只用于可选的本地检索、测试和包检查。

可以这样开始：

- “讨论下一段人物会怎样选择，先不写正文。”
- “按已定情节写这一章，保留人物知情和关系阶段。”
- “用[一稿一修的两次指令](examples/one-draft-one-revision.md)先写好人物心理与交流，再做一次场景级精修。”
- “全章精修这段对白，连同动作、神态、心理和环境一起读、一起处理。”
- “检查这组章节是否重复核验、流程压过人物，以及支线有没有阶段性收束。”

只要求更新技能或审阅时，不试改小说章节。写作和精修依本次已有授权完成，不为普通措辞和动作逐项请示；重大情节仍由作者决定。

## 文件怎样分工

```text
SKILL.md                         共同约定与任务路由，首次使用读取
references/
  collaboration.md               情节讨论、人物推演与写作约定
  scene-revision.md              全章场景精修与三类对话
  revision-batches.md            连续章节、版本与问题处置
  event-progression.md           章节执行及先后两遍审查
  scene-grammar.md               场景语法：场数、视点、入场退场、指代与冷读
  writing-brief.md               写作执行卡：写前六行、写后四道门、引用原句的自审
  chapter-shape.md               一章的轻重：主问题、转折、平均用力、声音与结尾
  strategy-index.md              全策略索引：按任务找，不从头读
  strategy-cards.md              可粘贴的策略卡片：一页一张
  dialogue.md                    对白执行入口与七项审查
  style.md                       文风执行入口
  transitions.md                 转场、状态与章尾承接
  character-*.md                 人物设计、模板及可选设计组合
  narrative-*.md                 阅读动力、跨章结构与支线收束
  emotional-immersion.md         情感牵引、人物内心、当日外观和世界沉浸（专项细则）
  six-dimension-quality.md       V3.0 三层六维、场景取舍、两次复读与章群交付
  two-pass-workflow.md           一稿一修：首稿整体成文、一次场景级精修与终验
  lived-scenes.md                私人诉求、生活与体感
  novel-humanizer.md             忠实表达审阅
  memory.md                      资料状态、接续、失效与归档
  details/                       按困难选读的对白与文风细则
  tooling/                       可选本地检索与范例取用说明
  prose-exemplars.md             原创对照示意，非效果证明
  dialogue-in-scene.md            连续话语与伴随动作的参照
  dialogue-audience.md            多人听众与话语作用参照
  role-workshop.md                获授权后的有限角色推演
scripts/
  context.py                     本地主题检索，不调用模型
  find_strategy.py               按关键词查策略，输出一句话与位置
  check_package.py               文件、链接、锚点与ZIP检查
examples/minimal/                新工作区的最小配置示例
tests/                          检索与包检查测试，以及未执行的文学行为评测方案
```

现有模块入口和常用标题锚点保持稳定，作品内引用无需迁移。入口说明当前怎样做，细则解释困难怎样辨认，案例用于理解可迁移机制；不要求每场全文读取，更不要求每次固定取若干正反例。人物和作品档案保留在作品里，不复制进技能发布包。

## 当前执行版 3.0.0

[快速入口](START-HERE.md)按任务接入[三层六维标准](references/six-dimension-quality.md)。原有六行卡和四道门继续承担逐章证据，章节重心可以是值得亲历的普通生活。综合精修按完整章群取舍场景，并交付基线到最终稿的实际差异。可用 `python scripts/find_strategy.py 重复调查` 或 `python scripts/find_strategy.py 逻辑留白` 按症状查方法。

以下为历史版本记录，现行规则以上述入口为准。

## 2.5.0 策略必须落地：执行卡与四道门

作者指出，skill 里已有的策略在成稿中看不到实际应用，自审也常只写“已按六维检查”。本版不再增加文学理论，而是把策略变成写前必须做的决定与交稿前必须留下的证据：

- 新增[写作执行卡](references/writing-brief.md)：本章一句话、场次表、声音差异、三个只能在此处的细节、解释性内心的替代、结尾；写后过四道门（场景、戏、声音、落地），每道门引用正文原句。
- 新增[一章的轻重](references/chapter-shape.md)：从“一天”到“一场戏”，处理平均用力、主问题、转折、解释性内心、人物声音、开头结尾与职业作家的三问。
- 主入口、[一稿一修](references/two-pass-workflow.md)与[两遍审查](references/event-progression.md)明确：没有引用原句的自审按未完成处理；批量写作也必须逐章过门。
- 新增行为测试：自审只有结论没有引文、填卡发现没有转折、一章想装四场、读了策略但成稿没体现。

这不是说新规则一上就能写好；它只保证“没有执行”会在交稿前暴露，而不是被一句“已自审”盖过去。

## 2.4.0 场景先于句子

作者指出后半部正文“像提纲、像摘要、读起来僵硬”，经抽样核对，问题不在句子不够漂亮，而在**场景层**：章内段落数、对白比例大幅下降，平均段落从三十余字涨到百字以上，一章切成四五个迷你场、十几个旧人轮流点名，代词与施事经常找不到对象。读者不是被打动得太少，而是先跟不上“谁在哪、在做什么”。

本版新增[场景语法](references/scene-grammar.md)：场景五问、入场三件事与退场一件事、一场一视点、一章的场数预算、概述与场景的分工、句子与指代、段落呼吸、对白自明、从大纲／交流底稿到正文的转换、结算章不逐人点名、遮住大纲的冷读验收，以及提要体、蒙太奇体、电报体和群像点名的合成反例。它被接入主入口、[一稿一修](references/two-pass-workflow.md)、[两遍审查](references/event-progression.md)、[六维标准](references/six-dimension-quality.md)与[小说 humanizer](references/novel-humanizer.md)，并新增两组[对照范例](references/prose-exemplars.md)（EX-007、EX-008）。

这不会自动改善已写章节。"先加心理、加外貌、加描写"在场景不成立时只会让读者更累；应先修入场、视点、指代与场数。技能更新不等于作者读感已验收，也不授权改写正文。

## 2.3.1 核心创作原则

在[主入口](SKILL.md)明确写前的两个判断。依据大纲、设定、人物卡和最新剧情，推演人物此刻会做什么，以及读者愿意看到什么。把两者落实到可信的选择、场面和后果中。

## 2.3.0 六维终验与修复性重写

全章深修逐场判断成熟保留、局部修补或整场重写，改后复读全章和必要的邻章，发现问题继续返工。多版本回修按作者裁定核对作者基线、当前底稿与历轮意见，并记录实际读审、改稿和复验范围。正式分批与交付物按本轮约定执行。见[全章场景精修](references/scene-revision.md)与[批次执行](references/revision-batches.md)。

## 2.2.0 六维一体与一稿一修

在2.1.0“情感牵引与沉浸感优先”的基础上，新增[六维质量标准](references/six-dimension-quality.md)与[一稿一修工作流](references/two-pass-workflow.md)。六维包括**持续心理、对白生命力、情感钩子、人物形象、场景沉浸、章群节奏与事实因果**，贯通写前、首稿、一次场景精修、两遍终验；旧对白专项的窄范围权限不变。

这里的“两轮”是减少后续机械返工的工作设计，不是承诺小说两遍必然达到高质量。程序只能验文件结构，写作效果仍需要真实读者和作者验证。

## 2.1.0 情感牵引与沉浸感优先（替代旧冲突）

本版新增[情感牵引、人物心理、外貌衣着与场景沉浸](references/emotional-immersion.md)执行模块，并将其接入首稿、全章精修、全书分批审读与人物卡。**优先纠正**长期只用动作和沉默让读者猜心理、读者看不清人物今天的样子、世界只有规则与地名、情感没有让人想追读的具体牵挂。允许直述心理、较长的内心与非功能性景色，不把“克制”当成默认最高原则。

原“每事件50%概率抽样决定是否描写衣着”的默认规则被移除，改为依据场景与人物连续性呈现；既有抽样记录仅作历史材料。保留对故事因果、作者授权、角色秘密、自然对白和反模板扩写的保护。**该版本是写作约定的更新，不意味着已经完成全书审读或证明文学效果改善。**

## 2.0.1精修保护

精修先比较具体收益与原文作用，允许完整读后保留；保护有意义的重复和情绪递进，具体措辞仍可修整。L0—L3只记处理规模，不表示授权或完成等级。风格收益不清时撤回相应改动，保留已验证的事实修复；发现机械化先停止扩批，复核受影响单元后按已有授权继续。具体见[场景精修](references/scene-revision.md#修改收益与原文保护)与[批次执行](references/revision-batches.md#撤回改动与停止机械化)。作品专属事实继续由作品档案维护，不从经验总结直接导入技能。

## 2.0.0执行重点

全章精修先完整读章，再按整场交流处理话语、行为、心理和环境。私人争执、调查质问、危险协作分别修；编辑在幕后核查，不把核查要求写成人物的反复确认。不靠每句配喝水、抬眼或摆衣角修补机械对白，也不把真正的闲聊和陪伴概述掉。

同一段相连情节集中引入新人不超过4名；先查个人卡判断能否复用旧人，或把适合的几项情节集中给一个角色。可以在已授权范围内设计少量新人，不一律禁止，也不每人重新审批；同时避免一群各司其职的工具人，或一个无所不能的旧角色。

各支线以约30—40章作阶段检查窗口，须有读者可以暂时放下的结果；某条仍悬着时，其他线应有收束。不是固定章号结案，不凭空编答案，也不把未写计划登记为回收。日常、长心理、必要解释和平静结尾仍可成立，不按每章冲突、爽点和钩子的配额生成。

批次完成状态对应实际稿件、审校标准和覆盖证据。全章读审、局部diff与仅核承接分别报告；正文或标准改变后，受影响的旧完成状态须复核。保留先情节、后完整交流的两遍审查，程序通过不等于文学效果通过。

## 可选本地检索

[工具说明](references/tooling/context-retrieval.md)包含命令、字符预算、主题选择与范例准入。最小配置见[示例配置](examples/minimal/novel-workspace.json)。现有作品按原配置使用，不要求重建目录。

```text
python <skill>/scripts/context.py build --root <作品目录> --mode discuss --query "家人 选择" --budget 9000
python <skill>/scripts/context.py build --root <作品目录> --mode draft --at-chapter 1 --brief cards/brief.md --ids P001 --budget 9000
python <skill>/scripts/context.py exemplars --root <作品目录> --query "手边事情 交流" --limit 1 --budget 2500
```

检索保留H2主题及H3条件，识别H1范围和旧档中独立的范围声明；围栏里的元数据示例不作为事实。目录内的嵌套备份默认排除，可用可选`catalog_exclude`数组排除更多相对路径；显式回查仍不能越过时点与状态过滤。脚本不是语义搜索，不保证查全，失败或遗漏须如实说明并回读必要原文。

## 校验与打包

在技能目录中运行：

```text
python -m unittest discover -s tests -p "test_*.py"
python scripts/check_package.py
python scripts/check_package.py --archive ../novel-coauthor-zh-3.0.0.zip
```

包检查验证UTF-8、包内路径与标题锚点，并可生成逐文件核对的ZIP；排除Git、缓存与编译产物，不安装软件。脚本测试使用合成夹具验证检索边界、元数据作用域、版本化文件引用及包内容，不验证文笔。`tests/behavior-cases.md`与`tests/prose-benchmark.md`是行为情境与文学效果评测方案，未执行独立模型评测时不能写成已经有效。宿主临时目录不可写时，将`TMP`/`TEMP`或Python的临时目录指向有权限的测试目录后运行，不修改小说作为测试。

## 来源和借鉴

小说表达模块沿用[blader/humanizer](https://github.com/blader/humanizer)当时声明的3.1.0结构审阅思路；上游许可见[UPSTREAM-LICENSE.txt](UPSTREAM-LICENSE.txt)，本包许可见[LICENSE](LICENSE)。作者声音、知识归属、视角、关系进度和原意约束按小说任务另行维护，不做AI身份检测。

本次结构重整参考了[Chinese-WebNovel-Skill的模块分工](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/blob/96709f477f4b59be856ebb10bec052dd0452b846/references/modules/module_template.md)、[转场诊断](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/blob/96709f477f4b59be856ebb10bec052dd0452b846/references/modules/transition/runtime.md)，以及[sumeru的阶段和问题追踪](https://github.com/xindoo/sumeru/blob/334d8bc8d2ad6548a7c834a811f679378d7bf3bc/skills/sumeru-review/SKILL.md)。只吸收问题定位、按需分层和可追溯的执行组织，未导入其脚本、小说语料和自动改大纲流程。

不采用每场必须有变化、按章数分配爽点、固定削减比例、每句配动作、按字数填充或固定每3章并行。这些项目的提示规则与宣传不能作为本技能文学效果的验证证据。
