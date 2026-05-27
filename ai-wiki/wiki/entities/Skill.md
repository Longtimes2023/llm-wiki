---
tags: [实体, 概念, AI协作, SOP, 程序性知识, 知识编译]
type: entity
name: Skill
category: 核心概念
sources:
  - 2026-05-11-skill-sop-for-ai
  - 2026-05-11-claude-code-6-skills
  - 2026-05-13-ai-pm-requirement-scheduling
  - 2026-05-13-ai-agent-productivity-20x
  - 2026-05-20-agent-skills-intro-claude-opus
  - 2026-05-21-agent-skills-woshipm
  - 2026-05-23-build-sop-personal-effectiveness
  - 2026-05-26-woshipm-pm-skills-claude
  - 2026-05-27-woshipm-central-skill-symlink
  - 2026-05-27-woshipm-ai-ecommerce-kol-agent
  - 2026-05-27-woshipm-yunshu-skill-practical-guide
created: 2026-05-11
updated: 2026-05-27
---

# Skill

> 写给 AI 的 SOP——将人的隐性经验编译为可复用的程序性知识包，让 AI 在约束内自主完成特定类任务

## 简介

Skill 是 AI 协作领域的一个核心概念，指的是将人的隐性经验（Know-how）编译为可复用的程序性知识包，让 AI 在约束内自主完成特定类任务。与 Prompt（临时表达意图）、知识库（持久存储事实）、Agent（完全自主决策）不同，Skill 占据了一个独特的位置——既是持久的，又是程序性的（Know-how），同时在编排上处于"人定约束、AI 灵活执行"的中间地带。

Skill 的理论基础来自认知心理学的 ACT-R 理论（Anderson, 1982）。该理论将知识分为陈述性知识（Know-what）和程序性知识（Know-how），人的学习过程就是从前者向后者的"知识编译"。Skill 做的事情是跳过反复练习，直接把编译好的程序性知识注入 AI——知识库让 AI「知道」，Skill 让 AI「会做」。

Skill 横跨 AI 协作系统的编排层和知识层：它包含知识文件（颜色规范、Token 速查表）、编排逻辑（5 步生成流程）和约束规则（踩坑教训），不是单纯的知识也不是单纯的流程，而是两者的结合。这种双重属性使 Skill 在 Prompt → 知识库 → Skill → Agent 的演进线中处于承上启下的关键位置。

## 关键信息

- **类型**：概念
- **领域**：AI 协作 / 知识工程 / 认知科学
- **理论支撑**：ACT-R 认知理论（Anderson, 1982）
- **核心区分**：知识库让 AI「知道」（Know-what），Skill 让 AI「会做」（Know-how）
- **相关概念**：[[提示词工程]]、[[AI Agent 智能体]]、[[Skills变现]]、[[MCP 模型上下文协议]]

## 核心特性

### 定义

Skill 的完整定义包含三个关键要素：

1. **隐性经验**：不是写在文档里的信息，而是脑子里说不出来但知道怎么做的东西——比如"拿到需求自然就知道该怎么画"的程序性知识
2. **编译**：跳过反复练习，直接把经验注入给 AI——人要靠反复练习才能完成知识编译，Skill 把编译结果直接交付
3. **约束内自主**：既不像 Workflow 那样把每一步写死（零判断空间），也不像 Agent 那样完全放手（全权决定）——在规范的护栏内给 AI 灵活发挥的空间

### 知识视角定位

| 概念 | 知识类型 | 持久性 | 说明 |
|------|---------|--------|------|
| Prompt | 偏 Know-how（表达意图） | 临时 | 一句咒语，会话结束消失 |
| Context | Know-what | 临时 | 信息窗口，有限上下文 |
| 知识库 | Know-what | 持久 | 给你一本书，长期存储事实 |
| Memory | 偏 Know-what（偏好记录） | 持久 | 用户偏好和习惯 |
| **Skill** | **Know-how** | **持久** | **给你一项技能，编译好的程序性知识** |

Skill 占据右上角——既是持久的，又是 Know-how 的。编译好的程序性知识不会随会话消失。

### 编排视角定位

| 概念 | 编排者 | 判断空间 | 说明 |
|------|--------|---------|------|
| Workflow | 人 | 零（全部写死） | 人用代码写死每一步，机器执行 |
| **Skill** | **人定约束，AI 执行** | **中间** | **人在护栏内给 AI 灵活空间** |
| Agent | AI | 全部（完全自主） | AI 自己决定目标和步骤 |

Skill 的甜蜜点在于"约束内自主"——人定边界，AI 在边界内灵活执行。

