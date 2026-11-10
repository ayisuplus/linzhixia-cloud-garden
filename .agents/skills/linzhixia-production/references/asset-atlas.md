# 资产图册

图册是唯一供人审阅的资产交付物。可搜索卡片展示原图和最少信息，不再配一张独立资产表。

数据源字段：`title`、`scope`、`assets`。每项为 `id`、`name`、`category`、`version`、`status`、`path`、`role`、`limits`、`source`。文件路径相对于项目根目录；`source`是采用依据或原记录文件路径。`related`可选，包含`path`和`role`，供四视图、拆解、提示词等附属参考。已有ID沿用；若源记录只有节点UUID可沿用UUID作追溯ID，不按排序每次重编号。

`status`用明确的人类描述，如作者采用、方向认可、候选待审、历史停用；显示原有争议与局部限制。`path`应指向真实主图，不能把尚未生成的路径塞入图册。缺图另写在scope或上游需求文档。历史候选可折叠或归档，不能悄悄提升为采用。

例如：

```json
{"title":"本场资产图册","scope":"仅本场已存在参考，不代表全项目资产齐全", "assets":[{"id":"PROP-001","name":"道具名","category":"道具","version":"v1","status":"候选待审","path":"素材/道具.png","role":"约束结构，不约束本镜姿态","limits":"背面尚未验证","source":"素材/生成记录.md","related":[]}]}
```

在项目根目录执行：

```powershell
python .agents/skills/linzhixia-production/scripts/build_asset_atlas.py --root . --manifest 视频制作/本场资产图册/assets.json --output 视频制作/本场资产图册/资产图册.html
```

生成器只校验文件、编号和必要说明，不能据此宣称图片已被目视验收。分享时携带引用图片，不以HTML和Git代替媒体备份。
