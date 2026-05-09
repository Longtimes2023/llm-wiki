---
tags: [实体, 产品经理, PM方法论, 开源, AI技能]
created: 2026-05-09
updated: 2026-05-09
sources:
  - 2026-05-09-pm-ai-playbook
---

# Product Manager Skills

> Dean Peters 开发的开源PM方法论库，将PM工作分解为46个可复用的"技能"和6个完整工作流，可运行在AI Agent上

## 简介

Product Manager Skills 是一个开源的产品经理方法论库，由 Dean Peters 开发维护。它的核心理念是"把PM工作分解成可复用的技能，而不是靠经验和感觉"——这代表了一种新趋势：将传统依赖个人经验和直觉的PM工作，转化为可标准化、可传授、可AI执行的技能单元。

与 PM Skills Marketplace 类似，Product Manager Skills 也是将PM方法论编码为AI可执行的形式，但侧重点不同：PM Skills Marketplace 强调成熟框架的结构化引导，而 Product Manager Skills 更侧重于工作分解和技能化，将PM工作拆解为更细粒度的可复用单元。

该工具可运行在 Claude Code、OpenClaw 等AI Agent平台上，意味着产品经理可以在日常工作中随时调用这些技能来辅助决策。

## 关键信息

- **类型**：工具（开源PM方法论库）
- **领域**：产品管理 / AI辅助决策
- **开发者**：Dean Peters
- **官方网站/地址**：https://github.com/deanpeters/Product-Manager-Skills
- **定价/开源状态**：开源
- **相关概念**：PM Skills Marketplace、提示词工程、AI产品经理工作流

## 核心特性

### 技能体系构成

- **46个经过验证的PM技能**：分为 Component（组件型，可独立使用的单一技能）和 Interactive（交互型，需要多轮对话引导的复杂技能）两大类
- **6个工作流**：跨越多天的完整流程（如从需求发现到产品上线的端到端流程），每个工作流串联多个技能形成闭环
- **AI Agent兼容**：可运行在 Claude Code、OpenClaw 等主流AI Agent平台上

### 设计哲学

核心理念是把PM工作从"依赖个人经验和感觉"转变为"可复用的结构化技能"。这与传统PM培训的"师傅带徒弟"模式不同，更像是一种"PM工作的标准化和数字化"，让方法论不再是少数人的隐性知识，而是可被AI执行和传播的显性知识。

Component 类技能适合快速调用（如生成用户画像模板），Interactive 类技能适合深度引导（如通过多轮对话完成一个完整的用户研究设计）。

### 工具/模型类实体的必填项

- **安装方式**：从 GitHub 仓库 https://github.com/deanpeters/Product-Manager-Skills 获取，部署到 Claude Code 或 OpenClaw 等 AI Agent 环境
- **基本用法**：在 AI Agent 中加载技能包，通过自然语言调用特定技能或启动某个工作流
- **适用场景**：产品经理希望将PM工作标准化、可复用化时使用；适合需要多人协作、方法论传承的团队场景；也适合新手PM通过AI引导学习成熟方法论

## 不同素材中的观点

- **2026-05-09-pm-ai-playbook**：这篇素材将 Product Manager Skills 作为推荐工具介绍，强调其"把PM工作分解成可复用的技能而非靠经验和感觉"的核心理念，认为这种技能化趋势能让产品经理事半功倍。素材同时推荐了 PM Skills Marketplace，两者定位互补：PM Skills Marketplace 偏框架引导，Product Manager Skills 偏工作分解。

## 实用信息

- **快速上手步骤**：1) 访问 GitHub 仓库获取技能包；2) 在 Claude Code 或 OpenClaw 等 AI Agent 中安装；3) 按需调用46个技能中的任何一个，或启动6个工作流之一
- **注意事项/避坑指南**：技能化≠机械化，使用时需理解每个技能背后的方法论逻辑而非机械执行。46个技能覆盖面广但不代表每个都适用于你的具体场景，建议先聚焦与自己工作最相关的5-10个技能深入使用

## 相关页面

- [[PM Skills Marketplace]]
- [[AI产品经理工作流]]
- [[提示词工程]]