### 架构分层

AI 协作系统从底层到顶层分五层：

1. **协议层**：MCP（模型上下文协议）
2. **工具层**：Tool（具体可调用的工具）
3. **上下文层**：Context（当前会话信息窗口）
4. **知识层**：Prompt / 知识库 / Memory
5. **编排层**：Workflow / **Skill** / Agent

Skill 特殊在横跨两层——知识层和编排层，这是它与其他概念的根本区别。

### 演进路径

AI 协作的分享形态正在沿一条清晰的线演进：

| 阶段 | 分享什么 | 比喻 | 传递深度 |
|------|---------|------|---------|
| 第一阶段 | Prompt | 教你一句咒语 | 显性知识，因人而异 |
| 第二阶段 | 知识库 | 给你一本书 | 持久的事实信息 |
| 第三阶段 | Skill | 给你一项技能 | 程序性知识，效果趋于一致 |
| 第四阶段 | Agent | 给你一个员工 | 完全自主的行动能力 |
| 未来 | Principle | 给你一个决策框架 | 元认知，知道该做什么 |
| 更远 | AI 角色 | 给你一个专业角色 | 一组 Skill + 决策框架 |

### Skill 的文件体系结构

一个成熟的 Skill 不是单文件，而是按职责拆分的文件体系（以 Figma 原型图 Skill 为例）：

| 文件 | 职责 | 类比 |
|------|------|------|
| SKILL.md | 总控文件，规定什么时候该做什么 | 大脑中的方法论 |
| design-style-guide.md | 视觉规范 | 设计手册 |
| figma-component-reference.md | 精确 Token 值 | 参数速查表 |
| figma-generation-guide.md | 5 步生成流程 | 操作规程 |
| lessons-learned.md | 踩坑教训（放 Memory 常驻） | 经验教训本 |

核心原则：不要把所有东西塞进一个文件，按职责拆分——方法论在脑子里，细节在手册里。

### Skill 构建四阶段

1. **直接上手试错**：不写规范直接让 AI 做，来回改五六轮。价值在于发现 AI 在哪犯错（如风格不对、数据编造、换行方式错误）
2. **从失败中提炼**：把反复出现的问题对应成规则——写 design-style-guide、做 Token 速查表、加约束条件
3. **组织成文件体系**：按职责拆分成独立文件，总控+规范+参数+流程+教训
4. **持续喂养**：每次新场景出问题立刻追加规则，越用越强

### Skill 构建 6 个技巧

1. **踩坑即沉淀**：AI 犯错后立刻说「帮我写进 lessons-learned」，同一错误不会犯第二次
2. **让 AI 自己找工具**：不替 AI 研究可用 API，直接告诉目标让它自己探索试错，省掉大量查文档时间
3. **先做一遍再提炼 Skill**：先让 AI 做真实任务，从过程中提炼固化部分。Skill 应从实践中生长，不是从想象中设计
4. **让 AI 帮你写 Skill**：对话中说「把刚才做的这些总结成规范文件」，用 AI 写 Skill 指导 AI 形成闭环
5. **用 Memory 做热补丁**：小教训先写 Memory，积累到一定量再整合进 Skill 正式文件。Memory 是 Skill 的草稿箱和快速迭代通道
6. **分享意图而非指令**：告诉「为什么这样做」比「做步骤1、步骤2」更鲁棒。约束目标和边界，把路径交给 AI——这就是 Skill 和 Workflow 的根本区别

### Skill 作业流程的四步法：跑通→复盘→封装→回溯

来源：[[2026-05-27-woshipm-yunshu-skill-practical-guide]]

作者云舒在写了上百个 Skill 后总结的"最核心一条经验"——**不要一开始就设计 Skill，先跑通再封装**。这与"先做一遍再提炼 Skill"的方向一致，但提供了更具体的四步作业流程：

| 阶段 | 关键动作 | 容易踩的坑 |
|------|---------|-----------|
| 1. 跑通 | 和 AI 定好目标 → 把真实场景跑出来（不需完美） | 追求一开始就完美，反而跑不通 |
| 2. 复盘 | 和 AI 讨论：哪些是正向流程 / 哪些是负向流程 / 哪些内容应该沉淀 | 跳过这一步直接封装，等于凭想象做产品 |
| 3. 封装 | 让 AI 基于复盘结果进行 Skill 封装 | 不让 AI 写，自己手写 Skill 容易脱离真实经验 |
| 4. 回溯 | 开新对话测试稳定性，不稳定就定位问题 | 不做回溯，永远不知道 Skill 是不是真的能复用 |

