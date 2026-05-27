---
tags: [素材摘要, Agent Skills, Claude Code, AI编程开发, Skill]
created: 2026-05-21
updated: 2026-05-21
source_type: article
source_url: https://www.woshipm.com/share/6377843.html
source_path: raw/articles/woshipm.com/agent-skills.md
---

# 2026-05-21-agent-skills-woshipm

> 沃垠AI 的长文教程，系统梳理了 Agent Skills 的定义、文件架构、description 触发机制、渐进式披露、与 Prompt/MCP/Agent/Projects 的边界，以及从 0 到 1 设计与安装 Skill 的完整方法。

## 基本信息

- **标题**：万字干货！Agent Skills从入门到精通
- **作者**：沃垠AI
- **来源**：人人都是产品经理
- **发布时间**：2026-04-15
- **原文链接**：https://www.woshipm.com/share/6377843.html
- **本地素材**：`raw/articles/woshipm.com/agent-skills.md`

## 核心观点

1. **Skills 是 2026 年 Agent 体系里最值得学习的能力封装方式**：文章把 Skills 定义为“给 AI 的标准操作手册”，认为没有 Skills 的 Agent 像刚入职的新同事，需要反复培训；有了 Skills 后则更像能直接接活的老同事，背后本质是把团队隐性经验、重复动作和质量标准封装成结构化能力包。
2. **Skills 的最小完整结构是 `SKILL.md + 可选资源目录`**：`SKILL.md` 是入口与总控，`scripts/` 放可执行代码，`references/` 放按需加载的规范文档，`assets/` 放模板/图片/字体等资源；Agent 以 `SKILL.md` 为第一指引，再按任务情况决定是否调度脚本、参考资料与素材资源。
3. **description 字段是 Skill 能否被准确触发的关键门控**：文章反复强调 description 不是写给人看的介绍，而是写给 Agent 路由器看的匹配规则，黄金结构是“核心功能 + 执行动作 + 明确触发关键词/场景”；如果 description 含糊，即使 Skill 本身很强，Agent 也可能“想不起来”调用它。
4. **渐进式披露解决了 Skill 文档过长导致的上下文爆炸问题**：作者用“书架上的工具书”比喻 Skills——平时不占上下文，需要时才调入相关章节；因此大型 Skill 可以拆成多层文件，在不牺牲规范密度的前提下保持模型上下文清爽。
5. **Skills 与 Prompt、MCP、Agent、Projects 处在不同分层**：Prompt 负责单次表达意图，MCP 提供工具与外部能力，Projects 承载项目上下文，Agent 负责自主执行；Skill 则更像“预制好流程的操作蓝图”，把提示、步骤、工具权限和输出标准打包成一个可复用能力层。
6. **制作 Skill 的成熟路径不是凭空设计，而是从真实工作反复试错中沉淀**：文章在信息图生成器案例中展示了完整流程：先明确单一职责和触发场景，再设计文件结构、编写 YAML 元数据和操作步骤、补充参考设计指南，最后通过自然语言触发测试与执行验证迭代优化。
7. **Skill 生态已经从 Claude Code 扩展到跨平台 Agent 标准**：文章回顾了 Anthropic 于 2025-10-16 首发 Agent Skills、2025-12-18 开放统一标准的过程，并列举了 Codex、Cursor、OpenClaw、Hermes 等平台陆续支持，说明 Skill 正在从产品特性演化为 Agent 时代的通用能力分发协议。

## 实操内容保留

### Skill 标准目录结构

```text
skill-name/
├── SKILL.md
│   ├── YAML frontmatter
│   │   ├── name:
│   │   └── description:
│   └── Markdown instructions
└── Bundled Resources
    ├── scripts/
    ├── references/
    └── assets/
```

### description 黄金结构示例

```yaml
name: security-code-review
description: Reviews code for security vulnerabilities and best practices. Use when the user asks to “review code”, “check for bugs”, “analyze security”, or mentions specific issues like SQL injection, XSS, or performance bottlenecks.
```

### 信息图生成器 Skill 的 YAML 元数据示例

```yaml
name: html-infographic-generator
description: 从用户文字中提炼核心关键点，生成Magazine Layout风格的深色主题HTML信息图网页；当用户需要将文字内容可视化、创建信息图、生成数据展示页面或制作图文混排页面时使用。
```

### 制作 Skill 的四阶段流程

1. 明确需求与边界：确定单一职责、触发关键词和所需资源。
2. 构建 Skill 文件夹：创建 `SKILL.md`，按需补充 `scripts/`、`references/`、`assets/`。
3. 编写核心指令：写清职责边界、编号步骤、输入输出规范、硬性约束。
4. 测试、调试与迭代：检查路径、YAML、触发效果与执行结果，必要时用 `claude --debug` 诊断。

## 关键概念

- [[Skill]]
- [[提示词工程]]
- [[MCP 模型上下文协议]]
- [[AI Agent 智能体]]
- Claude Code
- description 字段
- 渐进式披露

## 与其他素材的关联

- 与 [[2026-05-11-skill-sop-for-ai]] 形成互补：前者从 ACT-R 与程序性知识解释 Skill 本质，这篇则从文件结构、触发机制和工程化落地解释 Skill 怎么设计、怎么部署。
- 与 [[2026-05-11-claude-code-6-skills]] 可对照阅读：那篇更偏“装哪些 Skill、为什么装太多会降效”，这篇更偏“Skill 底层机制、文件结构与从零构建方法”。
- 与 [[2026-05-13-ai-agent-productivity-20x]] 互相补强：后者强调 Skill 在 Agent 系统中的复利角色，这篇补足了渐进式披露、YAML 元数据和资源目录这些工程实现细节。
- 可作为 [[AI编程开发]] 主题页中“自己制作 Skills（从 0 到 1）”和“跨 Agent 技能协议”部分的重要来源。

## 原文精彩摘录

> Skills，简单翻译过来就是“技能包”的意思。就像我们人一样，有很多的技能，比如骑车、游泳、开车、烹饪、摄影等。Skills，就是我们人类专门给AI准备的技能包。

> Description的首要任务不是给人看的，而是给AI的路由机制看的。它需要明确回答两个问题：1. 这个skill是做什么的？(功能定义) 2. 用户在什么场景/说什么话时应该使用它？(触发条件)

> Skills的设计非常聪明：平时绝不占用脑容量，只在需要时占用。你写好的几十个Skills，就像存放在书架上的工具书。Claude Code平时不去翻它们，只有当你触发了“测试代码”的技能时，Claude Code才会翻出小抄，只把关于“如何测试”的那张纸加载进大脑。

## 相关页面

- [[Skill]]
- [[AI编程开发]]
- [[提示词工程]]
- [[MCP 模型上下文协议]]
- [[AI Agent 智能体]]
