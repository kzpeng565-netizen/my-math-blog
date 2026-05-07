import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [
        // 核心：添加一个条件渲染器
    Component.ConditionalRender({
      component: Component.RecentNotes({
        title: "📅 最近更新",
        limit: 5,
        showTags: true,
      }),
      // 只有当页面的 slug 是 "index"（即首页）时才渲染
      condition: (page) => page.fileData.slug === "index",
    }),
    Component.Comments({
      provider: 'giscus',
      options: {
        repo: 'kzpeng565-netizen/my-math-blog',
        repoId: 'R_kgDOSWdnRw',
        category: 'Announcements',
        categoryId: 'DIC_kwDOSWdnR84C8g7E',
        mapping: 'pathname',
        strict: false,
        reactionsEnabled: true,
        inputPosition: 'bottom',
      }
    })
  ],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/jackyzha0/quartz",
      "Discord Community": "https://discord.gg/cRFFHYye7t",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer({
  title: "笔记目录", // 左侧显示的标题
  folderDefaultState: "open", // 👈 核心：设为 open 即可默认展开
  folderClickBehavior: "collapse", // 点击文件夹标题时折叠/展开
  useSavedState: true, // 记录用户上次的折叠状态（可选）
}),
  ],
  right: [
    Component.Graph(),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta(),],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({
      title: "笔记目录",
      folderDefaultState: "open", // 已为你设置为默认展开
      folderClickBehavior: "collapse",
      useSavedState: true,
    }),
  ],
  right: [],
}
