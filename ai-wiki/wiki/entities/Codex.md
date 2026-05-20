---
tags: [实体, 工具, AI, OpenAI, PPT, Skill, 运营素材, 自动化]
created: 2026-05-09
updated: 2026-05-10
sources: [2026-05-09-codex-visual-style-ppt, 2026-05-10-codex-canva-operations-assets, 2026-05-10-gpt-image-2-prompt-templates]
---

# Codex

> OpenAI 推出的任务执行型 AI 工具，支持安装自定义 Skill、批量生成带文本的高质量图片，也是运营素材自动化流水线的核心引擎——承担模板维护、数据生成、质检等全链路自动化角色；可直接调用 GPT-Image 2 生图无需 Skill，一分钟出封面图

## 简介

Codex 是 OpenAI 推出的 AI 任务执行工具，与传统的 AI 对话产品不同，它更侧重于"任务执行"——能够理解复杂的多步骤指令，安装和使用自定义 Skill，并批量完成包含文本内容的高质量图片生成。在 PPT 制作领域，Codex 的优势在于它能够同时处理文本内容生成（outline、prompts 文档）和图片生成（带精确文字的 PPT 页面），这是普通对话式 AI 工具难以做到的。

Codex 的 Skill 机制是其核心差异化能力。用户可以从 GitHub 安装社区开发的 Skill，也可以自己创建 Skill 来扩展 Codex 的能力。每个 Skill 本质上是一组预定义的工作流程和参数模板，让 Codex 在特定任务上表现更专业、更稳定。在视觉风格迁移 PPT 场景中，Codex + visual-style-ppt Skill 的组合目前被认为是最佳方案。

## 关键信息

- **类型**：工具
- **领域**：AI 任务执行 / 内容创作
- **官方网站**：https://openai.com
- **定价/开源状态**：需要 OpenAI 账户和付费额度
- **相关概念**：[[GPT Image 2]]、[[Canva]]、[[提示词工程]]

## 核心特性

- **Skill 安装与调用**：支持从 GitHub 链接直接安装 Skill，安装后可通过名称调用（如 `visual-style-ppt Skill`），也可以让 Codex 自动识别图片并调用对应 Skill
- **批量高质量带文本图片生成**：这是 Codex 相比其他平台的核心优势——能够理解并输出复杂文本内容，同时批量生成包含精确文字的高质量图片
- **直接调用 GPT-Image 2 生图**：无需额外 Skill，Codex 可直接调用 GPT-Image 2 生成图片，一分钟不到出封面图，替代了之前 Claude Code + Nano Banana 2 的又慢又不稳定方案
- **多文件协同输出**：可以同时生成 outline.md（内容大纲）、prompts.md（完整提示词）、图片、Style-used 文件等多个交付物，保持文件间的逻辑一致性
- **上下文理解与对话修改**：生成后支持选中内容"添加到对话"进行修改，也支持截图框选局部区域进行精准修改
- **运营素材流水线引擎**：在运营素材批量生产场景中，Codex 承担"自动化生产/代码执行/模板工程师"角色——从选题库读取数据、判断模板类型、填充6字段素材数据、生成 Canva brief/CSV、输出 HTML/SVG/React 模板代码、调用 [[Canva]] MCP/Autofill API 生成设计、执行质检规则，形成从选题到发布的完整自动化流水线
- **4套运营素材工作流**：①低门槛版（ChatGPT+Sheets+Canva Bulk Create）②半自动版（Codex+飞书多维表格+Canva+人工审核）③工程化版（Codex+Next.js/React+Tailwind+Playwright）④高级自动化版（Codex+Canva Autofill API/MCP+Zapier/Make）

### 工具类实体必填项

- **安装方式**：通过 OpenAI 平台使用 Codex；Skill 安装方式为将 GitHub 链接复制给 Codex 让其自动安装
- **基本用法**：1) 安装所需 Skill；2) 给出任务指令（如"提取这张图的风格 DNA"）；3) 提供文档/参考资料；4) 确认中间产物后继续生成；5) 或直接让 Codex 调用 GPT-Image 2 生成图片（无需 Skill）
- **关键参数/配置**：Skill 中的生产参数（页数、比例 16:9、输出类型、语言中文优先、文字密度低密度、是否需要日期/作者/Logo/水印）
- **适用场景**：需要高视觉品质的 PPT 制作、风格迁移类设计任务、需要批量生成带文本图片的场景、文章封面图生成。不适合需要可编辑文字 PPT 的场景（输出为图片版 PPTX）

