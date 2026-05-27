---
tags: [素材摘要]
created: 2026-05-20
updated: 2026-05-23
source_type: 网页文章
source_path: raw/articles/2026-05-20-woshipm-6377843-tg-test.md
---

# 万字干货！Agent Skills从入门到精通

> Skills是2026年最值得学习的AI技能——给AI的"标准操作手册（SOP）"，让Agent从"职场小白"变成"开箱即用的老同事"。核心架构包括SKILL.md（核心指令）、scripts（代码）、references（参考文档）、assets（素材资源），通过"渐进式披露"避免上下文撑爆。

## 基本信息

- **来源类型**：网页文章（人人都是产品经理）
- **原文位置**：raw/articles/2026-05-20-woshipm-6377843-tg-test.md
- **原文 URL**：https://www.woshipm.com/share/6377843.html
- **作者**：沃垠AI
- **发表日期**：2026-04-15
- **消化日期**：2026-05-20
- **字数**：9623 字

## 核心观点

1. **Skills 是 2026 年 AI 领域最重要创新之一**：从 2025-10-16 Anthropic 首次发布，到 2025-12-18 开放为统一标准，到 Codex/Cursor/OpenClaw/Hermes 等十余个 Agent 生态全面跟进，不到半年已成跨平台通用协议

2. **Skills 与 Prompt/MCP/Agent 的本质区别**：Prompt 是现炒菜（临时意图），MCP 是物流系统（工具和数据），Skills 是预制菜（沉淀好的可重复执行标准流程）。Skills 的核心价值是省 Token + 提稳定性，做法预设好后 AI 只需被点菜名就能执行

3. **渐进式披露（Progressive Disclosure）是 Skills 最核心的设计哲学**：Skills 分三层加载，平时不占上下文，只在触发时拉取对应文件。数十个 Skill 存在书架上，只在需要时翻出对应一张纸——这解决了把所有文档一次塞进上下文撑爆的老问题

4. **description 字段质量决定触发成败**：90% skill 未被触发的原因是 description 写得不够具体。黄金结构：`[一句话核心功能] + [具体执行动作] + [明确的触发关键词/场景]`；写法要用省略第二人称的祈使句，不超过 500 字；可运行 `claude --debug` 查看加载日志

5. **包含 3 条约束 + 1 个输出示例的 Skill 稳定性可提升 60%**：Anthropic 内部团队经验——使用"必须""严禁""总是"等绝对化词汇，给出示例格式和预期输出，能显著降低结果随机性

6. **Skill Creator 是必装元技能**：GitHub 已超 80k star，帮你从自然语言需求直接生成 SKILL.md + 测试用例，把创建 Skill 的过程本身也 Skill 化

## 实操内容保留

### SKILL.md 标准文件结构

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter: name + description (必需)
│   └── Markdown instructions (必需)
└── Bundled Resources (可选)
    ├── scripts/    – 可执行代码 (Python, Bash等)
    ├── references/ – 参考文档 (技术规范/API文档/设计指南)
    └── assets/     – 素材资源 (模板/图片/字体)
```

### SKILL.md 内容模板

```yaml
---
name: your-skill-name          # 小写字母+连字符，不超过64字符
description: |                 # 最多1024字符，决定触发时机
  [一句话核心功能] + [执行动作] + [触发关键词/场景]
allowed-tools: Read, Grep      # 可选：白名单工具
---

# Skill标题
## 功能说明
为Claude提供清晰的分步操作指南（用编号列表，不用段落文字）
## 目标 / 职责边界
能做什么，绝对不能做什么
## 示例
输入输出格式示例
## 注意事项
硬性约束（必须/严禁/总是）+ 常见陷阱
```

### description 黄金写法示例

```yaml
# 代码审查技能
name: security-code-review
description: >
  Reviews code for security vulnerabilities and best practices.
  Use when the user asks to "review code", "check for bugs", "analyze security",
  or mentions specific issues like SQL injection, XSS, or performance bottlenecks.

# PDF处理技能
name: pdf-processor
description: >
  Extracts text, tables, and metadata from PDF files; merges or splits documents.
  Use when working with PDF files, converting PDFs to text, filling forms,
  or when the user uploads a PDF and asks for summary/extraction.
```

### 安装 Skill 的命令

```
帮我安装这个skill，仓库地址是：
https://github.com/anthropics/skills/tree/main/skills/skill-creator
```

### 调试命令

```bash
claude --debug   # 查看 Skill 加载详细日志，诊断触发失败原因
```

### HTML信息图生成器 Skill 完整示例

YAML 元数据：
```yaml
---
name: html-infographic-generator
description: >
  从用户文字中提炼核心关键点，生成Magazine Layout风格的深色主题HTML信息图网页。
  当用户需要将文字内容可视化、创建信息图、生成数据展示页面或制作图文混排页面时使用。
---
```

设计规范要点：
- 背景色 `#0a0a0a` 或 `#1a1a1a`，深色主题
- 中文超大粗体（60-120px），英文小号点缀（12-16px）
- 高亮色方案（单色透明度渐变）：青色 `rgba(0,255,255,0.8)`、洋红 `rgba(255,0,255,0.8)`、金色 `rgba(255,215,0,0.8)`
- 通过 CDN 加载 Font Awesome 或 Material Icons，禁止用 emoji 做主图标

## 关键概念

- **[[Skill]]**：Agent Skills 的核心——写给 AI 的标准操作手册（SOP）
- **[[AI Agent 智能体]]**：Agent 是 Skills 的宿主环境，几乎所有主流 Agent 都已支持 Skills
- **[[MCP 模型上下文协议]]**：与 Skills 互补——MCP 提供工具和数据连接，Skills 提供执行规范和流程

## 与其他素材的关联

- **[[2026-05-11-skill-sop-for-ai]]**：冰冰酱从认知心理学（ACT-R）角度系统定义 Skill 本质，本文是互补的实操入门视角
- **[[2026-05-11-claude-code-6-skills]]**：讲"装哪些 Skill"，本文讲"怎么做 Skill"，形成完整的用法 → 制作路径
- **[[2026-05-13-ai-agent-productivity-20x]]**：把 Skills 放进完整 Agent 系统里讨论，本文专注 Skill 本身的架构和制作
- **[[2026-05-18-woshipm-ai-agent-productivity]]**：同一作者沃垠AI 的另一篇，关注 Agent 生产力，本文聚焦 Skills 工程

## 原文精彩摘录

> 没有Skills的Agent，就像一位刚入职的新同事，你得培训，反复教他。而有了Skills的Agent，则更像是一位老同事，开箱即用，配合默契，非常靠谱。
>
> 现在，只是学会怎么"问"AI，其实已经有点不够了。更重要的一件事是，学会怎么"教"AI。把你重复做的工作、团队里的隐性知识、那些"只有老员工才知道"的操作细节，封装成一个又一个的.skill文件。它们会成为你最好的数字同事。不摸鱼，不抱怨，随叫随到，而且越用越顺手。

> Skills的设计非常聪明：平时绝不占用脑容量，只在需要时占用。你写好的几十个Skills，就像存放在书架上的工具书。Claude Code平时不去翻它们，只有当你触发了"测试代码"的技能时，Claude Code才会翻出小抄，只把关于"如何测试"的那张纸加载进大脑。内存省了，思路也无比清晰。

> Anthropic内部团队的经验表明，最有价值的内容是"常见陷阱"章节——应持续累积Agent的失败模式，让后来者可以直接绕坑。包含至少3条明确约束和1个输出示例的skill，其结果的稳定性可提升60%。
