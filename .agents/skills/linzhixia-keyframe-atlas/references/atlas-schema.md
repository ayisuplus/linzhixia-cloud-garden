# 图册数据与命令

UTF-8 JSON。所有文件路径相对 `--root` 项目目录；限制为项目内已存在文件。生成的HTML根据输出目录计算相对链接。HTML名或目录不要求固定。

顶层字段：

统一工作台补充：`asset_atlas`为已存在资产图册路径，`scene_context`为本场共同身份/空间/美术约束。双视图需要asset_atlas，旧独立图册不要求。

- `schema_version`: 1。
- `title`, `subtitle`, `aspect_ratio`：图册标题、阶段说明、画幅。
- `source_manifest`：本次迁移的真实源清单路径。
- `story_script`：当前动作稿路径。
- `video_produced`: bool，是否已有本图册所称的正式视频；有部分试验时在subtitle中说明，不将试验当全片。
- `masters`: 数组，每项`id/title/path/role/status/limits`。status由来源决定，不因整理提升采用状态。
- `shots`: 按播放顺序排列，数量及秒数由场次决定。

每镜必填：

每镜可选`direction`：包含非空文本performance、space、lighting，以及checks字符串数组。补充表演、空间、光源和待检维度；既有action/dialogue/sound/next_link仍是镜头事实。所有限制与引用保留，不能只靠概要替代执行正文。

| 字段 | 内容 |
|---|---|
| `id`, `title` | 保留稳定镜头ID和名称 |
| `seconds`, `framing`, `purpose` | 正数时长预算、景别/机位、观众要看懂什么 |
| `presentation` | `{path, role, visible, missing, show_as_main, status}` |
| `refs` | `[{path, role}]`；presentation.path必须在refs中明确出现 |
| `entry_state`, `exit_state` | 计划动作起点、终点；不声称静帧同时具有这两个状态 |
| `action`, `dialogue`, `sound` | 视频计划与声音 |
| `invariants` | 非空字符串数组，关键保持项 |
| `next_link` | 如何接下一镜；最后一镜写段落结束 |
| `priority` | `normal` / `trial` / `gap`，普通/建议动态试验/缺完整画面 |
| `trial_recommended` | 可选bool，独立标记建议动态试验；缺画面镜头也可为true。未填时兼容旧数据，按priority为trial推断 |

`presentation.role`允许`opening`（起始）、`action`（关键动作）、`ending`（结束）、`interface`（界面）、`reference`（辅助参考）、`gap`（缺完整画面）。

- `show_as_main: false`时必须`role: gap`且`priority: gap`，主画面位置显示缺口；path仍可指向现有辅助图。
- `role: reference`不可展示为完整镜头主图；把该镜记为gap，并在refs中解释辅助用途。
- 角色起始或结束只有在图片实际吻合时使用。角色明确不等于已动态验证，status和missing保留局部限制。

最小单镜实例（文件路径只是格式示意，使用前换成真实文件）：

```json
{
  "id": "E02-B-003",
  "title": "把盒子交给对方",
  "seconds": 5,
  "framing": "两人中景",
  "purpose": "让观众看清谁接过盒子",
  "presentation": {"path": "素材/交接.png", "role": "action", "visible": "双方都扶着盒子。", "missing": "尚未松手。", "show_as_main": true, "status": "交接状态候选"},
  "refs": [{"path": "素材/交接.png", "role": "双手交接状态"}],
  "entry_state": "甲持盒，乙伸手。",
  "exit_state": "乙接稳，甲松手。",
  "action": "甲递出，乙接稳后甲才松手。",
  "dialogue": "无",
  "sound": "轻微纸盒摩擦声",
  "invariants": ["只有一个盒子，交接时始终有人承托"],
  "next_link": "下一镜由乙持盒开始。",
  "priority": "trial"
}
```

验证失败会返回非零退出码，不生成新HTML；不会擅自补图或把辅助图升格。检查包括重复ID、无效角色、主图引用不符、缺文件、缺口配置冲突和越出项目路径。视觉质量、动作可达性、作者认可状态需另行审阅。


## 可选制作分组入口

`state_frames` 可按镜头填写有序数组，每项 `{path, label, role, visible, limits}`，role限opening/action/ending。用于有实际起始、过程、结束图的镜头，直接在制作卡显示；每张也须列入该镜refs。没有多张图时不填，不因此要求每镜三帧。同机位状态对照不等于视频摄影机轨迹已经制作。

`production_guide` 可填写 `{ "path": "项目相对路径/生成分组.html", "label": "生成分组", "summary": "分组与验证状态摘要" }`。渲染器验证目标存在，在图册导航与正文顶部显示入口；分组计划另行记录覆盖、生成上限、成片时长与剪辑余量，不改变单镜秒数或把静帧升级为动态验收。
