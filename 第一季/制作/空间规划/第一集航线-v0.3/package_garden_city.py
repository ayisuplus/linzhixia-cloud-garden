"""Package the actual Blender frames; never substitutes a concept image for geometry."""
import json, argparse, hashlib, html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();out=root/'视频制作/第一集浮空园城-20261022-v0.3'
d=json.loads((out/'route-layout.json').read_text(encoding='utf8'));c=json.loads((out/'route-checks.json').read_text(encoding='utf8'))
assert all(v['pass'] for v in c['routes'].values()) and all(v['pass'] for v in c['docks'])
assert c['source_unchanged'] and not c['preserved_scene_objects']['unexpected_changes'] and all(v['screen_transition_pass'] for v in c['reveals'])
assert hashlib.sha256((root/d['previous_source']).read_bytes()).hexdigest()==d['previous_sha256']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
seqs=[('A','学院外缘：从围合学园看向水庭',['V03-A0','V03-AM','V03-A1'],'C-G03 → C-G04｜离开熟悉的学院，先看到沿途水庭与远处园院。'),('B','云岸转角：先藏、露一角，再展开',['V03-B0','V03-BM','V03-B1'],'C-G04｜同一双层水榭、同一35mm焦距；靠真实位置变化，揭示云岸下的天空与悬廊。'),('C','进入水巷：先见邻里，再接近家',['V03-C0','V03-CM','V03-C1','V03-C2'],'C-G05 → C-G06｜弯岸和两岸住宅收住城市大景，最后落回半园桥与修复作坊。')]
rows=[]
for sid,title,ids,desc in seqs:
    sheet=Image.new('RGB',(len(ids)*480,340),'#ede9df');dr=ImageDraw.Draw(sheet)
    for i,cid in enumerate(ids):
        im=Image.open(out/(cid+'.png'));assert im.size==(1280,720);sheet.paste(im.resize((480,270)),(i*480,0));dr.text((i*480+12,281),f'{i+1:02d} · '+next(v['title'] for v in d['cameras'] if v['id']==cid),font=small,fill='#28413d')
    sheet.save(out/(sid+'-sequence.jpg'),quality=94)
    buttons=''.join(f'<button onclick="document.getElementById(\'seq{sid}\').src=\'{cid}.png\'">{i+1} · {html.escape(next(v["title"] for v in d["cameras"] if v["id"]==cid))}</button>' for i,cid in enumerate(ids))
    rows.append(f'<section><h2>{title}</h2><p>{desc}</p><div class="buttons">{buttons}</div><img id="seq{sid}" src="{ids[1]}.png"><a href="{sid}-sequence.jpg">并排查看全部位置</a></section>')
allframes=Image.new('RGB',(1600,5*260+80),'#ede9df');dr=ImageDraw.Draw(allframes);dr.text((20,15),'长洲 · 首集浮空园城空间草模 v0.3',font=font,fill='#28413d')
for i,cam in enumerate(d['cameras']):
    im=Image.open(out/(cam['id']+'.png'));x=(i%3)*533;y=(i//3)*260+75;allframes.paste(im.resize((520,293)).resize((440,247)),(x,y));dr.text((x+4,y+225),cam['id'],font=small,fill='#ffffff')
allframes.save(out/'all-views.jpg',quality=93)
def xy(x,y):return (45+(x+1570)*.66,50+(1130-y)*.62)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850"><rect width="1200" height="850" fill="#ede9df"/>']
for b in d['platforms']:
    x,y=xy(*b['center'][:2]);rx,ry=b['radii'];svg.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx*.66}" ry="{ry*.62}" fill="#c6d6c6" stroke="#739591"/>')
for pts,col in [(d['walk_points'],'#758997'),(d['flight_points'],'#af542f')]:svg.append('<polyline fill="none" stroke="'+col+'" stroke-width="3" points="'+' '.join(f'{xy(*v[:2])[0]},{xy(*v[:2])[1]}' for v in pts)+'"/>')
for label,point in [('学园',d['flight_points'][0]),('A · 水庭',d['reveal_pairs'][0]['target']),('B · 双层水榭',d['reveal_pairs'][1]['target']),('半园 / 作坊',d['flight_points'][-1])]:
    x,y=xy(*point[:2]);svg.append(f'<text x="{x}" y="{y-10}" font-family="Microsoft YaHei" font-size="20" fill="#28413d">{label}</text>')
