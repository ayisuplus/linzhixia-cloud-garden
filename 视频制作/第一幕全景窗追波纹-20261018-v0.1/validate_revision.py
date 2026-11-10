"""Read-only content validation; does not render or automate a browser."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def data(path): return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
atlas=data('视频制作/第一幕关键帧图册-20261018-v1.8/atlas.json')
plan=data('视频制作/第一幕Seedance2.5生成分组-20261018-v0.3/plan.json')
manifest=data('视频制作/第一幕全景窗追波纹-20261018-v0.1/manifest.json')
provenance=data('视频制作/第一幕全景窗追波纹-20261018-v0.1/generation-inputs.json')
ids=[s['id'] for s in atlas['shots']]
assert len(ids)==len(set(ids))==18
assert sum(s['seconds'] for s in atlas['shots'])==99
assert [sid for u in plan['units'] for sid in u['shot_ids']]==ids
assert sum(u['requested_seconds'] or 0 for u in plan['units'])==106
assert sum(u['head_handle']+u['tail_handle'] for u in plan['units'])==11
assert sum(u['edit_seconds'] for u in plan['units'] if not u['requested_seconds'])==4
assert all(u['requested_seconds'] is None or u['requested_seconds']<=30 for u in plan['units'])
assert ids.index('E01-A-010')+1==ids.index('E01-A-010-W')
assert ids.index('E01-A-010-W')+1==ids.index('E01-A-011')
assert not atlas['video_produced'] and not plan['video_generated']
rejected={x['path'] for x in provenance.get('_history',[])}
for s in atlas['shots']:
    assert s['presentation']['path'] not in rejected
    assert all(f['path'] not in rejected for f in s.get('state_frames',[]))
assert sum(len(s.get('state_frames',[])) for s in atlas['shots'])==6
assert '衣架仍挂于杆端' not in json.dumps(atlas,ensure_ascii=False)
for f in manifest['frames']:
    assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
    assert (ROOT/f['generation']['prompt']).is_file()
    assert all((ROOT/r).is_file() for r in f['generation']['references'])

class Links(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.ids=set();self.images=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a: self.links.append(a[key])
        if tag=='img': self.images+=1

cache={}
def parse(p):
    if p not in cache:
        parser=Links();parser.feed(p.read_text(encoding='utf-8-sig'));cache[p]=parser
    return cache[p]
pages=['视频制作/第一幕关键帧图册-20261018-v1.8/关键帧图册.html','视频制作/资产图册-20261018-v1.2/资产图册.html','视频制作/第一幕Seedance2.5生成分组-20261018-v0.3/生成分组.html']
checked=0
for rel in pages:
    page=(ROOT/rel).resolve();parser=parse(page)
    for href in parser.links:
        u=urlsplit(href)
        if u.scheme or u.netloc: continue
        target=(page.parent/unquote(u.path)).resolve() if u.path else page
        assert target.is_relative_to(ROOT) and target.is_file(), (rel,href)
        if u.fragment and target.suffix=='.html': assert unquote(u.fragment) in parse(target).ids,(rel,href)
        checked+=1
assets=data('视频制作/资产图册-20261018-v1.2/assets.json')
assert len(assets['assets'])==104
assert len({a['id'] for a in assets['assets']})==104
assert len(manifest['frames'])==5
prior=data('视频制作/第一幕关键帧图册-20261017-v1.7/atlas.json')
assert [s['id'] for s in prior['shots']]==ids
for old,new in zip(prior['shots'],atlas['shots']):
    assert old['dialogue']==new['dialogue'] and old['seconds']==new['seconds']
    if new['id']=='E01-A-009': assert old['state_frames']==new['state_frames']
window=next(s for s in atlas['shots'] if s['id']=='E01-A-010-W')
assert '追上' in window['action'] and '同向近似同速' in window['action']
assert '不代表摄影机停住' in window['state_frames'][1]['limits']
assert not any('微型侧掠' in f['path'] for f in window['state_frames'])
report=dict(valid=True,shots=18,budget_seconds=99,state_frames=6,assets=104,html_pages=3,local_links_checked=checked,ai_generations=6,ai_raw_seconds=106,edit_insert_seconds=4,handles_seconds=11,media_hashes_verified=5,browser_visual_verified=False,browser_reason='file URL observation denied by browser security policy',video_generated=False)
(HERE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
