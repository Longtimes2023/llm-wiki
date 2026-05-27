---
tags: [实体, 产品经理, Skill, Claude, 插件, PM工具]
created: 2026-05-26
updated: 2026-05-26
sources:
  - 2026-05-26-woshipm-pm-skills-claude
---

# PM Skills 插件包

> 面向产品经理的 Claude 插件化 Skill 集合，把 PRD、竞品分析、用户画像、功能优先级、SWOT、OKR 等高频 PM 工作映射为可安装、可命令调用的工作流。

## 简介

PM Skills 插件包是素材 [[2026-05-26-woshipm-pm-skills-claude]] 中介绍的一组产品经理专用 Claude 插件。它的核心价值不是让 Claude 直接替产品经理做最终决策，而是把产品经理日常高频、可流程化、容易被文档事务挤占的工作固化成可调用命令：需要写 PRD 时调用 `/pm-execution:create-prd`，需要做竞品分析时调用 `/pm-market-research:competitor-analysis`，需要做用户画像时调用 `/pm-market-research:user-personas`。

与单次 Prompt 的区别在于，PM Skills 插件包把方法论入口、场景边界和输出流程预先封装起来。产品经理不必每次从零描述“你是一名资深 PM，请帮我写一份 PRD”，而是通过命令进入一个更稳定的工作流，再围绕系统追问补充需求、约束和上下文。它更接近“给 Claude 安装一套 PM 工作台”，而不是“问 Claude 一个问题”。

## 关键信息

- **类型**：Claude 插件化 Skill 集合 / PM 工作流工具包
- **面向人群**：产品经理、AI 产品经理、需要频繁输出 PM 文档和分析框架的知识工作者
- **安装入口**：`claude plugin marketplace add phuryn/pm-skills`
- **主要包名**：`pm-toolkit`、`pm-product-strategy`、`pm-product-discovery`、`pm-market-research`、`pm-data-analytics`、`pm-marketing-growth`、`pm-go-to-market`、`pm-execution`
- **主要输出**：PRD、竞品分析、用户画像、功能优先级建议、SWOT、OKR、Markdown 文档
- **相关概念**：[[Skill]]、[[Product Manager Skills]]、[[AI产品经理工作流]]、提示词工程

## 核心特性

### 1. 从“写 Prompt”变成“调用 PM 命令”

PM Skills 插件包把产品经理的高频场景做成命令入口。命令的意义不只是少打一段提示词，而是把任务类型先分流：PRD 归入 execution，竞品分析和用户画像归入 market research，功能优先级归入 product discovery，SWOT 归入 product strategy，OKR 归入 execution。这个分流过程相当于先告诉 Claude “现在进入哪一种产品工作流”，减少模型在任务理解上的摇摆。

这种命令化入口也便于团队形成共同语言。比如团队约定“需求初稿先跑 `/pm-execution:create-prd`，再由 PM 人工补评测和边界”，就比每个人各写各的 Prompt 更容易复用和沉淀。它把个人提示词经验向团队级工作流推进了一步。

### 2. 八个插件包覆盖 PM 工作链条

素材给出的链式安装命令一次装入八个包：

```bash
claude plugin install pm-toolkit@pm-skills && claude plugin install pm-product-strategy@pm-skills && claude plugin install pm-product-discovery@pm-skills && claude plugin install pm-market-research@pm-skills && claude plugin install pm-data-analytics@pm-skills && claude plugin install pm-marketing-growth@pm-skills && claude plugin install pm-go-to-market@pm-skills && claude plugin install pm-execution@pm-skills
```

从命名看，这套包覆盖了 PM 从战略、发现、市场研究、数据分析、增长、GTM 到执行的多个环节。它不是单点“写 PRD 工具”，而是试图把 PM 的一组常见工作流打成套件。对 AI PM 来说，这类套件的价值在于让基础动作标准化，节省整理文档和搭框架的时间，把注意力留给业务判断、风险识别和跨部门推动。

### 3. Markdown 输出让结果进入文档流

素材特别提到最终会生成 `.md` 文档。这个细节使 PM Skills 插件包不只是聊天辅助，而是可以接入实际文档流：Markdown 可以放进知识库、Git 仓库、Obsidian、团队文档或后续编译展示工具中。相比复制聊天记录，Markdown 更适合版本管理、评审和持续迭代。

