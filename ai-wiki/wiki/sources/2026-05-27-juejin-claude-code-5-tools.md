---
tags: [素材摘要, Claude Code, 生态, Skill, Plugin, 上下文工程, 可观测性, 团队协作]
created: 2026-05-27
updated: 2026-05-27
source_type: 文章
source_path: ../../raw/articles/2026-05-27-141917-tg-ad7cdc.fetched.md
---

# Claude Code 生态爆发：5 个必知的新工具

> 程序员 Sunday 在掘金梳理 Claude Code 正从单一终端工具长成插件平台，五款代表性工具分别对应工作流、可观测性、上下文工程、学习门槛、团队协作五个完全不同的方向。

## 基本信息

- **来源类型**：文章（掘金）
- **原文位置**：`raw/articles/2026-05-27-141917-tg-ad7cdc.fetched.md`
- **原文 URL**：https://juejin.cn/post/7619279067029209128
- **作者**：程序员 Sunday
- **发布日期**：2026-03-21
- **消化日期**：2026-05-27

## 核心观点

1. **Claude Code 已经从工具长成平台**：官方插件市场不只推 Skills，而是 `plugins / agents / hooks / MCP servers / LSP servers` 一整套生态——单工具叙事已经过时，正确的视角是"围绕 Claude Code 的开发生态"。

2. **Superpowers（100k+ stars）解决"工作流"问题，强制 AI 先想再写**：仓库自己的定位是"一整套建立在 composable skills 和初始指令之上的软件开发工作流"，不是单个 skill。核心动作是先退一步问清楚需求，再把后续流程一点点整理出来，再动手——直接对治"很多人用 AI 写代码最大的问题不是模型不够强，而是一上来就开写，写着写着需求就歪了"。安装方式：Claude 插件市场直接装。

3. **Claude HUD 第一次把 Claude Code 的运行状态可视化**：实时仪表盘形态（类比 npm install 的进度感）。解决"你根本不知道它现在到底在干嘛"的盲盒痛点。适合两类人——重度使用 Claude Code 且任务链路较长的人、经常觉得"AI 好像在乱跑但说不清问题出在哪"的人。**硬性要求 Claude Code v1.0.80+**。

4. **GET SHIT DONE（GSD）专治上下文腐烂**：诊断"为什么 Claude Code 一开始挺聪明，写着写着就变笨"——大模型上下文超了，模型不知道你前面做了什么。GSD 做的事情是"重新整理 Claude 干活时吃进去的上下文"。代表了 Claude Code 生态里非常重要的一层——**上下文工程**。适合做长链路开发任务（需求分析 → 代码落地 → 调试 → 收尾）、明显感觉到 Claude Code "用久了会变笨"的人。

5. **Learn Claude Code（34.2k stars）降低学习门槛**：定位与其他四个不同——前四个增强能力边界，它让"不会使用 Claude 的人把 Claude 用起来"。不是传统文档堆砌型教程，而是"在 Claude Code 里交互体验的课程"，提供中文版。适合刚接触 Claude Code、不知道从哪里入手的人。

6. **Claude Code Action 把 AI 装进团队协作流程**：前四个工具都围绕"本地使用 Claude Code"展开，这个跨到另一个层级——团队协作流程（issue、PR、Review）。作者的直白翻译："这玩意可以让 AI 员工进组开发了"。

7. **五款工具对应五个完全不同的方向**：这是文章的元结论——Superpowers→工作流、Claude HUD→可观测性、GSD→上下文腐烂、Learn Claude Code→学习门槛、Claude Code Action→协作流程。这种五维分裂正好说明"工具变平台"的真实形态：单点能力很难再代表 Claude Code 的全部价值，必须按需组合。

## 实操内容保留

### 代码/配置

（本文无代码块。提到的关键命令是"通过 Claude 的插件市场安装"，但未给出具体 marketplace add / install 命令）

### Prompt 模板

（本文无 Prompt 模板）

### 操作步骤

文章给出的操作粒度只到"装在哪里"，没有逐步教程。可用的最小操作信息：

1. **Superpowers**：通过 Claude 的插件市场直接安装（plugin 形态）
2. **Claude HUD**：要求 Claude Code 版本 ≥ v1.0.80，装上之后基本就能直接看到效果
3. **GET SHIT DONE / Learn Claude Code / Claude Code Action**：原文未给出具体安装命令，需读者自行查阅各项目 README

## 关键概念

- [[Claude Code]] — 本文所有五个工具围绕的 AI 编程 Agent 本体
- [[Skill]] — 文章把 Superpowers 与"单个 skill"做了关键对比，引出"composable skills + 初始指令"的工作流框架定位
- [[MCP 模型上下文协议]] — 文章列举的官方插件类型之一（"MCP servers"）
- [[AI Agent 智能体]] — 文章列举的官方插件类型之一（"agents"）
- [[Superpowers]] — Claude Code 工作流框架（100k+ stars）
- [[Claude HUD]] — Claude Code 运行状态可视化仪表盘
- [[GET SHIT DONE]] — Claude Code 上下文工程工具（专治上下文腐烂）
- [[Learn Claude Code]] — Claude Code 交互式学习课程（34.2k stars）
- [[Claude Code Action]] — Claude Code 团队协作集成（issue/PR/Review）
- [[上下文工程]] — Claude Code 生态里非常重要的一层
- 上下文腐烂 — 大模型上下文超了导致模型变笨的现象（GSD 的主要靶子）