**关键判断**：Agent 作业逻辑下任务复杂度明显变高（涉及脚本、工具调用、文件读取、subagent 分工），很多流程很难在一开始就完整设计出来。Prompt 时代可以"先设计再验证"（Chatbot 多轮对话相对简单），Agent 时代必须"先跑通再提炼"——试错成本最低，测试成本也大幅降低。

### Skill 的三层渐进式加载结构

来源：[[2026-05-27-woshipm-yunshu-skill-practical-guide]]

Agent 调用 Skill 不是一上来就把全部内容塞给模型，而是分多层级渐进式加载：

| 层级 | 内容 | 加载时机 | 作用 |
|------|------|---------|------|
| 第一层 | name + description | 一次对话中加载所有 Skill 的描述 | 触发判断（用哪个 Skill） |
| 第二层 | SKILL.md | 模型决定调用某 Skill 后才读取 | 主流程指引 |
| 第三层 | references / scripts / assets | 主流程各阶段按需调用 | 补充能力 |

**一句话总结**：name 和 description 负责触发，SKILL.md 负责主流程，参考资料负责在复杂场景下补充能力。关键不是目录看起来多完整，而是每一层都要服务于模型的真实作业流程。

这与 [[2026-05-21-agent-skills-woshipm]] 给出的"`SKILL.md + scripts/references/assets`"工程骨架完全吻合，但视角不同——沃垠从工程实现层讲文件结构是什么，云舒从作业机理讲这套结构如何被 Agent 实际调用。**两者形成"骨架 + 运行时"双视角**。

### Skill 的产品式迭代：围绕两个维度优化

来源：[[2026-05-27-woshipm-yunshu-skill-practical-guide]]

Skill 不是一次做完美，必须像产品一样迭代。每次优化前问自己两个问题：

1. **这个 Skill 根本上要做的问题是什么？**（边界守护——不要做着做着过界）
2. **当前 Skill 做的不好的点是什么？**（焦点守护——这次只解决一个最明显的问题）

**真实案例 1：多视角深度分析 Skill 演进**

| 版本 | 解决的问题 | 关键改动 |
|------|-----------|---------|
| 1.0 | 跑通 | subagent 自由选择视角对内容评估 |
| 2.0 | 视角稳定性 | 给每个 subagent 派单增加语料库，标准化判断逻辑 |
| 3.0 | 视角数量不够 | 5 个顾问 → 筛选扩到 10 个 |
| 不做 4.0（万能化） | 边界守护 | 新需求另开「设计 Skill」「debug Skill」，每个 Skill 对应明确场景 |

**真实案例 2：PPT Skill 演进**

| 版本 | 解决的问题 | 效果 |
|------|-----------|------|
| 1.0 | 能不能做 | 60 分 |
| 2.0 | 样式丰富度（增加底板和参考样式） | 65 分 |
| 3.0 | 内容适配（引入 subagent 设计逻辑） | 不只是套模板 |
| 4.0 | 减少人干预 | AI 更自主作业 |

**规律**：每个版本只解决一个当下最明显的问题，不要一开始追求完美。Skill 优化和产品迭代很像。这与 Jo斯达的 PM Skill 边界规则（[[2026-05-13-ai-pm-requirement-scheduling]]）一致——成熟 Skill 必须有清晰边界，不要做成万能工具。

### Skill 的元方法论：能不能做 = 能不能建立回溯验证机制

来源：[[2026-05-27-woshipm-yunshu-skill-practical-guide]]

Skill 本质是"人把一件事 SOP 化的能力"。云舒进一步把场景分成两类，给出可操作的判断模型：

| 场景类型 | 写 Skill 的核心动作 | 难点 | 真实案例 |
|---------|-----------------|------|---------|
| 熟悉领域 | 经验蒸馏：把脑子里"会做"的拆成 AI 能执行的流程 | 主要是"翻译"自己的隐性经验 | 作者已有的设计 Skill、写作 Skill |
| 不熟悉领域 | 建立回溯验证机制 | 难的不是让 AI 产出内容，而是判断它做的对不对 | 见下方两个对比案例 |

**两个不熟悉领域的对比案例**：

- **失败案例：六爻占卜 Skill**——场景看起来很适合 Skill 化（有规则、流程、参考资料），但作者不懂解卦、AI 也不懂，"我们俩加一起没办法构建一个可靠的回溯测试系统。我压根不知道解卦到底是准还是不准"，打磨半个月放弃。
- **成功案例：编程自动化测试 Skill**——作者也不是专业测试工程师，但可以让 AI 设计测试逻辑，通过回溯测试不断优化合理性，最后稳定运行后封装成 Skill。

