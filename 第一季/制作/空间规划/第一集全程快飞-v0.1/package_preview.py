"""Encode native frames, verify every image and movie, and preserve batch overlaps."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args()
root=Path(a.root).resolve();out=root/'视频制作/第一集全程快飞-20261023-v0.1'
expected=[out/'frames'/f'{f:04d}.png' for f in range(1,1393)]
assert all(f.is_file() for f in expected),'Missing native frames'
for f in expected:
    with Image.open(f) as im:
        assert im.size==(640,360),(f,im.size)
        im.verify()
def encode(name,start,count):
    target=out/name
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-start_number',str(start),'-i',str(out/'frames/%04d.png'),'-frames:v',str(count),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(target)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)]))
    stream=probe['streams'][0]
    assert int(stream['nb_read_frames'])==count and stream['r_frame_rate']=='24/1'
    assert abs(float(probe['format']['duration'])-count/24)<.001
    subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True)
    return probe
probes={}
for name,start,count in [('full-route-fast-flight-58s.mp4',1,1392),('E01-C-FAST-B01-30s.mp4',1,720),('E01-C-FAST-B02-30s.mp4',673,720)]:
    probes[name]=encode(name,start,count)
review=out/'render-review';review.mkdir(exist_ok=True)
for page,start in enumerate(range(1,1393,240),1):
    selected=list(range(start,min(start+240,1393),12))
    sheet=Image.new('RGB',(1600,5*250),(24,30,27));draw=ImageDraw.Draw(sheet)
    for j,f in enumerate(selected):
        with Image.open(expected[f-1]) as im:
            im=im.resize((400,225));x=(j%4)*400;y=(j//4)*250;sheet.paste(im,(x,y))
            draw.text((x+8,y+230),f'{(f-1)/24:.2f}s / frame {f}',fill='white')
    sheet.save(review/f'sequence-{page:02d}.jpg',quality=92)
with Image.open(expected[720]) as im:im.save(out/'poster.jpg',quality=94)
report={'status':'rendered playable reference; author temporal aesthetic review pending','source':'episode1-full-route-58s-v01.blend','source_sha256':hashlib.sha256((out/'episode1-full-route-58s-v01.blend').read_bytes()).hexdigest(),'renderer':'Blender 5.1 EEVEE','settings':{'width':640,'height':360,'fps':24,'samples':16,'volumetric_tile_size':8,'volumetric_samples':64},'frame_count':1392,'native_frames':True,'all_pngs_decodable':True,'full_video_decode_pass':True,'encoding':probes,'frames_sha256':hashlib.sha256(''.join(hashlib.sha256(f.read_bytes()).hexdigest() for f in expected).encode()).hexdigest(),'limits':['Low-resolution spatial reference; EEVEE shading differs from previous Cycles movie.','Source camera, route, duration, cloud geometry and materials preserved.','Contact sheets are sampled visual review, not continuous real-time viewing.','No audio, human handoff animation or AI model generation.']}
(review/'render-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
html='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>58秒全程快飞</title><style>body{margin:32px auto;max-width:1100px;background:#141d1b;color:#edf2eb;font:17px/1.7 system-ui}video{width:100%;background:#000}button,a{color:inherit}button{padding:9px 14px;margin:4px;background:#354d43;border:0;border-radius:6px}p{color:#becfc4}</style><h1>58秒，从宿舍到作坊</h1><video id="flight" controls preload="metadata" poster="poster.jpg" src="full-route-fast-flight-58s.mp4"></video><p>完整航线 · 24 fps · 640×360 · 无声空间预览。原生帧渲染，未抽帧提速。此版使用Eevee，光照观感与此前Cycles试飞存在差别。</p><div><button onclick="flight.currentTime=0;flight.play()">0秒 离架</button><button onclick="flight.currentTime=12;flight.play()">12秒 云桥与叠水</button><button onclick="flight.currentTime=20;flight.play()">20秒 绕墙露景</button><button onclick="flight.currentTime=28;flight.play()">28秒 高速跨区</button><button onclick="flight.currentTime=45;flight.play()">45秒 水巷进场</button><button onclick="flight.currentTime=54;flight.play()">54秒 落位</button></div><p>请重点观察：云岸之间是否仍看得出悬空；转角前后的遮挡与揭示是否来得及辨认；高速跨区是否过晃。几何检查与抽帧审阅不代替连续播放判断。</p><p><a href="E01-C-FAST-B01-30s.mp4">第一批：0—30秒</a> · <a href="E01-C-FAST-B02-30s.mp4">第二批：28—58秒</a> · <a href="episode1-full-route-58s-v01.blend">Blender时间线</a></p></html>'''
(out/'review.html').write_text(html,encoding='utf8')
readme=(out/'README.md').read_text(encoding='utf8')
old='新的全程MP4尚未渲染；没有进行全速连续观看、体积云光学遮挡验证或生成模型实测。以前的24秒视频仍是慢速局部稿，不代表本版58秒全程效果。继续录制时先检查高速转角和两端近物，不直接批量输出最终质量。'
new='2026-10-23已按本时间线完成全程MP4：`full-route-fast-flight-58s.mp4`，58秒、24fps、640×360、1392个原生渲染帧，无声。另有B01和B02各30秒版本；全部PNG和三个视频完整解码通过。使用Eevee 16采样，体积采样64、tile 8；保留源工程的轨迹、机位、云岸几何和材质，但光照与此前Cycles试飞不同，云雾偏低对比。工程文件未改。逐帧运动区间27偏移射线检查未检出几何碰撞；静止重叠、连续实体扫掠和动力学未验证。已抽帧审查全程及重点转角，连续播放舒适度与最终采用仍由作者审阅，未提交生成模型。约11.3秒、44.9—45.3秒、53.8—54秒有急转，详见`render-review/camera-turns.json`和`render-review/review-notes.md`。'
assert old in readme or new in readme
(out/'README.md').write_text(readme.replace(old,new),encoding='utf8')
print('FULL_ROUTE_DOCUMENTATION_UPDATED',flush=True)
print('FULL_ROUTE_MOVIE_VALIDATED',1392,58,flush=True)
