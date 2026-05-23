---
type: entity
name: Ollama
category: 开发工具
tags:
  - 本地部署
  - 开源模型
  - 私有化
  - 数据安全
sources:
  - 2026-04-29-yupi-ai-guide-programming-tech
  - 2026-04-29-deepseek-python-local-setup
  - 2026-05-17-pm-ai-knowledge-base-design-practice
  - 2026-05-18-woshipm-ai-knowledge-management-design-practice
  - 2026-05-21-woshipm-ai-knowledge-base-product-design
created: 2026-04-29
updated: 2026-05-21
---

# Ollama

> 一键部署各种主流开源模型的工具

## 简介

Ollama 是一款开源的本地大模型部署工具，能够一键部署和运行各种主流开源大模型，是实现私有化 AI 能力的核心工具。

## 核心价值

### 1. 数据安全和隐私
- 数据不上传至云端
- 所有计算在本地完成
- 保障企业敏感数据安全
- 符合合规要求

### 2. 一键部署
- 简单的命令行工具
- 自动下载模型文件
- 自动配置运行环境
- 标准化的运行方式

### 3. 模型生态丰富
- 支持 Llama 系列
- 支持 Mistral 系列
- 支持 Qwen（通义千问）
- 支持各种开源模型

### 4. API 兼容
- 提供 OpenAI 兼容 API
- 现有代码几乎无需修改
- 无缝切换云端和本地
- 标准化接口

## 不同素材中的观点

来自 [[2026-04-29-yupi-ai-guide-programming-tech]]：
- 为什么需要本地部署：数据不上传至云端，保障安全性和隐私性
- 医疗、金融等对数据安全极为敏感的行业刚需
- 一键部署各种主流开源模型
- 现实痛点：部署不难，但算力很贵

来自 [[2026-04-29-deepseek-python-local-setup]]：
- PyCharm + CodeGPT + Ollama 本地部署方案
- 本地运行开源模型，成本更低
- 完全可控，无数据泄露风险

来自 [[2026-05-17-pm-ai-knowledge-base-design-practice]]：
- Ollama在这篇产品实践里承担的是“价值验证器”角色：先证明文档问答可行，再决定是否升级为云端产品
- 本地部署最大的优势仍然是数据可控和零云成本，但一旦用户需要手机访问、多人共享或免安装使用，Ollama 方案会被可用性和协作性短板限制
- 作者把 Ollama 与 Dify、本地 Qwen 模型组合成原型，说明它很适合MVP早期低成本试验，而不一定适合作为最终组织级知识库的交付形态

来自 [[2026-05-18-woshipm-ai-knowledge-management-design-practice]]：
- 这篇素材再次强化了 Ollama 的定位：它非常适合在个人电脑上快速验证“文档能否被对话式调用”，但不天然等于一个可交付给团队的知识产品
- 文章把本地知识库比作“桌上盆栽”——离不开工位、关机即不可用——这个比喻准确指出了Ollama方案在可达性上的根本限制
- 因而 Ollama 更像 AI 知识管理产品早期的原型工具或私有化试验工具，后续是否继续沿用，取决于是否要支持多端访问、协作和统一治理

来自 [[2026-05-21-woshipm-ai-knowledge-base-product-design]]：
- 这篇素材再次把 Ollama 放在“先验证语义检索价值、再决定是否产品化升级”的位置：它适合快速试验文档问答，但不适合作为面向团队交付的最终形态
- 文章将本地方案的限制具体化为三类门槛：离开电脑就不可访问、多人难以共享、每个成员都要重复搭建环境，说明 Ollama 的主要边界并不是模型能力，而是交付形态
- 在产品路径上，Ollama 与 Dify、本地 Qwen 的组合承担的是原型验证层职责，真正进入组织级知识管理后，系统会转向带 API、移动端与权限能力的云端架构

## 实用信息

### 官方资源
- 官网：https://ollama.com/
- GitHub：Ollama 官方仓库
- 模型库：Ollama Model Library

### 快速开始

#### 安装
```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
下载安装包安装
```

#### 运行模型
```bash
# 拉取并运行模型
ollama run deepseek-coder
ollama run qwen:7b
ollama run llama2
```

#### API 调用
```bash
# 启动服务后调用
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder",
  "prompt": "写一个 Hello World"
}'
```

### 硬件要求

| 模型大小 | 最低显存 | 推荐显存 |
|---------|---------|---------|
| 7B | 8GB | 16GB |
| 13B | 16GB | 32GB |
| 34B | 32GB | 64GB |
| 70B | 64GB | 128GB |

### 适用场景
- 企业内部敏感数据处理
- 医疗、金融等合规要求高的行业
- 离线环境 AI 能力
- 成本敏感的大规模部署
- 研发环境快速迭代

## 现实痛点

### 算力成本
- GPU 硬件成本高
- 大模型需要大量显存
- 高性能 GPU 价格昂贵
- 长期运行电费成本

### 性能权衡
- 本地模型通常比云端小
- 能力可能不如云端大模型
- 推理速度受硬件限制
- 需要在性能和成本间平衡

## 相关页面
- [[DeepSeek]]
- [[Spring AI]]
- [[RAG 知识库]]
- [[AI编程开发]]
