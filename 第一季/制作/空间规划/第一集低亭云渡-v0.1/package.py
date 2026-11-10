"""Versioned review page and a plan derived from the saved transport data."""
import json,sys,math,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(sys.argv[1]);O=R/'视频制作/第一集低亭云渡-20261024-v0.1'
P=json.loads((O/'planning-data.json').read_text('utf8'));T=json.loads((O/'transport-data.json').read_text('utf8'))
im=Image.new('RGB',(1700,1120),'#edf0e6');d=ImageDraw.Draw(im)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
ink='#263e36';blue='#16828c';brown='#976848'
def pt(p):return (100+(p[0]+340)*2.12,180+(250-p[1])*1.78)
def line(points,fill,width=3):d.line([pt(p) for p in points],fill=fill,width=width)
def dash(a,b):
 a=pt(a);b=pt(b);L=math.dist(a,b)
 for q in range(0,int(L),22):
  e=min(q+12,L);d.line([(a[0]+(b[0]-a[0])*q/L,a[1]+(b[1]-a[1])*q/L),(a[0]+(b[0]-a[0])*e/L,a[1]+(b[1]-a[1])*e/L)],fill=blue,width=3)
d.text((65,35),'低亭云渡 · 园岛交通关系',font=font(39),fill=ink)
d.text((65,95),'院落、园岛高差与三处跌水保留；高塔退出天际线',font=font(23),fill=ink)
for i in sorted(P['islands'],key=lambda x:x['center'][2]):
 d.polygon([pt(p) for p in i['outline']],fill='#d2ddbd',outline='#769277')
for paths in P['internal_paths'].values():
 for p in paths:line(p,'#f9f6e9',6)
for w in P['water']:
 for p in [w['source_pool'],w['fall_xy']]:
  x,y=pt(p);d.ellipse((x-17,y-12,x+17,y+12),fill='#61a8a2')
 line([w['source_pool'],w['fall_xy']],blue,5)
for l in P['links']:line(l['points'],brown,7)
stations={s['id']:s for s in T['stations']}
for a,b in T['ferry_links']:dash(stations[a]['boat_center'],stations[b]['boat_center'])
for s in T['stations']:
 line(s['pier_points'],brown,5);line(s['gangway'],brown,4)
 x,y=pt(s['pavilion']['xy']);d.rectangle((x-7,y-6,x+7,y+6),fill=brown)
 x,y=pt(s['boat_center']);d.ellipse((x-6,y-6,x+6,y+6),fill=blue)
for i in P['islands']:
 x,y=pt(i['center']);label=f"{i['id']} {i['name']}  +{i['center'][2]}m"
 if i['id']=='E':label='E 云间亭  +72m'
 box=d.textbbox((0,0),label,font=font(20));ww=box[2]
 d.rounded_rectangle((x-ww/2-8,y-25,x+ww/2+8,y+8),7,fill='#f5f2e5')
 d.text((x-ww/2,y-23),label,font=font(20),fill=ink)
