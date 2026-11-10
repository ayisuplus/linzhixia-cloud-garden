"""Build review from saved scene metadata and rendered views."""
import json,argparse,html,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();out=root/'视频制作/第一集三维场景与道路-20261022-v0.1'
d=json.loads((out/'episode-layout.json').read_text(encoding='utf8'));checks=json.loads((out/'spatial-checks.json').read_text(encoding='utf8'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
sheet=Image.new('RGB',(1440,math.ceil(len(d["cameras"])/2)*305+100),'#eee9dd');dr=ImageDraw.Draw(sheet);dr.text((24,20),'未来女孩 · 第一集空间与道路 / v0.1',font=font,fill='#233d36');dr.text((24,57),'同一场景 · 完整墙体 · 尺度与连接为候选，非最终美术',font=small,fill='#53675d')
cards=[]
for i,c in enumerate(d['cameras']):
    src=out/(c['id']+'.png')
    # Preserve exact 16:9 ratio on the contact sheet.
    im=Image.open(src).resize((480,270));x=16+(i%2)*712;y=100+(i//2)*305;sheet.paste(im,(x,y));dr.text((x+492,y+12),c['id'],font=small,fill='#30463c')
    title=c['title'];dr.text((x+492,y+44),title[:9],font=small,fill='#30463c');dr.text((x+492,y+70),title[9:],font=small,fill='#30463c');dr.text((x+492,y+104),str(c['lens_mm'])+' mm',font=small,fill='#30463c')
    cards.append(f'<article><a href="{src.name}"><img src="{src.name}" loading="lazy"></a><h3>{c["id"]} · {c["title"]}</h3><p>{c["lens_mm"]} mm · {c["shot_groups"]}</p></article>')
sheet.save(out/'camera-sheet.jpg',quality=92)
def xy(x,y):return (90+(x+58)*11,100+(68-y)*11)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1050" viewBox="0 0 1100 1050"><style>text{font-family:Microsoft YaHei,sans-serif;fill:#283d36;font-size:16px}</style><rect width="1100" height="1050" fill="#f4f0e6"/><text x="32" y="35" font-size="27">第一集 · 空间连接与道路候选</text><text x="32" y="64">按保存坐标绘制 / 学院地坪 +6 m，城区 ±0 m；连接机制未定</text>']
def rect(a,b,c,e,color,label):
    x,y=xy(a,e);svg.append(f'<rect x="{x}" y="{y}" width="{(c-a)*11}" height="{(e-b)*11}" fill="{color}" stroke="#757b70"/><text x="{x+4}" y="{y+18}">{label}</text>')
rect(-57,42,-13,66,'#dddeda','水墨学院');rect(-54,50,-46,58,'#ded0bc','宿舍');rect(-44,49,-29,61,'#b9c3c2','水庭');rect(-27,49,-15,61,'#d9d5c9','舞室 / 小展示')
rect(-5,19,9.5,27,'#e1cfb2','修复作坊');rect(-22,10.8,17,16.2,'#a4c7bc','水巷');rect(-3,-3,3,2.4,'#d3c6af','卧室');rect(5.9,-2,11.9,3.8,'#dfc7a8','起居室');rect(-3,2.6,3.1,8.65,'#b9c9a4','庭院');rect(-12,20.4,-6,32.3,'#a4c7bc','叠水')
colors=['#b56535','#8a693e','#725c9a','#617a9d','#ba7450','#b18b42','#9d7151','#168d99','#67754a','#9275a5','#278c7b']
route_names={'home_to_work':'住家—作坊','home_to_living':'卧室—起居','dorm_to_dispatch':'宿舍—寄件口','dorm_to_hall':'宿舍—舞室','school_to_work':'学院—城区（暂定）','dock_to_repair':'收件—工作台','trial_line':'试穿走线','parcel':'包裹飞行','backstage_to_floor':'后台—展示地面','neighbour_walk':'西侧景观步道','east_garden_walk':'东侧园路'}
for i,(n,r) in enumerate(d['routes'].items()):
    pts=' '.join(f'{xy(v[0],v[1])[0]},{xy(v[0],v[1])[1]}' for v in r['points']);dash=' stroke-dasharray="7 5"' if r['kind']=='flight' else ''
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{colors[i]}" stroke-width="3"{dash}/>')
    xx=36+(i%4)*260;yy=896+(i//4)*29;svg.append(f'<line x1="{xx}" y1="{yy}" x2="{xx+22}" y2="{yy}" stroke="{colors[i]}" stroke-width="4"/><text x="{xx+30}" y="{yy+5}">{route_names[n]}</text>')
svg.append('<text x="36" y="1030">实线：人员路线；虚线：运送代理路线。仅离散几何检查，尚未绑定角色动作。</text></svg>');(out/'plan.svg').write_text(''.join(svg),encoding='utf8')
rows=''.join(f'<tr><td>{route_names[n]}</td><td>{r["samples"]}</td><td>{len(r["obstacle_hits"])}</td><td>{len(r["floor_gaps"])}</td></tr>' for n,r in checks['routes'].items())
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>未来女孩 · 第一集空间</title><style>body{margin:0;background:#f0ede4;color:#263d34;font:16px/1.7 system-ui,"Microsoft YaHei"}header,main{max-width:1280px;margin:auto;padding:28px}header{padding-top:56px}h1{font-size:40px;margin:0}h2{margin-top:42px}a{color:#246c73}nav{display:flex;gap:24px;flex-wrap:wrap}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:24px}article{background:#fffaf1;padding:12px;border-radius:10px}img,video{width:100%;display:block}h3,p{margin:9px 0}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:10px;border-bottom:1px solid #cbcabc}.note{padding:20px;background:#e0e6dc;border-radius:10px}</style><header><p>FUTURE GIRL · EPISODE 01</p><h1>从家，到作坊，再到书院</h1><p>空间与道路 v0.1 · 本地 Blender 可编辑候选</p><nav><a href="episode1-connected-sets-v01.blend">打开 / 下载 Blender 工程</a><a href="plan.svg">路线平面图</a><a href="README.md">范围与待确认项</a><a href="spatial-checks.json">几何检查记录</a></nav></header><main><img src="E01-OV.png"><p class="note">沿用卧室母版；扩展起居室、分岸作坊、试穿区、收件口、书院宿舍、水庭、舞室和沿途道路。学院外部保持水墨色；宿舍私人空间保留暖色。学校与城区的坡道、展示场地复用、全部新尺寸仍是空间候选，非作者采用决定。</p><h2>连接关系</h2><img src="plan.svg"><h2>实际保存机位</h2><div class="grid">'''+''.join(cards)+'''</div><h2>通路检查</h2><p>采样间距不超过 0.20 m；人员半径 0.25 m，三档高度射线及脚下支撑；飞行使用代理外廓偏移射线。结果仅支持这组离散路线，不代表最终角色碰撞或游戏导航验收。</p><table><tr><th>路线</th><th>采样点</th><th>障碍命中</th><th>地面缺口</th></tr>'''+rows+'''</table><p>原卧室文件哈希已核对；旧素材与旧图册保留。代理造型、流体、角色表演与全息换景未完成。</p></main></html>'''
(out/'review.html').write_text(page,encoding='utf8')
print('REVIEW_PACKAGED',out)
