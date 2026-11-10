import sys,json,subprocess,hashlib,shutil,math
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(sys.argv[1]);O=R/'视频制作/第一集云山园巷-20261024-v0.1';frames=sorted((O/'frames').glob('*.png'))
assert len(frames)==1392,len(frames)
for i,p in enumerate(frames):
 assert p.name==f'{i+1:04d}.png'
 with Image.open(p) as im:assert im.size==(960,540);im.verify()
video=O/'cloud-garden-flight-58s-v14.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-start_number','1','-i',str(O/'frames/%04d.png'),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
for start,name in [(0,'batch-A-00-30.mp4'),(28,'batch-B-28-58.mp4')]:
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(video),'-t','30','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(O/name)],check=True)
probes={}
for p in [video,O/'batch-A-00-30.mp4',O/'batch-B-28-58.mp4']:
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
 stream=next(s for s in probe['streams'] if s['codec_type']=='video');assert stream['r_frame_rate']=='24/1';assert int(stream['nb_frames'])==(1392 if p==video else 720);assert abs(float(probe['format']['duration'])-(58 if p==video else 30))<.001
 probes[p.name]=probe
(O/'video-validation.json').write_text(json.dumps({'png_count':1392,'all_png_verified':True,'all_three_videos_decoded':True,'render_mode':'compact-full; render-only mesh batching, editable source untouched','probes':probes},ensure_ascii=False,indent=2),encoding='utf8')
def sheet(ids,name,cols=5,width=320):
 h=int(width*9/16);canvas=Image.new('RGB',(cols*width,math.ceil(len(ids)/cols)*(h+24)),'#182020');draw=ImageDraw.Draw(canvas)
 for j,i in enumerate(ids):
  x=j%cols*width;y=j//cols*(h+24)
  with Image.open(frames[i]) as im:canvas.paste(im.resize((width,h)),(x,y))
  draw.text((x+5,y+h+3),f'{i/24:.3f}s / f{i+1}',fill='white')
 canvas.save(O/name,quality=92)
sheet(list(range(0,1392,12))+[1391],'flight-contact-sheet.jpg',10,192)
sheet(list(range(8*24,20*24+1,12)),'valley-contact.jpg')
sheet(list(range(49*24,51*24+13,2)),'turn-contact.jpg')
sheet(list(range(0,8*24+1,6)),'school-transition-contact.jpg')
sheet(list(range(27*24,29*24+1,6))+list(range(37*24,39*24+1,6)),'landmark-contact.jpg')
sheet(list(range(54*24,1392,6))+[1391],'arrival-contact.jpg')
# Replace preflight thumbnails with exact delivered movie frames.
for p in (O/'flight-preview').glob('*.png'):shutil.copyfile(O/'frames'/p.name,p)
chapters=[{'time':t,'title':title,'frame':round(t*24)+1} for t,title in [(0,'校园庭池寄件口'),(7,'离水入园'),(12,'树石山肩与望亭'),(19,'隐水庭园与云隙'),(27,'邻里院落与屋脊'),(37.5,'公共水湾'),(44,'屋脊与街巷转场'),(52.5,'重回作坊水巷'),(56.5,'作坊门侧收件')]]
(O/'route-chapters.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2),encoding='utf8')
page=(O/'review.html').read_text('utf8');buttons=''.join(f'<button onclick="document.querySelector(\'video\').currentTime={c["time"]};document.querySelector(\'video\').play()">{c["time"]:.1f}s {c["title"]}</button>' for c in chapters);page=page.replace('<!-- CHAPTERS -->',buttons);(O/'review.html').write_text(page,encoding='utf8')
poses=json.loads((O/'route-poses.json').read_text('utf8'));q=np.array([p['quaternion'] for p in poses]);q/=np.linalg.norm(q,axis=1)[:,None];angles=np.degrees(2*np.arccos(np.clip(abs(np.sum(q[1:]*q[:-1],axis=1)),0,1)));p=np.array([p['position'] for p in poses]);delta=np.linalg.norm(np.diff(p,axis=0),axis=1)
(O/'motion-validation.json').write_text(json.dumps({'max_adjacent_rotation_degrees':float(angles.max()),'max_rotation_time':float((angles.argmax()+1)/24),'route_length_m':float(delta.sum()),'max_step_m':float(delta.max()),'max_discrete_acceleration_m_s2':float(np.linalg.norm(np.diff(p,n=2,axis=0),axis=1).max()*576),'duration_seconds':58,'frames':1392},indent=2),encoding='utf8')
names=['cloud-garden-route-58s-v14.blend',video.name,'batch-A-00-30.mp4','batch-B-28-58.mp4','route-poses.json','design-data.json','audit.json','layout-route-comparison.png']
(O/'manifest.json').write_text(json.dumps({'files':{name:{'bytes':(O/name).stat().st_size,'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest()} for name in names},'source_v13_sha256':hashlib.sha256((R/'视频制作/第一集池涧水巷-20261024-v0.1/pond-lane-route-58s-v13.blend').read_bytes()).hexdigest()},indent=2),encoding='utf8')
print('PACKAGE_READY',flush=True)
