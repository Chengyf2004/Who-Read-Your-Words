# 谁会读你写的文字？

简体中文 | [English](README.en.md)

## 你是否遇到过这些情况？

**周报变成了调试日志。** 你让 AI 根据一周的 issue、提交记录和排查笔记，整理一份发给上级的工作周报。你希望上级看到的是：“完成登录服务偶发超时问题的修复，根因是连接池配置与重试策略冲突，修复上线后运行稳定。”AI 却写成：“周一先尝试优化数据库索引，但没有效果；周二调整连接池参数时引入了新的异常；周三推翻原判断，改查重试策略；根据后续要求，已删除部分排查细节……”本应汇报最终进展的周报，变成了一份包含错误判断、临时操作，甚至修改指令的试错实录。

**删除变成了反复强调。** 你让 AI 把已经否决的 Redis 方案从技术文档中彻底移除，因为最终读者根本不需要知道它曾经存在。AI 删除了原段落，却把标题改成《系统设计（Without Redis）》，开头补上一句“本文档不讨论 Redis”，后面又增加一节“为什么本文档不讨论 Redis”。Redis 从方案里消失了，却成了整份文档最醒目的主题。

这两种结果在字面上都执行了指令，却没有面向文档真正的读者。试错过程、修改指令和被否决的内容原本只是帮助 AI 完成任务的内部信息，最后却越过受众边界，进入了交付成品——这就是**内部过程泄露**。

`who-read-your-words` 会在写作前先问：**谁会读这些文字？这个读者真正需要知道什么？**

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

推荐使用 [skills CLI](https://skills.sh/docs/cli) 安装到 Codex 的用户级 Skills 目录：

```bash
npx skills add Chengyf2004/Who-Read-Your-Words --skill who-read-your-words --agent codex -g -y
```

也可以使用 GitHub CLI：

```bash
gh skill install Chengyf2004/Who-Read-Your-Words who-read-your-words --agent codex --scope user
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
python skills/who-read-your-words/scripts/audit_external_text.py README.md --profile state
```

根据文档类型选择 `state`、`change`、`decision` 或 `direct`。错误表示存在明显的受众边界问题；警告需要结合读者价值判断，不能直接当作删除指令。

使用 `--fail-on warning` 可以设置更严格的 CI 门槛，使用 `--verbose` 可以显示触发规则的原文行。

## 验证

使用 Python 标准库运行审计测试：

```bash
python -m unittest discover -s skills/who-read-your-words/scripts -p "test_*.py" -v
```

测试覆盖清晰的当前状态写作、与读者有关的限制、项目变更记录、直接确认、依赖隐藏对话的表述、迁移章节、围栏代码示例以及以工作过程为中心的标题。

## 仓库结构

```text
who-read-your-words/
├── README.md
├── README.en.md
├── LICENSE
├── .gitignore
└── skills/
    └── who-read-your-words/
        ├── SKILL.md
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