**结论**：人不熟悉的领域不是一定做不出来 Skill，**核心是看能否通过回溯机制来验证**。这把"哪些场景能 Skill 化"从模糊感觉变成可决策的判断标准——是否存在可重复、可对错判断的反馈回路。

### Skills 生态发展历史与跨平台扩散

- **2025-10-16**：Anthropic 首次发布 Agent Skills，仅限 Claude Code + Pro 付费用户
- **2025-12-18**：Anthropic 把 Agent Skills 作为统一标准对外开放，无需付费用户身份
- **2025-12 至今**：Codex、Cursor、Antigravity、OpenCode、Trae、Qoder、CodeBuddy 等 Coding Agent 陆续支持；Claude Cowork、Skywork、MiniMax Agent、扣子等桌面 Agent 跟进；OpenClaw（龙虾）、Hermes Agent（爱马仕）等新兴 Agent 原生支持

这说明 Skills 已从 Anthropic 专有特性演进为 **Agent 生态的跨平台通用协议**——类比 npm 之于 Node.js，一个 Skill 可以在不同 Agent 上复用。

### description 字段：触发即正义

description 是 Agent 判断是否调用该 Skill 的**唯一依据**，其质量直接决定触发成败。

**黄金结构公式**：`[一句话核心功能] + [具体执行动作] + [明确的触发关键词/场景]`

```yaml
# 好的写法示例
name: security-code-review
description: >
  Reviews code for security vulnerabilities and best practices.
  Use when the user asks to "review code", "check for bugs", "analyze security",
  or mentions SQL injection, XSS, or performance bottlenecks.
```

**写法注意事项**：
1. 用省略第二人称的**祈使句**（"把用户上传的文字生成 HTML"，而非"你帮我把这段文字生成 HTML"）
2. 字数不超过 500 字（YAML 支持最多 1024 字符）
3. 模拟用户的提问方式，把关键词塞进 description

**调试方法**：Skill 未被触发时，90% 的原因是 description 不够具体。运行 `claude --debug` 查看加载日志诊断问题。——来源：[[2026-05-20-agent-skills-intro-claude-opus]]

### Skill 质量阈值：约束 + 示例 = 60% 稳定性提升

Anthropic 内部团队经验（来源：[[2026-05-20-agent-skills-intro-claude-opus]]）：

> 包含至少 **3 条明确约束** 和 **1 个输出示例** 的 Skill，其结果的稳定性可提升 60%。

约束使用绝对化词汇：**必须**、**严禁**、**总是**、**绝不**。输出示例给出预期格式和实际内容，而非只描述格式。

### Skill 选择策略：装太多反而降效

Skill 的渐进式披露机制是核心优势——不用时不占上下文，用时才拉全文。但这个机制有一个隐性代价：**Skill 装太多会降低触发准确率**。Claude 需要扫描所有 Skill 的描述来决定用哪个，描述一多就开始乱猜，准确率直接掉到 50% 以下。官方建议合理持有量 20-30 个，且必须贴合自己工作流。

**唯一筛选标准**：它能不能替你每天省掉一步手动动作？答不上来就不装，比任何评分都管用。别人的"必装 Top 30"不能抄，因为别人的工作流不等于你的。

**"Setup Porn"陷阱**：花好几个小时配一堆 Skill 结果什么内容都没产出，本质是拿配置当拖延借口。正确做法是手动跑同一任务 3 次以上，再让 Skill Creator 帮你打包，不要反过来。——来源：[[2026-05-11-claude-code-6-skills]]

### Claude Code 精选 Skill 推荐（6 个）

经过 30+ 个 Skill 两个月实测，按"能不能替我每天省掉一步手动动作"筛出的 6 个：

**通用 3 个（不管写博客还是跑项目都用得上）**：

| Skill | 类型 | 核心价值 | 典型场景 |
|-------|------|---------|---------|
| Skill Creator | 官方元技能 | 主动问你流程怎么跑，帮你写 SKILL.md + 生成测试用例 | "把我昨天手动跑的选题流程打包成 skill" |
| Planning with Files | 社区（13,410 Stars，生态最高） | 强制 Claude 先写 task_plan.md，每两步更新 findings.md / progress.md | 写长文/长代码写到后面忘开头 |
| Document & Presentation Skills | 官方全家桶 | PDF/Word/Excel/PPT 一句话转换 | 23 页 PDF → 10 页品牌色 Slide |

**创作 3 个（每天写东西绕不开）**：

