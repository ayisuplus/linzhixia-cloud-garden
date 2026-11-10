"""Encode the exact rendered frames; review assets never imply author adoption."""
import sys,json,subprocess,hashlib,math,re,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=Path(sys.argv[1]);O=R/'视频制作/第一集云城层次-20261024-v0.1';F=O/'frames'
fps=24;frames=1392
context=json.loads((O/'render-context.json').read_text('utf8'))
assert hashlib.sha256((O/'cloud-neighbourhood-flight-58s-v19.blend').read_bytes()).hexdigest()==context['scene_sha256']
assert hashlib.sha256((O/'route-poses.json').read_bytes()).hexdigest()==context['poses_sha256']
stats=[]
for j in range(1,frames+1):
 p=F/f'{j:04d}.png'
 with Image.open(p) as im:
  im.load();assert im.size==(960,540);a=np.array(im.convert('RGB').resize((120,68)))
  stats.append({'frame':j,'mean':float(a.mean()),'std':float(a.std()),'near_white_fraction':float(np.mean(np.min(a,axis=2)>245)),'near_black_fraction':float(np.mean(np.max(a,axis=2)<10))})
assert len(list(F.glob('*.png')))==1392
def run(cmd):subprocess.run(cmd,check=True)
full=O/'cloud-neighbourhood-flight-58s-v19.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','1','-i',str(F/'%04d.png'),'-frames:v','1392','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(full)])
parts=[]
for name,start,end in [('B01-reference-0-30s.mp4',0,720),('B02-reference-28-58s.mp4',672,1392)]:
 p=O/name;run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(full),'-vf',f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(p)]);parts.append(p)
videos=[]
for p in [full,*parts]:
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration:format=duration','-of','json',str(p)],encoding='utf8'));s=meta['streams'][0];expected=1392 if p==full else 720
 assert int(s['nb_frames'])==expected and s['r_frame_rate']=='24/1';assert abs(float(meta['format']['duration'])-expected/24)<.01
 run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-']);videos.append({'file':p.name,'metadata':meta,'full_decode_passed':True})
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
def sheet(ids,name,cols=5):
 rows=math.ceil(len(ids)/cols);im=Image.new('RGB',(cols*320,rows*208),'#1d2d2b');d=ImageDraw.Draw(im)
 for j,f in enumerate(ids):
  x=j%cols*320;y=j//cols*208
  with Image.open(F/f'{f:04d}.png') as src:im.paste(src.resize((320,180)),(x,y))
  d.text((x+7,y+183),f'{(f-1)/24:05.2f}s · {f}',font=font,fill='#e8eee8')
 im.save(O/name,quality=91)
for k in range(3):sheet([1+s*24 for s in range(k*20,min((k+1)*20,58))],f'contact-{k+1:02}.jpg')
preview_ids=sorted(set(list(range(1,1393,72))+[1392]))
for f in preview_ids:shutil.copyfile(F/f'{f:04d}.png',O/'preview'/f'{f:04d}.png')
sheet(preview_ids,'preview-contact.jpg')
for name,lo,hi in [('cloud-reveal',26,35),('home-arrival',46,58)]:sheet(list(range(lo*24+1,min(hi*24+1,1393),12)),name+'-contact.jpg')
for t,name in [(0,'04-school-lane.png'),(15,'05-water-neighbours.png'),(45,'06-home-lane.png'),(57,'07-workshop-arrival.png')]:
 with Image.open(F/f'{t*24+1:04d}.png') as im:im.save(O/name)
