"""Package all 1392 rendered source frames; no time remapping or interpolation."""
from pathlib import Path
import argparse,subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.4';F=O/'frames'
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
for name,start,count in [('cloud-city-layered-flight-58s-v06.mp4',1,1392),('B01-layered-city-0-30s.mp4',1,720),('B02-layered-city-28-58s.mp4',673,720)]:
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

from html import escape
comparisons=''.join(f'<section><h2>{title}</h2><div class="pair"><figure><img src="../第一集云中园城-20261024-v0.3/preview-v05/{f:04}.png"><figcaption>v05</figcaption></figure><figure><img src="preview-v06/{f:04}.png"><figcaption>v06 · 相同机位</figcaption></figure></div></section>' for f,title in [(375,'下层水庭仍清楚'),(600,'近屋与庭院保留'),(697,'云下起伏与通透间隙'),(1177,'贴水与近处木构')])
page=(O/'review-template.html').read_text('utf8').replace('COMPARISONS',comparisons)
(O/'review.html').write_text(page,encoding='utf8')
(O/'打开云中园城v06.cmd').write_text('@echo off\nchcp 65001 >nul\nstart "" "D:\\blender\\blender.exe" "%~dp0cloud-city-layered-58s-v06.blend"\n',encoding='utf8')
print('PACKAGE_COMPLETE',flush=True)
