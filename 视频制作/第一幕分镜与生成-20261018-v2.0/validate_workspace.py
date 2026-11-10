"""Static integrity checks; not a browser or media playback acceptance test."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.images=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for k in ['href','src']:
            if k in a:self.links.append(a[k])
        if tag=='img':self.images+=1
cache={}
def readpage(path):
    if path not in cache:
        p=Page();p.feed(path.read_text(encoding='utf-8-sig'));cache[path]=p
    return cache[path]
path=HERE/'分镜与生成.html';page=readpage(path);checked=0
assert len(page.ids)==len(set(page.ids))
for href in page.links:
    u=urlsplit(href)
    if u.scheme or u.netloc:continue
    target=(path.parent/unquote(u.path)).resolve() if u.path else path
    assert target.is_relative_to(ROOT) and target.is_file(),href
    if u.fragment and target.suffix=='.html':assert unquote(u.fragment) in readpage(target).ids,href
    checked+=1
atlas=json.loads((HERE/'atlas.json').read_text(encoding='utf-8'))
plan=json.loads((HERE/'resolved-plan.json').read_text(encoding='utf-8'))
assert len(atlas['shots'])==21 and sum(s['seconds'] for s in atlas['shots'])==115
assert [sid for u in plan['units'] for sid in u['shot_ids']]==[s['id'] for s in atlas['shots']]
assert sum(u['requested_seconds'] or 0 for u in plan['units'])==126
assert sum(u['head_handle']+u['tail_handle'] for u in plan['units'])==15
html=path.read_text(encoding='utf-8')
from html import escape
for s in atlas['shots']:
    card=html.split('id="'+s['id']+'"',1)[1].split('</article>',1)[0]
    assert escape(s['presentation']['missing']) in card
    for f in s.get('state_frames',[]):assert escape(f['limits']) in card
assert len(list(HERE.glob('prompt-G*.txt')))==8
report=dict(valid=True,shots=21,budget_seconds=115,units=9,ai_batches=8,ai_raw_seconds=126,insert_seconds=4,handles_seconds=15,html_ids=len(page.ids),local_links_checked=checked,images=page.images,browser_visual_verified=False,video_generated=False,verification_scope='static links, source continuity, derived timing and prompt fields; separate unit tests cover snapshot and routing logic')
(HERE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