这也和 [[AI产品经理工作流]] 中反复出现的“AI 做 80% 事务性工作，人做 20% 判断”一致：AI 先把框架和初稿变成文件，人再在文件上补充业务事实、删掉不成立假设、标注风险和确认优先级。

## 不同素材中的观点

- **[[2026-05-26-woshipm-pm-skills-claude]]**：这篇素材提供了 PM Skills 插件包的安装和调用实操。作者强调不要把 Claude 当成“万能的、什么都不用管”的替身，而是把 PM 的完整工作流程复制进去，用命令化 Skill 处理琐碎文档和框架搭建。文章列出 marketplace 添加命令、八个包的一键安装命令、`claude plugin list` 验证命令，以及六个高频场景命令表。最值得保留的观点是：PRD 生成效果取决于系统追问和 PM 对问题的打磨，命令只是入口，真正让文档“写到心里”的仍然是对需求上下文的准确补充。

## 实用信息

### 安装步骤

1. 添加 marketplace：

```bash
claude plugin marketplace add phuryn/pm-skills
```

2. 安装常用 PM 插件包：

```bash
claude plugin install pm-toolkit@pm-skills && claude plugin install pm-product-strategy@pm-skills && claude plugin install pm-product-discovery@pm-skills && claude plugin install pm-market-research@pm-skills && claude plugin install pm-data-analytics@pm-skills && claude plugin install pm-marketing-growth@pm-skills && claude plugin install pm-go-to-market@pm-skills && claude plugin install pm-execution@pm-skills
```

3. 验证安装：

```bash
claude plugin list
```

### 高频命令

| 场景 | 命令 | 使用边界 |
|------|------|----------|
| 撰写 PRD | `/pm-execution:create-prd` | 适合生成结构化初稿；业务目标、风险和验收标准仍需 PM 补充 |
| 竞品分析 | `/pm-market-research:competitor-analysis` | 适合搭框架和收集维度；差异化洞察不能直接照收 |
| 用户画像 | `/pm-market-research:user-personas` | 适合生成假设画像；必须用真实用户数据或调研校准 |
| 功能优先级 | `/pm-product-discovery:prioritize-features` | 适合形成讨论基准；老板要求、资源约束和战略取舍需要人工确认 |
| SWOT 分析 | `/pm-product-strategy:swot-analysis` | 适合早期战略梳理；注意避免套话和泛泛而谈 |
| OKR 制定 | `/pm-execution:brainstorm-okrs` | 适合头脑风暴；最终 OKR 要回到业务北极星和团队承诺 |

### 注意事项

1. **不要把命令当决策器**：插件包负责执行流程，产品经理负责判断。PRD 是否成立、竞品洞察是否有用、用户画像是否真实，都不能只靠模型输出。
2. **多花时间回答追问**：作者强调“这些提示是它能否写到你心里的关键要素”。这说明 PM Skills 的质量上限由输入质量决定，尤其是背景、目标、约束、用户场景和验收标准。
3. **把输出纳入文件流**：既然插件会生成 `.md` 文档，就应把它作为可迭代文件继续维护，而不是停留在一次性对话。
4. **与自定义 Skill 互补**：通用插件包适合覆盖常见 PM 场景；当团队有行业特定流程、内部字段、审批链路或风控要求时，仍需要基于 [[Skill]] 方法论继续定制。

## 与相关概念的区别

- 与 [[Product Manager Skills]]：Product Manager Skills 更偏“PM 方法论库/工作分解”的长期知识资产，PM Skills 插件包更偏“安装到 Claude 后直接调用”的工具分发形态。两者都在推动 PM 方法论技能化，但一个强调库和体系，一个强调插件和命令。
- 与 [[Skill]]：Skill 是更上层的通用概念，PM Skills 插件包是 Skill 在产品经理职业场景中的具体实现。
- 与普通提示词：普通 Prompt 是一次性文本，PM Skills 插件包把触发入口、流程和输出格式持久化，减少每次重新表达任务的成本。

## 相关页面

- [[2026-05-26-woshipm-pm-skills-claude]]
- [[Product Manager Skills]]
- [[Skill]]
- [[AI产品经理工作流]]
- [[2026-05-13-ai-pm-requirement-scheduling]]
- [[2026-05-21-agent-skills-woshipm]]
