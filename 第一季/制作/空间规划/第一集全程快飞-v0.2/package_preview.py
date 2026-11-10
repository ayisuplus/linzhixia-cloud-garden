"""Package the revised native-frame flight and record only verified results."""
import argparse,json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve()
out=root/'视频制作/第一集全程快飞-20261023-v0.2';review=out/'render-review';review.mkdir(exist_ok=True)
frames=[out/'frames'/f'{f:04d}.png' for f in range(1,1393)]
assert all(f.is_file() for f in frames)
for f in frames:
    with Image.open(f) as im:assert im.size==(640,360);im.verify()
probes={}
for name,start,count in [('full-route-fast-flight-58s-v02.mp4',1,1392),('E01-C-FAST-B01-30s-v02.mp4',1,720),('E01-C-FAST-B02-30s-v02.mp4',673,720)]:
    target=out/name
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-start_number',str(start),'-i',str(out/'frames/%04d.png'),'-frames:v',str(count),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(target)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)]))
    assert int(probe['streams'][0]['nb_read_frames'])==count and probe['streams'][0]['r_frame_rate']=='24/1'
    assert abs(float(probe['format']['duration'])-count/24)<.001
    subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True);probes[name]=probe
for page,start in enumerate(range(1,1393,240),1):
    sheet=Image.new('RGB',(1600,1250),(24,30,27));draw=ImageDraw.Draw(sheet)
    for j,f in enumerate(range(start,min(start+240,1393),12)):
        with Image.open(frames[f-1]) as im:
            x=j%4*400;y=j//4*250;sheet.paste(im.resize((400,225)),(x,y));draw.text((x+8,y+230),f'{(f-1)/24:.2f}s / {f}',fill='white')
    sheet.save(review/f'sequence-{page:02d}.jpg',quality=92)
sheet=Image.new('RGB',(1600,1000),(24,30,27));draw=ImageDraw.Draw(sheet)
for row,group in enumerate([[229,241,247,253,265],[505,517,523,529,541],[997,1009,1015,1021,1033],[1129,1177,1225,1285,1321]]):
    for col,f in enumerate(group):
        with Image.open(frames[f-1]) as im:
            x=col*320;y=row*250;sheet.paste(im.resize((320,180)),(x,y));draw.text((x+8,y+190),f'{(f-1)/24:.2f}s / {f}',fill='white')
sheet.save(review/'crossings-and-water.jpg',quality=94)
with Image.open(frames[516]) as im:im.save(out/'poster.jpg',quality=94)
blend=out/'episode1-full-route-58s-v02.blend';report=json.loads((out/'flight-checks.json').read_text(encoding='utf8'))
validation={'source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'renderer':'Blender 5.1 EEVEE','width':640,'height':360,'fps':24,'native_frames':1392,'duration_s':58,'taa_samples':16,'volumetric_samples':64,'volumetric_tile_size':8,'all_png_decode_pass':True,'all_movie_decode_pass':True,'encoding':probes,'frames_sha256':hashlib.sha256(''.join(hashlib.sha256(f.read_bytes()).hexdigest() for f in frames).encode()).hexdigest(),'continuous_playback_aesthetic_acceptance':'pending author review; sampled images are not continuous viewing'}
(review/'render-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf8')
readme=f'''# 58秒全程快飞 v0.2：穿月窗、贴水与平顺转向

完整视频：full-route-fast-flight-58s-v02.mp4。24fps、640×360、1392个原生渲染帧、无声无字幕无切镜，Eevee低清空间预览。源v0.1工程与视频保留；新版不改建筑、云岸、窗洞、水面或既有美术，只改飞行与相机动画。

## 观看位置

- 10.5秒：穿A圆窗；22秒：穿B圆窗；42.5秒：穿C圆窗。三个都由西向东穿过真实开孔中心，先对准再穿越。
- 47—53.5秒：贴水飞行。原水面约z=-0.48，低飞根节点z=0.25，包裹/机体最低点约比水面高0.62—0.65米，相机约高1.04—1.07米；不是触水或流体模拟。
- 53.5秒后桥前上升，越过桥栏杆，再降至原收件终点；57秒左右稳定，58秒结束。

总路径约{report['distance_m']:.2f}米；最高动画速度约{report['max_speed_m_s']:.2f}米/秒。相机最大相邻帧转角从旧版54.81度降至{report['max_camera_turn_deg_per_frame']:.2f}度，通过提前看洞口、平滑朝向、放缓洞口局部速度实现，不通过拉长全片时长。

## 分批与文件

|批次|全程时间|帧区间|时长|
|---|---|---|---|
|E01-C-FAST-B01|0—30秒|1—720|30秒|
|E01-C-FAST-B02|28—58秒|673—1392|30秒|

两批共享48帧，剪掉第二批重复2秒后仍为58秒。对应视频文件名末尾带v02；没有提交生成模型，不能把Blender接续等同生成模型接续成功。

- episode1-full-route-58s-v02.blend：可编辑新动画，源版本保留。
- flight-checks.json：内部轨迹、过孔位置、时间与初步碰撞检查。
- render-review/independent-check.json：独立静态场景指纹和关键段加密碰撞审查。
- render-review/render-validation.json：实际渲染/编码参数及解码证据。
- render-review/crossings-and-water.jpg、sequence-*.jpg：带时间定位的抽帧。
- review.html：带时间按钮的本地播放器。

本轮是机载FPV空间参考；临时无人机对自身相机隐藏，人物装卸和最终包裹跟拍未制作。抽帧和几何检查不等于连续播放舒适度/最终美术通过，采用由作者审阅。制作脚本在第一季/制作/空间规划/第一集全程快飞-v0.2；复用v0.1渲染器的显式artifact/blend参数。
'''
(out/'README.md').write_text(readme,encoding='utf8')
html='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>58秒穿窗贴水试飞</title><style>body{margin:32px auto;max-width:1100px;background:#141d1b;color:#edf2eb;font:17px/1.7 system-ui}video,img{width:100%}button,a{color:inherit}button{padding:9px 14px;margin:4px;background:#354d43;border:0;border-radius:6px}p{color:#becfc4}</style><h1>穿过圆窗，掠过水面</h1><video id="flight" controls preload="metadata" poster="poster.jpg" src="full-route-fast-flight-58s-v02.mp4"></video><p>58秒 · 24fps · 无声低清空间预览。三次真实穿孔、桥前抬升，总时长不变。</p><div><button onclick="flight.currentTime=8.5;flight.play()">A窗</button><button onclick="flight.currentTime=20;flight.play()">B窗</button><button onclick="flight.currentTime=40;flight.play()">C窗</button><button onclick="flight.currentTime=47;flight.play()">贴水飞行</button><button onclick="flight.currentTime=53;flight.play()">抬升过桥</button></div><p><a href="E01-C-FAST-B01-30s-v02.mp4">第一批30秒</a> · <a href="E01-C-FAST-B02-30s-v02.mp4">第二批30秒</a> · <a href="episode1-full-route-58s-v02.blend">Blender工程</a></p><img src="render-review/crossings-and-water.jpg"></html>'''
(out/'review.html').write_text(html,encoding='utf8')
print('V02_VIDEO_VALIDATED',58,1392,flush=True)
