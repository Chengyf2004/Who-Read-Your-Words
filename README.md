# 谁会读你写的文字？

简体中文 | [English](README.en.md)

> **东坡肉离开了菜，却没有离开文档。**

你让 AI 写一份番茄炒蛋的做法，它却擅自加入了东坡肉。你要求删掉东坡肉，最后得到的文档标题却是《番茄炒蛋（无东坡肉）》，正文还用一大段篇幅解释为什么这道菜不需要东坡肉。

这不只是“没有删干净”，而是一种由受众错位引起的**内部过程泄露**：模型执行了修改，却把修改指令和被否决的内容继续当作高显著性主题，写给了根本不需要知道这段过程的最终读者。

`who-read-your-words` 是一个 Codex Skill，用来让所有面向外部读者的文字始终服务于真正会读到它们的人。

它能避免任务指令、修改过程、已放弃的方案和智能体操作泄露到受众不同的成品中。README 应当像 README，Pull Request 应当说明项目发生了什么变化，而面向委托人的进度回复仍然可以交代已经完成的工作。

## 它解决什么问题

开始写作前，这个 Skill 会在内部建立一份受众契约：

- 谁会阅读这段文字；
- 它将出现在哪个渠道、属于哪种文档；
- 读者需要理解什么或采取什么行动；
- 读者理应掌握哪些上下文；
- 文档描述的是当前状态、一次变更、一项决策，还是一场直接对话。

任务指令只用于控制写作，不会自动成为文档内容。随后，Skill 会根据已经确认的事实构建面向读者的内容，并在交付前执行两项检查：

- **孤立读者测试：** 没有隐藏的任务上下文时，目标读者能否理解并使用这份文字？
- **反事实测试：** 对于描述当前状态的文档，如果事物从一开始就是现在这样，其中每句话是否仍然应该存在？

## 写作模式

| 模式 | 常见文档 | 读者真正需要的内容 |
|---|---|---|
| `state` | README、用户指南、API 文档、落地页、界面文案 | 当前状态以及会影响行动的边界 |
| `change` | PR、提交说明、更新日志、发布说明、迁移指南 | 改变了什么、为什么重要、会产生什么影响 |
| `decision` | ADR、提案、复盘、评审回复 | 背景、证据、备选方案、理由和后果 |
| `direct` | 邮件、支持回复、利益相关者更新、完成报告 | 基于共同上下文的有效答复、结果或下一步行动 |

这个 Skill 并不排斥否定性内容。只要会影响读者的判断，限制、不兼容项、安全边界和弃用信息都应保留。关键不在于一句话是否定或涉及历史，而在于它是否真正服务于当前受众。

## 安装

将仓库克隆到 Codex 的 Skills 目录。

macOS 或 Linux：

```bash
git clone https://github.com/Chengyf2004/Who-Read-Your-Words.git ~/.codex/skills/who-read-your-words
```

Windows PowerShell：

```powershell
git clone https://github.com/Chengyf2004/Who-Read-Your-Words.git "$env:USERPROFILE\.codex\skills\who-read-your-words"
```

## 使用

编写对外文档时，可以显式调用这个 Skill：

```text
使用 $who-read-your-words，为第一次接触此项目的用户编写 README。
```

它也可以检查已经写好的文字：

```text
使用 $who-read-your-words，检查这份 PR 描述是否存在受众错位或任务过程泄露。
```

## 审计现有文本

仓库附带的检查器可以对 Markdown 和纯文本进行一次确定性的初步审计：

```bash
python scripts/audit_external_text.py README.md --profile state
```

根据文档类型选择 `state`、`change`、`decision` 或 `direct`。错误表示存在明显的受众边界问题；警告需要结合读者价值判断，不能直接当作删除指令。

使用 `--fail-on warning` 可以设置更严格的 CI 门槛，使用 `--verbose` 可以显示触发规则的原文行。

## 验证

使用 Python 标准库运行审计测试：

```bash
python -m unittest discover -s scripts -p "test_*.py" -v
```

测试覆盖清晰的当前状态写作、与读者有关的限制、项目变更记录、直接确认、依赖隐藏对话的表述、迁移章节、围栏代码示例以及以工作过程为中心的标题。

## 仓库结构

```text
who-read-your-words/
├── README.md
├── README.en.md
├── LICENSE
├── SKILL.md
├── .gitignore
├── agents/
│   └── openai.yaml
├── references/
│   └── audience-contracts.md
└── scripts/
    ├── audit_external_text.py
    └── test_audit_external_text.py
```

## 许可证

本项目采用 [MIT License](LICENSE)。

## 局限

检查器只能识别文字中的特征，无法完全准确地判断一段内容对特定受众是否有价值。写作模式和 Skill 提供的受众测试仍然是最终判断依据。审计只报告潜在问题，不会自动改写或删除内容。
