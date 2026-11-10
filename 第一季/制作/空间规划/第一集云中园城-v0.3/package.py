"""Package all 1392 rendered source frames; no time remapping or interpolation."""
from pathlib import Path
import argparse,subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.3';F=O/'frames'
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
for name,start,count in [('cloud-city-color-flight-58s-v05.mp4',1,1392),('B01-color-city-0-30s.mp4',1,720),('B02-color-city-28-58s.mp4',673,720)]:
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
plan=json.loads((O/'color-cloud-plan.json').read_text('utf8'))
swatches=''.join(f'<div class="swatch"><span style="background:{v["srgb_hex"]}"></span><strong>{v["role"].split("：")[0]}</strong><small>{v["srgb_hex"]}</small><p>{v["role"].split("：")[1]}</p></div>' for k,v in plan['palette'].items())
comparisons=''.join(f'<section><h2>{title}</h2><div class="pair"><figure><img src="../第一集云中园城-20261024-v0.2/preview-v04/{f:04}.png"><figcaption>上一版</figcaption></figure><figure><img src="preview-v05/{f:04}.png"><figcaption>本版 · 相同机位与时刻</figcaption></figure></div></section>' for f,title in [(600,'近处：墙、瓦、木构和植物分开'),(697,'远处：街区隐入云中'),(1177,'水巷：青碧水与暖木相衬')])
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>云内园城 · 色彩与云层 v05</title><style>body{margin:0;background:#132624;color:#edf1e4;font:17px/1.8 system-ui,"Microsoft YaHei"}main{max-width:1180px;margin:auto;padding:38px 22px}h1{font-size:38px;line-height:1.3}h2{font-size:25px}p{max-width:1020px}video,img{display:block;width:100%;border-radius:10px}a{color:#e2bd75}button{color:#e6e8db;background:#2d4b46;border:1px solid #628174;padding:8px 14px;border-radius:22px;font:inherit;cursor:pointer;margin:5px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}figcaption,small,.note{font-size:14px;color:#bed0c3}section{margin:40px 0}.palette{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.swatch{background:#203b35;border-radius:8px;padding:12px}.swatch span{display:block;height:54px;border-radius:4px;margin-bottom:10px}.swatch strong,.swatch small{display:block}.swatch p{font-size:14px;line-height:1.5;margin-bottom:0}.links{display:flex;gap:20px;flex-wrap:wrap}@media(max-width:750px){.pair{grid-template-columns:1fr}.palette{grid-template-columns:repeat(2,1fr)}h1{font-size:30px}}</style><main><small>未来女孩 · 第一集空间参考 · v05</small><h1>有疏密的云，有主次的园城颜色</h1><p>近处屋瓦、粉墙与木构清楚，远处街区隐入侧云；黛瓦和暖墙作基底，水与植物分出青绿层次，少量赭红、桂黄集中在庭院节点。城市仍生活在巨云内部。</p><video id="flight" controls preload="metadata" poster="preview-v05/0600.png" src="cloud-city-color-flight-58s-v05.mp4"></video><p class="note">完整58秒 · 960×540 · 24fps · 1392个原生帧 · 无插帧/变速 · 静音空间参考。相机与载体动画沿用v04。</p><div><button data-t="0">书院起点</button><button data-t="13.5">叠水庭院</button><button data-t="24.5">近景颜色</button><button data-t="29">远处隐现</button><button data-t="42">第三扇月窗</button><button data-t="48">贴水</button></div><section><h2>少量色族，明确落点</h2><div class="palette">SWATCHES</div><p class="note">以上为本轮设计的sRGB材质输入色块，计算转换后写入Blender；不是渲染画面取色或历史园林标准色。灯光、云层与显示变换会影响实际外观。暖木、青绿沿项目既有方向发展，人物/室内定款保留。</p></section>COMPARISONS<section><h2>云从一片灰，改为厚薄与受光的层次</h2><p>开口固定在庭院与街区空间中，近处有清空气；外围、侧面与上方仍由云围合。较厚的云保留冷青灰暗部，亮部接近中性白。第一轮偏褐暗云已退回，不作为当前结果。</p><p class="note">云和水纹仍为参考级。局部空面与侧云边缘可以继续细化；当前用于约束视频模型的空间、色彩落点与遮露关系。</p></section><nav class="links"><a href="cloud-city-color-58s-v05.blend">可编辑Blender工程</a><a href="../../第一季/制作/空间规划/第一集云中园城-v0.3/色彩与云层规划.md">色彩与云层规划</a><a href="README.md">交付与检查</a><a href="B01-color-city-0-30s.mp4">第1批0—30秒</a><a href="B02-color-city-28-58s.mp4">第2批28—58秒</a></nav><p class="note">工程链接未启动Blender时，请在目录双击“打开云中园城v05.cmd”。两批重叠2秒，去重后58秒。未提交生成服务。</p></main><script>document.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>{const v=document.getElementById('flight');v.currentTime=Number(b.dataset.t);v.play();});</script></html>'''.replace('SWATCHES',swatches).replace('COMPARISONS',comparisons)
(O/'review.html').write_text(page,encoding='utf8')
(O/'打开云中园城v05.cmd').write_text('@echo off\nchcp 65001 >nul\nstart "" "D:\\blender\\blender.exe" "%~dp0cloud-city-color-58s-v05.blend"\n',encoding='utf8')
print('PACKAGE_COMPLETE',flush=True)
