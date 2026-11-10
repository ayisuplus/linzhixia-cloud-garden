"""Encode, validate and compare the cloud revision against the same previous flight."""
import argparse,json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();out=root/'视频制作/第一集无人机试飞-20261022-v0.2';prev=out.with_name('第一集无人机试飞-20261022-v0.1')
audit=json.loads((out/'cloud-audit.json').read_text(encoding='utf8'));assert hashlib.sha256((root/audit['source']).read_bytes()).hexdigest()==audit['source_sha256']
expected=[out/'frames'/f'{i:04d}.png' for i in range(1,577)];assert all(p.exists() for p in expected)
for p in expected:
    with Image.open(p) as im:im.verify()
video=out/'drone-garden-flight-v02.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(out/'frames/%04d.png'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));assert int(probe['streams'][0]['nb_frames'])==576 and float(probe['format']['duration'])==24
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
sheet=Image.new('RGB',(1600,780),(24,30,27));draw=ImageDraw.Draw(sheet)
for i,f in enumerate([1,49,97,145,193,241,289,337,385,433,481,576]):
    im=Image.open(expected[f-1]);im.thumbnail((400,225));x=i%4*400;y=i//4*260;sheet.paste(im,(x,y));draw.text((x+10,y+231),f'{(f-1)/24:.2f}s / {f}',fill='white')
sheet.save(out/'flight-contact-sheet.jpg',quality=93)
compare=Image.new('RGB',(1920,1200),(24,30,27));draw=ImageDraw.Draw(compare)
for row,f in enumerate([200,576]):
    for col,directory in enumerate([prev,out]):
        im=Image.open(directory/('frames' if col==0 else 'preview')/f'{f:04d}.png');compare.paste(im,(col*960,row*600));draw.text((col*960+16,row*600+554),f'v0.{col+1} / frame {f} / {(f-1)/24:.2f}s',fill='white')
compare.save(out/'cloud-before-after.jpg',quality=94)
readme='''# 云岸修订后的同路线复飞 v0.2

24秒、24fps、640×360、576个原生渲染帧，无声、无切镜、无画面文字。视频：drone-garden-flight-v02.mp4。高清对照预览保持960×540；动画工程也保留960×540默认设置，本轮录屏脚本仅对输出视频使用640×360预演分辨率。

与v0.1完全相同的117.45米飞行、镜头位置/朝向/焦距、24秒时序和固定包裹。约5—9秒绕墙露景，12—24秒观察上下层云岸和天空空隙。可直接对照cloud-before-after.jpg，不通过改镜头制造提升。

## 本轮修改

原云岸可见硬壳改为有浓淡变化的体积云；沿真实岸线布置不规则边缘云团，下缘增加错落下垂的云团，少量外侧散絮打破整齐轮廓。原来的180个稀薄边缘体积隐藏。云岸之间保持天空空隙，建筑、地面、庭院、路桥、景墙、水榭和无人机造型不改，沿用原材质色族。

原支撑网格保留，承担既有结构/碰撞参考职责；新增云团是云质的外观表现，不是新增硬障碍。体积云表面及散絮不具有流体模拟；本次不增加剧情风场或天气动画。

## 验证范围

cloud-audit.json记录源文件SHA256、原对象数量与位置/网格点数检查，以及原576帧飞行和相机位置逐帧对照。旧物理网格未改，沿用其离散避障报告；新增体积云的光学遮挡通过实际渲染预览检查，不能把几何无碰撞等同于画面无遮挡。

检查全部576张PNG可解码、视频完整解码、24秒/24fps/576帧。抽帧和同机位对照用于外观审阅，不等同连续播放审美通过。云边低采样降噪仍可能出现细微闪动。没有提交下游视频生成模型，不宣称已验证其理解。

## 文件

- episode1-drone-rehearsal-v02.blend：云岸修订和原动画；v0.1源文件保留。
- drone-garden-flight-v02.mp4：干净参考视频。
- cloud-before-after.jpg：两个相同时刻的旧/新对照，仅供审阅。
- flight-contact-sheet.jpg：带时间定位的抽帧。
- cloud-audit.json、flight-checks.json：修改边界与轨迹证据。

脚本：第一季/制作/空间规划/第一集试飞-v0.2。依次运行refine_clouds.py、render_flight.py、package_flight.py，均须传--root项目绝对路径。媒体留项目本地，Git记录工程、脚本、元数据。
'''
(out/'README.md').write_text(readme,encoding='utf8')
html=(prev/'review.html').read_text(encoding='utf8').replace('drone-garden-flight-v01.mp4','drone-garden-flight-v02.mp4').replace('episode1-drone-rehearsal-v01.blend','episode1-drone-rehearsal-v02.blend').replace('绕墙以后，园城逐层展开','云岸散开，同一条路再飞一次').replace('本地空间试飞','云岸修订 v0.2 / 同路线复飞').replace('<h2>时间定位</h2>','<h2>同一机位：左旧 / 右新</h2><img src="cloud-before-after.jpg"><p>只修改云岸外观；轨迹、镜头和时序与上一版相同。</p><h2>时间定位</h2>')
(out/'review.html').write_text(html,encoding='utf8')
names=['episode1-drone-rehearsal-v02.blend','drone-garden-flight-v02.mp4','cloud-audit.json','flight-checks.json','flight-contact-sheet.jpg','cloud-before-after.jpg','README.md','review.html']
if (out/'review-notes.md').exists():names.append('review-notes.md')
manifest={'artifact':'episode1-drone-rehearsal-v02','source_sha256':audit['source_sha256'],'encoding':probe,'all_pngs_decodable':True,'video_full_decode_pass':True,'frames_sha256':hashlib.sha256(''.join(hashlib.sha256(p.read_bytes()).hexdigest() for p in expected).encode()).hexdigest(),'files':[{'path':n,'bytes':(out/n).stat().st_size,'sha256':hashlib.sha256((out/n).read_bytes()).hexdigest()} for n in names]}
(out/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');print('CLOUD_PACKAGE_COMPLETE',video)
