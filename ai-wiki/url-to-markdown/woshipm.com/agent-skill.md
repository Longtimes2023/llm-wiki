---
title: "为电脑上的所有 Agent，统一一套 Skill 库 – 人人都是产品经理"
author: "甜橙, 亨亨"
site: "woshipm.com"
published: 2026-04-26T09:04:47
source: "https://www.woshipm.com/ai/6384088.html"
domain: "woshipm.com"
language: "zh-Hans"
description: "Skill 使用中易被忽视的割裂 电脑上的 AI 工具越来越多，有 Claude Code、OpenCode、Cursor、OpenClaw 小龙虾、Codex、Trae……由于不同的模型各有擅长，不同的 Agent 工具各有场景，单押一个反而低效，因此，多"
word_count: 2917
---

[搜索](https://api.woshipm.com/search/list.html)

注册 | 登录

登录人人都是产品经理即可获得以下权益

- 关注优质作者
- 收藏优质内容
- 查阅浏览足迹
- 免费发布作品
- 参与提问答疑
- 交流互动学习
立即登录

## 为电脑上的所有 Agent，统一一套 Skill 库

2026-04-26 1 评论 3399 浏览 9 收藏

13 分钟

> AI工具的繁荣带来了Skill管理的混乱噩梦——多Agent并存时，重复安装、版本漂移、资产黑盒化等问题层出不穷。本文提出革命性的「中央Skill」方案，通过软链接技术实现跨工具统一管理，不仅彻底解决同步难题，更揭示了Skill作为AI时代确定性资产的核心价值：它是沉淀工作方法的SOP，会随AI进化而增值而非贬值。

## Skill 使用中易被忽视的割裂

电脑上的 AI 工具越来越多，有 Claude Code、OpenCode、Cursor、OpenClaw 小龙虾、Codex、Trae……由于不同的模型各有擅长，不同的 Agent 工具各有场景，单押一个反而低效，因此，多 Agent 并用已经是现实，同时开着两三个 Agent 是常态。

这些 Agent 工具多了之后，我发现了一个头大的问题， **Skill 不好管理，每个 Agent 都有独立的 Skill 文件夹，默认状态下彼此隔离，互不感知。**

结果是：

- 装一个新 Skill，要重复在不同的 Agent 装好几次；
- 这个 Agent 装了 3 个 Skill，那个 Agent 装了 4 个，电脑上一共几个 Skill，得一个一个文件夹查；
- 改一个 Skill，要多个 Agent 同步，改了这个，忘了那个；
- 时间一长，哪份版本落后了，自己都搞不清楚。

有一个产品经理都懂的系统设计原则： **Single Source of Truth，单一事实来源。** 同一份数据，一旦有了多个副本，就已经埋下了分裂的种子。副本越多，同步成本越高；同步一旦被省略，版本开始各自漂移；最终没有人知道哪个是最新的，某一天报个错，花费大量时间排查，最后发现是一个版本同步的问题。

更隐蔽的代价是， **逐渐不知道自己有什么 Skill 了。** 装了、忘了、过时了也没删，Skill 库慢慢变成一个连自己都不信任的黑盒。这份本该复利积累的 Skill 资产， **在无意间反而成为系统的负担。**

## 解法：让所有 Agent 共用一份源

我推荐的 Skill 管理方法，是 **「中央 Skill」，把所有 Agent 的 Skill 文件夹，统一指向同一个中央文件夹，采用软链接实现。**

有两个先决条件，决定了「中央 Skill」方案的可行性：

1. Skill 的运作原理，有点像进阶版的提示词，是文本格式，只要 AI 能找到这个文本，就能执行；
2. 在 Agent 的软件中，安装 Skill，实际上，只是把 Skill 复制了一份，放置到软件目录下的「Skills」文件夹。

![](https://image.woshipm.com/wp-files/2026/04/C5BtbaHXOw7JEJFuwUdZ.png)

软链接的原理，其实很简单， **软链接其实就是一个“指路牌”。** 原先是每个 Agent 的软件目录里，都有自己单独的一个 Skills 文件夹，每个 Agent 只认自己的，现在，Claude Code 去~/.claude/skills/找 Skill，就会发现，这个路径现在不再存放真实文件，而是一块“指路牌”，把 Claude Code 无缝引导到统一维护的「中央 Skill 文件夹」。

**中央文件夹里改了什么，所有 Agent 立刻看到，实时穿透，没有延迟，也不占用额外存储空间。**

![](https://image.woshipm.com/wp-files/2026/04/oM4atqyZHvQ5ioQXn6Vb.png)

理解了原理之后，操作也很简单，就三步：

- 第一步：创建中央 Skill 文件夹，可以放在电脑的任意位置，只要管理起来方便就行；
- 第二步：进入到各个 Agent 的软件目录，将原有的「Skills」文件夹删除掉，如果原先的 Skills 文件夹已经有一些 Skill，可以直接复制到中央 Skill 文件夹；
- 第三步：通过终端，在 Agent 的软件目录里，创建以skills命名的软链接，让其指向中央 Skill 文件夹；
- 第四步：重复操作二、三步，把每个 AI 工具的 Skill 都集中到中央 Skill，ClaudeCode、Cursor、Codex、Trae、Openclaw、Open Code、Qoder……

熟悉电脑的伙伴们可以立刻动手了，不熟悉的小伙伴，可以拉到文章最后，我放置了详细的手把手操作步骤教程。

## 统一中央 Skill，三个问题同时解决

**版本永远一致。** 中央文件夹改一处，全部同步，版本分裂从根本上不再可能发生。更新也很便利，中央 Skill 更新，所有 Agent 调用的就都是最新版。

**管理有了主场。** 所有 Skill 在一个地方，只要打开这个中央 Skill 文件夹，知道自己有多少个 Skill，哪些在用，哪些该清理，Skill 库重新成为可被信任的资产。

**新 Skill 自动归库。** 因为~/.claude/skills/是软链接，除了直接把 Skill 丢进中央文件夹，依然可以让 Claude Code 帮忙安装任何新 Skill，新的 Skill 文件，实际也会落进中央文件夹，无需任何额外操作，并且电脑上的所有 Agent，也相应的自动生效，不必每个 Agent 都分别安一遍。

再进一阶，这个中央 Skill，直接初始化成 Git 仓库推到 GitHub，完整版本历史，改错随时回滚。如果有多台设备，通过 Github 远程仓库的git push和git pull同步，连跨设备的统一都实现了。

## 变与不变：Skill 是 AI 时代里少有的确定性

以上三点，是操作层面的收益。但我真正想说的，是一个更深一点的感受。

AI 在快速变化。模型在迭代，每隔几个月就有新的能力边界被突破；Agent 工具在演进，今天的最优选，明天可能有更好的替代；就连”该用什么工具”这个问题本身，答案都在持续更新。

这种速度制造了一种特定的焦虑：投入一个工具，可能很快过时；学习一套用法，可能很快失效。在这个语境里，“什么值得长期投入”是一个真实的问题。

**Skill 不在这个变化里。**

把 Skill 理解成 Prompt 模板，没有错，但只说了表层。

更准确的定义是： **Skill 是你和 AI 协作的 SOP，是你把自己的工作方式，一点点沉淀进 AI 的过程。**

而 SOP，是所有工作流的沉淀，真人操作，得按这个步骤来；AI 操作，也得按这个步骤来；以后换了更强的 AI，同样的 Skill 在更强的引擎上，只会发挥更大的效果，但也还是得按这个步骤来。

这就是方法论，Skill 属于自己，不属于任何一个工具。

**Skill 的价值曲线，和 AI 的进化轨道是独立的。** AI 越强，自己的方法论越能发挥更大的价值。

这让 Skill 库，成为 AI 时代里为数不多的确定性，成为快速变化的时代里，不变的东西。这是统一管理 Skill 库真正的理由，不光为了方便，也是为了能让这些方法论有一个稳定的地方持续沉淀和进化，不因版本的混乱而失效，不因 AI 的迭代而贬值。

## 手把手教程

### 第一步：创建中央 Skill 文件夹

1. 在文稿中，选择你想放置中央 Skill 的文件目录，新建一个文件夹，命名为SharedSkills（也可以是其他名字）。

### 第二步：清理 Agent 原有 skills 文件夹

1. 右键点击在 Finder（访达）， 点击「前往文件夹」，输入 ~/ ，回车，进入用户目录；

![](https://image.woshipm.com/wp-files/2026/04/ALdRa7WB7hpWeHwSjt9w.png)

1. 此刻 Claude、OpenClaw 等应用的目录都在隐藏状态，点击快捷键Shift + Command +.，让隐藏文件夹展示出来，就能看到.claude、.openclaw等应用目录；
2. 以 Claude 为例，进入软件目录.claude里的skills文件夹，这里面是之前安装的所有 Skill，挑选想要保留的，复制，粘贴到刚刚创建的中央 Skill 文件夹SharedSkills；如果没有 skills 文件夹，说明之前没有安装过 Skill，直接进入下一步；
3. 回到.claude，把skills文件夹删除。

![](https://image.woshipm.com/wp-files/2026/04/UVZalAoiLtWYu0NLF0Dg.png)

### 第三步：通过终端，创建软链接

1. 这是唯一一个必须使用终端的操作， **按Command + 空格，输入「终端」，回车打开；**
2. 运行软链接创建命令。

运行命令前，需要知道你的SharedSkills文件夹的完整路径。最简单的方式： **把SharedSkills文件夹从 Finder 直接拖入终端窗口，** 终端会自动填入完整路径，复制下来备用。

![](https://image.woshipm.com/wp-files/2026/04/Nf7QbMW6ndQlbZGiFPuJ.png)

然后在终端里输入以下命令，把路径替换成你实际的路径：

> ln -s 你的SharedSkills完整路径 ~/.claude/skills

\# 格式是 ln -s 真实文件夹 软链接位置，先写中央文件夹的路径，再写Claude目录

2

比如我的中央文件夹放在文稿目录下，命令就是：

> ln -s ~/Documents/SharedSkills ~/.claude/skills

\# 意思是引用 ~/Documents/SharedSkills ，然后在~/.claude/skills 创建 软链接

输入命令后，回车执行，没有任何输出就代表成功。

再次回到.claude文件夹，就会看到，目录里又多了一个skills文件夹，只不过这个文件夹图标上，出现了一个小箭头「↗」。这是 macOS 标识软链接的方式，代表这个文件夹是一个入口，不是真实存放文件的地方。双击，就跳转到了SharedSkills中央 Skill 文件夹，配置完成。

### 第四步：处理其他的 Agent 工具

刚刚以 Claude 举例，其他的 Agent，也一样如法炮制。

1. 重复操作二、三步，把每个 AI 工具的 Skill 都集中到中央 Skill，ClaudeCode、Cursor、Codex、Trae、Openclaw、Open Code、Qoder……

唯一需要调整的，就是软链接的创建命令，需要换成另外的 Agent 路径。

> ln -s SharedSkills完整路径 ~/.其他Agent路径/skills

#.其他Agent路径，例如.openclaw.cursor.codex等

这样操作之后，所有的 Agent，都可以在中央文件夹 SharedSkills 中进行管理，并且新添加的 Skill，也会自动归集在一起。以后，只需维护 SharedSkills 一个文件夹即可。

本文由人人都是产品经理作者【亨亨】，微信公众号：【产品变量】，原创/授权 发布于人人都是产品经理，未经许可，禁止转载。

题图来自Unsplash，基于CC0协议

更多精彩内容，请关注人人都是产品经理微信公众号或下载App