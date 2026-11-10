from pathlib import Path
from PIL import Image
import hashlib,json,shutil,csv
w=Path.cwd()/'视频制作'
out=w/'主角定稿素材-20261013'
out.mkdir(exist_ok=True)
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assets=[]
groups=[
('01-便服','知夏便服定款三件套-20261012-v3.0','知夏-便服','v3.0','知夏便服精修-20261012-v0.1/知夏-便服15-后脑发结玉簪与双白袜.png'),
('02-校服','知夏水墨校服定款三件套-20261012-v1.0','知夏-水墨校服','v1.0','知夏水墨书院校服-20261012-v0.1/知夏-水墨书院校服05-暖白布靴.png'),
('04-工作服','知夏工作服定款三件套-20261013-v1.0','知夏-工作服','v1.0','知夏工作服精修-20261013-v0.2/知夏-工作服16-花叶绣纹布靴.png')]
def copy(group,name,src,role):
    src=w/src
    assert src.is_file(),src
    dst=out/group/name
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists(): assert hashfile(dst)==hashfile(src)
    else: shutil.copy2(src,dst)
    assert hashfile(dst)==hashfile(src)
    with Image.open(dst) as im:
        size=list(im.size);im.verify()
    assets.append(dict(group=group,role=role,label=group[3:]+'｜'+role,file=str(dst.relative_to(w)).replace('\\','/'),source=str(src.relative_to(w)).replace('\\','/'),sha256=hashfile(dst),size=size,bytes=dst.stat().st_size))
for group,folder,prefix,version,source in groups:
    copy(group,'00-定款原图.png',source,'定款原图')
    for i,(kind,role) in enumerate([('四视图','四视图'),('穿搭分解','穿搭分解'),('妆造分解','妆造分解')],1):
        copy(group,f'{i:02d}-{role}.png',f'{folder}/{prefix}{kind}-{version}.png',role)
    for i,(view,label) in enumerate([('01_front-half','正面半身'),('02_facing-left','左向侧面'),('03_back','背面'),('04_facing-right','右向侧面')],4):
        copy(group,f'{i:02d}-{label}.png',f'{folder}/四视图独立图/{view}.png',label)
copy('00-面容依据','面容主参考-便服07.png','知夏便服精修-20261012-v0.1/知夏-便服07-花绣与玉坠.png','面容依据·服装为历史')
copy('03-睡衣','00-定款09-青瓷绿短裤无云纹.png','知夏睡衣精修-20261012-v0.1/知夏-睡衣09-青瓷绿短裤无云纹.png','定款原图')
copy('05-场景参考','01-半园卧室02.png','半园卧室试稿-v0.1/知夏卧室-清晨-候选02.png','卧室02·方向参考')
copy('05-场景参考','02-半园修复工坊03.png','半园修复工坊试稿-v0.1/半园修复工坊-候选03.png','工坊03·方向参考')
prompts={
'00-面容依据':[w/'知夏便服精修-20261012-v0.1/便服07-实际生成提示词.txt'],
'01-便服':[w/'知夏便服精修-20261012-v0.1/便服15-实际生成提示词.txt',*sorted((w/groups[0][1]).glob('*.txt'))],
'02-校服':[*sorted((w/'知夏水墨书院校服-20261012-v0.1').glob('*实际*提示词.txt')),*sorted((w/groups[1][1]).glob('*.txt'))],
'03-睡衣':[w/'知夏睡衣精修-20261012-v0.1/睡衣08-实际生成提示词.txt',w/'知夏睡衣精修-20261012-v0.1/知夏-睡衣09-青瓷绿短裤无云纹-实际修正提示词.txt'],
'04-工作服':[w/'知夏工作服精修-20261013-v0.2/知夏-工作服16-实际修正提示词.txt',*sorted((w/groups[2][1]).glob('*.txt'))],
'05-场景参考':[w/'半园卧室试稿-v0.1/prompt-02.txt',w/'半园修复工坊试稿-v0.1/prompt-03.txt']}
for group,files in prompts.items():
    title='# '+group+'｜来源与完整提示词\n\n当前状态以本包README和定款原图为准；以下提示词保留历史制作原文，不覆盖后续作者决定。全角色取消皮肤云纹，去智能配件，个人作品不导入Eagle。\n\n'
    if group=='00-面容依据':title+='仅供面容；该图旧服装和配件不得作为当前定款。\n\n'
    if group=='03-睡衣':title+='当前为09去腿纹版；三件套与独立视图未制作，本轮未新增图片。\n\n'
    if group=='05-场景参考':title+='两张场景仅为已认可方向参考，不是多机位定稿。\n\n'
    for f in files:
        assert f.exists(),f
        title+='## '+str(f.relative_to(w)).replace('\\','/')+'\n\n'+f.read_text(encoding='utf-8-sig').strip()+'\n\n'
    (out/group/'来源与提示词.md').write_text(title.rstrip()+'\n',encoding='utf-8')
manifest=dict(date='2026-10-13',scope='当前可用素材；原图及历史文件原位保留',assets=assets,sleepPackage='not_created',imageCount=len(assets))
(out/'素材清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Index existing media and prompt files without moving source files.
rows=[]
current={a['source']:a['role'] for a in assets}
for p in sorted(w.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in ['.png','.jpg','.jpeg','.webp','.mp4','.wav','.mp3','.txt','.md']:continue
    rel=p.relative_to(w)
    if rel.parts[0] in [out.name,'assets','历史归档']:continue
    key=rel.as_posix()
    state='当前入口引用' if key in current else '制作过程/参考/历史，非定款入口'
    rows.append(dict(path=key,status=state,bytes=p.stat().st_size,sha256=hashfile(p)))
with (out/'全量素材索引.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['path','status','bytes','sha256']);writer.writeheader();writer.writerows(rows)
print(json.dumps({'images':len(assets),'indexedFiles':len(rows),'files':[a['file'] for a in assets]},ensure_ascii=False))
