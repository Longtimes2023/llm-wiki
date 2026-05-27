---
type: entity
name: MCP 模型上下文协议
category: 核心技术
tags: [MCP, Model Context Protocol, 工具调用, 标准化协议, Canva]
sources: [2026-04-29-yupi-ai-guide-core-concepts, 2026-04-29-yupi-ai-guide-programming-tech, 2026-05-10-codex-canva-operations-assets, 2026-05-13-ai-agent-productivity-20x, 2026-05-18-ai-agent-week-into-day]
created: 2026-04-29
updated: 2026-05-24
---

# MCP 模型上下文协议

> Model Context Protocol，AI 与外部工具/数据的标准化交互协议

## 简介

MCP（Model Context Protocol）是模型上下文协议，为 AI 与外部工具和数据的交互提供了标准化方式。它使得不同系统之间的工具调用和数据交换变得统一和可互操作。

## 核心价值

### 1. 标准化服务接口
- 统一的工具调用格式
- 统一的数据交换协议
- 统一的错误处理机制
- 统一的认证方式

### 2. 增强 AI 功能
- 让 AI 调用外部工具
- 让 AI 访问外部数据
- 扩展 AI 能力边界
- 实现复杂功能组合

### 3. 生态互操作性
- 不同系统之间可互操作
- 工具可复用可共享
- 降低集成成本
- 促进生态发展

## 两大核心技能

### 1. 接入别人的 MCP 服务
- 发现可用的 MCP 服务
- 理解服务接口定义
- 集成到自己的项目中
- 调用服务增强功能

### 2. 开发自己的 MCP 服务
- 设计服务接口
- 实现服务逻辑
- 发布服务供他人使用
- 维护和更新服务

## 不同素材中的观点

来自 [[2026-04-29-yupi-ai-guide-core-concepts]]：
- Model Context Protocol，模型上下文协议
- AI 与外部工具/数据的标准化交互，增强 AI 功能
- 16 个核心概念之一

来自 [[2026-04-29-yupi-ai-guide-programming-tech]]：
- 是 AI 编程开发的四大核心业务领域之一
- 提供给 AI 的标准化服务
- 让 AI 调用外部工具和数据，增强功能
- Spring AI 框架原生支持 MCP

来自 [[2026-05-10-codex-canva-operations-assets]]：
- Canva 提供远程 MCP server，是 MCP 在设计工具领域的重要落地案例
- 通过 Canva MCP，AI 助手可调用设计生成、设计编辑、素材/品牌管理、设计库检索、导出、评论协作等能力
- 在运营素材自动化流水线中，[[Codex]] 通过 MCP 调用 [[Canva]] 实现从选题到设计的全链路自动化（读取选题→生成素材brief→调用品牌模板→批量改图→导出→审核流程）
- 这使 Codex 从"写代码/生成图片"的角色扩展为"工作流编排引擎"

来自 [[2026-05-13-ai-agent-productivity-20x]]：
- MCP 的核心价值被概括为把多工具协作的集成成本标准化：Agent 继续使用统一的语言，Gmail、Notion、Slack、Stripe、Google Calendar 等工具保留各自接口，MCP 负责双向翻译
- 在实际工作流里，MCP 不是单点工具调用，而是把总结收件箱、提取会议纪要、创建付款链接、在 Notion 建项目、起草跟进邮件等动作串成一个连续任务
- 文章强调 MCP 让用户不必手动切换多个标签页，本质上降低的是跨 SaaS 编排的摩擦，而不是单个 API 接入的门槛
- 当 MCP 与 Agent、Skill、上下文文件组合后，AI 的角色会从"会调用一个工具"升级为"能在多个业务系统之间跑完整流程"

来自 [[2026-05-18-ai-agent-week-into-day]]：
- MCP由Anthropic开发，作为AI与各类工具之间的"通用翻译器"，彻底解决了多工具集成的碎片化问题：Agent使用统一交互语言，各类工具保留原有接口，MCP负责中间的双向翻译和适配
- 主流Agent框架（Cowork、Codex、Manus、Perplexity等）均已内置MCP支持，提供"连接器"或"技能"菜单，用户只需登录授权即可一键完成工具连接，无需任何开发工作
- MCP连接后可实现跨工具的无缝工作流编排：一个指令即可触发Agent在多个工具中执行连续操作，无需用户在不同应用间切换，典型案例包括：
  - 总结收件箱 → 从Granola提取会议笔记 → 创建Stripe付款链接 → 在Notion中设置项目 → 起草后续跟进邮件
  - 检查日历 → 总结当日会议 → 从Notion提取项目状态 → 在Slack发送团队更新 → 创建跟进任务
- MCP的真正价值不在于单个工具调用，而在于成为所有工具的统一协调层，让信息和行动在不同平台间自由流动，消除了传统工作流中的上下文切换成本

## 快速开发工具

### MCPify
- 官网：http://mcpify.ai/
- 一句话创建自己的 MCP 服务
- 快速开发和部署
- 自动生成接口文档

### Spring AI 原生支持
- Spring AI 框架已原生支持 MCP
- 简化 MCP 服务开发
- 与 Spring 生态无缝集成

## 实用信息

### MCP vs Function Call

| 维度 | Function Call | MCP |
|------|--------------|-----|
| 范围 | 单模型内 | 跨系统跨模型 |
| 标准化 | 各厂商自定义 | 统一标准协议 |
| 可复用性 | 特定场景 | 通用可复用 |
| 生态支持 | 大模型厂商 | 社区生态 |

### 应用场景
- 企业内部工具标准化
- AI 应用之间功能共享
- 多智能体协作系统
- 插件生态系统建设

## 相关页面
- [[AI Agent 智能体]]
- [[ReAct]]
- [[Spring AI]]
- [[Canva]]
- [[AI编程开发]]
