---
tags: [实体, 工具, AI编程, Anthropic, 终端工具, 平台]
type: entity
name: Claude Code
category: AI 编程工具
sources:
  - 2026-05-11-claude-code-6-skills
  - 2026-05-13-ai-agent-productivity-20x
  - 2026-05-20-agent-skills-intro-claude-opus
  - 2026-05-21-agent-skills-woshipm
  - 2026-05-26-woshipm-pm-skills-claude
  - 2026-05-27-juejin-claude-code-5-tools
  - 2026-05-27-woshipm-central-skill-symlink
  - 2026-05-27-woshipm-yunshu-skill-practical-guide
created: 2026-05-27
updated: 2026-05-27
---

# Claude Code

> Anthropic 出品的 AI 编程 Agent——已从"能在终端里写代码的 AI 工具"演进为承载 plugin/agent/hook/MCP server/LSP server 的开发平台

## 简介

Claude Code 是 Anthropic 推出的 AI 编程协作工具，最初的形态是"可以在终端里写代码的 AI 工具"——开发者在命令行里用自然语言描述需求，Claude 在本地工作目录中读文件、写代码、跑命令、修改代码。但 2026 年 3-5 月以来，掘金、沃垠 AI、深思圈等多个独立观察者都给出了同一个判断：**Claude Code 已经不是单个工具，开始长生态了**。原因是官方插件市场开始推一整套扩展形态——不光是 Skills，还有 `agents、hooks、MCP servers、LSP servers`。

这种形态转变的核心信号是：用户的注意力从"它能不能帮我写代码"转向"我需要给它装哪些扩展点"。Claude Code 的价值边界由用户自己组装的扩展集合决定，而不是单一模型能力。围绕它已经长出五类工具（工作流、可观测性、上下文工程、学习课程、协作集成），分别对应不同的痛点。这跟 VSCode 早期通过插件生态完成从编辑器到开发平台跃迁的路径几乎一致——同样是核心工具开放扩展点 → 社区涌入 → 出现头部插件 → 工具变平台。

Claude Code 在 Agent 生态里的特殊位置：它是 Skill 跨平台扩散的源头节点。2025-10-16 Anthropic 首次发布 Agent Skills 时仅限 Claude Code + Pro 付费用户，2025-12-18 把 Skills 作为统一标准对外开放后，Codex、Cursor、Antigravity、OpenCode、Trae、Qoder、CodeBuddy 等十余个 Coding Agent 都跟进支持。也就是说，**Claude Code 不仅自身是平台，还是定义 Agent 生态通用协议的事实标准制定者**。

## 关键信息

- **类型**：工具 / 平台
- **领域**：AI 编程 / Agent 开发 / Coding Assistant
- **官方网站**：https://claude.com/code（命令行工具，安装在本地终端）
- **定价**：付费订阅（Pro 订阅或 API 计费）
- **关键版本**：v1.0.80+（部分生态工具如 Claude HUD 的硬性最低要求）
- **扩展形态**：Skills / plugins / agents / hooks / MCP servers / LSP servers
- **相关概念**：[[Skill]]、[[Superpowers]]、[[Claude HUD]]、[[GET SHIT DONE]]、[[Learn Claude Code]]、[[Claude Code Action]]、[[上下文工程]]、[[MCP 模型上下文协议]]、[[AI Agent 智能体]]

## 核心特性

### 五类扩展点

Claude Code 在官方插件市场上推的扩展点已经从单一的 Skill 扩展到五类，每类解决一类问题：

| 扩展类型 | 解决什么 | 形态 |
|---------|---------|------|
| Skills | 程序性知识包（"会做某件事"） | SKILL.md + scripts/references/assets |
| plugins | 整套工作流 / 多 skill 组合 | 通过插件市场安装的复合扩展 |
| agents | 子代理 / 角色分工 | 调度其他 agent 的 agent |
| hooks | 事件触发点（如 PreToolUse / PostToolUse） | 在特定事件触发时执行的脚本 |
| MCP servers | 外部工具与数据源接入 | 通过 MCP 协议暴露能力 |
| LSP servers | 语言服务器（代码理解 / 跳转 / 补全） | 标准 LSP 协议 |

### 五个生态方向（按问题域切片）

围绕 Claude Code 已经长出的五个工具，刚好对应五个完全不同的方向：

| 方向 | 代表工具 | 解决的痛点 |
|------|---------|----------|
| 工作流 | [[Superpowers]]（100k+ stars） | "一上来就开写，写着写着需求就歪了" |
| 可观测性 | [[Claude HUD]] | "你根本不知道它现在到底在干嘛" |
| 上下文工程 | [[GET SHIT DONE]] | "用久了就变笨"——大模型上下文超了 |
| 学习门槛 | [[Learn Claude Code]]（34.2k stars） | 不知道从哪里入手的新用户 |
| 协作流程 | [[Claude Code Action]] | issue / PR / Review 等团队链路 |

### Claude Code 上下文资产体系

深思圈（[[2026-05-13-ai-agent-productivity-20x]]）和云舒（[[2026-05-27-woshipm-yunshu-skill-practical-guide]]）都强调，Claude Code 真正可迁移的核心资产是上下文层面的：**`agents.md` / `memory.md` / Skill / MCP**。这四个文件构成了一个 Agent harness 的可携带核心——换平台只需要带走这些，模型本体可以替换。本素材印证了这个判断：Anthropic 在产品形态上推的就是这四类资产的官方扩展点。