svg.append('<text x="35" y="824" font-family="Microsoft YaHei" font-size="18" fill="#28413d">橙：包裹航线　蓝灰：步行主线　绿色椭圆仅表示云岸范围，不是实际轮廓／全城地图</text></svg>');(out/'route-plan.svg').write_text(''.join(svg),encoding='utf8')
limits='云质仍是简化形态代理，庭院之间仍偏分离平台与长桥；桥接建筑中层、屋顶与邻院地面交织尚未深化。树木、材质、水雾、水流均非最终美术。三组静态位置证明局部遮挡变化，不代表整条航线的动态节奏已验收。'
css='body{margin:0;background:#ede9df;color:#28413d;font:17px/1.8 system-ui,"Microsoft YaHei"}main{max-width:1280px;margin:auto;padding:42px}h1{font-size:42px;line-height:1.25}h2{margin-top:50px}img{display:block;width:100%;border-radius:6px}a{color:#8c462a}nav,.buttons{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}button{border:1px solid #6e8d82;background:#f7f3e9;padding:10px 15px;color:#28413d;cursor:pointer;border-radius:4px}button:focus{background:#c6d6c6}.note{padding:22px;background:#d8e2d7;border-left:5px solid #608276}.muted{font-size:15px;color:#61736b}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:12px;border-bottom:1px solid #bbc8bd}@media(max-width:700px){main{padding:16px}.grid{display:block}}'
body=f'<p>未来女孩林知夏 / EPISODE 01 · SPATIAL CANDIDATE v0.3</p><h1>城在云上，景随行程展开</h1><p>本轮重做首集航线沿途的空间组织。保留卧室、半园两岸、作坊与学院室内；撤掉地面底板与规则街区阵列。</p><nav><a href="episode1-floating-garden-v03.blend">Blender 工程</a><a href="route-plan.svg">真实坐标路线图</a><a href="README.md">制作说明</a><a href="route-checks.json">几何检查记录</a></nav><p class="note">空间草模／待作者审阅。包裹航线 {d["flight_distance_m"]/1000:.2f} km，步行主线 {d["walking_route_distance_m"]/1000:.2f} km。距离是建模工作假设，不是已确定的世界地理；本页没有生成或呈现正式剧情视频。</p><img src="V03-SIDE.png"><p>侧看高低云岸与桥下天空。实体云质负责承托；普通水雾只参与视觉。反重力内部技术未在本轮设计。</p>'
body+=''.join(rows)+f'<h2>重复遇见同一处景物</h2><div class="grid"><div><img src="V03-B1.png"><p>转角后第一次看清双层水榭。</p></div><div><img src="V03-MID.png"><p>独立回看机位：在另一高度重新看见同一座水榭和连接廊桥。此机位不是新增航点。</p></div></div><h2>水有来去，旅程有落点</h2><div class="grid"><div><img src="V03-WATER.png"><p>上池、叠水、下池与回水管占位；水榭已移到侧岸。不是水利工程验证。</p></div><div><img src="V03-HOME.png"><p>原半园、桥和对岸作坊继续作为收件落点。</p></div></div><h2>整个首集航线片段</h2><img src="V03-OV.png"><p>只覆盖首集沿途片段，不代表长洲全城平面。</p><h2>检查与尚未解决的内容</h2><p>包裹路径 {c["routes"]["parcel"]["samples"]} 个离散位置、步行主线 {c["routes"]["regional_walk"]["samples"]} 个离散位置未检出障碍或地面缺口。2557个原场景网格数量与预期变换保持；三组指定地标射线从被屏墙遮挡变为越过屏墙。</p><p class="note">{limits}</p><p class="muted">原始v0.1、v0.2仍保留。v0.2只证明尺度和粗路径，未落实浮空园城美术。所有画面为本地Blender实图，没有用概念图替代实际模型。</p>'
(out/'review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>长洲浮空园城 v0.3 · 首集空间审阅</title><style>'+css+'</style><main>'+body+'</main></html>',encoding='utf8')
readme=f'''# 第一集浮空园城空间 v0.3

本轮回应作者对v0.2“没有浮空城特点、没有园林移步换景”的修正。最新世界依据为《物质基础-卷三-城市与建筑-长洲云城-v0.3》；沿用项目production及shot-previs技能。

- 实际工程：[episode1-floating-garden-v03.blend](episode1-floating-garden-v03.blend)，[浏览审阅](review.html)。若聊天链接不唤起Blender，可在Blender中用文件→打开选择此文件。
- 删除新版中的大底板、落地支墩、规则方块阵列。用薄云岸、空隙、不同高度的庭院、悬廊、叠水重新组织沿途；148个新增住宅/院落翼部仍为粗体块。原版文件未修改。
- A/B/C三组使用真实路径上的位置与同一35mm焦距。月窗提供侧景线索，屏墙仍遮住主地标；B组形成遮住→局部露出→完整显露。水巷新增两次弯折，最后再接原半园水巷。不是复制《原神》资产或地图，而是把作者希望的发现与揭示落实为空间机制。
- C-G03学院外缘→C-G04水庭/层叠园城→C-G05两岸住家→C-G06作坊收件，剧情职责和原角色身份不变。双层水榭在不同高度反复出现，帮助认路；不新增故事事件。
- 叠水进入下一层收水池，水榭放侧岸；管线仅为回水去向占位。普通雾、实体云质分别建模，不设传送门，不确定反重力/推进实现方式。
- 航线{d['flight_distance_m']:.2f}m，步行主线{d['walking_route_distance_m']:.2f}m。没有把公里行程压成10秒；frame_end=1，未制作定时动画。

## 本轮实际验证

{c['routes']['parcel']['samples']}个包裹采样点（27偏移射线、≤0.5m步长）；{c['routes']['regional_walk']['samples']}个步行采样点（≤0.25m步长、三高度径向探测、地面支撑）。本次未检出障碍或地面缺口。寄收端支撑间隙约2mm。2557个原始网格的顶点/面数量与预期世界变换保持，学校仍按前版平移。此检查不是逐顶点坐标完整同一性证明、连续体碰撞、角色动作或游戏导航测试。新庭院支路/坡廊未作完整无障碍通行验证。

三组指定中心视线均先命中屏墙、后越过屏墙；B后视线命中目标水榭屋顶，C后视线命中作坊屋顶。不是所有像素的可见性测试。15张实图已用于本轮审阅；没有动态片段或声音。

## 独立复核与限制

独立空间审查确认浮空承托可读、B组三位置存在真实遮挡揭示、同一双层亭可从不同高度回认。复核指出白色薄饼式云岸、平台分离、直水巷和B0缺少线索；本轮已加实体月窗、弯水巷及抵近机位，前两项仍属于后续造型深化。

{limits}

所有原创成果留项目。Git保存工程、脚本及数据；PNG/JPG按项目规则本地保存，需随项目备份。当前为候选，不自动替换任何采用美术图。生成脚本：第一季/制作/空间规划/第一集航线-v0.3/。仅使用本地CPU渲染，未调用Meshy/云端生成或游戏引擎。
'''
(out/'README.md').write_text(readme,encoding='utf8')
ad=json.loads((root/'视频制作/资产图册-20261022-v1.6/assets.json').read_text(encoding='utf8'));f='视频制作/第一集浮空园城-20261022-v0.3/'
for item in ad['assets']:
    if item['id']=='SCENE-E01-DELIVERY-CORRIDOR-3D':
        item.update(name='第一集浮空园城航线｜遮挡与揭示空间草模',version='v0.3',status='空间候选：浮空与局部换景已建模，美术及全程节奏待审',path=f+'V03-SIDE.png',role='C-G01—C-G06沿途浮空承托、层叠庭院、三组换景和弯水巷',limits=limits,source=f+'README.md')
        item['related']=[{'path':f+'review.html','role':'当前空间与换景审阅'},{'path':f+'episode1-floating-garden-v03.blend','role':'当前可编辑Blender工程'},{'path':f+'B-sequence.jpg','role':'真实三位置遮挡对照'},{'path':'视频制作/第一集航线空间-20261022-v0.2/review.html','role':'历史v0.2：仅尺度铺开，浮空园城表现被作者指出不足'}]
ad['title']='未来女孩林知夏 · 资产图册 v1.7';ad['scope']+=' 航线空间v0.3按作者修正为浮空园城，沿用原资产ID，旧版留作历史。'
atlas=root/'视频制作/资产图册-20261022-v1.7';atlas.mkdir(exist_ok=True);(atlas/'assets.json').write_text(json.dumps(ad,ensure_ascii=False,indent=2),encoding='utf8')
manifest={'artifact':'episode1-floating-garden-v03','files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.suffix in ['.blend','.json','.html','.png','.jpg','.svg','.md'] and p.name!='delivery-manifest.json'],'images_reviewed_as':'Static geometric candidate; not final art, animation or author adoption'}
(out/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');print('GARDEN_PACKAGE_OK',len(ad['assets']),len(d['cameras']))
