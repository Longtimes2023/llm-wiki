---
tags:
  - 素材摘要
  - AI Agent
  - 自动化
  - 工作流
  - 效率提升
  - MCP
  - 上下文工程
created: 2026-05-18
updated: 2026-05-18
source_path: raw/articles/2026-05-18-woshipm-ai-agent-productivity.md
---

# 生产力提升20倍的秘密：用AI Agent把一周工作压缩进一天

> 基于 Remy Gaskill 在 The Startup Ideas Podcast 分享的 AI Agent 工作流系统，深度解析从"问答模式"到"目标-结果模式"的转变。核心框架包括 Observe-Think-Act 循环、agents.md 大脑构建、memory.md 记忆系统、MCP 工具连接、技能标准化和文件夹结构组织。

## 基本信息

- 标题：生产力提升20倍的秘密：用AI Agent把一周工作压缩进一天
- 作者：深思圈
- 来源站点：人人都是产品经理
- 发布时间：2026-03-25
- 原始链接：https://www.woshipm.com/ai/6362871.html
- 原始素材：`raw/articles/2026-05-18-woshipm-ai-agent-productivity.md`

## 核心观点

1. **从"问答模式"到"目标-结果模式"是 Agent 生产力的代际跃迁**：传统聊天像打乒乓球，最终还是人在做事。AI Agent 则不同——给它一个目标，它会自己规划步骤、执行任务、交付结果。文章称生产力可提升 10-20 倍，把一周工作压缩进一天。

2. **Agent 的底层运作逻辑是 Observe-Think-Act 三步循环**：Agent 持续执行"观察→思考→行动"循环，直到根据设定参数判断任务完成。这套循环跨平台通用，Claude Code、Codex、Cowork、Manus、OpenClaw 都是不同的"Agent 容器/框架"。学到的技能可迁移，不会被特定工具锁定。

3. **agents.md 文件是 Agent 的大脑/系统提示词**：在文件夹中创建 agents.md，放入角色、业务背景、个人偏好、常用工具和工作方式。Agent 在每个任务开始前加载。可用聊天模型以访谈方式（约 15-20 个问题）自动构建。这标志着从"提示词工程"到"上下文工程"的转变。

4. **memory.md 文件为 Agent 配备可控制的记忆系统**：在 agents.md 中添加两行指令——"每个任务开始前读取 memory.md"和"当我纠正你或你学到新东西时更新 memory.md"。Agent 会记住用户偏好并随时间改进。保持 agents.md 在 200 行以内，定期清理 memory.md。

5. **MCP 协议是 Agent 与外部工具的通用翻译器**：MCP 作为双向翻译器让 Agent 连接 Gmail、Google Calendar、Notion、Stripe、Slack 等工具。一个提示词可让 Agent 总结收件箱、提取会议笔记、创建付款链接、设置项目、起草邮件，无需切换标签页。

6. **Skills（技能）是 Agent 的标准作业流程，具有复利效应**：你解释一次流程，Agent 就能每次完美重复。创建方法有两种：提供源材料，或从实际会话中构建。技能可累积，每周自动化 3-5 个小流程。真实案例：广告库分析技能将 3-4 小时工作压缩为几分钟，一年节省 300-400 小时。

7. **技能链接和定时任务实现完全自主的自动化**：晨间简报技能检查日历 → 看到播客安排 → 自动触发研究技能。大多数框架支持定时任务（如每天 9 点运行）。更激进的案例：每三小时自动抓取汽车市场平台，匹配即通知。

8. **按部门划分的文件夹结构是 Agent 团队组织方式**：为每个公司/客户创建大文件夹，按部门划分子文件夹（executive assistant、content team、marketing、sales），每个有自己的 agents.md、memory.md、技能和 MCP 连接。

9. **起步路径：从工具使用者到数字团队管理者**：选框架（推荐 Cowork）→创建文件夹→构建 agents.md→添加 memory.md→连接 3-5 个核心工具→处理真实任务→每周自动化 3-5 个小流程。

