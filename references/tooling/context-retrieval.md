# 本地检索工具与表达范例

只在需要资料库检索、元数据定位或独立取表达范例时读取；简单讨论和已给全文的片段不要求运行脚本。连续性边界与记录职责见[记忆管理](../memory.md)。脚本失败不等于资料不存在，报告实际失败并用rg或原文继续必要检索，不假报工具已成功。

## 检索助手

Python 3.10 或更新版本的标准库即可，不联网、不调用模型；剧情检索不读工作区以外的路径。独立范例命令还会读取技能自带的固定范例文件，不开放任意外部路径。下列目录名与实体名仅作示例；实际扫描路径由 `novel-workspace.json` 指定，通用配置示例见 `examples/minimal/`。采用其他目录名时显式标注记录元数据，不依赖目录推断类别。

```text
python <skill>/scripts/context.py index --root <工作区>
python <skill>/scripts/context.py build --root <工作区> --mode discuss --query "妹妹 好友 死亡 调查" --ids P001 P002 E002 --budget 9000
python <skill>/scripts/context.py build --root <工作区> --mode clues --ids F002 --budget 7000
python <skill>/scripts/context.py build --root <工作区> --mode character --select "02_人物/P002_妹妹.md#知情边界" --budget 7000
python <skill>/scripts/context.py build --root <工作区> --mode draft --at-chapter 8 --brief 08_写作/任务/第008章.md --ids P001 --budget 12000
```

`index` 写入可重建的 `.novel-cache/index.json`，终端只报告数量。`build` 每次从配置指定目录重新扫描，不依赖可能过时的缓存；按稳定 ID、元数据别名和关键词排序。每次按文件当前内容计算 hash，输出路径、行号、状态和相关原文。默认不检索 00_来源、正文全文、工具研究和所有风格样本。需要时用 `--include <相对文件路径>` 明确加入。

递归扫描还会跳过`.git`、`.novel-cache`、`__pycache__`、`备份`、`修订备份`和`草稿记录`目录，避免资料目录中嵌套的旧副本混进当前包。可在工作区配置中用可选的`catalog_exclude`数组排除额外相对路径。明确使用`--include`或`--select`仍可回查这些历史文件，但不能绕过时点与状态过滤；不把历史内容自动当作现状。

`--budget` 是整个输出包的字符上限，不是精确 token 上限，更不是本次会话总费用。索引读取与本地扫描不会把全部文件放入对话，但此前聊天和额外回查仍占上下文。助手必须控制后续读入，不能生成小资料包后又读全库。

接续卡、用户指定的文档/主题簇和匹配 `--ids` 的主档必须完整纳入；超过预算则报错，不把关键规则截成半句。档案富集后可用 `--select "相对路径#二级标题"` 选取完整主题簇，不要求缩写或拆散原档。其余资料按小节检索，列出遗漏数量和少量回查位置。遇到待决条件或证据不足，缩小任务、增加针对性回查；不能把“未检索到”说成“不存在”。

只查 P001 不代表一定覆盖所有约束，引用规则 ID 或证据文件可补取；同义改写可能漏检，必要时用 `rg` 搜索。脚本负责选材料，人物推演和逻辑判断由助手完成。


## 独立取用叙述范例

剧情资料继续用 `build`；表达参考另用 `exemplars`，复用完整H2主题、ID、关键词评分、`--select` 与字符预算。普通 `build` 的全部模式均排除 `kind=exemplar`，显式 `--include/--select` 也不能把它变成剧情资料。范例包不加载接续卡、任务卡、人物档或其来源全文，不能提供写作授权。

```text
python <skill>/scripts/context.py exemplars --root <工作区> --query "疲劳争执 不耐烦" --limit 1 --budget 2500
python <skill>/scripts/context.py exemplars --root <工作区> --ids EX-002 --budget 2500
python <skill>/scripts/context.py exemplars --root <工作区> --select "@skill/references/prose-exemplars.md#EX-004：手边的事跨过几轮话" --budget 2500
```

`--limit` 为1—3，默认2；无相关组返回空参考包，不强塞全部范例。显式选择超数量或预算报错，隐式检索只纳入放得下的完整组并报告遗漏，不截去适用边界。词面检索并不理解场景，读入后仍须确认适用条件；必要时换关键词或显式选ID。没有工作区的独立场景可从[范例选择表](../prose-exemplars.md#选择与迁移)直接读取相应H2，不要求为此建配置。

内置库仅含本技能原创示意，标为 `origin=synthetic, status=illustrative`；不是作者认可样本，也不是经过验证的“优秀答案”。作品私有库放在作品目录，按需要给配置添加可选字段，旧配置不用改：

```json
"prose_exemplars": ["写作/私有表达范例.md"]
```

一个H2是一组完整对照，包含稳定ID、叙事问题、修改前后、机制、适用与不适用条件、来源和认可范围。私有组先标 candidate；只有作者明确认可其作为表达参考，且人工去除了专名、身份答案、未来事件及关系发展等作品事实后，才标 approved/accepted、填写认可依据并设 `sanitized=true`。建议元数据：

```json
{"id":"EX-LOCAL-001","kind":"exemplar","origin":"private","status":"candidate","usage":"expression-only","sanitized":false,"approval":"","source_chapter":37,"aliases":["未完成体验","动作等待"],"sources":["私有稿件与修订稿的实际位置"]}
```

`source_chapter` 只标范例出处，不作为人物状态生效章节。独立包也把旧库的 `chapter` 视为出处；它不会因此放行剧情档的未来章节。来源路径只作追溯，不自动读取。未认可、已否决、混有未隔离作品事实或缺少来源的私有组不选入，显式指定也报错。即使正文 accepted，也不能省略表达参考认可与脱敏；整章正向评价不等于每组对照已被认可。

脚本只能验证元数据声明，无法语义证明脱敏或鉴别伪造认可。写入私有库时须人工核对，生成时仍守当前人物知情边界。私有库不放入技能的公开仓库，不复制到发布包；未得到发表授权，不上传原稿、对照或含私有语料的资料包。
