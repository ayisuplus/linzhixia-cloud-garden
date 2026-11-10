"""Encode native frames and package the local, silent rehearsal for review."""
import argparse,json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();out=root/'视频制作/第一集无人机试飞-20261022-v0.1'
checks=json.loads((out/'flight-checks.json').read_text(encoding='utf8'));n=checks['frames'];fps=checks['fps']
expected=[out/'frames'/f'{f:04d}.png' for f in range(1,n+1)]
assert all(p.exists() for p in expected),'Render not complete'
for p in expected:
    with Image.open(p) as im:im.verify()
assert hashlib.sha256((root/checks['source']).read_bytes()).hexdigest()==checks['source_sha256'],'Source changed'
video=out/'drone-garden-flight-v01.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-i',str(out/'frames/%04d.png'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
assert int(probe['streams'][0]['nb_frames'])==n and abs(float(probe['format']['duration'])-24)<.02
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
canvas=Image.new('RGB',(1600,990),(26,31,30));draw=ImageDraw.Draw(canvas)
for i,f in enumerate([1,49,97,145,193,241,289,337,385,433,481,576]):
    with Image.open(expected[f-1]) as im:
        im.thumbnail((400,225));x=i%4*400;y=i//4*330;canvas.paste(im,(x,y));draw.text((x+12,y+239),f'{(f-1)/fps:.2f} s / frame {f}',fill='white')
canvas.save(out/'flight-contact-sheet.jpg',quality=93)
readme='''# 无人机局部复飞 v0.1

24秒、24fps、960×540、576个原生渲染帧，无声、无切镜、无画面文字。播放 `drone-garden-flight-v01.mp4`，或打开 `review.html`。

本段沿v0.4原航线第15—19号点飞行约117米：景墙/月窗—绕墙—悬空水院—云岸前行。不是1.89公里全程，也不是第一集正式配送成片。跟拍相机朝向同一水榭，避免顺机头拍摄丢失揭示对象；无人机放在画面下方。

## 本段要看什么

- 0—7秒：近景白墙和月窗移动，水榭先被遮挡或局部框出。
- 7—12秒：墙端移开，水榭、上层云岸与下层院落展开。
- 12—24秒：上层水院、下层住宅、云隙和跨层连接的相对运动，验证浮空层次。

## 保留与范围

v0.4源场景未覆盖。临时四旋翼仅用于试飞，沿用原SAME_PARCEL和刚性底座；载具造型未采用。包裹固定，不吊挂。此段没有角色、领取动作、瀑布流体运动或风场模拟。使用Cycles/OptiX GPU、12采样及降噪；云和水材质继承v0.4。低采样的细叶/云边可能有轻微闪动；最终外观仍由已采用场景美术约束。

## 验证边界

flight-checks.json记录576帧实际机位、飞行位置、目标和逐帧地标视线。机体包络27偏移射线、航段不大于0.2米间隔，相机中心加6偏移轨迹，以及相机到机体视线，本次未检出障碍。旋翼扫掠最大水平径向约0.586米，小于检查半径0.61米。属于离散几何检查，不是完整连续扫掠或航空动力学验收。

已校验576张PNG可解码、MP4全程解码、24秒/24fps/576帧及源场景SHA256。视频逐帧编码，不插帧、不加速。接近转角时减速，角点速度归零，再转向出发；用于观察空间，不代表已定稿的自然飞行节奏。交付联系图为抽帧审阅，不冒充连续观看或下游视频模型实测。

## 文件与重现

- `episode1-drone-rehearsal-v01.blend`：可编辑无人机/包裹/相机动画。
- `drone-garden-flight-v01.mp4`：干净参考视频。
- `flight-contact-sheet.jpg`：带时间的审阅抽帧，不作为生成输入。
- `flight-checks.json`：实际路径、机位和检查记录。
- `delivery-manifest.json`：文件大小、校验与编码信息。

脚本位于 `第一季/制作/空间规划/第一集试飞-v0.1`。先用Blender运行build_flight.py（--root 项目绝对路径 --render preview），审阅后用render_flight.py续渲，最后用Python运行package_flight.py。原始帧在frames/，媒体按项目既有规则留在本地，Git记录源工程、脚本和元数据。
'''
(out/'README.md').write_text(readme,encoding='utf8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>长洲园城 · 无人机复飞</title><style>body{margin:0;background:#182722;color:#f1eee5;font:17px/1.8 system-ui,"Microsoft YaHei"}main{max-width:1280px;margin:auto;padding:28px}h1{font-size:32px}video,img{width:100%;display:block;background:#000;border-radius:8px}a{color:#bdcdb7}nav{display:flex;gap:24px;flex-wrap:wrap}p{max-width:1000px}button{border:1px solid #92a592;border-radius:5px;background:#2c4439;color:#fff;padding:9px 16px;margin:5px;cursor:pointer}</style><main><p>未来女孩林知夏 / 本地空间试飞</p><h1>绕墙以后，园城逐层展开</h1><video id="flight" controls autoplay muted playsinline preload="auto" poster="preview/0001.png" src="drone-garden-flight-v01.mp4"></video><p>24秒 · 24fps · 连续跟拍 · 约117米 · 无声。临时四旋翼与固定包裹，检查浮空感和移步换景。</p><div><button onclick="v.currentTime=0;v.play()">从头播放</button><button onclick="v.currentTime=5;v.play()">5秒：月窗框景</button><button onclick="v.currentTime=8;v.play()">8秒：绕墙展开</button><button onclick="v.currentTime=16;v.play()">16秒：云岸层次</button></div><p>本次只试飞局部，不代表1.89公里全程。画面形状与飞行节奏是参考，临时无人机不是定稿造型。</p><nav><a href="drone-garden-flight-v01.mp4">独立视频</a><a href="episode1-drone-rehearsal-v01.blend">Blender动画工程</a><a href="README.md">范围与验证</a><a href="flight-checks.json">机位与几何检查</a></nav><h2>时间定位</h2><img src="flight-contact-sheet.jpg"><script>const v=document.getElementById('flight');</script></main></html>'''
(out/'review.html').write_text(html,encoding='utf8')
names=['episode1-drone-rehearsal-v01.blend','drone-garden-flight-v01.mp4','flight-checks.json','flight-contact-sheet.jpg','README.md','review.html']
manifest={'artifact':'episode1-drone-rehearsal-v01','source_sha256':checks['source_sha256'],'encoding':probe,'all_pngs_decodable':True,'video_full_decode_pass':True,'frames_sha256':hashlib.sha256(''.join(hashlib.sha256(p.read_bytes()).hexdigest() for p in expected).encode()).hexdigest(),'files':[{'path':name,'bytes':(out/name).stat().st_size,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest()} for name in names]}
(out/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');print('FLIGHT_PACKAGE_COMPLETE',video)