10. **思维模式转变是最根本的杠杆**：agents.md = 员工手册，memory.md = 工作日志，skills = 专业技能，MCP = 工作权限。整个系统映射了人类组织的管理逻辑。

## 实操内容保留

### Agent 文件夹结构模板

```
公司名/
├── executive-assistant/
│   ├── agents.md
│   ├── memory.md
│   └── skills/
├── content-team/
│   ├── agents.md
│   ├── memory.md
│   └── skills/
├── head-of-marketing/
│   ├── agents.md
│   ├── memory.md
│   └── skills/
└── sales/
    ├── agents.md
    ├── memory.md
    └── skills/
```

### agents.md 构建提示词

```
用访谈的方式问我问题，提取所有你需要的上下文信息，
然后帮我构建一个 agents.md 文件。
```

模型会问约 15-20 个问题，从工作角色、公司业务、目标客户、沟通风格、常用工具到邮件签名偏好，全部提取并生成 agents.md。

### memory.md 配置指令

在 agents.md 中添加两行：
```
在每个任务开始前读取 memory.md 文件
当我纠正你或者你学到新东西时，更新 memory.md 文件
```

### 起步七步路径

1. 选择一个 Agent 框架（Cowork 适合初学者）
2. 创建"executive assistant"文件夹
3. 用访谈式提示词构建 agents.md
4. 添加带有自动更新指令的 memory.md
5. 通过 MCP 连接最常用的 3-5 个工具
6. 开始用 Agent 处理真实任务，重复流程转化为技能
7. 每周自动化 3-5 个小流程

## 关键概念

- AI Agent 智能体 — 本素材主角，Observe-Think-Act 循环
- MCP 模型上下文协议 — 连接 Agent 与外部工具的通用翻译器
- 上下文工程 — 从提示词工程到上下文工程的转变
- Cowork — 推荐的初学者 Agent 框架
- Antigravity — 文中提到的 Agent 容器/框架之一

## 与其他素材的关联

- [2026-05-09-pm-ai-playbook](sources/2026-05-09-pm-ai-playbook.md) — 两者都讨论 AI 提升生产力的人机分工原则，本文提供更具体的 Agent 系统架构方法论
- [2026-04-29-yupi-ai-guide-core-concepts](sources/2026-04-29-yupi-ai-guide-core-concepts.md) — 鱼皮指南定义了 AI Agent 核心概念，本文深入展开 agents.md/memory.md/skills 实操体系
- [2026-05-17-ai-short-drama-workflow](sources/2026-05-17-ai-short-drama-workflow.md) — 短剧 Agent 是垂直任务型智能体案例，本文强调通用 Agent 工作流方法论
- [2026-05-17-ai-pm-interview-claude-workflow](sources/2026-05-17-ai-pm-interview-claude-workflow.md) — 面试复盘工作流实际上是技能（skill）的实践

## 原文精彩摘录

> 大多数人使用 AI 的方式还停留在最初级的阶段：输入问题，获得答案，然后自己动手完成工作。但有一小群人已经跨越到了完全不同的维度，他们让 AI agent 自动管理邮件、日历、广告投放和日常运营，生产力提升了 10 到 20 倍。这不是夸张，而是正在发生的现实。

> 这个循环是跨平台通用的。Claude Code、Codex、Antigravity、Cowork、Manus、OpenClaw，这些都只是不同的"agent harnesses"（agent 容器或框架）。Remy 把它们比作不同品牌的汽车。一旦你学会了如何开车——踩油门、刹车、转方向盘——你就能开任何车。同样的循环，不同的风味。

> 如果你每周自动化 3-5 个微小的手动流程，最终你会自动化整个工作流。这不是一夜之间发生的，而是一个渐进的过程。但正因为是渐进的，它可持续、可控制。

> 循环非常简单：连接工具 → 构建上下文 → 创建技能 → 自动化流程 → 重复。从执行助理开始，本周构建一个技能，下周再构建一个。把这个过程堆叠数月，你就能把一周的工作压缩进一天。这不是科幻，而是现在就可以实现的现实。
