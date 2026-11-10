"""Deterministic single-component cloud support body, generated outside Blender."""
from pathlib import Path
import argparse,json,numpy as np
from scipy.ndimage import gaussian_filter,label
import trimesh

def marching_cubes(field,level,spacing):
 # Consistent tetrahedralization; shared edge vertices are welded below.
 corners=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]])
 vals=np.stack([field[x:field.shape[0]-1+x,y:field.shape[1]-1+y,z:field.shape[2]-1+z] for x,y,z in corners],axis=-1)
 active=np.argwhere((vals.min(-1)<level)&(vals.max(-1)>=level));cv=vals[tuple(active.T)].astype(np.float64);tris=[]
 for tet in [[0,1,2,6],[0,2,3,6],[0,3,7,6],[0,7,4,6],[0,4,5,6],[0,5,1,6]]:
  v=cv[:,tet]-level;pos=(active[:,None,:]+corners[tet])*np.array(spacing);mask=(v>0).dot(1<<np.arange(4))
  for code in range(1,15):
   sel=mask==code
   if not sel.any():continue
   inside=[j for j in range(4) if code&(1<<j)];outside=[j for j in range(4) if not code&(1<<j)]
   def edge(i,j):
    t=v[sel,i]/(v[sel,i]-v[sel,j]);return pos[sel,i]+t[:,None]*(pos[sel,j]-pos[sel,i])
   if len(inside)==1:tris.append(np.stack([edge(inside[0],j) for j in outside],axis=1))
   elif len(inside)==3:tris.append(np.stack([edge(outside[0],j) for j in inside],axis=1))
   else:
    i,j=inside;k,l=outside;a,b,c,d=edge(i,k),edge(i,l),edge(j,k),edge(j,l)
    tris.extend([np.stack([a,b,c],1),np.stack([b,d,c],1)])
 triangles=np.concatenate(tris);mesh=trimesh.Trimesh(vertices=triangles.reshape(-1,3),faces=np.arange(triangles.size//3).reshape(-1,3),process=True,validate=True);mesh.merge_vertices(digits_vertex=5);mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices();mesh.fix_normals()
 print('BOUNDARY_EDGES',int((np.bincount(mesh.edges_unique_inverse)!=2).sum()),flush=True)
 trimesh.repair.fill_holes(mesh)
 assert mesh.is_watertight,'cloud boundary must be closed'
 return mesh.vertices,mesh.faces,None,None
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();R=Path(a.root);O=R/'视频制作/第一集巨云重构-20261024-v0.1';O.mkdir(exist_ok=True,parents=True)
banks=json.loads((R/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text('utf8'))['platforms']
step=7.5;origin=np.array([-1820,-300,-430.]);xs=np.arange(-1820,440,step);ys=np.arange(-300,1270,step);zs=np.arange(-430,105,step);X=xs[:,None,None];Y=ys[None,:,None];Z=zs[None,None,:]
field=np.full((len(xs),len(ys),len(zs)),-100.,np.float32)
# One coherent root body with an outer shoulder, a school head and a broad neck.
for cx,cy,cz,rx,ry,rz in [(-650,430,-205,945,610,185),(-1350,970,-124,300,230,156),(-1120,755,-160,320,255,170),(-220,100,-180,430,270,165)]:
 v=(1-((X-cx)/rx)**2-((Y-cy)/ry)**2-((Z-cz)/rz)**2)*65
 v+=2.8*np.sin(X/47+np.sin(Y/83))*np.cos(Y/39+Z/63)+1.7*np.sin((X+Y)/23)*np.cos(Z/19)
 np.maximum(field,v,out=field)
# Local living terraces merge down into that body. Their visible circular grass plates are removed.
for b in banks:
 cx,cy,top=b['center'];rx,ry=b['radii'];xy=(1-((X-cx)/(rx*1.12))**2-((Y-cy)/(ry*1.15))**2)*55
 xy+=9*np.sin((X-cx)/31)*np.cos((Y-cy)/37)+5*np.sin((X+Y)/19)
 v=np.minimum(np.minimum(xy,top-Z),Z+245);np.maximum(field,v,out=field)
field=gaussian_filter(field,.8)
print('FIELD_BOUNDARIES',[float(np.take(field,i,axis=ax).max()) for ax in range(3) for i in [0,-1]],flush=True)
components,n=label(field>0);sizes=np.bincount(components.ravel())[1:];assert n==1,(n,sizes.tolist())
verts,faces,normals,values=marching_cubes(field,level=0,spacing=(step,step,step));verts+=origin
np.savez_compressed(O/'mother-cloud-body.npz',vertices=verts,faces=faces)
np.savez_compressed(O/'mother-cloud-field.npz',field=field,origin=origin,step=step)
(O/'body-topology.json').write_text(json.dumps({'voxel_step_m':step,'solid_components':int(n),'vertices':len(verts),'faces':len(faces),'bounds':[verts.min(0).tolist(),verts.max(0).tolist()],'body_role':'one connected supporting cloud mass; not ordinary penetrable fog','banks':banks},ensure_ascii=False,indent=2),encoding='utf8')
print('BODY_READY',len(verts),len(faces),int(n))
