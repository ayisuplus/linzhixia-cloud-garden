"""Render only explicitly reviewed image mappings; reference order is not shot order."""
from pathlib import Path
import json
from html import escape as e

d = Path(__file__).resolve().parent
m = json.loads((d / 'manifest.json').read_text(encoding='utf-8'))
css = '''body{background:#f5f1e8;color:#383c32;font:17px/1.7 system-ui;max-width:1200px;margin:auto;padding:28px}img{width:100%;border-radius:10px}article{background:white;padding:22px;border-radius:16px;margin:28px 0}.gap{padding:24px;border:2px dashed #b68a4a;background:#fff8ea}.tag{font-size:14px;color:#6b5531}.notice{border-left:4px solid #a88445;padding:10px 18px;background:#f8f1de}.ref{max-width:650px}a{color:#476858}details{margin-top:18px}summary{cursor:pointer;font-weight:bold}small{color:#696c62}nav a{display:inline-block;margin:6px}h2{margin:0 0 12px}figure{margin:14px 0}figcaption{padding:8px 0}'''
page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>晨起｜图文对应审阅</title><style>'+css+'</style><h1>第一幕 · 逐镜看实际画面</h1><p class="notice">已修正第一拳、第三拳、坐稳和托背的主图引用。每张图只描述实际可见内容。第10、11、14、15镜缺完整画面，现有局部参考另列；全部动态仍未制作。</p><p><a href="README.md">修订说明</a> · <a href="../../第一季/分镜/第一集-A-今天没有安排-托盘智能杯-v0.7.md">完整动作稿</a></p><details><summary>杯盘当前外观参考</summary><img class="ref" src="'+e(m['image'])+'"><p>保留荷叶盘，盘沿无圆环，读数在杯身。此图没有知夏。</p></details><nav>'
page += ''.join('<a href="#'+s['id']+'">'+s['id'][-2:]+' '+e(s['title'])+'</a>' for s in m['shots'])+'</nav>'
for s in m['shots']:
    p = s['presentation']
    assert any(x['path'] == p['path'] for x in s['refs']), s['id']
    assert (d / '../../' / p['path']).resolve().is_file(), p['path']
    page += '<article id="'+s['id']+'"><h2>'+e(s['id']+' '+s['title'])+'</h2><div class="tag">'+e(p['status'])+' · 视频预算 '+str(s['seconds'])+' 秒</div>'
    if p['showAsMain']:
        page += '<figure><a href="../../'+e(p['path'])+'"><img loading="lazy" src="../../'+e(p['path'])+'" alt="'+e(p['visible'])+'"></a><figcaption><b>图中可见：</b>'+e(p['visible'])+'</figcaption></figure>'
    else:
        page += '<div class="gap"><b>此镜完整画面尚缺</b><p>'+e(p['missing'])+'</p></div><details><summary>查看现有辅助参考（非本镜成片画面）</summary><img class="ref" loading="lazy" src="../../'+e(p['path'])+'"><p>'+e(p['visible'])+'</p></details>'
    if p['showAsMain']:
        page += '<p class="notice"><b>尚未体现：</b>'+e(p['missing'])+'</p>'
    page += '<details><summary>视频计划：动作与对白（尚未制作）</summary><p>'+e(s['action'])+'</p><p><b>对白：</b>'+e(s['dialogue'])+'</p><p><b>声音：</b>'+e(s['sound'])+'</p><p>'+e(s['note'])+'</p></details><details><summary>全部制作参考及用途</summary>'
    page += ''.join('<p><a href="../../'+e(x['path'])+'">'+e(Path(x['path']).name)+'</a>：'+e(x['role'])+'</p>' for x in s['refs'])+'</details></article>'
(d / '审阅.html').write_text(page+'</html>', encoding='utf-8')
print('Rendered 16 explicit mappings; 4 complete-frame gaps shown visibly.')