| Skill | 类型 | 核心价值 | 典型场景 |
|-------|------|---------|---------|
| SEO Blog Writer & Lead Magnet | 社区 | 三合一：关键词研究 + SEO 长文 + 11 页 PDF 引流手册 | 把邮件诱饵从"下次再做"变"顺手就做" |
| Newsletter Automation | 社区 | 全链路：Perplexity 采编 → HTML 排版 → Gmail 草稿箱 | 独立 Newsletter 从 1-2 小时砍到 10 分钟审稿 |
| Content Repurposer | 社区 | 读你历史帖子抓语气特征，并行生成 Twitter/LinkedIn/Newsletter | 多平台分发从半小时压到一分钟 |

**按场景选 Skill**：
- 每天在 Claude 里反复跑同一串动作 → 先装 Skill Creator
- 写长内容经常写到后半段忘了开头设定 → 装 Planning with Files
- 写博客/公众号想一份长稿出多平台 → 装 Content Repurposer
- 刚点进 Claude Code → Settings → Capabilities → Skills 打开，顺手开 skill-creator

——来源：[[2026-05-11-claude-code-6-skills]]

### 下一步演进：Principle（决策框架）

沿 ACT-R 继续推演，程序性知识之后是元认知：

- Skill 解决「怎么做某件事」（程序性知识）
- Principle 解决「怎么判断该做哪件事」（元认知/决策框架）
- 比方：Skill 是厨师会做红烧肉，Principle 是厨师知道今天该做什么菜——要看食材、看客人、看场合

已经出现的 SkillHub、ClawHub 等 Skill 集市对应 App Store 早期（单个能力分发）。Principle 成熟后会出现「AI 角色市场」——装载不再是个体技能而是完整专业角色（如产品设计师角色自带画原型+写PRD+竞品分析等一组 Skill 和决策框架）。

### PM 工作流 Skill：需求拆解与智能排期

需求拆解和智能排期是 Skill 在产品经理日常中的典型落地形态。它们不是让 AI 完全替 PM 决策，而是把 PM 脑子里的 checklist、异常场景库、关键路径、排序规则和文件写回约束编译成可执行流程。

需求拆解 Skill 的输入是客户成功、销售或业务方给出的自然语言需求，输出是开发可直接使用的 Feature、Story 和 Gherkin 验收场景。它会先抽取用户角色、核心目标、关键场景、非功能需求、约束条件，再按 SaaS 模块（租户管理、用户与权限、订阅计费、产品配置、运营后台）归类；每个 Story 至少生成 1 个正向场景和 1 个异常场景。真正有价值的不是“帮你写文档”，而是强制每个需求先回答类似 5W2H 的问题，把模糊成本前置暴露出来。

这类 Skill 还需要适配真实工作流：继承模式允许基于 STORY-008 生成 STORY-012，而不覆盖旧 Story；异常场景库会提示权限变更、并发修改等容易遗漏的边界；关键路径校验会扫描租户开通、用户加入、订阅变更、计费计量、跨租户数据隔离等 SaaS 核心链路是否断档。这体现了 Skill 与普通 Prompt 的差异：Prompt 只表达一次意图，Skill 则把组织反复踩过的坑沉淀为持续生效的护栏。

智能排期 Skill 则把 Story 清单到迭代计划的过程结构化。它读取 `stories.md` 中“已确认但优先级为空”的 Story，用“业务价值 × 0.4 + (1 – 实现成本/10) × 0.2 + (10 – 风险等级) × 0.1 + 用户影响范围 × 0.3”计算默认分数，再解析依赖关系构建依赖图，保证被依赖 Story 排在依赖它的 Story 前面。同层 Story 按得分排序，未确认的依赖项跳过并提示，循环依赖（如 STORY-001 → STORY-003 → STORY-001）直接警告人工检查。最后只有在 PM 确认后，才把分数和“已排期”状态写回文件。

这个案例说明，成熟 Skill 的边界必须写清楚：需求拆解 Skill 不排优先级、不做变更管理、不设计技术方案；智能排期 Skill 不写代码、不分配具体开发人员、不做跨项目资源协调。它们只是“外挂大脑”，自动化繁琐的澄清、校验、算分和依赖解析；真正的大脑仍然是承担业务判断和责任的产品经理。——来源：[[2026-05-13-ai-pm-requirement-scheduling]]

### PM Skills 插件化分发：从方法论文件到可安装工作台

[[2026-05-26-woshipm-pm-skills-claude]] 展示了 Skill 在产品经理职业场景中的另一个演进方向：不是每个 PM 都从零写 `SKILL.md`，而是通过 marketplace 安装已经打包好的 [[PM Skills 插件包]]。素材中的命令先添加 `phuryn/pm-skills` marketplace，再安装 strategy、discovery、market research、data analytics、marketing growth、go-to-market、execution 等多个 PM 插件包，把 PRD、竞品分析、用户画像、功能优先级、SWOT、OKR 等任务变成 `/pm-*` 命令。

