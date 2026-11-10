# LibTV Marketplace

LibTV 的 Codex 插件目录，只提供一个生产插件：[`libtv`](plugins/libtv)。

| 安装标识 | 展示名 | 连接地址 | 版本 |
| --- | --- | --- | --- |
| `libtv` | LibTV | `https://mcp.liblib.tv/mcp` | `1.0.0` |

接入方式是 Codex 原生 HTTP Remote MCP：插件不预置 client ID、回调地址或凭据，也不含本地
server，客户端按服务端 OAuth 元数据完成注册与登录。

## 安装

本仓库公开可读，无需 GitHub 授权，本机 Git 能正常访问 GitHub 即可。

```bash
codex plugin marketplace add https://github.com/liblib-ai/marketplace.git --ref main
codex plugin add libtv@libtv        # 生产：https://mcp.liblib.tv/mcp
```

装完重新加载插件或新建 Codex 任务，在 MCP 连接管理里对 `libtv` 完成 LibTV OAuth 登录即可
使用。每位使用者用自己的 LibTV 身份完成授权。

> 装过按环境拆包时期旧 `libtv` 的同学，请先 `codex plugin remove libtv` 再安装，否则新包会与
> 残留配置争同一个 `mcp_servers.libtv` 项。测试包 `libtv-test` 与预发包 `libtv-pre` 已从本
> 目录撤下：已安装者可继续使用，但不再收到更新。

## 随包 Skills

| Skill | 展示名 | 用途 |
| --- | --- | --- |
| `libtv-to-treatment` | LibTV 导演提案 | 把画布里的图片、视频、音频、剧本与分镜整理成中文 16:9 可翻页导演提案 |
| `libtv-blender-live-action` | LibTV Blender联动视频生成 | 出图 → Blender 白模运镜 → Seedance 2.5 实拍化的完整制作链路 |
| `music-driven-product-ad` | LibTV 编曲成片 | 配乐驱动的一镜到底产品广告，自带 8 首曲谱与 macOS 演奏/录屏脚本 |

三者都依赖 LibTV Remote MCP，需先完成授权；纯生成媒体或普通编辑画布不会触发它们。
`music-driven-product-ad/scripts/` 只含 Swift 源码，使用前需自行编译，并要求 macOS 15+。

## 更新

```bash
codex plugin marketplace upgrade libtv
codex plugin add libtv@libtv
```

更新后新建 Codex 任务验证。未授权时连接地址返回 `401` 并给出 `WWW-Authenticate: Bearer`，
两个 OAuth well-known 端点返回 `200`，这是预期状态。

## 许可

`music-driven-product-ad` 自带曲谱资产。除 `mendelssohn-wedding-march` 外，Mutopia 版本均为
**公有领域**；该曲源版及其衍生曲谱为 **CC BY-SA 4.0**（排版 © 2017 Alexander Brock，基于
Durand & Cie. 出版的 Dubois 改编版，plate D. & F. 9516）。分发与再发布须保留该署名与许可
声明，详见 `plugins/libtv/skills/music-driven-product-ad/references/repertoire.md` 与
`assets/scores/catalog.json`。
