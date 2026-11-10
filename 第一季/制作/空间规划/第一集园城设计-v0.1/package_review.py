"""Build a local review, measured palette and native-frame video package."""
import argparse,json,subprocess,hashlib,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--video',action='store_true');a=p.parse_args();root=Path(a.root);out=root/'视频制作/第一集园城设计-20261023-v0.1'
d=json.loads((out/'design-audit.json').read_text(encoding='utf8'))
titles=['书院：规整庭院与水墨层次','上层游园：主亭、附院与水庭','中层聚落：疏密变成院落与池水','下层园城：沿水布置与云隙','月窗：从孤立墙面接回庭院','水巷：低屋、院墙与近水路径']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
for k,(name,*_) in enumerate(d['review_views']):
    sheet=Image.new('RGB',(1920,594),'#18231f');draw=ImageDraw.Draw(sheet)
    for col,variant in enumerate(['before','after']):
        with Image.open(out/'views'/variant/(name+'.png')) as im:assert im.size==(960,540);sheet.paste(im,(960*col,54))
        draw.text((960*col+18,12),('原版  ' if col==0 else '新候选  ')+titles[k],font=font,fill='#e9e6d9')
    sheet.save(out/'views'/(name+'-compare.jpg'),quality=94)
panel=Image.new('RGB',(1280,792),'#18231f');dr=ImageDraw.Draw(panel)
for row,name in enumerate(['02-upper','03-middle']):
    with Image.open(out/'views'/(name+'-compare.jpg')) as im:panel.paste(im.resize((1280,396)),(0,row*396))
panel.save(out/'design-comparison.jpg',quality=94)
def srgb(v):return 12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
swatches=[]
for key,label in [('ink','书院深木 / 深瓦'),('paper','书院粉墙'),('gray','书院石色'),('roof','园城灰瓦'),('wood','暖木构件'),('wall','暖粉墙'),('stone','园石与路'),('green','植物'),('water','水色')]:
    rgb=[round(max(0,min(1,srgb(v)))*255) for v in d['palette_linear_rgba'][key][:3]];code='#'+''.join(f'{v:02x}' for v in rgb)
    swatches.append(f'<div class="swatch"><i style="background:{code}"></i><b>{label}</b><small>{code}</small></div>')
cards=[]
for title,(name,*_) in zip(titles,d['review_views']):
    cards.append(f'<section><h2>{title}</h2><div class="pair"><figure><img src="views/before/{name}.png"><figcaption>原版</figcaption></figure><figure><img src="views/after/{name}.png"><figcaption>新候选</figcaption></figure></div></section>')
page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第一集园城设计候选</title><style>body{margin:0;background:#15231f;color:#e8e8d9;font:17px/1.65 system-ui,'Microsoft YaHei';}main{max-width:1440px;margin:auto;padding:32px}h1{font-size:36px}h2{font-size:24px}p{max-width:1000px;color:#ced6ce}a{color:#c9dba9}section{margin:36px 0;border-top:1px solid #496053;padding-top:20px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img,video{width:100%;display:block}figcaption{padding:6px 0}.swatches{display:flex;flex-wrap:wrap;gap:12px}.swatch{width:130px;background:#26382f;padding:10px}.swatch i{display:block;height:54px}.swatch b,.swatch small{display:block;font-size:13px}.pill{background:#354c3c;padding:6px 12px;border-radius:30px;display:inline-block}@media(max-width:800px){.pair{grid-template-columns:1fr}main{padding:16px}}</style><main><span class="pill">Blender 实景候选 · 尚待作者采用</span><h1>让庭院、屋顶和留白一起成立</h1><p>58秒路线保留三个穿窗与末段贴水。沿线区分书院、层叠游园、临水街巷；保留采用色族，用主次建筑、院墙、廊与水庭组织疏密。</p><p><a href="../../第一季/制作/空间规划/第一集园城设计-v0.1/设计说明.md">设计说明</a> · <a href="garden-city-design-v01.blend">场景工程</a> · <a href="garden-city-flight-58s-v03.blend">飞行动画工程</a> · <a href="review/independent-diagnosis.md">原版运动诊断</a></p><section><h2>58秒新版复飞</h2><video controls preload="metadata" src="garden-city-flight-58s-v03.mp4"></video><p>原生24fps，未插帧。内部过窗时刻重新分配，总长仍58秒。声音、最终云光和生成模型效果不在本轮验收内。</p></section>'''+''.join(cards)+'''<section><h2>沿用材质，明确颜色的职责</h2><div class="swatches">'''+''.join(swatches)+'''</div><p>色块来自工程BSDF线性RGB输入，经标准sRGB转换；不是画面取样。深瓦/木构表现结构，浅墙表现体块，青绿留给水与植被；学校维持水墨方向。新旧对照机位、光照及渲染设置相同。</p></section><p>本地参考场景，非最终游戏资产或建筑工程设计。源版本保留；未提交视频生成模型。连续运动的舒适度与最终采用由作者观看判断。</p></main></html>'''
(out/'review.html').write_text(page,encoding='utf8')
if a.video:
    frames=out/'frames';assert all((frames/f'{i:04d}.png').exists() for i in range(1,1393));probes={}
    for name,start,count in [('garden-city-flight-58s-v03.mp4',1,1392),('E01-C-FAST-B01-30s-v03.mp4',1,720),('E01-C-FAST-B02-30s-v03.mp4',673,720)]:
        target=out/name;subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-start_number',str(start),'-i',str(frames/'%04d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(target)],check=True)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)]));assert int(info['streams'][0]['nb_read_frames'])==count;assert abs(float(info['format']['duration'])-count/24)<.001
        subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True);probes[name]=info
    for page,start in enumerate(range(1,1393,240),1):
        sheet=Image.new('RGB',(1600,1250),'#18231f');draw=ImageDraw.Draw(sheet)
        for j,f in enumerate(range(start,min(start+240,1393),12)):
            with Image.open(frames/f'{f:04d}.png') as im:sheet.paste(im.resize((400,225)),(j%4*400,j//4*250))
            draw.text((j%4*400+8,j//4*250+230),f'{(f-1)/24:.2f}s / {f}',fill='white')
        sheet.save(out/'review'/f'new-sequence-{page:02d}.jpg',quality=92)
    (out/'review'/'encoding-check.json').write_text(json.dumps(probes,ensure_ascii=False,indent=2),encoding='utf8')
manifest={str(f.relative_to(out)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in list(out.glob('*.blend'))+list(out.glob('*.mp4'))+list((out/'views').glob('*-compare.jpg'))}
(out/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('DESIGN_REVIEW_PACKAGED',a.video)
