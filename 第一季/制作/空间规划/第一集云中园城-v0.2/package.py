"""Package all 1392 rendered source frames; no time remapping or interpolation."""
from pathlib import Path
import argparse,subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.2';F=O/'frames'
files=sorted(F.glob('*.png'));assert len(files)==1392,len(files)
frame_summary=[]
for i,f in enumerate(files,1):
 assert f.stem==f'{i:04}'
 with Image.open(f) as im:
  im.load();assert im.size==(960,540)
  small=np.array(im.convert('RGB').resize((96,54)),dtype=float)
  frame_summary.append({'frame':i,'mean_rgb':small.mean((0,1)).tolist(),'std':float(small.std())})
assert min(x['std'] for x in frame_summary)>1,'Unexpected near-uniform frame'
videos=[]
for name,start,count in [('cloud-city-full-flight-58s-v04.mp4',1,1392),('B01-cloud-city-0-30s.mp4',1,720),('B02-cloud-city-28-58s.mp4',673,720)]:
 target=O/name
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-start_number',str(start),'-i',str(F/'%04d.png'),'-frames:v',str(count),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,avg_frame_rate,nb_frames','-of','json',str(target)]))
 assert int(meta['streams'][0]['nb_frames'])==count
 assert abs(float(meta['format']['duration'])-count/24)<.001
 subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True)
 videos.append({'file':name,'source_start_frame':start,'source_end_frame':start+count-1,'probe':meta,'full_decode':'passed'})
 print('VIDEO_VERIFIED',name,flush=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
sample=list(range(1,1393,12));sample.append(1392)
for page in range((len(sample)+35)//36):
 sheet=Image.new('RGB',(1920,6*202),(21,32,32));d=ImageDraw.Draw(sheet)
 for j,f in enumerate(sample[page*36:(page+1)*36]):
  x=j%6*320;y=j//6*202
  with Image.open(F/f'{f:04}.png') as im:sheet.paste(im.resize((320,180)),(x,y))
  d.text((x+5,y+181),f'{(f-1)/24:.2f}s · {f}',fill='white',font=font)
 sheet.save(O/f'contact-{page+1:02}.jpg',quality=90)
# Every second frame covering the new camera glance, four six-by-six contact sheets.
critical=list(range(253,481,2))
for page in range((len(critical)+35)//36):
 sheet=Image.new('RGB',(1920,6*202),(21,32,32));d=ImageDraw.Draw(sheet)
 for j,f in enumerate(critical[page*36:(page+1)*36]):
  x=j%6*320;y=j//6*202
  with Image.open(F/f'{f:04}.png') as im:sheet.paste(im.resize((320,180)),(x,y))
  d.text((x+5,y+181),f'{(f-1)/24:.2f}s · {f}',fill='white',font=font)
 sheet.save(O/f'water-reveal-contact-{page+1:02}.jpg',quality=90)
(O/'media-validation.json').write_text(json.dumps({'frames':1392,'dimensions':[960,540],'fps':24,'interpolated':False,'all_pngs_decoded':True,'videos':videos,'minimum_thumbnail_std':min(x['std'] for x in frame_summary)},ensure_ascii=False,indent=2),encoding='utf8')
(O/'frame-statistics.json').write_text(json.dumps(frame_summary,indent=2),encoding='utf8')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>云内园城 · 58秒完整试飞</title><style>body{margin:0;background:#142320;color:#edf2e8;font:17px/1.8 system-ui,"Microsoft YaHei"}main{max-width:1180px;margin:auto;padding:40px 22px}h1{font-size:36px;line-height:1.35}p{max-width:960px}video,img{display:block;width:100%;border-radius:10px}button,a{color:#bfdfc9}button{background:#29463f;border:1px solid #527267;padding:8px 14px;border-radius:22px;cursor:pointer;font:inherit;margin:5px}.links{display:flex;gap:20px;flex-wrap:wrap}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:28px 0}figure{margin:0}figcaption,.note{color:#b5c7be;font-size:15px}.badge{color:#b8d9ca;font-size:14px;letter-spacing:.1em}section{margin:35px 0}@media(max-width:720px){.pair{grid-template-columns:1fr}h1{font-size:29px}}</style><main><p class="badge">未来女孩 · 第一集空间参考 · v04</p><h1>从云中穿行，看见下层水庭</h1><p>局部云层让开水庭视线，保留顶部与两侧云围合；经过叠水庭院时平缓向下观看，再对准下一扇月窗。建筑与飞行位置沿用上一版。</p><video id="flight" controls preload="metadata" poster="preview-v04/0331.png" src="cloud-city-full-flight-58s-v04.mp4"></video><p class="note">完整58秒 · 24fps · 960×540 · 1392个原生渲染帧，无插帧、无变速。静音空间预演。</p><div id="chapters"><button data-t="0">起点</button><button data-t="9.5">第一扇月窗</button><button data-t="12.5">下层水庭展开</button><button data-t="20">第二扇月窗</button><button data-t="25">云内庭院</button><button data-t="42">第三扇月窗</button><button data-t="48">贴水飞行</button><button data-t="55.5">终点收稳</button></div><section><h2>同一时间点的变化</h2><div class="pair"><figure><img src="../第一集云中园城-20261024-v0.1/preview-v03/331.png"><figcaption>上一版：云遮挡加上仰视，下层水面落在画外。</figcaption></figure><figure><img src="preview-v04/0331.png"><figcaption>本版：局部空气开口与平缓俯视，让下层水面和跌水边进入画面。</figcaption></figure></div></section><section><h2>云内空间继续保留</h2><div class="pair"><figure><img src="preview-v04/0600.png"><figcaption>近庭院可读，远处街区与屋顶之间仍有云。</figcaption></figure><figure><img src="preview-v04/1177.png"><figcaption>末段贴水保持开敞水面。</figcaption></figure></div></section><p>这是给视频模型使用的空间参考候选。云纹理、局部灰白空面与完整瀑布呈现仍有精修空间；最终采用以作者观看为准。</p><nav class="links"><a href="cloud-city-water-reveal-58s-v04.blend">可编辑Blender工程</a><a href="README.md">工程与检查说明</a><a href="B01-cloud-city-0-30s.mp4">第1批：0—30秒</a><a href="B02-cloud-city-28-58s.mp4">第2批：28—58秒</a></nav><p class="note">两批重叠2秒，合并去重后58秒。若文件链接没有启动Blender，请在目录中双击“打开云中园城v04.cmd”。</p></main><script>document.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{const v=document.getElementById('flight');v.currentTime=Number(b.dataset.t);v.play();});</script></html>'''
(O/'review.html').write_text(page,encoding='utf8')
(O/'打开云中园城v04.cmd').write_text('@echo off\nchcp 65001 >nul\nstart "" "D:\\blender\\blender.exe" "%~dp0cloud-city-water-reveal-58s-v04.blend"\n',encoding='utf8')
print('PACKAGE_COMPLETE',flush=True)
