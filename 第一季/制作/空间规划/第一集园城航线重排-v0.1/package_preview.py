"""Local review sheets and player, using only rendered frames."""
from pathlib import Path
import json, argparse, html
from PIL import Image, ImageDraw
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--folder',default='preview');a=p.parse_args()
root=Path(a.root);out=root/'视频制作/第一集园城航线重排-20261023-v0.1';review=out/'review';review.mkdir(exist_ok=True)
paths=sorted((out/a.folder).glob('*.png'))
paths=[f for f in paths if (int(f.stem)-1)%12==0]
for k in range(0,len(paths),20):
    sheet=Image.new('RGB',(1600,1250),'#172322');d=ImageDraw.Draw(sheet)
    for j,f in enumerate(paths[k:k+20]):
        im=Image.open(f).convert('RGB');im.thumbnail((400,225));x=(j%4)*400;y=(j//4)*250;sheet.paste(im,(x,y));d.text((x+8,y+230),f'{(int(f.stem)-1)/24:.1f} s / {f.stem}',fill='white')
    sheet.save(review/f'sequence-{k//20+1:02}.jpg',quality=92)
doc='''<!doctype html><meta charset="utf-8"><title>58秒 · 航线重排与沿线园城</title><style>body{margin:32px auto;max-width:1200px;background:#172322;color:#eee;font:18px/1.7 system-ui}video,img{width:100%;border-radius:8px}a{color:#aad8cd}section{margin:32px 0}button{padding:8px 16px;margin:6px;font:inherit}</style><h1>58秒 · 航线重排与沿线园城</h1><p>场景与路线候选：提前对准圆窗、连续院落与林丛、贴水后抵达收件处。参考级材质，未提交视频生成模型。</p><video id="v" controls preload="metadata" src="garden-city-flight-58s-v04.mp4"></video>'''
data_path=out/'flight-checks.json'
if data_path.exists():
    data=json.loads(data_path.read_text(encoding='utf8'))
    for g in data['gates']:
        t=g['crossings'][0]['time_s'];doc+=f'<button onclick="v.currentTime={max(0,t-3):.3f};v.play()">{html.escape(g["id"])} 进近</button>'
doc+='<p><a href="garden-city-flight-58s-v04.blend">Blender 工程</a> · <a href="README.md">修订说明</a></p>'
for f in sorted(review.glob('sequence-*.jpg')):doc+=f'<section><img src="review/{f.name}" alt="实际渲染抽帧"></section>'
(out/'review.html').write_text(doc,encoding='utf8')
print('REVIEW_SHEETS_READY',len(paths))
