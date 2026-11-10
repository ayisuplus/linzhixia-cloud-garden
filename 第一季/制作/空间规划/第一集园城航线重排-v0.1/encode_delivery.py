"""Encode the native 24fps sequence and verify all deliverables."""
import argparse, json, subprocess, hashlib
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root);out=root/'视频制作/第一集园城航线重排-20261023-v0.1'
frames=out/'frames';sizes=set()
for n in range(1,1393):
    with Image.open(frames/f'{n:04}.png') as im:im.load();sizes.add(im.size)
assert len(sizes)==1
jobs=[('garden-city-flight-58s-v04.mp4',1,1392),('E01-C-FAST-B01-30s-v04.mp4',1,720),('E01-C-FAST-B02-30s-v04.mp4',673,720)];checks=[]
for name,start,count in jobs:
    dest=out/name
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-start_number',str(start),'-i',str(frames/'%04d.png'),'-frames:v',str(count),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(dest)],check=True)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]))
    stream=next(s for s in info['streams'] if s['codec_type']=='video');assert int(stream['nb_read_frames'])==count and stream['r_frame_rate']=='24/1';assert abs(float(info['format']['duration'])-count/24)<.01
    subprocess.run(['ffmpeg','-v','error','-i',str(dest),'-f','null','-'],check=True)
    checks.append({'file':name,'frames':count,'fps':24,'duration_s':count/24,'size':[stream['width'],stream['height']],'decode':'pass','sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(out/'review/encoding-check.json').write_text(json.dumps({'png_frames':1392,'png_sizes':list(sizes),'videos':checks},indent=2),encoding='utf8')
files=[out/n for n,_,_ in jobs]+[out/'garden-city-flight-58s-v04.blend',out/'garden-city-space-v01.blend']
(out/'delivery-manifest.json').write_text(json.dumps([{'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],indent=2),encoding='utf8')
print('DELIVERY_VERIFIED',checks)
