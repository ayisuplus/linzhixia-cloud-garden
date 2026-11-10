# 分镜与生成：一个入口、两种视图

2026-10-18作者确认。资产图册独立；分镜图册和生成执行在一个HTML中切换，仍是不同职责，不增加第四份人工维护表。

## 数据与阅读顺序

- `atlas.json`为本场镜头事实源，保存稳定ID、实际图片、观看目的、摄影、动作、对白声音、起止与衔接、参考和限制；上游剧情稿仍提供创作依据。
- `plan.json`用schema_version 2，保存atlas_source、模型与规格核验记录、units。每批字段为id/title/shot_ids/method/head_handle/tail_handle/why/reference_strategy/safe_cut/fallback/runs；不复制动作、对白、提示词或派生时长。
- 构建器按镜号生成HTML、resolved-plan.json和prompt-G*.txt。派生文件用于交接，不独立修改。源数据改后重新构建；页面不提供在线编辑/自动保存。
- 分镜阅读：故事总览→编号/时长/观看目的→实际关键帧→摄影/表演/声音三栏→起点/终点/下一镜→折叠详情。母版可展开查看。多状态图并排，不重复主图，保留各帧限制与整镜限制。
- 执行阅读：批次总览→覆盖镜头缩略图与角色→成片/请求/余量→参考、剪点、失败拆法→完整提示词→真实执行与采用记录。一个批次可含多个镜头，调整批次不重编号镜头。
- 默认按故事顺序、每镜一次的整镜主计划；`coverage_order: edit_reorder`允许按生成需要将非连续整镜合批。每镜仍恰好一次，批次增加generation_note解释硬切与成片重排；story_ranges和beats.story_start/story_end从atlas推导。非连续批次timeline_start/end为null，界面逐镜显示成片区间，不把生成游标冒充故事时间。重试追加runs；镜内拆段仍需另行增加区间覆盖结构。

## 按需补充的分镜维度

direction可选字段：performance（可见表演）、space（位置、方向、支点）、lighting（光源与变化）、checks（相关待检项）。补充既有action/framing/sound，不另写一份冲突的动作时间线。共同身份与场景继承母版，按镜写变化。未知焦段、距离、角度、色温不填假数；不用的栏目不强填。

提示词逐镜展开当前状态、动作、摄影、表演、对白、声音、下一镜衔接、参考与限制；不依赖“同上”或聊天记忆。图册可以简洁，执行正文须独立可用。参考槽位、首尾帧或其他模式取决于实际端点，不强制“全能参考”“禁止首尾帧”或“每镜独立生成”。页面不发送请求，历史参数不等于现场能力已核验。

## 输入冻结与回填

准备提交时，在现有图册构建命令增加`--snapshot-unit G05 --snapshot-dir 项目内新目录`，同时提供root/manifest/plan。工具复制参考、记录哈希、镜头内容、规划参数与完整提示词，创建prepared输入快照；目录必须不存在。不覆盖、不提交、不生成任务ID。端点槽位等确定后仍须记录最终实际请求，不能把规划快照当服务回执。

每次运行在units[].runs追加对象，字段：status、snapshot（项目相对request.json）、engine、model_version、task_id、output、actual_seconds、issues、adoption、in_out。状态按实际填写prepared/submitted/running/failed/candidate/accepted。未知留空，不造示例回执。视频生成的实际运行须有工具、模型版本和任务ID；剪辑插镜不虚构模型任务ID。采用时in_out必须为真实视频内的[入点秒,出点秒]，adoption记录作者决定。

已提交输入和旧结果不随新分镜重建；下一次输入另建目录。校验检查快照结构/批次/文件哈希、视频输出路径和采用区间格式，不代替真实播放、声音检查、视觉质量或作者采用。

## 模板来源

借鉴作者提供的[AI漫剧分镜脚本模板](https://www.douyin.com/article/7689669127904558693)中的空间、表演、动作因果和视听同步维度，按镜头选用；未照搬全篇，特定生成平台的假设不作为项目规则。
