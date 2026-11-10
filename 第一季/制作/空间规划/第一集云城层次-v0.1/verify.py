import sys,json,re,hashlib,ast
from pathlib import Path
from PIL import Image
R=Path(sys.argv[1]);O=R/'视频制作/第一集云城层次-20261024-v0.1'
A=json.loads((O/'audit.json').read_text('utf8'));M=json.loads((O/'media-validation.json').read_text('utf8'))
for p,h in A['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
assert A['stable'] and A['final_verdict']['status']=='pass_with_sampling_limits'
assert not A['flight']['swept_27_hits'] and not A['asset_preservation']['unexpected_changes']
assert M['native_frames']==1392 and M['all_pngs_decoded'] and len(M['videos'])==3 and all(v['full_decode_passed'] for v in M['videos'])
imgs=[]
for p in sorted(O.glob('*.png'))+sorted(O.glob('*.jpg')):
 with Image.open(p) as im:im.load();imgs.append({'file':p.name,'size':list(im.size)})
refs=re.findall(r'(?:src|href|poster)="([^"]+)"',(O/'review.html').read_text('utf8'))
for ref in refs:assert (O/ref).is_file(),ref
for p in Path(__file__).parent.glob('*.py'):ast.parse(p.read_text('utf8'))
result={'audit_hashes_match':True,'source_v18_preserved':True,'three_videos_full_decode':True,'native_frames':1392,'fps':24,'full_duration_seconds':58,'still_images_decoded':imgs,'html_local_references':len(refs),'visual_review':'Final per-second and critical half-second contact sheets plus selected full-size frames; not uninterrupted real-time visual acceptance','remaining_visual_limits':['some broad empty lawns','simplified solid island underside visible in places','final entrance depth visually subtle at oblique view','distant buildings repeat and are visual proxies'],'generated_model_video':False}
(O/'final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
manifest={p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.rglob('*')) if p.is_file() and p.name!='manifest.json' and p.suffix not in ['.log','.blend1','.pyc'] and not any(x in p.parts for x in ['frames','__pycache__'])}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('V19_FINAL_VERIFIED',len(imgs),'images',len(refs),'references',len(manifest),'delivery files')
