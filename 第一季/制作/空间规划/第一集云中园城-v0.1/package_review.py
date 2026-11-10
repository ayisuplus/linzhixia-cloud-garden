from pathlib import Path
import argparse,json,hashlib,subprocess
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.1'
frames=sorted((O/'reveal-frames-v03').glob('*.png'));assert len(frames)==96,len(frames)
listing=O/'encode-frames.txt';listing.write_text('\n'.join("file '"+str(f.resolve()).replace('\\','/')+"'\nduration 0.0833333333333333" for f in frames)+"\n",encoding='utf8')
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(listing),'-vf','fps=12','-frames:v','96','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'cloud-window-reveal-8s-v03.mp4')],check=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for chunk in range(2):
 sheet=Image.new('RGB',(6*320,8*202),(23,34,33));draw=ImageDraw.Draw(sheet)
 for j,f in enumerate(frames[chunk*48:(chunk+1)*48]):
  x=j%6*320;y=j//6*202;im=Image.open(f).resize((320,180));sheet.paste(im,(x,y));draw.text((x+5,y+181),f'{(int(f.stem)-1)/24:.2f}s',font=font,fill='white')
 sheet.save(O/f'motion-contact-{chunk+1}.jpg',quality=88)
page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>一朵云里的城市</title><style>body{margin:32px auto;max-width:1200px;padding:0 18px;background:#172322;color:#eee;font:18px/1.75 system-ui}a{color:#b8ddcf}img,video{display:block;width:100%;border-radius:8px}figure{margin:30px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}.pair figure{margin:0}figcaption,small{color:#bdc9c2;font-size:15px}section{margin:38px 0}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>一朵云里的城市</h1><p>按作者最新方向重搭：云从两侧、上方和生活面下方包围城市；庭院、街巷和天光开口是云内部的空间。原建筑、配色和58秒路线保留。</p><section><h2>穿窗与云中显露 · 8秒验证段</h2><video controls preload="metadata" poster="preview-v03/230.png" src="cloud-window-reveal-8s-v03.mp4"></video><p>对应全程第9—17秒，12fps，未插帧。用于看包围关系、窗后目标和局部云遮露；完整58秒视频尚未重录。工程仍是24fps、1392帧。</p></section><section class="pair"><figure><img src="preview-v03/outside.png"><figcaption>外部：云的共同包围轮廓，城市部分显露。</figcaption></figure><figure><img src="preview-v03/inside.png"><figcaption>内部：庭院清晰，侧云与上方云带围合，保留天光。</figcaption></figure></section><section><h2>沿线空间</h2><div class="pair"><figure><img src="preview-v03/331.png"><figcaption>下一扇月窗与远区之间保留云的遮挡。</figcaption></figure><figure><img src="preview-v03/1177.png"><figcaption>水巷留出开敞面，保留贴水飞行。</figcaption></figure></div></section><p>这是参考级云和场景，使用近似体积补光。云的外观、局部灰白空面和下层水庭的显露仍可继续细化，未标为最终采用。</p><p><a href="README.md">交付说明</a> · <a href="city-within-cloud-reference-v03.blend">参考渲染工程</a> · <a href="city-within-cloud-58s-v03.blend">Cycles工程</a> · <a href="../../第一季/制作/空间规划/第一集云中园城-v0.1/设计说明.md">设计说明</a></p><p>若聊天中的 .blend 链接不启动 Blender，请在本目录双击“打开云中园城.cmd”。</p></html>'''
(O/'review.html').write_text(page,encoding='utf8')
(O/'打开云中园城.cmd').write_text('@echo off\nchcp 65001 >nul\nstart "" "D:\\blender\\blender.exe" "%~dp0city-within-cloud-reference-v03.blend"\n',encoding='utf8')
meta=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,avg_frame_rate,nb_frames','-of','json',str(O/'cloud-window-reveal-8s-v03.mp4')],capture_output=True,text=True,check=True);(O/'video-metadata.json').write_text(meta.stdout,encoding='utf8')
manifest=[]
for path in sorted(O.iterdir()):
 if path.is_file() and path.suffix in {'.blend','.mp4','.json','.html','.jpg','.md','.cmd'} and path.name!='delivery-manifest.json':manifest.append({'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(O/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
