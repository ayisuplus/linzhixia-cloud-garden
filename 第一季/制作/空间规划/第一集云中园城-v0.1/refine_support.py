"""Clear inhabited air above every terraced district from the common support cloud."""
from pathlib import Path
import argparse,json,ast,numpy as np,trimesh
from scipy.ndimage import gaussian_filter,label
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.1';P=R/'视频制作/第一集巨云重构-20261024-v0.1'
helper=R/'第一季/制作/空间规划/第一集巨云与遮露重构-v0.1/build_body.py';tree=ast.parse(helper.read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='marching_cubes'],type_ignores=[]),str(helper),'exec'))
d=np.load(P/'mother-cloud-field.npz');field=d['field'].copy();origin=d['origin'];step=float(d['step']);X=origin[0]+np.arange(field.shape[0])[:,None,None]*step;Y=origin[1]+np.arange(field.shape[1])[None,:,None]*step;Z=origin[2]+np.arange(field.shape[2])[None,None,:]*step
banks=json.loads((R/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text('utf8'))['platforms']
for b in sorted(banks,key=lambda b:b['center'][2],reverse=True):
 x,y,z=b['center'];rx,ry=b['radii'];plan=(1-((X-x)/(rx*1.03))**2-((Y-y)/(ry*1.03))**2)*55
 air=np.minimum(np.minimum(plan,Z-(z+.5)),z+26-Z)
 np.minimum(field,-air,out=field)
# Only remove support volume; no new physical obstacle can be introduced.
assert np.all(field<=d['field']+.0001)
verts,faces,_,_=marching_cubes(field,0,(step,step,step));verts+=origin
np.savez_compressed(O/'refined-support-body.npz',vertices=verts,faces=faces)
np.savez_compressed(O/'refined-support-field.npz',field=field,origin=origin,step=step)
components,n=label(field>0)
(O/'support-refinement.json').write_text(json.dumps({'solid_components':int(n),'only_removed_volume':True,'living_air_above_floor_m':[.5,26],'scope':'Remove cloud volume that encroached into lower terrace air; retain common support below. Original architectural geometry unchanged.'},indent=2),encoding='utf8');print('SUPPORT_REFINED',len(verts),len(faces),int(n),flush=True)
