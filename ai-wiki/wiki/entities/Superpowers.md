---
tags: [实体, 工具, Claude Code, 工作流, 插件, GitHub]
type: entity
name: Superpowers
category: Claude Code 生态工具
sources:
  - 2026-05-27-juejin-claude-code-5-tools
created: 2026-05-27
updated: 2026-05-27
---

# Superpowers

> 截至 2026-03 已超 100k stars 的 Claude Code 工作流框架——不是单个 skill，而是建立在 composable skills 和初始指令之上的"先想清楚再开写"软件开发方法论

## 简介

Superpowers 是 Claude Code 生态里目前最炸的扩展项目——程序员 Sunday 在 2026-03-21 写稿时已经超过 100k stars（上午还是 99K）。它的仓库自己对它的定义很直接：**它不是单个 skill，而是一整套建立在 composable skills 和初始指令之上的软件开发工作流。** 也就是说，Superpowers 的形态比 Skill 更高一层——把多个 Skill 组合成一套有约束的工作方法。

它解决的问题是 AI 编程实践中**最常见的失败模式**："一上来就开写，写着写着需求就歪了"。Sunday 在文章里直接点破：现在很多人用 AI 写代码，最大的问题根本不是模型不够强，而是一上来就开写。Superpowers 干的事，本质上就是给 Claude 加了一层固定的工作流——让 Claude 先想清楚具体的步骤和方案、和你确认了之后，再动手去写代码。

可以把它理解成给 Claude Code **多了一个方法论**：原本默认的"你说一句、AI 立刻执行 skills 跑一堆 token"的模式被替换成"先退一步问清楚 → 把后续流程一点点整理出来 → 再确认 → 再往下执行"。这就是它在 100k+ stars 这个量级仍然在快速增长的根本原因——它不解决新能力，而是修复"模型够强但用法不对"的实际生产力问题。

## 关键信息

- **类型**：工具 / 工作流框架
- **领域**：AI 编程 / Claude Code 生态
- **stars**：100k+（2026-03-21 数据；上午为 99K，写稿时已超 100K）
- **形态**：composable skills + 初始指令（不是单个 skill）
- **安装方式**：Claude 插件市场直接安装（plugin 形态）
- **核心定位**：在 Claude Code 上加一层"先想再写"的工作流约束
- **相关概念**：[[Claude Code]]、[[Skill]]、[[Claude HUD]]、[[GET SHIT DONE]]、[[Learn Claude Code]]、[[Claude Code Action]]

## 核心特性

### 核心机制：先想清楚再开写

Superpowers 的核心动作分三步：

1. **先退一步问清楚你到底要做什么**——不立刻执行，先澄清需求
2. **把后续流程一点点整理出来**——拆分步骤、写出方案
3. **和你确认后再动手去写代码**——确认即护栏，避免跑偏

这种"先想再写"的约束直接对治了 AI 编程实践里的头号失败模式。Sunday 原话：

> 现在很多人用 AI 写代码，最大的问题根本不是模型不够强，而是一上来就开写。写着写着需求就歪了。

### 形态：composable skills + 初始指令

Superpowers 不是单个 Skill，而是把多个 Skill 用一份初始指令"编排"起来的复合扩展。这种形态比单 Skill 更高一层：

| 层级 | 形态 | 典型代表 |
|------|------|---------|
| 原子能力 | 单个 Skill | Skill Creator / Planning with Files |
| 工作流框架 | composable skills + 初始指令 | **Superpowers** |
| 完整平台 | 多扩展点（Skills/agents/hooks/MCP/LSP）| Claude Code 本体 |

它处在原子能力和完整平台中间，承担"把多个原子能力按一套方法论组合起来"的工作。

### 适用人群

- 经常用 Claude Code 写代码、但容易"写着写着跑偏"的开发者
- 需要在动手前强制做需求澄清的团队
- 想给 Claude Code 加方法论护栏、不想每次都手动提醒"先讨论再写代码"的人

### 与同类工具的区别

- 与单个 Skill 的区别：单 Skill 是"会做某件事"的程序性知识包；Superpowers 是"按这套方法做一连串事"的工作流。
- 与 [[Claude HUD]] 的区别：Superpowers 修改的是 Claude 的**做事方式**（行为层）；Claude HUD 修改的是 Claude 的**可观测性**（展示层）。两者正交，可以同时装。
- 与 [[GET SHIT DONE]] 的区别：GSD 解决的是 Claude 用久了上下文腐烂的问题；Superpowers 解决的是 Claude 一上来就跑偏的问题。一个是中期问题（写着写着变笨），一个是开局问题（开头就跑歪）。

## 不同素材中的观点

- **[[2026-05-27-juejin-claude-code-5-tools]]**：程序员 Sunday 把 Superpowers 列为 Claude Code 生态五个必知工具的第一个，强调它的核心价值是"把 Claude Code 从会写代码变成会按流程做项目"。文章用"逼格不一样"形容它和普通 Skill 的差异——它不是让你说一句就执行 skills 跑一堆 token，而是先退一步问清楚再往下执行。100k+ stars 的高位增长被解释为"它解决的是真痛点——很多人用 AI 写代码最大的问题不是模型不够强，而是一上来就开写"。

## 实用信息

### 快速上手步骤

1. 打开 Claude Code 的插件市场
2. 搜索 Superpowers 并直接安装（plugin 形态，类似 VSCode 装插件）
3. 装完后下次和 Claude Code 协作时，它会先帮你澄清需求、整理步骤再动手

### 常用提示词/命令

文章未给出具体命令——它的核心机制是装上之后自动改变 Claude Code 的行为模式，不需要手动调用。

### 注意事项/避坑指南

1. **它替换的是默认工作流，不是额外功能**：装上之后 Claude Code 整体作风会从"立刻动手"变成"先确认再动手"。如果你的场景就是想要快速产出小改动（如改一个 typo），可能会觉得"啰嗦"
2. **配合 GSD 使用更稳**：Superpowers 解决开局跑偏，GSD 解决用久了变笨——两者解决的是同一条任务链路上的不同阶段问题
3. **本质是方法论框架，不是技术魔法**：它的价值来自强制改变协作节奏，不是给 Claude 装了什么新能力。如果你已经有"先和 AI 讨论再动手"的习惯，它的边际收益较小

## 相关页面

- [[Claude Code]]
- [[Skill]]
- [[Claude HUD]]
- [[GET SHIT DONE]]
- [[Learn Claude Code]]
- [[Claude Code Action]]
- [[上下文工程]]
- [[AI编程开发]]
- [[2026-05-27-juejin-claude-code-5-tools]]
