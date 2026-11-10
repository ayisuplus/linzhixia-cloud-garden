"""Package actual Blender renders, without modifying their image content."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集云海城市-20261023-v0.1';old=R/'视频制作/第一集园城航线重排-20261023-v0.1/frames';review=O/'review';review.mkdir(exist_ok=True)
frames=[505,697,817,241,481,1010,1177]
for f in frames:
 before=Image.open(old/f'{f:04}.png').convert('RGB');after=Image.open(O/'preview-v04'/f'{f:04}.png').convert('RGB');before=before.resize((960,540));sheet=Image.new('RGB',(1920,580),'#1f2c35');sheet.paste(before,(0,40));sheet.paste(after,(960,40));d=ImageDraw.Draw(sheet);d.text((12,12),f'BEFORE (EEVEE) / {(f-1)/24:.2f}s',fill='white');d.text((972,12),'CLOUD SEA CANDIDATE (CYCLES) / SAME CAMERA',fill='white');sheet.save(review/f'compare-{f:04}.jpg',quality=94)
text='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>云海中的园城 · 空间候选</title><style>body{background:#17232c;color:#edf1f2;font:18px/1.75 system-ui;max-width:1440px;margin:40px auto;padding:0 24px}img{width:100%;height:auto;border-radius:8px}a{color:#b5d8e6}figure{margin:28px 0}small{color:#b5c4cd}</style><h1>云海中的园城</h1><p>保留已认可的近景建筑和58秒航线，调整连续低云海、岸云厚薄和远景城区。这里展示实际 Blender 静帧，尚未重录58秒整片。</p><p><a href="cloudsea-city-v04.blend">可编辑 Blender 工程</a> · <a href="README.md">制作说明与检查范围</a></p><figure><img src="preview-v04/overview.png"><figcaption>额外全景检查机位，不插入原58秒航线。</figcaption></figure><h2>沿原航线的同机位对照</h2><p>左：上版EEVEE预览；右：本版Cycles渲染。相机一致，渲染器不同，因此照明细节也有差异；不能把全部亮度变化归因于云体修改。</p>'''
for f in frames:text+=f'<figure><img src="review/compare-{f:04}.jpg"><figcaption>{(f-1)/24:.2f} 秒 · <a href="preview-v04/{f:04}.png">查看新版原图</a></figcaption></figure>'
text+='<p>云海、远景与当前氛围均为候选；保留失败试验用于回溯。关键帧检查不等于连续飞行观看通过。</p></html>';(O/'review.html').write_text(text,encoding='utf8')
files=[O/'cloudsea-city-v04.blend',*sorted((O/'preview-v04').glob('*.png'))];manifest=[]
for f in files:
 if f.suffix=='.png':Image.open(f).verify()
 manifest.append({'file':str(f.relative_to(O)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(O/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');print('PACKAGED',len(files),'files')
