---
tags: [素材摘要, AI产品经理, Skill, Claude, 产品经理工具]
created: 2026-05-26
updated: 2026-05-26
source_type: article
source_url: https://www.woshipm.com/ai/6376737.html
source_path: raw/articles/2026-05-26-woshipm-pm-skills-claude.md
author: 秀琴江湖飘
---

# 2026-05-26-woshipm-pm-skills-claude

> 秀琴江湖飘介绍如何把一组产品经理 PM Skills 插件安装到 Claude 中，把 PRD、竞品分析、用户画像、功能优先级、SWOT 和 OKR 等高频 PM 文档任务转成可调用的命令式工作流。

## 基本信息

- **标题**：把这几个产品经理skills焊死到Claude上！
- **作者**：秀琴江湖飘
- **来源**：人人都是产品经理
- **发布时间**：2026-04-14
- **原文链接**：https://www.woshipm.com/ai/6376737.html
- **本地素材**：`raw/articles/2026-05-26-woshipm-pm-skills-claude.md`

## 核心观点

1. **PM Skills 的价值不是把 Claude 当万能替身，而是把完整工作流程复制进去**：作者开头明确提醒“别一上来就把他当成万能的，你什么都不用管”。这说明 PM Skills 的正确定位是把 PRD、竞品分析、用户画像等可流程化环节固化为可调用工作流，而不是把产品判断、需求取舍和业务责任外包给模型。
2. **安装路径已经从“自己写 Skill”下降到“添加 marketplace + 一键安装多个插件包”**：文章给出 `claude plugin marketplace add phuryn/pm-skills` 和一条链式安装命令，一次装入 `pm-toolkit`、`pm-product-strategy`、`pm-product-discovery`、`pm-market-research`、`pm-data-analytics`、`pm-marketing-growth`、`pm-go-to-market`、`pm-execution` 八个包。相比从零写 SKILL.md，这代表 PM 方法论开始以插件包形式分发。
3. **PM 高频任务被映射为命令式入口，降低了调用成本**：作者把“撰写 PRD、竞品分析、用户画像、功能优先级、SWOT 分析、OKR 制定”分别映射到 `/pm-execution:create-prd`、`/pm-market-research:competitor-analysis`、`/pm-market-research:user-personas`、`/pm-product-discovery:prioritize-features`、`/pm-product-strategy:swot-analysis`、`/pm-execution:brainstorm-okrs`。这让 PM 不必每次重新组织长 Prompt，而是通过明确命令进入对应流程。
4. **PRD 生成的关键仍然是前置问题打磨，而不是命令本身**：作者用“视频播放需求文档”演示 `/pm-execution:create-prd`，强调系统提出的提示问题是“能否写到你心里的关键要素”，要多花时间打磨这些问题。这与既有 AI PM 方法论一致：AI 可以生成文档骨架，但问题定义、需求细节和验收边界仍需要 PM 负责。
5. **Markdown 输出把 PM 文档从一次性对话变成可保存、可编译、可交付的文件**：文章最后提到插件会生成 `.md` 文档，并可进一步编译展示。这个细节重要，因为它把 Claude 输出从聊天窗口中的临时文本，推进到可纳入团队文档库、版本管理和后续迭代的交付物。

## 实操内容保留

### 安装 marketplace

```bash
claude plugin marketplace add phuryn/pm-skills
```

### 一键安装全部 PM Skills 插件包

```bash
claude plugin install pm-toolkit@pm-skills && claude plugin install pm-product-strategy@pm-skills && claude plugin install pm-product-discovery@pm-skills && claude plugin install pm-market-research@pm-skills && claude plugin install pm-data-analytics@pm-skills && claude plugin install pm-marketing-growth@pm-skills && claude plugin install pm-go-to-market@pm-skills && claude plugin install pm-execution@pm-skills
```

### 验证安装

```bash
claude plugin list
```

### 常用场景命令表

| 场景 | 命令 | 对 PM 工作的意义 |
|------|------|------------------|
| 撰写 PRD | `/pm-execution:create-prd` | 把需求背景、目标、流程、边界和交付格式收束成文档生成流程 |
| 竞品分析 | `/pm-market-research:competitor-analysis` | 降低信息收集与对比表搭建成本，但洞察仍需人工判断 |
| 用户画像 | `/pm-market-research:user-personas` | 把目标用户、场景、痛点和行为假设结构化 |
| 功能优先级 | `/pm-product-discovery:prioritize-features` | 辅助把功能列表转成可讨论的优先级候选 |
| SWOT 分析 | `/pm-product-strategy:swot-analysis` | 将战略分析框架变成可调用命令，适合早期方向讨论 |
| OKR 制定 | `/pm-execution:brainstorm-okrs` | 把目标和关键结果的头脑风暴流程标准化 |

### PRD 使用流程

1. 在 Claude 输入 `/pm-execution:create-prd`。
2. 告诉它需求，例如“写一份关于视频播放的需求文档”。
3. 认真回答和打磨它追问的关键问题，因为这些问题决定最终 PRD 是否贴合真实需求。
4. 让它生成 `.md` 文档，再根据团队文档规范继续整理或编译展示。

## 关键概念

- [[PM Skills 插件包]]：本文直接介绍的 Claude PM 技能插件集合，以 marketplace 和命令方式安装、调用。
- [[Product Manager Skills]]：既有 PM 方法论技能库实体，本素材补充了“如何把 PM Skills 直接安装进 Claude 并按命令调用”的实操视角。
- [[Skill]]：PM Skills 插件包是 Skill 从“可构建的方法论”走向“可安装的工作流包”的具体样本。
- [[AI产品经理工作流]]：本文将 PRD、竞品分析、用户画像、优先级、SWOT、OKR 六类高频工作纳入可调用流程，补强该主题的 PM 专项工具链维度。
- Claude plugin：文章中用于添加 marketplace、安装插件包和验证插件列表的命令入口，暂不单独建实体页。

## 与其他素材的关联

- 与 [[2026-05-13-ai-pm-requirement-scheduling]] 形成直接补充：那篇讲需求拆解与智能排期两个定制 Skill，这篇给出更通用的 PM Skills 插件包，把 PRD、优先级和 OKR 等流程也纳入命令化调用。
- 与 [[2026-05-21-agent-skills-woshipm]] 互补：那篇解释 Agent Skills 的文件结构、description 触发与渐进式披露，这篇则展示普通 PM 用户如何不写 Skill、直接安装 marketplace 中的 PM 插件。
- 与 [[2026-05-09-pm-ai-playbook]] 的“AI 处理 80% 事务性工作，人做 20% 判断”一致：PM Skills 负责文档和框架生产，PM 仍要负责需求定义、业务取舍和最终验收。
- 与 [[Product Manager Skills]] 形成同一趋势的两个侧面：一个侧重 PM 方法论库与工作分解，一个侧重 Claude 插件化安装与命令式调用。

## 原文精彩摘录

> 之所以把skils放到今天这篇文章，原因是在工作中，别一上来就把他当成万能的，你什么都不用管。

> 接下来当你需要他帮你工作的时候只需要在输入框中：/pm-****

> 这些提示是它能否写到你心里的关键要素，不妨多花点时间去打磨这些问题。会有意想不到的收获。

> 最终它会生成.md文档，这里还要感谢群里的小伙伴的无私奉献。

## 相关页面

- [[PM Skills 插件包]]
- [[Product Manager Skills]]
- [[Skill]]
- [[AI产品经理工作流]]
- [[2026-05-13-ai-pm-requirement-scheduling]]
- [[2026-05-21-agent-skills-woshipm]]
