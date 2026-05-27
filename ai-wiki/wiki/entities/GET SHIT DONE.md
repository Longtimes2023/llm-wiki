---
tags: [实体, 工具, Claude Code, 上下文工程, 上下文腐烂]
type: entity
name: GET SHIT DONE
category: Claude Code 生态工具
aliases: [GSD]
sources:
  - 2026-05-27-juejin-claude-code-5-tools
created: 2026-05-27
updated: 2026-05-27
---

# GET SHIT DONE

> Claude Code 生态里专治"上下文腐烂"的工具，简称 GSD——重新整理 Claude 干活时吃进去的上下文，让它写着写着不要变笨

## 简介

GET SHIT DONE（简称 GSD）是 Claude Code 生态里专门解决**上下文腐烂（context rot）** 的工具。它的名字非常粗暴，但解决的问题极其精准——这是 Claude Code 用户最普遍但最难说清的痛点：**为什么 Claude Code 一开始还挺聪明，写着写着就开始变笨了？**

GSD 给出的诊断答案是：**大模型的上下文超了，导致模型不知道你前面做了什么。** 这是 LLM Agent 协作的结构性问题——模型本身没退化，但随着任务链路推进，上下文窗口里塞满了历史工具调用、文件内容、对话片段。当上下文逼近窗口上限时，重要信息被淹没在噪音里，模型表现下降，看起来就像"变笨"。

GSD 干的事情就是**帮你重新整理 Claude 干活时吃进去的上下文**。具体机制文章没展开，但定位非常清晰——它代表了 Claude Code 生态里非常重要的一层：**[[上下文工程]]**。这一层之所以重要，是因为它直接决定了 Agent 在长链路任务下的可持续性——没有上下文工程，再强的模型也会在第 50 步开始失忆。

## 关键信息

- **类型**：工具 / 上下文工程工具
- **领域**：AI 编程 / Claude Code 生态 / Context Engineering
- **核心定位**：专治"上下文腐烂"——重新整理 Claude 吃进去的上下文
- **简称**：GSD
- **生态层级**：上下文工程层
- **相关概念**：[[Claude Code]]、[[Superpowers]]、[[Claude HUD]]、[[Learn Claude Code]]、[[Claude Code Action]]、[[上下文工程]]

## 核心特性

### 解决的问题：上下文腐烂

Sunday 在文章里描述的现象很常见：

> 为什么 Claude Code 一开始还挺聪明，写着写着就开始变笨了？

诊断根因：

> 大模型的上下文超了，导致模型不知道你前面做了什么。

GSD 的核心动作：

> 帮你重新整理 Claude 干活时吃进去的上下文，也就是"上下文腐烂"的问题。

### 适用人群

文章明确给出两类典型用户：

| 用户类型 | 触发场景 |
|---------|---------|
| 经常做长链路开发任务的人 | 从需求分析一路干到代码落地、调试、收尾——长链路是上下文腐烂的高发场景 |
| 已经明显感觉到 Claude Code "用久了会变笨" 的人 | 已经踩过坑、知道问题存在的用户 |

### 在 Claude Code 生态里的位置：上下文工程层

文章给出 Claude Code 五个工具的方向矩阵，GSD 代表的是**上下文工程**这一层。这一层在 AI Agent 协作里的价值正在被越来越多人意识到：

- [[Superpowers]]：工作流层——让 Claude 先想再写
- [[Claude HUD]]：可观测性层——让你看见 Claude 在干嘛
- **GSD：上下文工程层——让 Claude 不要变笨**
- [[Learn Claude Code]]：学习门槛层——让新用户能上手
- [[Claude Code Action]]：协作流程层——把 AI 装进团队链路

### 与同类工具的区别

- 与 [[Superpowers]] 的区别：Superpowers 解决"一上来就开写跑偏"的**开局问题**；GSD 解决"写着写着变笨"的**中后期问题**。两者在任务链路的不同阶段发挥作用，互补而非替代。
- 与传统对话压缩 / Memory 机制的区别：传统机制是被动地把旧上下文丢弃或压缩；GSD 是主动"重新整理"——更接近"上下文垃圾回收 + 重组"。
- 与 Claude Code 内置的 `/compact` 命令的关系：文章没明确对比，但 GSD 显然不是简单的压缩，而是更高阶的上下文工程能力。

### 上下文工程作为新兴学科

GSD 的另一层意义在于：它代表 Claude Code 生态里**上下文工程**作为一个独立工程方向的浮出水面。这与深思圈（[[2026-05-13-ai-agent-productivity-20x]]）和云舒（[[2026-05-27-woshipm-yunshu-skill-practical-guide]]）反复强调的观点对齐——AI Agent 时代真正的可迁移资产是上下文层面的（agents.md / memory.md / Skill / MCP），而**如何管理这些上下文资产**就是上下文工程要回答的问题。GSD 是这个新学科的第一个有名字的工具化产物。

## 不同素材中的观点

- **[[2026-05-27-juejin-claude-code-5-tools]]**：程序员 Sunday 把 GSD 列为 Claude Code 生态五个必知工具的第三个，并把它的差异化定位讲得非常清楚——"如果说 Superpowers 解决的是'别一上来就瞎写'的问题，Claude HUD 解决的是'让你知道 Claude 目前在干嘛'的问题，那 GSD 解决的就是另一个更深层的问题：为什么 Claude Code 一开始还挺聪明，写着写着就开始变笨了？" 文章把 GSD 提升到**上下文工程**这个生态层的代表性高度——"GSD 这种项目，代表的是 Claude Code 生态里非常重要的一层：上下文工程"。这是这个词条最有价值的洞察——GSD 不只是一个工具，它定义了一个新的工程方向。

## 实用信息

### 快速上手步骤

1. 安装 GSD（文章未给出具体安装命令，需查项目 README）
2. 装上之后用于长链路任务（如需求分析 → 代码落地 → 调试 → 收尾的完整开发流程）
3. 当感觉 Claude Code 开始变笨时，调用 GSD 重新整理上下文

### 常用提示词/命令

文章未给出具体命令。

### 注意事项/避坑指南

1. **它解决的是中后期问题，不是开局问题**：如果你的痛点是"一上来就跑偏"，应该装 [[Superpowers]]；GSD 适合用久了变笨的场景
2. **长链路任务收益最大**：短任务上下文还没用完，GSD 边际收益小；长链路任务（需求分析→代码→调试→收尾）才是它的主战场
3. **它是上下文工程的代表，不是终极方案**：上下文工程作为一个学科还在早期，GSD 给出了"重新整理上下文"这一种解法，未来会有更多 GSD 类工具出现
4. **配合 Claude HUD 使用更稳**：HUD 让你看见 Claude 在干啥，GSD 让 Claude 不要变笨——一个负责发现问题，一个负责修复问题

## 相关页面

- [[Claude Code]]
- [[Superpowers]]
- [[Claude HUD]]
- [[Learn Claude Code]]
- [[Claude Code Action]]
- [[上下文工程]]
- [[AI编程开发]]
- [[2026-05-27-juejin-claude-code-5-tools]]
- [[2026-05-13-ai-agent-productivity-20x]]
- [[2026-05-27-woshipm-yunshu-skill-practical-guide]]
