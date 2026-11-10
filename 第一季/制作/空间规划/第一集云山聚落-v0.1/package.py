import sys,json,subprocess,hashlib,html
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(sys.argv[1]);O=R/'视频制作/第一集云山聚落-20261024-v0.1';frames=sorted((O/'frames').glob('*.png'))
assert len(frames)==1392,len(frames)
for p in frames:
 with Image.open(p) as im:assert im.size==(960,540);im.verify()
video=O/'cloud-hamlet-flight-58s-v11.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-start_number','1','-i',str(O/'frames/%04d.png'),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
for start,end,name in [(0,30,'batch-A-00-30.mp4'),(28,58,'batch-B-28-58.mp4')]:
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(video),'-t',str(end-start),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(O/name)],check=True)
for p in [video,O/'batch-A-00-30.mp4',O/'batch-B-28-58.mp4']:subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));(O/'video-validation.json').write_text(json.dumps({'png_count':1392,'all_png_verified':True,'all_three_videos_decoded':True,'probe':probe},ensure_ascii=False,indent=2),encoding='utf8')
idx=list(range(0,1392,12))+[1391];sheet=Image.new('RGB',(1920,10*132),'#181e22');draw=ImageDraw.Draw(sheet)
for j,i in enumerate(idx):
 with Image.open(frames[i]) as im:im=im.resize((192,108));x=(j%10)*192;y=(j//10)*132;sheet.paste(im,(x,y));draw.text((x+5,y+111),f'{i/24:05.2f}s  f{i+1}',fill='white')
# 117 samples need twelve rows.
if len(idx)>100:
 sheet=Image.new('RGB',(1920,12*132),'#181e22');draw=ImageDraw.Draw(sheet)
 for j,i in enumerate(idx):
  with Image.open(frames[i]) as im:im=im.resize((192,108));x=(j%10)*192;y=(j//10)*132;sheet.paste(im,(x,y));draw.text((x+5,y+111),f'{i/24:05.2f}s  f{i+1}',fill='white')
sheet.save(O/'flight-contact-sheet.jpg',quality=90)
def focus_sheet(ids,name,columns=5):
 canvas=Image.new('RGB',(columns*320,((len(ids)+columns-1)//columns)*204),'#182020');draw=ImageDraw.Draw(canvas)
 for j,i in enumerate(ids):
  with Image.open(frames[i]) as im:canvas.paste(im.resize((320,180)),((j%columns)*320,(j//columns)*204))
  draw.text(((j%columns)*320+5,(j//columns)*204+183),f'{i/24:.3f}s / f{i+1}',fill='white')
 canvas.save(O/name,quality=92)
focus_sheet(list(range(8*24,20*24+1,12)),'valley-contact.jpg')
focus_sheet(list(range(49*24,51*24+13,2)),'turn-contact.jpg')
sys.path.insert(0,str(Path(__file__).parent.parent/'第一集山水总图白模-v0.1'))
import layout as L
import numpy as np
poses=json.loads((O/'route-poses.json').read_text('utf8'));stations=L.nearest(np.array([p['position'][:2] for p in poses]))[0]
chapters=[]
for station,title in [(.018,'檐下起飞'),(.118,'出廊见谷'),(.40,'过谷见邻里'),(.575,'水湾入街'),(.86,'作坊水巷'),(.932,'短段贴水')]:
 i=int(np.argmin(abs(stations-station)));chapters.append({'time':round(i/24,3),'title':title,'frame':i+1})
(O/'route-chapters.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2),encoding='utf8')
page=(O/'review.html').read_text('utf8');buttons=''.join(f'<button onclick="document.querySelector(\'video\').currentTime={c["time"]};document.querySelector(\'video\').play()">{c["time"]:.1f}s {c["title"]}</button>' for c in chapters)
if '<nav id="chapters">' not in page:page=page.replace('</video>','</video><nav id="chapters">'+buttons+'</nav>')
(O/'review.html').write_text(page,encoding='utf8')
names=['cloud-hamlet-masterplan-v11.blend','cloud-hamlet-route-58s-v11.blend','cloud-hamlet-flight-58s-v11.mp4','batch-A-00-30.mp4','batch-B-28-58.mp4','route-poses.json','landscape-data.json']
(O/'manifest.json').write_text(json.dumps({'files':{name:{'bytes':(O/name).stat().st_size,'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest()} for name in names},'source_v10_sha256':hashlib.sha256((R/'视频制作/第一集山谷植物-20261024-v0.1/valley-masterplan-v10.blend').read_bytes()).hexdigest()},indent=2),encoding='utf8')
print('PACKAGE_READY',flush=True)
