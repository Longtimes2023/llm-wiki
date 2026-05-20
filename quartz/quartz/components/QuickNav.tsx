import { QuartzComponent, QuartzComponentConstructor } from "./types"
import { classNames } from "../util/lang"

const QuickNav: QuartzComponent = ({ displayClass }) => {
  return (
    <div class={classNames(displayClass, "quick-nav")}>
      <h3>快速导航</h3>
      <ul>
        <li><a href="/wiki/overview" class="internal">📚 知识库总览</a></li>

        <li class="nav-divider">主题入口</li>
        <li><a href="/wiki/topics/AI%E5%86%85%E5%AE%B9%E5%88%9B%E4%BD%9C" class="internal">✍️ AI 内容创作</a></li>
        <li><a href="/wiki/topics/AI%E5%88%9B%E6%84%8F%E8%AE%BE%E8%AE%A1" class="internal">🎨 AI 创意设计</a></li>
        <li><a href="/wiki/topics/AI%E7%BC%96%E7%A8%8B%E5%BC%80%E5%8F%91" class="internal">💻 AI 编程开发</a></li>
        <li><a href="/wiki/topics/AI%E4%BA%A7%E5%93%81%E7%BB%8F%E7%90%86%E5%B7%A5%E4%BD%9C%E6%B5%81" class="internal">📐 AI 产品经理</a></li>
        <li><a href="/wiki/topics/AI%E8%90%A5%E9%94%80%E8%B6%8B%E5%8A%BF" class="internal">📣 AI 营销趋势</a></li>
        <li><a href="/wiki/topics/AI%E5%8A%9E%E5%85%AC%E8%87%AA%E5%8A%A8%E5%8C%96" class="internal">🗂️ AI 办公自动化</a></li>
        <li><a href="/wiki/topics/%E6%95%B0%E6%8D%AE%E9%A9%B1%E5%8A%A8%E8%BF%90%E8%90%A5" class="internal">📊 数据驱动运营</a></li>
        <li><a href="/wiki/topics/%E9%B1%BC%E7%9A%AE%20AI%20%E6%8C%87%E5%8D%97" class="internal">🐟 鱼皮 AI 指南</a></li>

        <li class="nav-divider">素材摘要</li>
        <li><a href="/wiki/sources" class="internal">📁 所有素材 (32)</a></li>

        <li class="nav-divider">综合分析</li>
        <li><a href="/wiki/synthesis" class="internal">🔬 综合报告 (1)</a></li>

        <li class="nav-divider">对比分析</li>
        <li><a href="/wiki/comparisons" class="internal nav-placeholder">⚖️ 暂无对比分析</a></li>

        <li class="nav-divider">其他</li>
        <li><a href="/log" class="internal">📋 更新日志</a></li>
      </ul>
    </div>
  )
}

QuickNav.css = `
.quick-nav {
  margin-bottom: 1.5rem;
}

.quick-nav h3 {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--gray);
  font-weight: 600;
  margin: 0 0 0.6rem 0;
}

.quick-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid var(--lightgray);
  border-radius: 10px;
  overflow: hidden;
}

.quick-nav li a {
  display: block;
  padding: 0.42rem 0.85rem;
  font-size: 0.84rem;
  color: var(--darkgray);
  text-decoration: none;
  border-bottom: 1px solid var(--lightgray);
  transition: background 150ms ease, color 150ms ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-nav li:last-child a {
  border-bottom: none;
}

.quick-nav li a:hover {
  background: color-mix(in srgb, var(--secondary) 10%, transparent);
  color: var(--secondary);
}

.quick-nav li a.nav-placeholder {
  color: var(--gray);
  font-style: italic;
  cursor: default;
  pointer-events: none;
}

.quick-nav li.nav-divider {
  padding: 0.28rem 0.85rem;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--secondary);
  background: color-mix(in srgb, var(--secondary) 8%, transparent);
  border-bottom: 1px solid var(--lightgray);
}
`

export default (() => QuickNav) satisfies QuartzComponentConstructor