## 不同素材中的观点

- **[[2026-05-09-codex-visual-style-ppt]]**：Codex 被认为是目前执行 visual-style-ppt Skill 的最佳平台，因为它"足够聪明，能够很好地理解并输出我需要的文本内容，还能批量完成极高质量的带有文本的图片"。替代方案包括 Lovart、LibTV、扣子（Coze），但 Codex 效果最佳。作者之前在 Coze 上做的 PPT 风格克隆技能操作困难且评分极低，转到 Codex 后效果大幅提升。

- **[[2026-05-10-codex-canva-operations-assets]]**：Codex 在运营素材批量生产场景中承担"自动化流水线引擎"角色，核心思路是不要让 Codex "自由发挥设计"，而是让它维护5-8套固定模板，根据选题判断用哪个模板并填充标题/副标题/标签/CTA/配图提示词。文章提出了4套递进工作流（低门槛→半自动→工程化→高级自动化），并提供了4个关键提示词模板（批量素材表生成、Canva Bulk Create CSV、HTML/SVG批量出图项目、素材质检）。Codex 与 [[Canva]] 的深度组合是运营素材自动化的最佳实践——Canva 负责可编辑设计生成，Codex 负责数据生成和流程编排。

- **[[2026-05-10-gpt-image-2-prompt-templates]]**：Codex 可直接调用 GPT-Image 2 生图，不再需要配合 Skill（之前用 Claude Code + Nano Banana 2 又慢又不稳定）。Codex + Obsidian 是公众号封面图最佳拍档：Codex 调用 Image 2 生成封面图，Obsidian 文章写完后自动填充封面图字段，一分钟不到出图。Codex 也是消费 Prompt-as-Code 工业级提示词模板的最佳 Agent——将 JSON/YAML 结构化模板给 Codex 学习，即可批量出提示词、批量出图一条龙。

## 实用信息

- **快速上手步骤**：
  1. 打开 Codex，将 Skill 的 GitHub 链接复制给它安装（如 https://github.com/irenerachel/visual-style-ppt-skill）
  2. 给它参考图或网页链接，让它提炼风格 DNA
  3. 提供文档内容，确认生成的 outline 和 prompts 文件
  4. 说"生成图片"或"继续"，先出多宫格再逐页输出
  5. 确认后说"打包"导出 PPTX
  6. 或直接让 Codex 调用 GPT-Image 2 生成图片（无需安装 Skill）

- **常用提示词/命令**：
  - "调用 visual-style-ppt Skill"
  - "提取这张图的风格 DNA"
  - "生成图片" / "继续"
  - "打包"
  - "帮我生成一张XX的XX图"（直接调用 GPT-Image 2 无需 Skill）

- **注意事项/避坑指南**：
  - 生成的 PPT 是图片版，打包后无法再修改文字，所有文字修改须在图片阶段完成
  - 使用多宫格策略时，先确认缩略图版式再逐页放大，不要跳过缩略图直接生成
  - 明确只用一个 Style source 和一个 Style Lock，避免混入多个风格导致不一致
  - Image 2 的人像和角色细节仍是弱项，人像相关需求考虑 Nano Banana Pro
  - 运营素材场景中，不要让 Codex "自由发挥设计"，而是固定模板让 Codex 填充
  - 提示词必须分两层：内容提示词（选题拆解）和设计提示词（视觉brief），不要混在一起
  - AI 出图最容易翻车的是复杂文字，关键文字应放在可编辑模板层而非让 AI 直接渲染
  - 素材需拆成6个标准字段（main_title/subtitle/badge_text/visual_direction/CTA/compliance_note）以支持批量化

## 相关页面

- [[GPT Image 2]]
- [[Canva]]
- [[AI创意设计]]
- [[提示词工程]]
