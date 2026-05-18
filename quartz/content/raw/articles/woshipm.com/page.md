---
url: https://www.woshipm.com/ai/6394061.html
title: "从个人痛点到企业级知识库：一款基于大模型的智能知识管理产品设计实践 – 人人都是产品经理"
description: "一、洞察本质：从“文件名称搜索”到“语义意图理解”的鸿沟 1.1 用户故事：一个真实的“知识焦虑”场景 我是一名AI领域的研究者与内容创作者，电脑中存储了上千份行业报告、技术白皮书、会议纪要。 某天我需要查找“AI在银行客服场景中的应用案例”，但面对文件夹里密"
author: "王佳亮  关注"
published: "2026-05-12T15:05:37"
coverImage: "https://image.woshipm.com/2024/01/03/7a554982-aa29-11ee-9c9e-00163e142b65.png"
language: "zh-Hans"
captured_at: "2026-05-17T16:48:34.507Z"
---

# 从个人痛点到企业级知识库：一款基于大模型的智能知识管理产品设计实践 – 人人都是产品经理

[![](https://image.woshipm.com/2023/06/07/c05110fe-0530-11ee-b68f-00163e0b5ff3.jpg?x-oss-process=image/quality,q_80/format,webp)](https://ke.qidianla.com/courses/bcpm)

## 从个人痛点到企业级知识库：一款基于大模型的智能知识管理产品设计实践

[![](https://image.woshipm.com/wp-files/2019/10/J1uoNRu68MclzQ0PVRs0.jpg!/both/72x72)](https://www.woshipm.com/u/871971)

2026-05-12

0 评论 1349 浏览 6 收藏 23 分钟

[零基础想转行产品经理？别担心！我们的实战营专为转行者设计，提供体系化课程和项目实战，帮你弥补经验短板，成功实现职业转型，拿到心仪offer。](https://ke.qidianla.com/courses/bcpm)

> 知识工作者的痛点被精准击中——当传统文件搜索沦为低效的‘文件名匹配游戏’，如何跨越从存储到理解的认知鸿沟？本文揭秘一款云端AI知识库的实战搭建过程，从RAG技术选型到Yuxi框架的巧妙应用，展示如何让尘封文档在对话中‘活’起来，打造真正的智能知识副驾。

![](https://image.woshipm.com/2024/01/03/7a554982-aa29-11ee-9c9e-00163e142b65.png)

## 一、洞察本质：从“文件名称搜索”到“语义意图理解”的鸿沟

### 1.1 用户故事：一个真实的“知识焦虑”场景

我是一名AI领域的研究者与内容创作者，电脑中存储了上千份行业报告、技术白皮书、会议纪要。

某天我需要查找“AI在银行客服场景中的应用案例”，但面对文件夹里密密麻麻的PDF和Word文档，传统的本地搜索只能按文件名匹配——而大部分文件命名是“2024\_金融科技峰会材料”、“客户分享-张三”等毫无语义的信息。我逐一打开、浏览、关闭，耗时半小时仍无果。

这不是个例。根据我对20位知识工作者的非正式调研， **87%的人表示经常找不到已存储的文档内容，63%的人曾因“找不到”而重复下载或重新整理资料** 。传统文件系统与人类记忆之间的认知鸿沟，正成为知识利用率低下的首要原因。

### 1.2 问题抽象：存储≠知识，检索≠理解

从产品功能角度看，现有解决方案存在三个断层：

![](https://image.woshipm.com/wp-files/2026/05/mtqrNvwZxTwmIzmyzFHI.png)

### 1.3 初步解决方案：本地RAG应用

我很快尝试了行业主流方案： **Ollama（本地模型运行）+Dify（工作流编排）+本地大模型（如Qwen）** 。

这套技术组合（RAG：检索增强生成）成功实现了在电脑上通过对话从文档中提取信息。例如提问“AI如何在零售场景应用？”，系统能准确从《AI+零售行业》报告中给出段落并标注来源。

然而，本地部署立即暴露了两个致命弱点：

- **可用性缺陷** ：一旦关闭电脑，手机无法访问。知识库成了“桌上盆栽”，离不开工位。
- **协作性缺陷** ：书友会成员想共享资料、协同学习，每人需要重复搭建环境，技术门槛高。

至此，产品价值主张自然浮现： **构建一个可随时随地从任何设备访问、支持多用户的云端AI知识库，让组织成员像聊天一样抽取文档精华** 。

考虑到未来的扩展性，这个功能实现后，未来我可以通过配置用户和权限的方式，将功能开放给其他书友会的成员使用，大家只要打开网站登录后就可以使用服务，不用额外配置和下载飞书，比较便捷。基础的操作流程如下图所示。

![](https://image.woshipm.com/wp-files/2026/05/5J5I2nn3zRRUJ2GFBgBG.png)

## 二、产品定位与价值主张：不止于工具，而是知识的“智能副驾”

### 2.1 产品愿景

![](https://image.woshipm.com/wp-files/2026/05/1fLlXbPfqTRhMAWOiNNj.png)

### 2.2 目标用户与场景

![](https://image.woshipm.com/wp-files/2026/05/6pARDEdkPUuxYjBShCy0.png)

### 2.3 核心价值点（运用KANO模型）

使用KANO模型对功能特性进行分层：

![](https://image.woshipm.com/wp-files/2026/05/f9BBuq54QZaVjLL7NzjH.png)

本产品第一版优先满足基本型+部分期望型，保证可用；后续迭代加入兴奋型特性制造差异化。

## 三、技术选型策略：在成本、可控性与扩展性间取得平衡

### 3.1 决策框架

作为最小可行产品（MVP），技术选型遵循四个评估维度（权重由高到低）：

1. **成本** （40%）：初期零云成本，优先使用开源社区版和免费额度。
2. **可扩展性** （25%）：未来需支持多用户、文件管理、API集成，不能锁死在单机方案。
3. **部署与维护复杂度** （20%）：必须一条命令或几分钟内完成，不依赖复杂运维。
4. **文档与社区活跃度** （15%）：遇到问题能快速找到解决方案。

### 3.2 候选方案比对

因为是试验阶段，目标是先把产品搭建起来，服务平台的选择，因此主要考虑这几个维度：成本、稳定性、可扩展性和说明文档的完备性。

最初打算使用Cherry Studio，后来发现社区版虽然免费，但是无法满足服务器部署的需求，企业版提供了Agent和MCP的管理，但价格又太贵。因此放弃。

![](https://image.woshipm.com/wp-files/2026/05/ZqXItal5l6ep7hCFaj6i.png)

工具选型主要解决的是将解析文档，同大模型结合，能理解用户的意图，输出用户希望的信息。如果没有现成工具，其实这块自己通过 Langchain+向量数据库的方式，也是可以实现的，就是复杂了些。我们还是希望可以使用现成工具，通过工作流的配置来实现这个功能。类似于将Coze的工作流部署在服务器上。

继续寻找，有一款Maxkb产品，但只有专业版以上的产品才开放API，社区版无法使用API，那就意味着无法同我的后端程序集成。只能放弃。

![](https://image.woshipm.com/wp-files/2026/05/MfryZ5b2D0cxD5SggnjF.png)

WeKnora是腾讯的知识管理开源平台，有腾讯背书，比较可靠，但是文档解析接口一个月只有200次，这个不适合ToC产品构建。

![](https://image.woshipm.com/wp-files/2026/05/n4TbJzQovNron1NaKdFJ.png)

我又找了其他一些平台产品，内容比较多，整理后通过表格呈现，方便大家阅读。另外也看了些国外的产品，像Dify，如果未来是希望做成复杂工作流的知识库，Dify也不错，但目前只是搭建轻量级的，综合评估下来，相对还是Yuxi比较好用，决定使用Yuxi这个工具。

![](https://image.woshipm.com/wp-files/2026/05/2v0IUOnyjJaS77eEfnZ7.png)

**决策理由** ：Yuxi结合了向量检索与知识图谱，适合处理复杂关联的知识问答；提供完整的RESTful API（包括流式输出）；Docker部署三步完成，且完全开源无调用次数限制。其轻量级特性与MVP目标高度吻合。

## 四、产品构建实战：从零到可用的操作指南

### 4.1 环境准备

**前置条件** ：安装Docker Desktop（配置国内镜像加速）。

**步骤一：获取代码**

![](https://image.woshipm.com/wp-files/2026/05/xCfAWzAk0uaimdaPO3C6.png)

浅克隆技术说明：–depth 1仅下载最新提交，减少80%以上下载量。

**步骤二：配置环境变量（推荐脚本方式）**

![](https://image.woshipm.com/wp-files/2026/05/Dh4hlo6ImV6OLF3Wtj8Z.png)

**步骤三：启动服务**

![](https://image.woshipm.com/wp-files/2026/05/6Htlib1vFJTlpKXvLm2h.png)

服务首次启动需要等待镜像拉取和编译，请耐心等待 2-3 分钟。

如果你是科学上网，取决于网速，如果觉得慢，也可以使用国内的镜像，在Dockers中进行配置： 打开 Docker → Settings → Docker Engine

![](https://image.woshipm.com/wp-files/2026/05/sqmfyHPBUwEMj7TuXWx1.png)

**步骤四：验证访问**

- Web界面：http://localhost:5173
- API文档：http://localhost:5050/docs

首次访问需设置超级管理员账号密码。

### 4.2 知识库创建

**4.2.1 新建知识库**

新建知识库非常容易，只要点击【新建知识库】输入知识库名称就可以。

![](https://image.woshipm.com/wp-files/2026/05/d77cudPHhq83rNdzGjAd.png)

创建好之后，将你需要的文档上传上去就可以，非常便捷。

![](https://image.woshipm.com/wp-files/2026/05/l85tFgOg9hYx56lL6bzA.png)

**4.2.2 使用知识库**

我们在对话框中提问我们需要的内容。比如，我提问“AI如何在零售场景应用？”，希望可以从知识库中检索到刚才上传的《AI+零售行业》这份资料，并获得答案。输入后，有点小异常。

![](https://image.woshipm.com/wp-files/2026/05/UYmzkYRpbuwruOvCDELB.png)

如果报这个错误，也不用担心，主要原因是后端 API 默认用了 ASCII 编码，不认识中文。很好解决：

![](https://image.woshipm.com/wp-files/2026/05/qpNtCOvabXuGkeAWojqB.png)

这个时候，我们再输入之前的提问“AI如何在零售场景应用？”，输出正常。

![](https://image.woshipm.com/wp-files/2026/05/9nMQ56i99xgehGlylVKb.png)

![](https://image.woshipm.com/wp-files/2026/05/B5vPKuBC8tgJjyXc0HXA.png)

### 4.3 产品实现

**4.3.1 功能规划（基于用户反馈）**

完成了知识库部署，虽然我们在本地已经实现了在对话框中通过问答的方式完成知识检索，但对话框这种方式还有些不完美，通过初期5位书友会成员的内测，收集到以下需求：

![](https://image.woshipm.com/wp-files/2026/05/GY3JpkDBuhNdveYmuTuB.png)

综合以上几点，我们的知识库升级主要实现以下几大功能。

暂时无法在飞书文档外展示此内容

基于以上，制定V1.1版本功能清单：

- **必须（MUST）** ：服务器部署、用户登录、手机响应式界面、基础问答API集成。
- **应该（SHOULD）** ：关键词检索、文件上传/下载。
- **可以（COULD）** ：多文档总结、用户权限分组（书友会独立空间）。

**4.3.2 API接口集成与前后端实现**

既然我们需要在服务器部署，搭建自己的客户端，那就需要用到Yuxi提供的API接口能力，第一步我们先实现后端同Yuxi的集成，这个时候，我们要用到一个工具APIFOX，用来测试Yuxi接口返回的内容。

Yuxi提供了标准REST API，其中问答接口支持流式输出（SSE风格）。使用APIFOX测试发现响应结构。

我们发现为了实现流式输出，大模型不是一次性返回所有结果，而是一个字或是一个词，是一个JSON片断，在加载过程中，”status”: “loading”，程序要持续读取，当”status”: “finished”, 意味着大模型输出结束。

![](https://image.woshipm.com/wp-files/2026/05/j3dUINYtSSxdk1mdqJAX.png)

![](https://image.woshipm.com/wp-files/2026/05/zBq1UpJ9LIBZf8waGyVM.png)

### 4.4 整体技术栈

接下来，我们根据Yuxi接口规范，编制后端和前端页面代码。我本人开发使用的是Visual Studio 2026，C#.Net MVC 开发框架。

![](https://image.woshipm.com/wp-files/2026/05/cYjUXowffx5DvzmBnTOz.png)

大模型对于知识库的分析，使用了 MinIO对象存储和Milvus向量数据库，因此，我们可以使用MinIO相关接口来读取存储在里面文档。产品核心端到端流程如下。

![](https://image.woshipm.com/wp-files/2026/05/9hObLGDdXL6q0U3E3vy2.png)

**产品端实现** ：采用C#.NET MVC开发后端，负责：

- 用户认证（Session + JWT）
- 调用Yuxi API完成问答，流式转发给前端
- 对接MinIO对象存储，实现文件上传/下载
- 同时提供简单关键词检索（基于Milvus向量索引的标量过滤）

前端采用响应式设计（Bootstrap），对移动端优化按钮大小与输入布局。

**4.4.1 产品界面与交互设计要点**

1）主页

对于知识库而言，我相信大多数用户还是习惯用关键字来查询，这样简便直接。因此，我这里为用户设计了两种检索模式，优先用户快捷检索，在快捷检索未查询到信息时，用户可使用智能检索助理辅助检索。

产品主页面如下所示。这样设计的好处是用户进入平台，可以直观浏览相关的内容，有需要，第一时间可以输入检索内容直接检索，节省用户时间。

![](https://image.woshipm.com/wp-files/2026/05/vKvywgINRwSZsjOggWNx.png)

- 上半部突出快速检索框（关键词+按钮）
- 下半部显示最近上传的文件列表、热门提问
- 原因：产品数据表明，70%的用户在30秒内希望不经过对话就能直接浏览或搜索，因此“快捷检索”优先级高于“AI助理”。

2）智能检索页

如果用户希望深度检索知识库中的内容，可以使用智能检索功能，产品设计了一个智能助理，通过常见的对话方式，同用户交互。

![](https://image.woshipm.com/wp-files/2026/05/LcrFkJPu5u7DT0Ckp3ED.png)

为了方便用户在手机端使用，产品也做了移动端适配，以下是用户在移动端使用智能检索的效果。例如用户希望检索知识库中有关于【供应链】相关的报告，系统可以对知识库中的内容基于大模型进行深入理解和分析，进行归纳总结，基于用户意图，给出用户希望检索的资料，并对资料进行概要提炼。

![](https://image.woshipm.com/wp-files/2026/05/zTU1KEkOBZTY4MzcW057.jpeg)

- 类似主流AI对话界面（如ChatGPT），突出历史对话记录
- 每个回答下方显示 **来源文件** ，点击可下载原文档
- 移动端适配：底部固定输入框，使用Viewport适配

**用户价值表达** ：

> “通过这两种模式，我们既满足了‘我知道我要什么’的精确查询场景，又支持‘我模糊记得有相关概念’的探索式场景，覆盖了知识检索的完整心智模型。”

## 五、产品价值验证与数据分析

### 5.1 与竞品对比的差异化优势

![](https://image.woshipm.com/wp-files/2026/05/xIr2bVhhUZsemM0m2U5u.png)

### 5.2 关键业务指标（产品发布后追踪）

建议追踪以下指标验证产品价值：

- **知识检索时间** ：从打开页面到获得答案的平均时长（目标<30秒）
- **问答采纳率** ：用户对回答点击“有用/无用”的比例（目标>80%）
- **文档复用率** ：被AI检索引用的文档占全部文档的比例（目标>60%，避免僵尸文档）
- **DAU/MAU** ：对于社群产品，目标周活渗透率>30%

### 5.3 成本核算（以20人团队为例）

![](https://image.woshipm.com/wp-files/2026/05/awrJZruQ7fmzzEe8iKNs.png)

## 六、迭代路线图：从“工具”到“平台”

### 6.1 下一阶段功能规划（V2.0）

基于产品反馈，规划三个增强方向：

![](https://image.woshipm.com/wp-files/2026/05/yTCE02LwmWSLD9lORH50.png)

### 6.2 技术债务与风险管理

- **大模型依赖风险** ：硅基流动等第三方API可能变更或收费上涨。预案：支持Ollama本地模型切换（如Qwen-14B），牺牲一定精度换取可控性。
- **向量数据库运维** ：Milvus在单机模式下数据量增长后性能下降。预案：定期清理或归档旧知识库，或迁移至云原生向量数据库（如Zilliz Cloud）。
- **用户数据隐私** ：若开放公网，需签订协议并加密传输。预案：所有敏感信息（API Key、文档内容）使用AES-256加密存储。

## 七、总结

产品经理常常陷入一种错觉：以为找到更强大的工具、更先进的算法，就能解决一切问题。但真正的跃迁，发生在你放下“如何实现”的技术执念，转而追问“为何存在”的价值原点那一刻。

起初，我只是想让自己少花半小时翻找文档；后来才明白，知识工作者真正的痛苦不是“找不到”，而是“找到了也无法对话、无法提炼、无法让沉睡的文字重新开口说话”。

就像我最终选择Yuxi而非等待一个完美的All-in-One框架一样——三天跑通全链路的粗糙行动，胜过三个月研究K8s配置的精致犹豫。产品经理不是在挑选最好的锤子，而是在钉子还模糊不清时，就敢挥出第一锤，并在敲击中校准方向。

对于产品经理而言，我们做的从来不是“存储工具”，而是“激活装置”。让一份尘封的PDF在对话中被唤醒，让一个蹲在马桶上的用户能随口问出“供应链相关报告”——这些看似微小的场景，恰恰是知识从生产资料变为生产关系的转折点。

当你意识到一个人打开知识库的动机，往往不是“浏览”，而是“求救”——他正被某个具体问题困住，急需一个能听懂人话的副驾，而不是又一个需要学习的系统——你就会把所有傲慢的复杂设计砍掉，留下最简单的对话框和最醒目的来源链接。

这种“独乐乐不如众乐乐”的朴素信仰，最终会让一个自用的脚本，长成服务于数十个团队的生意。说到底，产品经理的成就感不是代码跑通的那声欢呼，而是某个深夜，用户发来一句话：“真的找到了，谢谢你。”

最后感谢开源社区提供了Yuxi这样的优秀项目，让个人开发者也能以低成本构建AI应用。

本文内容基于真实实践，所有操作均已在Ubuntu 22.04 + Docker 24.0环境下验证通过。产品目前已经部署上线。欢迎大家提出宝贵意见和建议！

本文由人人都是产品经理作者【王佳亮】，微信公众号：【佳佳原创】，原创/授权 发布于人人都是产品经理，未经许可，禁止转载。

题图来自Unsplash，基于CC0协议

更多精彩内容，请关注人人都是产品经理微信公众号或下载App

[![](https://image.woshipm.com/2026/05/09/3491f096-4b7e-11f1-9542-00163e09d72f.png?x-oss-process=image/quality,q_80/format,webp)](https://996.pm/YDLOg)

[![](https://image.woshipm.com/wp-files/2019/10/J1uoNRu68MclzQ0PVRs0.jpg!/both/150x150)](https://www.woshipm.com/u/871971)

![](https://static.woshipm.com/tag/1601_1@2x.png)

《产品经理知识栈》作者，专注于互联网产品知识与理念分享~公众号：佳佳原创

110篇作品 747634总阅读量

[风控系列②-信贷催收业务模式与系统架构搭建](https://www.woshipm.com/pd/5795229.html "风控系列②-信贷催收业务模式与系统架构搭建")

[![风控系列②-信贷催收业务模式与系统架构搭建](https://image.woshipm.com/wp-files/2023/04/M9EWYKlNAVeiWg3YMEQA.jpg!/both/120x80)](https://www.woshipm.com/pd/5795229.html "风控系列②-信贷催收业务模式与系统架构搭建")

[抖音和外卖，相互成就？](https://www.woshipm.com/it/5753137.html "抖音和外卖，相互成就？")

[![抖音和外卖，相互成就？](https://image.woshipm.com/wp-files/2023/02/M3mO5OoGlrdpaiU592zX.jpg!/both/120x80)](https://www.woshipm.com/it/5753137.html "抖音和外卖，相互成就？")

[避开坑洞：B端产品需求管理必备指南](https://ke.qidianla.com/courses/bcpm)

[![](https://image.woshipm.com/2023/08/02/68ee3c82-3100-11ee-b430-00163e0b5ff3.png?x-oss-process=image/quality,q_80/format,webp)](https://ke.qidianla.com/courses/bcpm)

[旅游业的变迁，是OTA平台最大的风向标](https://www.woshipm.com/share/5891179.html "旅游业的变迁，是OTA平台最大的风向标")

[![旅游业的变迁，是OTA平台最大的风向标](https://image.woshipm.com/2023/04/13/d184589e-d9e9-11ed-a8b0-00163e0b5ff3.jpg!/both/120x80)](https://www.woshipm.com/share/5891179.html "旅游业的变迁，是OTA平台最大的风向标")

[财务软件设计之发票](https://www.woshipm.com/share/5934499.html "财务软件设计之发票")

[![财务软件设计之发票](https://image.woshipm.com/2023/04/17/89803f0e-dcf5-11ed-a8f2-00163e0b5ff3.png!/both/120x80)](https://www.woshipm.com/share/5934499.html "财务软件设计之发票")

[这届双十一，关系着电商是强弩之末还是柳暗花明](https://www.woshipm.com/it/5927038.html "这届双十一，关系着电商是强弩之末还是柳暗花明")

[![这届双十一，关系着电商是强弩之末还是柳暗花明](https://image.woshipm.com/2023/04/13/88d6514c-d9df-11ed-8440-00163e0b5ff3.jpg!/both/120x80)](https://www.woshipm.com/it/5927038.html "这届双十一，关系着电商是强弩之末还是柳暗花明")

评论

1. 目前还没评论，等你发挥！

 [![](https://image.woshipm.com/2023/08/28/9c1876ea-4550-11ee-87b8-00163e0b5ff3.jpg?x-oss-process=image/quality,q_80/format,webp) 无人指导下的自我成长：我的业务提升之路](https://ke.qidianla.com/courses/90pm)

- [![TikTok多收了三五斗](https://image.woshipm.com/wp-files/2023/11/iEg4d1nVNJK37nb8Dtlf.jpg!/both/130x88)](https://www.woshipm.com/it/5950073.html)
	[TikTok多收了三五斗](https://www.woshipm.com/it/5950073.html)
- [![网易云、QQ音乐、酷狗、汽水……你的音乐软件懂你吗？](https://image.woshipm.com/2023/04/17/55b375ce-dcf5-11ed-ab4d-00163e0b5ff3.png!/both/130x88)](https://www.woshipm.com/it/5847238.html)
	[网易云、QQ音乐、酷狗、汽水……你的音乐软件懂你吗？](https://www.woshipm.com/it/5847238.html)
- [![HMI设计与B端C端设计思维区别](https://image.woshipm.com/wp-files/2023/02/BncQAGvGBw9ay0GlEeBk.png!/both/130x88)](https://www.woshipm.com/pd/5745335.html)
	[HMI设计与B端C端设计思维区别](https://www.woshipm.com/pd/5745335.html)

[*专题* ![](https://liangcang-prod.oss-cn-hangzhou.aliyuncs.com/55b5eac92aab2289d9a67c3929f8ea9d/2024/02/28/179b565e-d5ff-11ee-a232-00163e142b65.png?x-oss-process=image/quality,q_80/format,webp)](https://www.woshipm.com/topic/city)

[智慧城市设计指南](https://www.woshipm.com/topic/city)

随着现代科技的不断发展进步，智慧城市的建设也在不断发展，本专题的文章分享了智慧城市设计指南。

[*专题* ![](https://liangcang-prod.oss-cn-hangzhou.aliyuncs.com/55b5eac92aab2289d9a67c3929f8ea9d/2024/01/29/bde94294-be5a-11ee-854d-00163e142b65.png?x-oss-process=image/quality,q_80/format,webp)](https://www.woshipm.com/topic/cms)

[内容管理系统（CMS）的设计指南](https://www.woshipm.com/topic/cms)

内容管理系统是一种位于WEB 前端（Web 服务器）和后端办公系统或流程（内容创作、编辑）之间的软件系统。本专题的文章分享了内容管理系统（CMS）的设计指南。

[*专题* ![](https://liangcang-prod.oss-cn-hangzhou.aliyuncs.com/55b5eac92aab2289d9a67c3929f8ea9d/2022/12/07/c1bffb5e-75d3-11ed-93eb-00163e0b5ff3.png?x-oss-process=image/quality,q_80/format,webp)](https://www.woshipm.com/topic/buy)

[拼团功能的设计指南](https://www.woshipm.com/topic/buy)

本专题的文章分享了拼团功能的设计指南。

[*专题* ![](https://liangcang-prod.oss-cn-hangzhou.aliyuncs.com/55b5eac92aab2289d9a67c3929f8ea9d/2023/04/04/b828425e-d2bc-11ed-aa25-00163e0b5ff3.png?x-oss-process=image/quality,q_80/format,webp)](https://www.woshipm.com/topic/algorithm)

[算法的知识汇总](https://www.woshipm.com/topic/algorithm)

本专题分享了算法相关的知识，汇总了算法的基础知识和进阶知识。

[*专题* ![](https://liangcang-prod.oss-cn-hangzhou.aliyuncs.com/55b5eac92aab2289d9a67c3929f8ea9d/2023/05/23/51f149d0-f937-11ed-bbb6-00163e0b5ff3.png?x-oss-process=image/quality,q_80/format,webp)](https://www.woshipm.com/topic/tog)

[TO G产品设计指南](https://www.woshipm.com/topic/tog)

本专题的文章以To G领域为例，从产品经理的角度，分享TO G产品设计指南。

[*专题* ![](https://liangcang-prod.oss-cn-hangzhou.aliyuncs.com/55b5eac92aab2289d9a67c3929f8ea9d/2023/05/29/8c1d7b9e-fdf4-11ed-88d8-00163e0b5ff3.png?x-oss-process=image/quality,q_80/format,webp)](https://www.woshipm.com/topic/activity-2)

[抽奖类活动的设计指南](https://www.woshipm.com/topic/activity-2)

抽奖作为一种活跃用户的运营手段之一，在产品运营的工作里是一项大家必须掌握的技能。本专题的文章分享了抽奖类活动的设计指南。

[网站统计](http://tongji.baidu.com/hm-web/welcome/ico?s=b85cbcc76e92e3fd79be8f2fed0f504f)