---
name: linzhixia-production
description: 为《未来女孩林知夏》适配故事到成片插件，定位本项目采用内容、图册数据与原有制作脚本；用于项目制作和交接。
---

# 《未来女孩林知夏》制作入口

先读项目根目录AGENTS.md、制作进度.md、制作配置.json；最新作者决定优先。本技能保留项目入口，通用制作方法唯一维护于[film-production](../../../../../OpenCut/toolkit/plugins/film-studio/skills/film-production/SKILL.md)，按任务只加载对应专项技能。

主流程沿共用技能：**灵感 → 故事 → 剧本 → 资产 → 静帧 → 视频**。分镜、预演与声音试配在全片静帧中统一审阅；既有资产/分镜/生成数据是职责划分，不是额外必经阶段。沿现有入口逐步整合，不迁移历史文件。

## 本项目保留项

- 剧情、角色、服装、配色、现有素材与采用状态沿当前进度，不从插件示例或另一作品继承。
- 资产图册、带图分镜、生成执行三项职责保留；JSON仅为内部数据，不增手工维护表。稳定ID、旧素材、拒绝候选和历史输入不移动、不重编号。
- 生成视频（含本地试验）前按已有要求审阅逐镜完整输入。已有同范围授权不重复询问；输入实质修改只重新审受影响部分。
- 新视频执行按最低成本有效方案：本地H3可做且可用则优先；需视频输入用已核实云端H3；实际H3失败及原因支持才升级Seedance2.5；达标停止追加生成。旧模型默认不再支配新执行，历史计划/任务保留。
- 尽量合并并用满当次已核实上限；复杂镜头不默认拆短试片。先完整合理批次，实际失败后再局部补拍；不可吞对白或拖慢正片。
- 原创成果留本项目，后期沿达芬奇；不强制ToonFlow或Eagle。工具连接/认证和GPU可用性现场核实。

## 既有数据与命令

- 资产制作按[资产规范](references/asset-atlas.md)，沿用scripts/build_asset_atlas.py。
- 分镜与关键帧沿用[linzhixia-keyframe-atlas](../linzhixia-keyframe-atlas/SKILL.md)，其references和scripts保留。
- 生成交接按[镜头表规范](references/video-handoff.md)，沿用scripts/validate_generation_plan.py及现有输入快照工具。原命令保持显式--root，不复制共享渲染器。
- [统一工作台规范](references/unified-workspace.md)继续管分镜/生成双视图；动作、对白、起止和参考只维护一处，批次引用镜号，时长与提示词派生。
