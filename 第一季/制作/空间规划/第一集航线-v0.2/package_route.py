"""Publish route overview, actual-coordinate plan, evidence, and versioned asset atlas."""
from pathlib import Path
import argparse,json,math,hashlib,html
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();out=root/'视频制作/第一集航线空间-20261022-v0.2'
d=json.loads((out/'route-layout.json').read_text(encoding='utf8'));c=json.loads((out/'route-checks.json').read_text(encoding='utf8'))
assert all(r['pass'] for r in c['routes'].values()) and all(r['pass'] for r in c['docks']) and c['source_unchanged'] and c['old_adjacent_ramp_removed']
def xy(x,y):return (50+(x+1580)*.55,120+(1180-y)*.55)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="900" viewBox="0 0 1300 900"><style>text{font-family:Microsoft YaHei,sans-serif;fill:#263e36;font-size:17px}</style><rect width="1300" height="900" fill="#f2eee4"/><text x="35" y="42" font-size="30">第一集 · 跨街区寄送航线 v0.2</text>']
svg.append(f'<text x="35" y="76">飞行 {d["flight_distance_m"]/1000:.2f} km · 步行 {d["walking_route_distance_m"]/1000:.2f} km · {len(d["blocks"])} 个新增建筑体块｜模型距离，尚非世界观定案</text>')
for b in d['blocks']:
    x,y,z=b['center'];w,h,_=b['size'];px,py=xy(x-w/2,y+h/2);color='#a7aaa3' if 'SCHOOL' in b['district'] else '#c5b49b'
    svg.append(f'<rect x="{px}" y="{py}" width="{w*.55}" height="{h*.55}" fill="{color}" stroke="#7e887c" stroke-width=".5"/>')
for pts,col,dash in [(d['walk_points'],'#478294',''),(d['flight_points'],'#bc612f','stroke-dasharray="8 4"')]:
    st=' '.join(f'{xy(v[0],v[1])[0]},{xy(v[0],v[1])[1]}' for v in pts);svg.append(f'<polyline points="{st}" fill="none" stroke="{col}" stroke-width="3" {dash}/>')
for i,st in enumerate(d['stops']):
    px,py=xy(*st['point'][:2]);svg.append(f'<circle cx="{px}" cy="{py}" r="10" fill="#bc612f"/><text x="{px}" y="{py+5}" text-anchor="middle" style="fill:white;font-size:13px">{i+1}</text>')
    svg.append(f'<text x="1000" y="{180+i*55}">{st["label"]}</text>')
svg.extend(['<text x="1000" y="680" style="fill:#bc612f">虚线：包裹航线</text><text x="1000" y="710" style="fill:#478294">实线：跨区步行路</text>', '<text x="35" y="867">旧近邻学校坡道已移除；住家与作坊仍隔水相对。建筑仅占体积，结构、美术及边界转换待深化。</text></svg>'])
(out/'route-plan.svg').write_text(''.join(svg),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
sheet=Image.new('RGB',(1500,3*330+90),'#f1eee4');dr=ImageDraw.Draw(sheet);dr.text((20,16),'第一集 · 从宿舍到作坊的整条航线',font=font,fill='#263e36');dr.text((20,52),'距离已拉开；中间建筑先用体块铺实。',font=small,fill='#52695f');cards=[]
for i,v in enumerate(d['cameras']):
    src=out/(v['id']+'.png');im=Image.open(src);assert im.size==(1280,720);x=(i%3)*500+10;y=(i//3)*330+90;sheet.paste(im.resize((480,270)),(x,y));dr.text((x,y+275),v['title'],font=small,fill='#263e36')
    cards.append(f'<article><a href="{src.name}"><img src="{src.name}" loading="lazy"></a><h3>{v["title"]}</h3><p>{v["shots"]} · {v["lens_mm"]} mm</p></article>')
sheet.save(out/'route-sheet.jpg',quality=93)
css='body{background:#f1eee4;color:#263e36;font:17px/1.7 system-ui,"Microsoft YaHei";margin:0}main{max-width:1300px;margin:auto;padding:40px}h1{font-size:40px;margin:8px 0}h2{margin-top:40px}a{color:#286b76}nav{display:flex;gap:24px;flex-wrap:wrap}img{width:100%;display:block}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:24px}article{background:#fffaf0;padding:12px;border-radius:10px}.note{padding:20px;background:#dfe6db;border-radius:10px}.metrics{display:flex;gap:36px;padding:25px 0;font-size:23px}'
body=f'<p>FUTURE GIRL · EPISODE 01 / v0.2</p><h1>跨过街区，才抵达家与作坊</h1><div class="metrics"><span>航线 {d["flight_distance_m"]/1000:.2f} km</span><span>步行 {d["walking_route_distance_m"]/1000:.2f} km</span><span>{len(d["blocks"])} 个建筑体块</span></div><nav><a href="episode1-delivery-corridor-v02.blend">Blender 工程</a><a href="route-plan.svg">路线地图</a><a href="README.md">范围说明</a><a href="route-checks.json">检查记录</a></nav><p class="note">根据作者修正拉开学校与住家距离。旧近邻坡道退出当前布局；保留住家与作坊隔水相对。学校与城区之间已有学习庭院、叠水与薄雾、上中下三片园城及长水巷。新增建筑是粗体块，距离和地形仍为拍摄工作假设。</p><img src="V02-OV.png"><p>总览中的橙线是路线标记，仅总览渲染显示；实际场景没有实体发光航道。大底板用于尺度示意，不确定世界观中的固定地面。</p><h2>实际坐标路线图</h2><img src="route-plan.svg"><h2>按旅程顺序看空间</h2><div class="grid">'+''.join(cards)+'</div><h2>当前验证边界</h2><p>包裹路径3642个采样位置、跨区步行9755个采样位置，均无本次射线检测发现的障碍或地面缺口；寄收端点约2毫米台面间隙。离散检查不等于完整碰撞或角色动作验收。没有把1.8公里压成旧版10秒路径动画；正式飞行节奏、运镜、角色及建筑细化留待后续。</p>'
(out/'review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>第一集寄送航线 v0.2</title><style>'+css+'</style><main>'+body+'</main></html>',encoding='utf8')
f='视频制作/第一集航线空间-20261022-v0.2/';ad=json.loads((root/'视频制作/资产图册-20261022-v1.5/assets.json').read_text(encoding='utf8'))
for item in ad['assets']:
    if item['id']=='SCENE-E01-CONNECTED-SETS-3D':item['status']='历史空间候选：近邻学校布局已被作者否定，室内可复用';item['limits']+=' 当前跨区关系请见航线空间v0.2；旧文件保留。'
ad['title']='未来女孩林知夏 · 资产图册 v1.6';ad['scope']+=' 本版按作者修正新增公里尺度航线；旧近邻学校布局标记为历史。'
ad['assets'].append({'id':'SCENE-E01-DELIVERY-CORRIDOR-3D','name':'第一集跨街区寄送航线｜学校至作坊','category':'场景','version':'v0.2','status':'航线空间候选，距离与建筑体块待审','path':f+'V02-OV.png','role':'展开C段完整行程：学院、学习庭院、叠水薄雾、三片园城、长水巷和作坊','limits':'约1.80公里飞行、2.42公里步行是本轮建模尺度；建筑粗模、边界机制、正式运镜与角色尚未完成','source':f+'README.md','related':[{'path':f+'review.html','role':'九段机位与全程审阅'},{'path':f+'episode1-delivery-corridor-v02.blend','role':'可编辑Blender工程'},{'path':f+'route-plan.svg','role':'实际坐标地图'}]})
atlas=root/'视频制作/资产图册-20261022-v1.6';atlas.mkdir(exist_ok=True);(atlas/'assets.json').write_text(json.dumps(ad,ensure_ascii=False,indent=2),encoding='utf8')
print('PACKAGED',len(ad['assets']),'assets')
