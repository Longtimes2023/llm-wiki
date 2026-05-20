---
tags: [素材摘要, Claude Code, Skill, 内容创作, 工作流]
created: 2026-05-11
updated: 2026-05-11
source_type: 文章
source_path: raw/articles/2026-05-11-222540-tg-dec9a9.md
---

# Claude Code Skills 精选：装了30+个Skill后只留下这6个

> Skill 装太多会降低触发准确率到 50% 以下，筛选标准只有一个——能不能替你每天省掉一步手动动作

## 基本信息

- **来源类型**：文章（掘金）
- **原文位置**：raw/articles/2026-05-11-222540-tg-dec9a9.md
- **原文 URL**：https://juejin.cn/post/7628449448600600603
- **消化日期**：2026-05-11

## 核心观点

1. **Skill 装太多会降低触发准确率**：装 30+ 个 Skill 后，Claude 需要扫描所有 Skill 描述来决定用哪个，描述一多就开始乱猜，触发准确率掉到 50% 以下。官方建议持有量 20-30 个，且必须贴合自己工作流
2. **Skill 选择唯一标准：能否替你每天省掉一步手动动作**：答不上来就不装，比任何评分都管用。别人的"必装 Top 30"不能抄，因为别人的工作流不等于你的
3. **渐进式披露是 Skill 的核心机制**：Skill 就是 SKILL.md + 参考资料按需加载，不用时不占上下文，用时才拉全文。如果把所有内容塞主文件，上下文全是 Skill，反而无法判断该用哪个
4. **创作类 Skill 的价值在于"顺手做"而非"省时间"**：SEO Blog Writer 把邮件诱饵从"下次再做"变成了"顺手就做"；Newsletter Automation 把 1-2 小时运营链砍到 10 分钟审稿；Content Repurposer 先读你过去的帖子抓出你的语气特征再套各平台语感
5. **"Setup Porn"陷阱**：花好几个小时配一堆 Skill 结果什么内容都没产出，本质是拿配置当拖延借口。正确做法是手动跑同一任务 3 次以上再让 Skill Creator 打包

## 实操内容保留

### 代码/配置

（本文无实操代码/配置）

### Prompt 模板

- Skill Creator 典型指令：`"把我昨天手动跑的选题流程打包成 skill"`
- Newsletter Automation 前置配置：需接 Perplexity API + Gmail MCP，配置一次后一劳永逸
- 按场景选 Skill：
  - 每天在 Claude 里反复跑同一串动作 → 先装 `Skill Creator`
  - 写长内容经常写到后半段忘了开头设定 → 装 `Planning with Files`
  - 写博客/公众号想一份长稿出多平台 → 装 `Content Repurposer`
  - 刚点进 Claude Code 连 Skills 开关没开过 → Settings → Capabilities → Skills 打开，顺手开 `skill-creator`

### 操作步骤

1. 开启 Claude Code Skills 功能：Settings → Capabilities → Skills
2. 先装 Skill Creator（元技能，帮你创建其他 Skill）
3. 按自己的工作流场景逐个添加，每次只装 1 个并跑一次验证
4. 手动跑同一任务 3 次以上 → 用 Skill Creator 打包成自定义 Skill
5. 控制总量在 20 个以内，确保触发准确率稳定

## 关键概念

- [[Skill]] — 本文核心主题，精选策略和具体推荐 Skill 的载体
- Skill Creator — 官方元技能，帮你写 SKILL.md + 生成测试用例，10 多个独立来源将其放在起点
- Planning with Files — 社区 Skill（13,410 Stars，生态最高），强制 Claude 先写 task_plan.md 再执行，解决长文/长代码写到后面忘开头的问题
- Document & Presentation Skills — 官方全家桶（PDF/Word/Excel/PPT），一句话从 PDF 抽数据做品牌色 Slide
- SEO Blog Writer & Lead Magnet — 社区三合一 Skill（关键词研究 + SEO 长文 + 11 页 PDF 引流手册）
- Newsletter Automation — 社区全链 Skill（Perplexity 采编 → HTML 排版 → Gmail 草稿箱）
- Content Repurposer — 社区多平台分发 Skill，先读你历史帖子抓语气特征再适配 Twitter/LinkedIn/Newsletter
- Setup Porn — 陷阱概念，花几小时配置一堆 Skill 但不产出内容，拿配置当拖延借口
- [[Skills变现]] — Skill 产品化变现方法论，与本文选择策略互补

## 与其他素材的关联

- 与 [[2026-05-11-skill-sop-for-ai]] 的关系：互补。冰冰酱那篇讲 Skill 的本质定义（ACT-R 理论、知识/编排双象限、构建四阶段），本文讲 Skill 的选择策略和实战推荐。理论 + 实战形成闭环
- 与 [[2026-05-10-skills-monetization-5-points]] 的关系：互补。伍德安思壮那篇讲 Skill 如何变现（赛道/设计/实现/验证/模式），本文讲应该选择哪些 Skill 来装。变现和选型是 Skill 生态的两面
- 与 [[2026-05-10-50-short-video-hooks-claude-opus]] 的关系：间接关联。Content Repurposer 解决多平台分发问题，短视频钩子公式是分发内容的关键开头技巧

## 原文精彩摘录

> 装太多本身就是坑，根据情况触发正确的准确率会直接掉到 50% 以下。Claude 得扫所有 skill 的描述决定用哪个，描述一多它就开始乱猜。官方建议创作者合理持有量 20 到 30 个，而且得是贴你自己工作流的那种。

> 真正让我觉得它值得留下来的，是它把邮件诱饵这件事从"下次再做"变成了"顺手就做"。博客最亏的一环就是读者看完之后走了，你连个邮箱都收不到。但你如果有 PDF 可以送，起码还能留一个联系方式回来。以前我懒得专门为每篇文章做一份诱饵，现在这一步直接折进主流程，我也没什么借口不做了。

> 它跟直接让 Claude 改写最大的区别，是它会先去读你过去发过的帖子,把你自己的语气特征先抓出来,然后再往各平台的语感上套。Twitter 第一条必须是强钩子,LinkedIn 开头要像同事在说话,Newsletter 头段又得像老朋友给你写信。你手动"改写"的时候其实是在重写三遍。

> 素材里有个说法叫 "Setup Porn"，意思就是花好几个小时配一堆 skill，结果什么内容都没产出，本质就是拿配置当拖延借口。手动跑同一个任务 3 次以上，再让 Skill Creator 帮你打包，不要反过来。

## 相关页面

- [[Skill]]
- [[Skills变现]]
- [[AI内容创作]]
- [[AI编程开发]]