这个案例说明 Skill 已经从“单个能力文件”进入“职业工作台”形态：多个 Skill 按 PM 工作链条组织，用户通过命令选择具体工作流。它降低了启动成本，但不改变 Skill 的基本边界——Claude 可以复制完整工作流程、生成 Markdown 文档和提出关键问题，产品经理仍必须补充真实需求、判断哪些问题关键、验收输出是否符合业务目标。换句话说，插件化分发让 Skill 更容易安装，不能让 PM 的判断责任消失。

## 不同素材中的观点

- **[[2026-05-21-agent-skills-woshipm]]**：沃垠AI 的人人都是产品经理长文，从工程实现层面对 Agent Skills 做了一次完整拆解：先用“给 AI 的员工手册”类比解释 Skill 的定位，再系统梳理标准文件夹结构 `SKILL.md + scripts/references/assets`、description 字段的路由作用、渐进式披露如何避免上下文爆炸，以及 Skill 与 Prompt、MCP、Agent、Projects 的分层差异。文章还用“HTML 信息图生成器”案例演示了从单一职责定义、YAML 元数据、Markdown 指令到参考设计指南的完整制作流程，并补充了官方/社区 Skill 来源、安装方式和 4 阶段测试迭代框架，适合作为 Skill 工程化落地的操作手册。

- **[[2026-05-20-agent-skills-intro-claude-opus]]**：沃垠AI 的万字实操入门教程，从 Skills 的历史（2025-10-16 Anthropic 首发，2025-12-18 开放标准，Codex/Cursor/OpenClaw/Hermes 等十余个 Agent 全面跟进）出发，重点讲解三个核心"魔法机关"：YAML 元数据（智能开关）、渐进式披露（随用随取的小抄）、子代理召唤（影分身机制）。给出 description 字段的黄金结构公式 `[功能] + [执行动作] + [触发关键词]`，以及含 3 条约束 + 1 个输出示例可使稳定性提升 60% 的 Anthropic 内部数据。以 HTML 信息图生成器为手把手案例，覆盖命名规范、文件结构设计、设计规范细节、HTML/CSS 输出要求的完整实践。

- **[[2026-05-11-skill-sop-for-ai]]**：冰冰酱基于 ACT-R 认知理论系统定义了 Skill 的本质——将隐性经验编译为可复用程序性知识包。通过两张象限图（知识视角：Know-what/Know-how × 临时/持久；编排视角：写死/自主 × 人/AI）精准定位了 Skill 在 AI 协作体系中的位置。以 Figma 原型图 Skill 为实战案例展示了四阶段构建过程（试错→提炼→组织→持续喂养）和 6 个构建技巧（踩坑即沉淀、让 AI 自己找工具、先做再提炼、AI 写 Skill、Memory 热补丁、分享意图非指令）。提出演进路径：Prompt→知识库→Skill→Agent→Principle→AI角色市场。

- **[[2026-05-11-claude-code-6-skills]]**：掘金作者实战筛选 Claude Code Skill 的经验——装 30+ 个 Skill 两个月后只留 6 个。核心洞察：装太多 Skill 会降低触发准确率到 50% 以下（Claude 扫描所有描述决定用哪个，描述一多就乱猜）。提出唯一筛选标准"能不能替我每天省掉一步手动动作"和"Setup Porn"陷阱概念（拿配置当拖延借口）。推荐 6 个精选 Skill：通用类（Skill Creator 元技能 / Planning with Files 长文规划 13,410 Stars / Document & Presentation Skills 官方全家桶），创作类（SEO Blog Writer 三合一 / Newsletter Automation 全链路 / Content Repurposer 语气感知多平台分发）。

- **[[2026-05-13-ai-pm-requirement-scheduling]]**：Jo斯达展示了 Skill 在产品经理需求管理中的具体落地：一个需求拆解 Skill 将客户成功/销售的自然语言需求转成 Feature、Story 和 Gherkin 验收场景，并通过继承模式、异常场景库、SaaS 关键路径校验适配真实敏捷流程；另一个智能排期 Skill 读取 stories.md，按业务价值、实现成本、风险等级、用户影响范围打分，结合依赖图排序，只处理“已确认”的 Story，并在用户确认后写回优先级和“已排期”状态。这个案例强调 Skill 是“外挂大脑”而非替代 PM 判断，自动化的是 checklist、算分和依赖解析，最终决策仍由人负责。