d.rounded_rectangle((65,944,1635,1080),16,fill='#dce4d6')
d.text((90,963),'棕色实线：实体栈桥 / E—F 两层短换层桥亭    青色虚线：云舟联系示意，未作航迹验证',font=font(22),fill=ink)
d.text((90,1001),'学园：地面 +126m → 云基内升降 14m → 侧港 +112m → 云舟接驳；无外露高塔',font=font(22),fill=ink)
d.text((90,1039),'俯视投影允许园岛重叠，实际标高不同。尺寸为创作推定；升降与云舟均为静态模型。',font=font(19),fill='#63766c')
im.save(O/'transport-plan.png')
captions=[('01-overview.png','七岛总览：高差保留，六组高塔撤除。'),('02-clear-structure.png','关闭局部云雾后的结构视图。'),('03-water-gardens.png','听瀑园：候舟亭与院落、池岸保持低矮轮廓。'),('04-low-waterside-pavilion.png','候舟亭—栈桥—登舟板—云舟，实际搭出的静态连接。'),('05-home-workshop.png','半园与作坊：候舟口避开跌水口，各自保留局部水庭。'),('06-school-hidden-port.png','学园侧港：云基内局部升降与出口，地面仍是低亭。')]
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>低亭云渡 v18</title><style>body{margin:0;background:#f3f1e7;color:#263e36;font:17px/1.7 system-ui,"Microsoft Yahei",sans-serif}main{max-width:1440px;margin:auto;padding:35px 5vw 65px}h1{font-size:38px}h2{margin-top:40px}img{width:100%;display:block;border-radius:9px}figure{margin:26px 0}figcaption,.meta{color:#63766c}nav{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}button{font:inherit;padding:9px 18px;border:1px solid #819986;border-radius:23px;background:transparent;cursor:pointer}button.active{background:#263e36;color:white}.note{padding:16px 22px;background:#e6e8dc;border-left:4px solid #9e6742}a{color:#167d7b}.links{display:flex;gap:25px;flex-wrap:wrap}</style><main><p class="meta">《未来女孩林知夏》 · 低亭云渡 v18 · 2026-10-24</p><h1>园岛有高差，房子保持低矮</h1><p>撤掉六组高层换层塔及其高架桥，七岛、九组院落、三处跨岛跌水与原建筑配色保留。低亭、栈桥和云舟承担接驳；半园入口仅保留跨 6 米高差的两层桥亭。</p><p class="note">本页为静态空间候选，云基、树石与水流仍属参考造型。云舟与升降装置未运行模拟；新58秒航线未制作、未重录。</p><nav><button class="active" data-src="01-overview.png">新版总览</button><button data-src="../第一集园岛深化-20261024-v0.1/01-overview.png">对照：上一版高塔</button><button data-src="02-clear-structure.png">结构清晰视图</button></nav><img id="hero" src="01-overview.png" alt="低亭云渡总览"><h2>候舟、登舟与云基侧港</h2>'''
for name,cap in captions[2:]:page+=f'<figure><img loading="lazy" src="{name}" alt="{html.escape(cap)}"><figcaption>{html.escape(cap)}</figcaption></figure>'
page+='''<h2>交通关系</h2><figure><img loading="lazy" src="transport-plan.png" alt="园岛交通关系图"><figcaption>虚线表示云舟联系意图，不是已经验证的飞行轨迹。岛内原园路继续使用，跨岛交通与水系分开。</figcaption></figure><p>学园局部升降行程为14米，井道与横廊在原云基中实际开口。轿厢展示在上层，下层门关闭；剩余岛际高差交给云舟。E—F 的两层换层桥亭保留原楼梯，仍有原14厘米入口台阶。</p><div class="links"><a href="low-pavilion-cloud-ferry-v18.blend">Blender工程</a><a href="README.md">修改说明</a><a href="audit.md">独立复核</a></div><p class="meta">如果聊天或网页中的工程链接未启动Blender，请在Blender使用“文件 → 打开”，选择本页同目录的 low-pavilion-cloud-ferry-v18.blend。</p></main><script>for(const b of document.querySelectorAll('button'))b.onclick=()=>{document.getElementById('hero').src=b.dataset.src;for(const c of document.querySelectorAll('button'))c.classList.toggle('active',b===c)};</script></html>'''
(O/'review.html').write_text(page,encoding='utf8')
(O/'README.md').write_text('''# 第一集低亭云渡 v18

作者指出园岛出现高楼感，本版修正交通设施主导天际线的问题。源v17保留，新版另存。

- 撤除 L1/L2/L3/L4/L6/L7 的塔楼、墙檐、阳台和相依高架桥；仅保留E—F之间6米高差、两层的L5桥亭。
- 七岛各设低候舟亭与云舟码头，B/C旧换层位置改小歇亭。码头沿实际园路接入；半园候舟口移至园路南侧拐点，避开出水口。
- 学园用云基内14米升降井与水平横廊接侧港，原实体云基实际局部切口。轿厢停在上层、下门关闭，运行和门联锁尚未模拟。不是把44米岛间高差全部塞进云基。
- 六条云舟联系只是交通网络意图；船、登舟板、候舟亭已建实体，但尚未模拟起降、回转、避让或班次。旧无人机路线未转成v18航线。
- 七岛位置/高度、九院落、三跌水及原材料节点保留。学校局部园路绕井改线；仅清除与新增通行带冲突的树石组，逐对象记录于transport-data.json。

## 文件

- `low-pavilion-cloud-ferry-v18.blend`：当前静态工程，Blender 5.1.0保存。
- `review.html`：六机位、前版同机位对照和交通图。
- `transport-plan.png`：实际岛形/道路/站点的俯视关系图，虚线不代表可执行航迹。
- `planning-data.json` / `transport-data.json`：构建数据、源文件哈希、删除与修改范围。
- `audit.md` / `audit.json`：独立静态审查证据及边界。

打开工程：启动Blender → 文件 → 打开 → 进入本目录 → 选择`.blend`。网页链接不能代替系统文件关联。

## 验收边界

当前用于视频参考前的空间判断。云基实体外轮廓、重复树石、船体细节仍简化；不是最终美术、可玩导航、真实建筑设计或云舟运行验证。58秒总预算保留，本轮未录新视频、未提交生成模型。既有采用稿与历史版本保持。
''',encoding='utf8')
(O/'.gitignore').write_text('*.log\n*.blend1\n__pycache__/\n*.pyc\n',encoding='utf8')
print('V18_PACKAGE_READY')