(O/'frame-statistics.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
validation={'native_frames':1392,'dimensions':[960,540],'fps':24,'duration_seconds':58,'interpolated':False,'all_pngs_decoded':True,'videos':videos,'min_frame_std':min(s['std'] for s in stats),'max_near_white_fraction':max(s['near_white_fraction'] for s in stats),'max_near_black_fraction':max(s['near_black_fraction'] for s in stats),'continuous_visual_review':'pending; decoding and contact sheets do not prove motion comfort','audio':'silent spatial reference'}
(O/'media-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf8')
D=json.loads((O/'development-data.json').read_text('utf8'));houses=sum(len(q['houses']) for q in D['background_islands'])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>长洲云城 · 沿途层次 v19</title><style>body{margin:0;background:#f3f1e7;color:#263e36;font:17px/1.7 system-ui,"Microsoft Yahei",sans-serif}main{max-width:1440px;margin:auto;padding:32px 5vw 65px}h1{font-size:38px}h2{margin-top:38px}img,video{width:100%;display:block;border-radius:10px;background:#152824}figure{margin:25px 0}figcaption,.meta{color:#63766c}nav,.links{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}button{font:inherit;padding:8px 15px;border:1px solid #819986;border-radius:22px;background:transparent;cursor:pointer}.note{padding:16px 20px;background:#e6e8dc;border-left:4px solid #9e6742}a{color:#167d7b}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:850px){.pair{grid-template-columns:1fr}}</style><main><p class="meta">《未来女孩林知夏》 · 园岛参考预演 v19 · 2026-10-24</p><h1>沿途有街坊，云里有更远的城市</h1><p>近处补院墙漏窗、学园连廊、邻里屋檐和作坊棚架；中远处补低矮园岛城区。局部云带参与遮挡与揭示，七座主园岛及原院落、水景继续保留。</p><video id="flight" controls playsinline preload="metadata" poster="04-school-lane.png" src="cloud-neighbourhood-flight-58s-v19.mp4"></video><nav><button data-time="0">0s 学园街边</button><button data-time="8">8s 降入云隙</button><button data-time="14">14s 听瀑邻里</button><button data-time="24">24s 下层收水庭</button><button data-time="33">33s 云间亭与桥廊</button><button data-time="43">43s 半园邻里</button><button data-time="53">53s 作坊到达</button></nav><p class="note">58秒 · 960×540 · 24fps · 1392原生帧 · 无声空间参考。建筑、树石、云基和水流为简化造型；人物装卸、云舟运行和流体未制作。用于判断布局、空间层次与运镜，不代表生成模型成片已通过。</p><div class="links"><a href="B01-reference-0-30s.mp4">参考段一：0—30秒</a><a href="B02-reference-28-58s.mp4">参考段二：28—58秒</a><a href="cloud-neighbourhood-flight-58s-v19.blend">带58秒相机的Blender工程</a></div><p>两段各30秒，共用28—30秒，用作后续生成参考时需去掉重复区间。本轮未调用视频生成模型。</p><h2>从独立园子补到沿途城区</h2><div class="pair"><figure><img loading="lazy" src="../第一集低亭云渡-20261024-v0.1/01-overview.png"><figcaption>v18：七座主要园岛。</figcaption></figure><figure><img loading="lazy" src="01-overview.png"><figcaption>v19：同机位，补远景城区与局部云层。</figcaption></figure></div><figure><img loading="lazy" src="02-city-depth.png"><figcaption>多层屋顶与园岛形成远近关系，背景内部仅做视觉代理。</figcaption></figure><div class="pair"><figure><img loading="lazy" src="04-school-lane.png"><figcaption>学园：廊檐与院墙围合近景。</figcaption></figure><figure><img loading="lazy" src="06-home-lane.png"><figcaption>半园：连续园界、漏窗和邻里屋檐。</figcaption></figure></div><h2>复核与范围</h2><p>已对旧园路、候舟接口、水景、源资产保留及保存航线做独立几何复核。全帧图像与三个视频完整解码检查通过，逐秒抽帧与云中揭示、末段转弯另外留图。连续观看的舒适度和最终采用仍以作者审阅为准。</p><div class="links"><a href="README.md">修改说明</a><a href="audit.md">几何审查</a><a href="visual-review.md">抽帧审查</a><a href="contact-01.jpg">全程抽帧 1</a><a href="contact-02.jpg">全程抽帧 2</a><a href="contact-03.jpg">全程抽帧 3</a></div><p class="meta">若链接没有启动Blender，请在软件中选择“文件 → 打开”，进入本页所在目录选择带flight的工程。</p></main><script>const v=document.getElementById('flight');for(const b of document.querySelectorAll('[data-time]'))b.onclick=()=>{v.currentTime=Number(b.dataset.time);v.play()};</script></html>'''
(O/'review.html').write_text(page,encoding='utf8')
(O/'README.md').write_text(f'''# 第一集云城层次 v19

本轮作者授权补足参考视频里的城市层次，延续七主岛骨架及低亭云渡方向。源v18另存保留。

## 修改

- {len(D['main_buildings'])}组近景低屋、{len(D['street_edges'])}段带实际漏窗的园界，半园南侧连接为连续园墙；补学园书廊和作坊棚架。
- {len(D['plant_groups'])}组沿边界生长的竹/灌木组，既有树石保留。
- {len(D['background_islands'])}组背景园岛，合计{houses}座简化低屋。是完整体积的远景代理，未制作房间或全域导航。
- 局部云带、云下缘与四段薄云遮露。普通雾均不承重，主岛实体承托保留。
- 作坊原后厅体块和一片装饰窗在同一旋转盒范围内开实际门洞，补地坪和门框；其余源物体/原材料不变。箱组避开棚内入口。

## 完整参考片

`cloud-neighbourhood-flight-58s-v19.mp4`：960×540、24fps、1392原生帧、58秒，无声。起点是学园庭院，终点为作坊门廊外，无人物寄件/收件动作。

两条30秒派生参考：B01=0—30秒，B02=28—58秒，重叠2秒。并未提交生成模型，也未验证下游入口参数；实际生成时需继续按项目规则冻结输入与审阅完整提示词。

`cloud-neighbourhood-flight-58s-v19.blend`保存1392帧相机；`cloud-neighbourhood-v19.blend`为无新增航线的静态工作版。`route-poses.json`逐帧位姿，`render-context.json`冻结本次源哈希和渲染规格。

## 复核

独立几何报告见`audit.md/json`，初轮和二轮问题记录保留。源v18全部2893对象保留，仅两项门洞网格作声明修改；轨迹按1.2×1.2×0.8米的27偏移线离散扫描，不能等同精确连续实体包络或真实动力学。

`media-validation.json`为图像与视频全解码结果，`contact-01..03.jpg`为逐秒抽帧，另有云中揭示/末段半秒抽帧。抽帧、解码和几何检查不替代连续观看舒适度或作者采用。

云基底部仍有简化硬轮廓，重复屋顶与植物未精雕；云舟、升降设施和水流是静态表现。尺寸为创作推定，不作施工/结构认证。本轮重点是给后续视频制作提供可辨认的空间关系。

## 复现与文件

脚本位于`第一季/制作/空间规划/第一集云城层次-v0.1`，依次build.py、flight.py、render.py、package.py；显式传项目根目录。原生frames保留本地并从Git排除，交付MP4、工程、静帧、位姿和审核证据入版本库。工程链接不启动Blender时，请在Blender“文件 → 打开”选择本目录文件。
''',encoding='utf8')
(O/'.gitignore').write_text('*.log\n*.blend1\nframes/\n__pycache__/\n*.pyc\n',encoding='utf8')
print('V19_PACKAGE_READY',houses,'background houses',len(stats),'decoded frames',flush=True)
