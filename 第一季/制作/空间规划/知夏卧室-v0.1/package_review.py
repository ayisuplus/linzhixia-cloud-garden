"""Package actual renders for review; no reference pixels are redrawn."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve()
out=root/'视频制作/知夏卧室三维空间-20261022-v0.1'
labels=['卧室全景','床侧关系','贴地拖鞋','衣柜与窗侧','贴窗起点','通廊回望','庭院借景','贴窗终点']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
sheet=Image.new('RGB',(1120,4*355+78),'#f4f0e5');dr=ImageDraw.Draw(sheet)
dr.text((20,20),'知夏卧室 · 同一场景的 8 个机位 · 空间候选 v0.1',font=font,fill='#31463b')
cards=[]
for i,label in enumerate(labels):
    cid=f'C{i+1:02}';im=Image.open(out/f'{cid}.png').convert('RGB');im.thumbnail((552,311))
    x=(i%2)*560;y=78+(i//2)*355;sheet.paste(im,(x,y));dr.text((x+12,y+314),f'{cid}  {label}',font=font,fill='#31463b')
    cards.append(f'<figure><a href="{cid}.png"><img src="{cid}.png"></a><figcaption>{cid} · {label}</figcaption></figure>')
sheet.save(out/'camera-sheet.jpg',quality=93)
thumbs=Image.new('RGB',(1280,4*205),'#f4f0e5');d=ImageDraw.Draw(thumbs)
for i,idx in enumerate([0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,72]):
    im=Image.open(out/'path-frames'/f'{idx:04d}.png');im.thumbnail((320,180));x=i%4*320;y=i//4*205;thumbs.paste(im,(x,y));d.text((x+5,y+180),f'{idx/12:.2f}s',font=font,fill='#31463b')
thumbs.save(out/'path-contact.jpg',quality=92)
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>知夏卧室 · 空间与机位</title><style>body{margin:0;background:#f5f1e8;color:#33463a;font:17px/1.75 system-ui,"Microsoft YaHei"}main{max-width:1200px;margin:auto;padding:30px}h1{font-size:36px}a{color:#507b65}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:20px}figure{margin:0;background:#fffaf0;padding:10px;border-radius:8px}img,video{width:100%;display:block}figcaption{padding:10px}aside{padding:18px;background:#e6e9dc;border-left:4px solid #849a79}.plan{max-width:700px;margin:auto}small{color:#747c6d}</style><main><small>未来女孩林知夏 / 2026.10.22 / SPATIAL STUDY 01</small><h1>卧室、通廊入口与窗外庭院</h1><p>沿用现行布局与木色、暖墙、绿色织物方向。八个机位来自同一套三维几何，没有按镜头拆墙或移动家具。</p><aside>这是空间候选，不是最终美术：尺寸与未见区域为推断；布料、植物、家具细节为代理。闭柜与开帘只是当前检查状态，不代表晨起动作已完成。</aside><p><a href="zhixia-bedroom-v01.blend">可编辑 Blender 工程</a> · <a href="README.md">范围与检查记录</a> · <a href="camera-sheet.jpg">八机位总览</a></p><div class="grid">'''+''.join(cards)+'''</div><h2>贴窗路径 · 几何预演</h2><p>6.08秒，12fps，73帧。保存的摄影机沿窗平移1米，距玻璃0.23米；只验证当前空间与路径，不含波纹、水巷换景或正式动作节奏。</p><video controls preload="metadata" poster="C05.png" src="window-path.mp4"></video><h2>空间关系与机位</h2><img class="plan" src="plan.svg"><p><a href="spatial-checks.json">相机与尺寸检查</a> · <a href="walk-checks.json">拟定通路离散射线检查</a></p></main></html>'''
(out/'review.html').write_text(html,encoding='utf8')
files=['zhixia-bedroom-v01.blend','camera-sheet.jpg','window-path.mp4','plan.svg','spatial-checks.json','walk-checks.json']+[f'C{i:02}.png' for i in range(1,9)]
(out/'artifact-manifest.json').write_text(json.dumps({'status':'spatial candidate, author review pending','files':[{'path':f,'bytes':(out/f).stat().st_size,'sha256':hashlib.sha256((out/f).read_bytes()).hexdigest()} for f in files]},ensure_ascii=False,indent=2),encoding='utf8')
print('REVIEW_PACKAGE_OK')