- **[[2026-05-13-ai-agent-productivity-20x]]**：深思圈把 Skill 放进更完整的 Agent 系统里讨论，强调 Skill 的本质是“写给 AI 的 SOP”，是整个体系里复利最强的一层。它的重要性不在单次 prompt 更漂亮，而在把提案格式、广告分析、晨间简报、播客嘉宾研究等可重复流程打包为可调用能力，再与上下文、记忆、MCP 和定时调度串联，形成会持续运行的自主工作流。文章还给出两种高复用的构建方式：基于课程/流程文档直接生成 Skill，或先与 Agent 手动跑完真实流程，再把结果提炼成 Skill。

- **[[2026-05-20-self-as-product-sop]]**：这篇文章虽然讨论的是“自我产品化”，但其核心写法本质上也是 Skill 思维在个人成长场景的投射：把产品经理对自己的成长管理从零散灵感升级为可执行 SOP，用立项评审、PPRD、Backlog、Sprint、Dashboard 和定期复盘把隐性的成长经验编译成持续可复用的流程。它说明 Skill 并不只适用于 AI 协作或工具调用，也是一种更广义的“把 know-how 结构化、流程化、可持续迭代”的思维方式。

- **[[2026-05-23-build-sop-personal-effectiveness]]**：蔡锦海给出的"工作 SOP"是 Skill 概念的镜像投影——Skill 是写给 AI 的 SOP，工作 SOP（PDCA/5问/SCQA/重要紧急四象限）是写给人自己的 SOP。两者本质同源：把重复发生的工作场景编译成可调用的标准动作。差别只在编译载体（AI 文件 vs 大脑习惯）和执行者（AI 自主 vs 人主动）。这条线索很重要——它说明 Skill 思维不是 AI 时代独有，而是"能力强的人"沉淀经验的通用模式，AI 出现只是让这种沉淀第一次能被精确编译并直接注入另一个执行体。详见 [[工作SOP]]。

- **[[2026-05-26-woshipm-pm-skills-claude]]**：秀琴江湖飘介绍的 PM Skills 插件包把 Skill 从”可构建的流程文件”推进到”可安装的职业工作台”。它通过 `claude plugin marketplace add phuryn/pm-skills` 添加市场，再用 `claude plugin install` 一次安装八个 PM 包，并用 `/pm-execution:create-prd`、`/pm-market-research:competitor-analysis` 等命令触发具体工作流。这篇素材的价值不在底层架构，而在用户视角：Skill 真正普及后，普通 PM 不一定先学习 YAML、description 和资源目录，而是先用命令调用别人打包好的流程；但作者提醒”别一上来就把他当成万能的”，说明 Skill 的边界仍是”流程辅助”，不是”责任转移”。

- **[[2026-05-27-woshipm-central-skill-symlink]]**：甜橙和亨亨从多 Agent 并用的真实痛点出发，提出”中央 Skill”方案——用软链接把所有 Agent 的 Skill 文件夹统一指向同一中央文件夹，实现 Single Source of Truth。操作上只需创建 SharedSkills 文件夹、删除各 Agent 原有 skills 目录、用 `ln -s` 创建软链接三步。这篇文章的独特贡献不在工程架构，而在两个更深层的洞察：(1) Skill 碎片化不只是操作不便，而是”逐渐不知道自己有什么 Skill——Skill 库变成自己都不信任的黑盒”，这是资产管理的失败；(2) 在模型快速迭代、工具不断演进的 AI 时代，Skill 是为数不多的确定性——“Skill 的价值曲线和 AI 的进化轨道是独立的，AI 越强，自己的方法论越能发挥更大的价值”。这两个观点将 Skill 从”可复用的程序性知识包”提升为”可积累、可增值的确定性资产”，为统一管理 Skill 提供了超越便利性的深层理由。

- **[[2026-05-27-woshipm-ai-ecommerce-kol-agent]]**：Elaine.H 的"达人帮你挑"电商 AI 导购 PRD 把 Skills 定位为 **"原子化执行单元"**，与 Agent 层形成严格分层关系——Agent 层是"全局唯一调度中枢"（具备自主决策与流程跳转能力），Skills 层是"无自主决策能力的执行手脚"，仅接收 Agent 下发的固定指令，完成单一闭环任务，输出标准化结果。关键规则：**技能之间无直接调用**，所有工具统一标准化入参出参格式，由 Agent 中枢统一调度；工具调用支持超时熔断、异常重试、降级兜底；调用结果必须可溯源、可审计、全程留痕。这种"大脑+手脚"的严格分层与本词条已有的"Workflow（写死）→ Skill（约束内自主）→ Agent（完全放手）"编排视角形成具体的工程落地——在企业级多技能 Agent 架构中，Skills 退化为"被调度的能力原子"，Agent 承担所有判断责任，从而保证海量 KOL 分身并行部署时的可控性和稳定性。这把 Skill 的"约束内自主"在企业级场景具体化为"接收指令、独立完成、标准输出"三件事，是 Skill 在大规模 Agent 系统中的标准位置。

