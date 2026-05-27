---
title: 把这几个产品经理skills焊死到Claude上！
source_url: https://www.woshipm.com/ai/6376737.html
author: 秀琴江湖飘
source: 人人都是产品经理
published: 2026-04-14
fetched_at: 2026-05-26
fetched_via: local_python_html_extract
---

# 把这几个产品经理skills焊死到Claude上！

> 还在为写PRD、做竞品分析、画用户画像熬夜？把这套产品经理Skills焊死到Claude上，一个命令搞定。本文手把手教你安装pm-toolkit，用AI把完整工作流程复制进去，让琐碎文档不再占用你的核心时间。

上周写了一篇建议所有产品经理重新学一次Claude的用法。

之所以把skils放到今天这篇文章，原因是在工作中，别一上来就把他当成万能的，你什么都不用管。

那么这篇文档我将从头到尾告诉你如何使用你的skils。

安装教程：

1、打开你的Claude，在终端运行：

```bash
claude plugin marketplace add phuryn/pm-skills
```

2、一键安装全部：

```bash
claude plugin install pm-toolkit@pm-skills && claude plugin install pm-product-strategy@pm-skills && claude plugin install pm-product-discovery@pm-skills && claude plugin install pm-market-research@pm-skills && claude plugin install pm-data-analytics@pm-skills && claude plugin install pm-marketing-growth@pm-skills && claude plugin install pm-go-to-market@pm-skills && claude plugin install pm-execution@pm-skills
```

3、验证安装：

```bash
claude plugin list
```

如果展示的和作者一样，那么说明安装成功了，接下来当你需要它帮你工作的时候只需要在输入框中：`/pm-****`。

当然你可能不知道安装的这些 skils 是啥意思，作者整理了常用的几个场景。

| 场景 | 命令 |
|------|------|
| 撰写 PRD | `/pm-execution:create-prd` |
| 竞品分析 | `/pm-market-research:competitor-analysis` |
| 用户画像 | `/pm-market-research:user-personas` |
| 功能优先级 | `/pm-product-discovery:prioritize-features` |
| SWOT 分析 | `/pm-product-strategy:swot-analysis` |
| OKR 制定 | `/pm-execution:brainstorm-okrs` |

到这一步基本上就已经完结了。下面作者通过写一份关于视频播放的需求文档，看一下效果怎么样。

同样在你的终端输入 `/pm-execution:create-prd`，告诉它你的需求。你安装好这个 skils 最大作用是它会把你的完整的工作流程全部复制进去。

这些提示是它能否写到你心里的关键要素，不妨多花点时间去打磨这些问题。会有意想不到的收获。

最终它会生成 `.md` 文档，这里还要感谢群里的小伙伴的无私奉献。

如果你觉得 md 文档观赏不高，那么你可以用这个网站来进行编译：https://md.sszgr.com/

最后还是那句话，老师傅一出手、就知有没有。希望你有了这些工具能大幅度提高自己的工作效率，今后不把大量琐碎的工作占用自己的时间。别画图，写文档了。

本文由人人都是产品经理作者【秀琴江湖飘】，微信公众号：【秀琴江湖飘】，原创/授权 发布于人人都是产品经理，未经许可，禁止转载。
