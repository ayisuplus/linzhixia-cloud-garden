---
name: linzhixia-keyframe-atlas
description: "为《未来女孩林知夏》适配共用关键帧图册技能，定位本项目当前清单、双视图计划、数据格式与原命令；用于项目图册制作、精修和交接，保留本片采用及生成约束。"
---

# 《未来女孩林知夏》关键帧图册入口

图像用途、状态选择、连续性、缺口判读和HTML交接统一使用[共用关键帧图册](../../../../../OpenCut/toolkit/plugins/film-studio/skills/shot-design/references/keyframe-atlas.md)。这里仅适配本片的数据、双视图和既有命令。

## 本项目依据与约束

- 从项目根 `AGENTS.md`、`制作进度.md`、`创作速查卡.md` 和[制作职责约定](../linzhixia-production/SKILL.md)定位当前动作稿、清单、采用素材及候选；晨起v0.8、16镜和90秒只属历史示例，不是后续场次默认值。
- 图册是六步流程的“静帧”及“分镜与生成”的分镜视图，与全片播放共用镜号、画面和时长，不另建必经交付。执行视图遵循production技能；两边共用镜头资料，见[统一工作台规范](../linzhixia-production/references/unified-workspace.md)。
- 双视图在原命令加 `--plan 项目内批次目录/plan.json`，输出 `分镜与生成.html`；支持 `#storyboard`、`#execution`、镜号和批次ID入口。atlas为schema_version 1、计划为schema_version 2；不带plan的旧构建继续有效。
- 数据格式与本片补充字段见[图册规范](references/atlas-schema.md)；首次经验与判读示例按需读[项目经验](references/project-lessons.md)。稳定ID、原图、历史候选与来源路径保留，公共能力不自动迁移本片数据或页面。
- 图册精修保持已有画面和已定配色；作者明确要求改图时使用当前可用内置imagegen，记录来源、提示词和新版本。原创成果留在本项目，不自动导入Eagle；ToonFlow只在作者明确要求画布时使用。
- 动态试验沿作者合批策略，当前尽量一次生成多镜、每批用满已核实的30秒，难镜是批内重点验收项，不因风险标签默认拆短试片。实际结果暴露问题后再决定补帧或补拍；输入审阅与采用决定沿项目规则。
- 粗分镜、声音节奏和白模分工按[shot-design](../../../../../OpenCut/toolkit/plugins/film-studio/skills/shot-design/SKILL.md)；新试验按[低成本规则](../../../../../OpenCut/toolkit/plugins/film-studio/skills/video-execution/references/cost-routing.md)选择本地H3、必要时云端H3、真实失败支持时Seedance2.5，达标停止追加生成。图册整理本身不授予媒体生成或付费调用。

## 原命令保持有效

在本项目根运行，输入输出替换为当前场次实际路径：

```powershell
python .agents/skills/linzhixia-keyframe-atlas/scripts/build_atlas.py --root . --manifest 视频制作/本场次图册/atlas.json --output 视频制作/本场次图册/关键帧图册.html
```

只校验时使用 `--check-only`；共享实现仍为 `OpenCut/toolkit/scripts/atlas/build_atlas.py`，本地脚本仅保留兼容入口，不复制渲染器。链接恢复见[公共工具库](../../../../../OpenCut/toolkit/README.md)。静态图册、结构校验、动态验证和作者采用分别报告。
