# 园城候选 v0.1 独立几何审查

本报告针对 build.local.log 已出现 DESIGN_CANDIDATE_READY 后保存的 garden-city-design-v01.blend，源哈希见 design-geometry-check.json。只读 CPU 检查，未改工程，未把首轮 after 图当成最终结果。

## 结论

当前不能通过布局完整性审查。原室内/原材质保护通过，但新增路网、种植和被替换屋顶附件存在实际交叠或残留，需修正后再冻结。

## 必须修正

1. **旧屋顶附件仍悬空。** roof-check.json 检出11条旧 Roof ridge cap 和11块 Filled roof gable 高出新屋面约2.16米。例：(-1310,999,46.30)的旧脊条，下方新 Learning garden 屋顶最高仅44.14。原因是新 long_y 屋面沿长边转向、按窄边重算起坡，而旧通用附件未纳入对应屋顶的隐藏清单。应随每个替换屋顶处理其旧附件，不能仅处理已移除40组庭院的附件。全部清单见 residual_above_new_roofs。
2. **环路直接穿院墙/建筑。** Linked garden walk_17/18.001 穿 Upper west annex 东墙/主厅；_44/45/46.001 穿 Upper east annex 前墙/主厅；_14/15.002 穿 Middle north study 主厅。应先确定院落边界，再绕院生成道路，不能让相同椭圆独立穿过固定庭院。
3. **连接路反穿自己的庭院。** Academy north study walk link_0 在约(-1363.60,1020.08,36.15)命中前墙，在(-1372,1038.25,36.09)命中侧屋墙。Middle north study walk link_0 在约(-698.71,636.8,23.43)命中前墙。固定朝南入口与按岛心极角选择的环路点不兼容；应从入口外侧的可达路点接入，必要时沿院墙外绕行。
4. **树种在路上、树穿房。** Shore pine group 与 Linked garden walk 使用同一椭圆半径(.64rx,.60ry)，多个树干直接占路。应把树布置在路侧并按树冠尺寸预留建筑净空。Upper moon pool bank pine 穿 Upper west court roof.001；Lower west pond bank pine 穿 Lower west court roof.001。Upper west/east annex、Middle north study、Quiet west study和Academy west study的院松冠穿主厅墙；小庭院需要按实际冠幅调整种植位置，不能统一(x+.25w,y+1)。
5. **C窗造景占既有水巷。** Moon C rock composition 的3块石和 framing pine 主干与 South waterside lane 相交。应沿完整既有道路边界避让，不能只避原飞行中心线。

以上道路报告中的320条命中是不同高度/横向采样结果，不是320处独立障碍；按path/obstacle去重查看即可。

## 已通过与需区分的结果

- 原29584个环境对象未删除；14408个变化均为设计脚本声明的隐藏对象，未发现未声明修改；材质节点/参数比对无变化，也无新增材质。源工程哈希前后一致。
- 原40组庭院区域的旧通用饰件残留筛查为0；但这不包含上文仍保留院落的新旧屋顶附件问题。
- 6个池塘与墙、台基、庭院铺面/新增道路的三角面交叉检查未报命中。该方法不排除完全包容关系，不能等同全场无重叠。
- 屋顶之间报告26组交叉，多为本来相接的主厅/侧屋，可先按接屋设计意图看最终图；不把全部屋面交点列为阻断。
- plant_structure_triangle_intersections保留了原始筛查结果，池岸岩石与水面、同树枝叶之间接触可能有意；必须修的是上文明确列出的墙、屋顶和道路相交。

## 检查边界

新路检查采用5个横向位置、3个人行高度沿各段射线，针对新增局部道路；不是全城可导航验证。几何交叉不替代最终视觉审查，未进行完整动画渲染或连续观看。源工程与旧成果保持不变。