- **[[2026-05-27-woshipm-yunshu-skill-practical-guide]]**：云舒（云舒的AI实践笔记）写了上百个 Skill 后总结的"实操作业手册"，从一线踩坑路径反推 Skill 工程的可复制做法。三个核心贡献：(1) **Skill ≠ 大号 Prompt** 的精确边界——最简单的 Skill 等价于 Prompt，但 Skill 在「调用方式」（多 Skill 描述预加载 + 模型自动选）和「承载复杂度」（可包含规则/参考文档/Python脚本/素材库，分阶段调用）两个维度上突破了 Prompt 的天花板，这与 [[提示词工程]] 词条 "Prompt→Skill 演进" 形成具体的工程化差异说明。(2) **"先跑通再封装"四步作业法**（跑通→复盘→封装→回溯）+ Agent 时代必须先跑通的原因（任务复杂度涉及脚本、工具调用、subagent 分工，没法一次性设计）—— 这是冰冰酱 [[2026-05-11-skill-sop-for-ai]] "先做再提炼"原则的最具体实操化。(3) **三层渐进式加载机制**（name+description 触发 → SKILL.md 主流程 → references/scripts/assets 按需）+ **熟悉/不熟悉领域的元判断模型**——熟悉领域走经验蒸馏，不熟悉领域看能否建立回溯验证机制（六爻占卜失败 vs 编程自动化测试成功的对比，把"哪些场景能 Skill 化"从模糊感觉变成可决策的判断标准）。同时用多视角深度分析 Skill 1.0→3.0 + PPT Skill 1.0→4.0 两个真实演进案例佐证"像做产品一样迭代"的方法论。

## 实用信息

### 快速上手步骤

1. 找一个你经常让 AI 做的任务（如画原型图、写文案、做数据分析）
2. 不写规范，直接让 AI 做一遍，记录它犯错的地方
3. 把反复出现的错误写成规则文件（如 design-style-guide.md）
4. 组织成 SKILL.md 总控 + 各职责文件的体系
5. 每次踩坑立刻追加规则（或先写 Memory 再整合）

### 常用提示词/命令

Skill 构建过程中的关键指令：
> 「帮我写进 lessons-learned」— 踩坑后立刻沉淀
> 「把刚才做的这些总结成规范文件」— 让 AI 写 Skill
> 「按照 SKILL.md 的流程执行」— 调用已构建的 Skill

### 注意事项/避坑指南

1. **不要一开始就写完美的 Skill**：先做再提炼，从实践中生长而非想象中设计
2. **不要把所有东西塞进一个文件**：按职责拆分，方法论在脑子里，细节在手册里
3. **不要写死每一步操作**：分享意图而非指令，约束目标和边界，把路径交给 AI——这是 Skill 和 Workflow 的根本区别
4. **不要忽略踩坑的价值**：每个错误都是一条新规则，踩坑即沉淀
6. **PM 需求管理类 Skill 适合拆成两段**：先用需求拆解 Skill 输出 Feature/Story/Gherkin 和异常场景，再用智能排期 Skill 按分数与依赖关系给出迭代候选。不要让同一个 Skill 同时承担需求澄清、技术方案、资源分配和变更管理，否则边界会失控
7. **通用插件包适合起步，深度业务仍需定制**：[[PM Skills 插件包]] 能快速覆盖 PRD、竞品分析、用户画像、SWOT、OKR 等通用 PM 场景，但行业术语、内部审批链路、评测红线和团队文档格式仍需要在实践中继续定制或二次封装

## 相关页面

- [[提示词工程]]
- [[AI Agent 智能体]]
- [[Skills变现]]
- [[MCP 模型上下文协议]]
- [[AI产品经理工作流]]
- [[PM Skills 插件包]]
- [[工作SOP]]
- [[自我产品化]]
- [[AI导购]]
- [[2026-05-26-woshipm-pm-skills-claude]]
- [[2026-05-27-woshipm-ai-ecommerce-kol-agent]]
- [[2026-05-27-woshipm-yunshu-skill-practical-guide]]
