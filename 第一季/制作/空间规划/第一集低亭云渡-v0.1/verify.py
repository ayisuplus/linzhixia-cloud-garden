import sys,json,hashlib,re,ast
from pathlib import Path
from PIL import Image
R=Path(sys.argv[1]);O=R/'视频制作/第一集低亭云渡-20261024-v0.1'
A=json.loads((O/'audit.json').read_text('utf8'))
for p,h in A['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
imgs=[]
for p in sorted(O.glob('*.png')):
 with Image.open(p) as im:im.load();imgs.append({'file':p.name,'size':list(im.size)})
page=(O/'review.html').read_text('utf8')
refs=re.findall(r'(?:src|href|data-src)="([^"]+)"',page)
for ref in refs:assert (O/ref).is_file(),ref
for p in Path(__file__).parent.glob('*.py'):ast.parse(p.read_text('utf8'))
assert len(imgs)==7
checks=['missing_floor','body_clearance_hits','off_island_or_over_cut','headroom_hits']
for x in A['walking_checks']+A['transport_walk_checks']:
 for k in checks:assert not x.get(k), (x,k)
for k in ['unexpected_changes','unrecognised_removal_groups','forbidden_old_transport_leftovers','original_material_changes','original_materials_missing','A_change_outside_declared_cutters']:assert not A['asset_preservation'][k],k
assert A['stable'] and A['asset_preservation']['source_hash_matches_metadata']
result={'images_decoded':imgs,'html_local_references':len(refs),'audit_hashes_match':True,'source_preserved':True,'new_video':False,'visual_review':'Six static rendered views inspected; low silhouettes and boarding relationships readable. Cloud cores, plants and water remain simplified. No continuous video review.'}
(O/'final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.iterdir()) if p.is_file() and p.name!='manifest.json' and p.suffix not in ['.log','.blend1']}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('V18_DELIVERY_VERIFIED',len(imgs),'images,',len(refs),'references, audit hashes match')
