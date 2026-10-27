
<div align="center">

当前版本 **2.0.0**。围绕作者当前作品讨论情节、推演人物、写作与全章精修，保留作者声音、人物知情及长篇连续性。讨论、候选、未终审工作稿和已接受正文分别管理。
# novel_skill-CN

**中文长篇小说协作 · 内置小说 humanizer**

[![License: MIT](https://img.shields.io/badge/License-MIT-374151?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)](#本地检索)
![中文](https://img.shields.io/badge/写作语言-中文-9B4444?style=flat-square)

[开始使用](#开始使用) · [运行机制](#运行机制) · [小说 humanizer](#小说-humanizer) · [来源和借鉴](#来源和借鉴)

</div>

## 使用

将本目录完整放入技能目录，并命名为`novel-coauthor-zh`，保留内部相对路径。用`$novel-coauthor-zh`调用；在已有作品目录工作时先读其`novel-workspace.json`和指定接续卡。不需要模型密钥、外部写作平台或联网服务。Python 3.10+只用于可选的本地检索、测试和包检查。

可以这样开始：

- “讨论下一段人物会怎样选择，先不写正文。”
- “按已定情节写这一章，保留人物知情和关系阶段。”
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
  dialogue.md                    对白执行入口与七项审查
  style.md                       文风执行入口
  transitions.md                 转场、状态与章尾承接
  character-*.md                 人物设计、模板及可选设计组合
  narrative-*.md                 阅读动力、跨章结构与支线收束
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
  check_package.py               文件、链接、锚点与ZIP检查
examples/minimal/                新工作区的最小配置示例
tests/                          检索与包检查测试，以及未执行的文学行为评测方案
```

现有模块入口和常用标题锚点保持稳定，作品内引用无需迁移。入口说明当前怎样做，细则解释困难怎样辨认，案例用于理解可迁移机制；不要求每场全文读取，更不要求每次固定取若干正反例。人物和作品档案保留在作品里，不复制进技能发布包。

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
python scripts/check_package.py --archive ../novel-coauthor-zh-2.0.0.zip
```

包检查验证UTF-8、包内路径与标题锚点，并可生成逐文件核对的ZIP；排除Git、缓存与编译产物，不安装软件。脚本测试使用合成夹具验证检索边界、元数据作用域、版本化文件引用及包内容，不验证文笔。`tests/behavior-cases.md`与`tests/prose-benchmark.md`是行为情境与文学效果评测方案，未执行独立模型评测时不能写成已经有效。宿主临时目录不可写时，将`TMP`/`TEMP`或Python的临时目录指向有权限的测试目录后运行，不修改小说作为测试。

## 来源和借鉴

小说表达模块沿用[blader/humanizer](https://github.com/blader/humanizer)当时声明的3.1.0结构审阅思路；上游许可见[UPSTREAM-LICENSE.txt](UPSTREAM-LICENSE.txt)，本包许可见[LICENSE](LICENSE)。作者声音、知识归属、视角、关系进度和原意约束按小说任务另行维护，不做AI身份检测。

本次结构重整参考了[Chinese-WebNovel-Skill的模块分工](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/blob/96709f477f4b59be856ebb10bec052dd0452b846/references/modules/module_template.md)、[转场诊断](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/blob/96709f477f4b59be856ebb10bec052dd0452b846/references/modules/transition/runtime.md)，以及[sumeru的阶段和问题追踪](https://github.com/xindoo/sumeru/blob/334d8bc8d2ad6548a7c834a811f679378d7bf3bc/skills/sumeru-review/SKILL.md)。只吸收问题定位、按需分层和可追溯的执行组织，未导入其脚本、小说语料和自动改大纲流程。

不采用每场必须有变化、按章数分配爽点、固定削减比例、每句配动作、按字数填充或固定每3章并行。这些项目的提示规则与宣传不能作为本技能文学效果的验证证据。
