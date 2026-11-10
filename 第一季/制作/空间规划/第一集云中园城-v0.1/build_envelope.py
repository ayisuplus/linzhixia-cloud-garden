"""Cloud contains the city: a common cloud envelope with inhabited air pockets and sky openings."""
from pathlib import Path
import argparse,json,ast,numpy as np,trimesh
from scipy.ndimage import gaussian_filter,label
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.1';O.mkdir(parents=True,exist_ok=True)
helper=R/'第一季/制作/空间规划/第一集巨云与遮露重构-v0.1/build_body.py';tree=ast.parse(helper.read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='marching_cubes'],type_ignores=[]),str(helper),'exec'))
step=9.;origin=np.array([-1840,-350,-520.]);xs=np.arange(-1840,450,step);ys=np.arange(-350,1300,step);zs=np.arange(-520,430,step);X=xs[:,None,None];Y=ys[None,:,None];Z=zs[None,None,:]
field=np.full((len(xs),len(ys),len(zs)),-100.,np.float32)
for cx,cy,cz,rx,ry,rz in [(-650,430,-60,950,620,350),(-1350,970,35,300,240,280),(-1120,755,-20,330,280,300),(-220,100,-25,440,290,280)]:
 v=(1-((X-cx)/rx)**2-((Y-cy)/ry)**2-((Z-cz)/rz)**2)*75
 v+=7*np.sin(X/68+np.sin(Y/97))*np.cos(Y/59+Z/85)+4*np.sin((X+Y)/31)*np.cos(Z/43)
 np.maximum(field,v,out=field)
def air(cx,cy,cz,rx,ry,rz):
 global field
 v=(1-((X-cx)/rx)**2-((Y-cy)/ry)**2-((Z-cz)/rz)**2)*55
 np.minimum(field,-v,out=field)
# A continuous inhabited interior. The cloud surrounds its lateral and upper edges.
air(-650,430,62,850,515,155)
air(-1350,970,85,246,180,130)
air(-1115,800,105,190,130,130)
# Open courtyards have real sky and daylight; overhead cloud remains between the openings.
for q in [(-1330,975,270,150,115,230),(-805,740,240,170,130,210),(-660,565,235,145,120,200),(-375,315,210,125,110,190),(-155,25,185,210,84,205),(-1020,490,210,115,95,190)]:air(*q)
# Near-field cavities keep actual architecture and its entrance sightlines legible.
banks=json.loads((R/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text('utf8'))['platforms']
for b in banks:
 x,y,z=b['center'];rx,ry=b['radii'];air(x,y,z+42,rx+38,ry+35,76)
flight=json.loads((R/'视频制作/第一集巨云重构-20261024-v0.1/flight-checks.json').read_text('utf8'))
# This is ordinary enveloping cloud, not an invented solid ceiling. Carve viewing corridors,
# keeping real support cloud separate and retaining local translucent curtains later.
for row in flight['records'][::24]:
 x,y,z=row['camera'];air(x,y,z+8,42,42,48)
field=gaussian_filter(field,.7)
assert all(np.take(field,i,axis=ax).max()<0 for ax in range(3) for i in [0,-1])
c,n=label(field>0);sizes=np.bincount(c.ravel())[1:];main=int(sizes.argmax())+1
if n>1:field=np.where((c==main)|(field<=0),field,-1)
verts,faces,_,_=marching_cubes(field,0,(step,step,step));verts+=origin
np.savez_compressed(O/'enveloping-cloud.npz',vertices=verts,faces=faces)
np.savez_compressed(O/'envelope-field.npz',field=field,origin=origin,step=step)
(O/'envelope-topology.json').write_text(json.dumps({'grid_step_m':step,'initial_components':int(n),'retained_main_component':True,'vertices':len(verts),'faces':len(faces),'bounds':[verts.min(0).tolist(),verts.max(0).tolist()],'role':'Ordinary cloud enveloping the city; stable structural cloud is separate, retained from the checked route. Sky openings and inhabited air pockets are visual layout, not a newly decided world technology.'},ensure_ascii=False,indent=2),encoding='utf8')
print('ENVELOPE_READY',len(verts),len(faces),flush=True)
