"""Sculpt connected rock masses with view openings; explicit fixed world positions."""
from pathlib import Path
import numpy as np,json,ast,trimesh
R=Path(__file__).resolve().parents[4];O=R/'视频制作/第一集云山水城-20261024-v0.1'
helper=R/'第一季/制作/空间规划/第一集巨云与遮露重构-v0.1/build_body.py'
tree=ast.parse(helper.read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='marching_cubes'],type_ignores=[]),str(helper),'exec'))
def make(name,lo,hi,step,lobes,holes=(),water_cut=False):
 axes=[np.arange(a,b+step,step,dtype=np.float32) for a,b in zip(lo,hi)];x,y,z=np.meshgrid(*axes,indexing='ij');f=np.full(x.shape,-10,dtype=np.float32)
 for (cx,cy,cz),(rx,ry,rz) in lobes:
  d=1-np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2)
  # Smooth union avoids a pile of disconnected spheres.
  h=np.maximum(.10-np.abs(f-d),0)/.10;f=np.maximum(f,d)+h*h*.025
 f+=.05*np.sin(x*.51+z*.18)*np.cos(y*.43-z*.10)+.023*np.sin(x*1.09+y*.71+z*.84)
 for (cx,cy,cz),(rx,ry,rz) in holes:
  hole=1-np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2);f=np.minimum(f,-hole)
 if water_cut:
  # Basin bed retained at67.7m; unobstructed horizontal spillway and vertical fall.
  basin=np.sqrt(((x+985)/14.5)**2+((y-801)/8.5)**2)
  f=np.minimum(f,np.maximum(basin-1,(67.7-z)/8))
  channel=np.maximum.reduce([np.abs(y-801)/2.2-1,(-1008-x)/12,(x+985)/12,(67.7-z)/8]);f=np.minimum(f,channel)
  fall=np.maximum.reduce([np.abs(y-801)/3.7-1,np.abs(x+1011)/10-1,(44.8-z)/6,(z-69)/6]);f=np.minimum(f,fall)
 verts,faces,_,_=marching_cubes(f,0,spacing=(step,)*3);verts+=np.array(lo)
 np.savez_compressed(O/(name+'.npz'),vertices=verts,faces=faces)
 return {'name':name,'vertices':len(verts),'faces':len(faces),'bounds':[verts.min(0).tolist(),verts.max(0).tolist()]}
records=[]
records.append(make('Main-cloud-stone',(-1025,773,-9),(-940,850,122),.65,[
 ((-983,815,27),(31,23,30)),((-985,809,47),(28,19,26)),((-984,802,62),(19,13,8)),
 ((-977,820,83),(10,12,29)),((-981,819,64),(14,15,23)),((-997,827,68),(10,11,25)),
 ((-963,817,55),(13,12,23)),((-956,808,32),(12,15,22)),((-1003,818,35),(14,17,21)),
 ((-990,835,35),(18,9,26))],holes=[((-991,812,49),(6,50,8)),((-970,820,76),(4.2,19,6))],water_cut=True))
# A low mid-city rock ridge shapes a lateral reveal; it does not become a second main peak.
records.append(make('Middle-low-ridge',(-710,610,-8),(-630,666,64),.65,[
 ((-676,635,19),(28,15,20)),((-692,636,30),(12,13,23)),((-676,638,32),(13,12,20)),
 ((-654,634,20),(17,12,17)),((-641,632,10),(9,10,12))],holes=[((-674,636,26),(6,25,7))]))
(O/'rock-meshes.json').write_text(json.dumps(records,indent=2),encoding='utf8');print(records)