## 与其他素材的关联

- 与 [[2026-05-11-claude-code-6-skills]] 的关系：**互补的两个视角**。2026-05-11 的素材聚焦"装哪 6 个 Skill"——通用 3 个（Skill Creator / Planning with Files / Document & Presentation Skills）+ 创作 3 个（SEO Blog Writer / Newsletter Automation / Content Repurposer），并提出"装太多会降触发准确率到 50% 以下"的天花板。本文跨出 Skill 单一形态，转向 plugin / agent / hook / MCP server / LSP server 等更宽的扩展点，并按"问题方向"（工作流/可观测性/上下文/学习/协作）而非"职业场景"重新切片。两篇合在一起就是：单点 Skill 选 6 个 + 五个方向各装一个生态工具 = 完整的 Claude Code 工作台。

- 与 [[2026-05-21-agent-skills-woshipm]] 的关系：**Skill 工程化 vs 生态扩展的两条主线**。沃垠那篇讲清楚了 Skill 内部怎么写（SKILL.md + scripts/references/assets），这篇讲清楚了 Skill 外部还能装什么（plugin/agent/hook/MCP/LSP）。两者构成 Claude Code 完整可扩展性的内外两面。

- 与 [[2026-05-27-woshipm-central-skill-symlink]] 的关系：**多 Agent 时代的 Skill 资产管理 vs Claude Code 内部的多扩展类型管理**。中央 Skill 那篇解决"多个 Agent 都要 Skill"的横向问题，本文揭示"单个 Agent 内部也已经有 plugin/skill/agent/hook/MCP/LSP 多种扩展形态"的纵向问题。两个方向叠加意味着 Skill 资产管理面临"横向多 Agent × 纵向多扩展类型"的二维爆炸，未来必然出现统一的资产清单工具。

- 与 [[2026-05-13-ai-agent-productivity-20x]] 的关系：**深思圈强调 Agent harness 的核心可迁移资产是 `agents.md` / `memory.md` / Skill / MCP**——这与本文揭示的"Claude Code 已经在官方推 plugins / agents / hooks / MCP servers / LSP servers"完全对齐。深思圈给出概念框架，Sunday 这篇给出 Claude Code 平台上的具体落地证据：上下文资产管理不仅是方法论，已经是 Anthropic 在产品形态上推动的方向。

## 原文精彩摘录

> 现在很多同学还是把 Claude Code 当成一个"可以在终端里写代码的 AI 工具"。但是，这两天我越来越觉得，Claude Code 这玩意儿已经不是单个工具了，现在开始长生态了。原因是因为，现在打开 Claude Code 官方开始推各种 plugin 了。不光是 skills 而是各种的 agents、hooks、MCP servers、LSP servers。

> Superpowers 现在已经超过 100k stars 了（上午还是 99K 呢...），仓库自己对它的定义也很直接：它不是单个 skill，而是一整套建立在 composable skills 和初始指令之上的软件开发工作流。... 它强调的不是你说一句，AI 执行 skills 完成一大堆的任务，跑一大堆 token。而是先退一步，问清楚你到底要做什么，再把具体的后续流程一点点整理出来，再往下执行。这也是它为什么会火的原因。因为，现在很多人用 AI 写代码，最大的问题根本不是模型不够强，而是一上来就开写。写着写着需求就歪了。

> 第三个是名字非常粗暴，叫 GET SHIT DONE。... GSD 解决的是另一个更深层的问题：为什么 Claude Code 一开始还挺聪明，写着写着就开始变笨了？其实出现这个问题的原因大多数情况下上是因为大模型的上下文超了，导致模型不知道你前面做了什么。因此 GSD 做的事情就是帮你重新整理 Claude 干活时吃进去的上下文，也就是上下文腐烂的问题。所以我会觉得，GSD 这种项目，代表的是 Claude Code 生态里非常重要的一层：上下文工程。

> Claude Code 现在最值得关注的，已经不是"它能不能帮你写代码"了。而是围绕它，一整套新的开发生态，已经开始长出来了。前面的这 5 个工具，其实刚好对应了 5 个完全不同的方向：Superpowers 解决工作流的问题；Claude HUD 解决可观测性的问题；GET SHIT DONE 解决上下文腐烂的问题；Learn Claude Code 解决学习门槛的问题；Claude Code Action 解决协作流程的问题。... Claude Code，正在从一个工具，慢慢长成一个平台。

## 相关页面

- [[Claude Code]]
- [[Superpowers]]
- [[Claude HUD]]
- [[GET SHIT DONE]]
- [[Learn Claude Code]]
- [[Claude Code Action]]
- [[上下文工程]]
- [[Skill]]
- [[MCP 模型上下文协议]]
- [[AI编程开发]]
- [[2026-05-11-claude-code-6-skills]]
- [[2026-05-21-agent-skills-woshipm]]
- [[2026-05-27-woshipm-central-skill-symlink]]
- [[2026-05-13-ai-agent-productivity-20x]]