### 与同类工具的区别

- 与 Codex / Cursor 的关系：都是 Coding Agent，但 Claude Code 是 Skills 标准的源头节点。Codex / Cursor 后来跟进支持 Skills，本质上是把 Claude Code 的扩展协议引入自家平台。
- 与 GitHub Copilot 的关系：Copilot 是 IDE 内嵌补全 + Chat 形态，Claude Code 是终端 Agent 形态，主要场景是"让 AI 在工作目录里自主完成多步任务"，而不是"实时补全光标位置的代码"。

## 不同素材中的观点

- **[[2026-05-27-juejin-claude-code-5-tools]]**：程序员 Sunday 给出 Claude Code 形态转变的关键判断——"已经不是单个工具，开始长生态了"。围绕它已经长出五个工具（Superpowers / Claude HUD / GET SHIT DONE / Learn Claude Code / Claude Code Action），分别对应工作流、可观测性、上下文工程、学习门槛、协作流程五个完全不同的方向。文章的元结论是"Claude Code 正在从一个工具，慢慢长成一个平台"——这是 Claude Code 词条最重要的形态判断。

- **[[2026-05-11-claude-code-6-skills]]**：从 Claude Code 内部的 Skills 使用经验出发，指出 Skills 装太多会降触发准确率到 50% 以下，唯一筛选标准是"能不能替你每天省掉一步手动动作"。给出 6 个精选 Skill（Skill Creator / Planning with Files / Document & Presentation Skills + SEO Blog Writer / Newsletter Automation / Content Repurposer）。这是 Claude Code 单 Skill 形态的最佳实践视角。

- **[[2026-05-21-agent-skills-woshipm]]**：沃垠 AI 系统拆解 Claude Code 的 Skill 工程骨架——`SKILL.md + scripts/references/assets`，并讲清楚 description 字段如何影响触发、渐进式披露如何避免上下文爆炸。这是 Claude Code 单 Skill 工程实现层的最佳参考。

- **[[2026-05-20-agent-skills-intro-claude-opus]]**：沃垠 AI 的万字入门教程视角，从 2025-10-16 首发到 2025-12-18 开放标准的演进历史出发，讲 Skills 的三个核心"魔法机关"（YAML 元数据 / 渐进式披露 / 子代理召唤）。

- **[[2026-05-27-woshipm-central-skill-symlink]]**：从多 Agent 并用的视角看 Claude Code——它和 Codex / Cursor / Antigravity 等同时使用时会面临 Skill 碎片化问题，作者提出用软链接把所有 Agent 的 Skills 目录指向同一中央文件夹。这是 Claude Code 不再独占 Skills 协议后的横向资产管理视角。

- **[[2026-05-27-woshipm-yunshu-skill-practical-guide]]**：云舒在写了上百个 Claude Code Skill 后给出的实操作业法——"跑通→复盘→封装→回溯"四步，并指出 Agent 时代必须先跑通再封装的核心原因是任务复杂度涉及脚本、工具调用、subagent 分工，没法一次性设计完整。

## 实用信息

### 快速上手步骤

1. 安装：参考 Claude 官方文档（命令行工具，按操作系统下载）
2. 打开 Settings → Capabilities → Skills，启用 Skills 功能
3. 顺手开启 `skill-creator`（官方元技能，帮你创建其他 Skill）
4. 装 Claude HUD（如果 v1.0.80+），第一次能可视化 Claude 在干什么
5. 跑同一个任务 3 次以上，再用 Skill Creator 打包成自定义 Skill

### 常用提示词/命令

- 用 Skill Creator 打包流程：`"把我昨天手动跑的选题流程打包成 skill"`
- 调用已构建的 Skill：`"按照 SKILL.md 的流程执行"`
- 调试 Skill 未触发：`claude --debug` 查看加载日志

### 注意事项/避坑指南

1. **不要装太多 Skill**：装 30+ 个后触发准确率会掉到 50% 以下。官方建议持有 20-30 个，必须贴合自己工作流
2. **"Setup Porn" 陷阱**：花几小时配置一堆 Skill 但什么内容都没产出——拿配置当拖延借口。先手动跑同一任务 3 次以上，再让 Skill Creator 打包
3. **关注上下文腐烂**：用久了 Claude Code 会变笨，是因为上下文超了。装一个 GSD 类的上下文工程工具能显著缓解
4. **版本红线**：部分生态工具（如 Claude HUD）要求 Claude Code v1.0.80+，安装新工具前先升级
5. **多 Agent 时的 Skill 资产管理**：如果同时用 Claude Code / Codex / Cursor，考虑用中央 Skill 文件夹 + 软链接的方案，避免碎片化

## 相关页面

- [[Skill]]
- [[Superpowers]]
- [[Claude HUD]]
- [[GET SHIT DONE]]
- [[Learn Claude Code]]
- [[Claude Code Action]]
- [[上下文工程]]
- [[MCP 模型上下文协议]]
- [[AI Agent 智能体]]
- [[Codex]]
- [[Cursor]]
- [[GitHub Copilot]]
- [[AI编程开发]]
- [[2026-05-27-juejin-claude-code-5-tools]]
