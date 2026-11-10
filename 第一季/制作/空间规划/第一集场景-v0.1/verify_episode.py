"""Discrete, reproducible geometry checks against the saved scene, not a gameplay claim."""
import bpy,json,sys,argparse,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(a.root);out=root/'视频制作/第一集三维场景与道路-20261022-v0.1'
data=json.loads((out/'episode-layout.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(out/'episode1-connected-sets-v01.blend'));s=bpy.context.scene
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];names=[]
for o in s.objects:
    if o.type!='MESH' or o.get('physical',True)==False or any(c.name=='E01_FLIGHT_PROXY' for c in o.users_collection):continue
    ev=o.evaluated_get(dg);m=ev.to_mesh();base=len(verts)
    verts.extend([ev.matrix_world@v.co for v in m.vertices]);faces.extend([tuple(base+i for i in f.vertices) for f in m.polygons]);names.extend([o.name]*len(m.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces)
def ray(p,d,dist):
    q,n,i,t=bvh.ray_cast(Vector(p),Vector(d),dist)
    return (q,n,names[i],t) if i is not None else None
report={'scope':'Discrete samples at <=0.20m spacing. Walk: 0.25m radial rays at three body heights and floor probes. Flight: 27 sampled offset rays per position around a box envelope; not complete swept-volume coverage. Not continuous collision, gameplay, accessibility or structural certification.','routes':{},'source_unchanged':hashlib.sha256((root/data['bedroom_source']).read_bytes()).hexdigest()==data['bedroom_source_sha256']}
for name,r in data['routes'].items():
    hits=[];floor=[];count=0
    for av,bv in zip(r['points'],r['points'][1:]):
        av,bv=Vector(av),Vector(bv);delta=bv-av;steps=max(1,math.ceil(delta.length/.20))
        for j in range(steps+1):
            q=av.lerp(bv,j/steps);count+=1
            if r['kind']=='walk':
                h=ray(q+Vector((0,0,.15)),(0,0,-1),.35)
                if not h or abs(h[0].z-q.z)>.10:floor.append({'point':list(q),'object':h[2] if h else None,'height':h[0].z if h else None})
                for z in [.20,.90,1.65]:
                    for k in range(16):
                        h=ray(q+Vector((0,0,z)),(math.cos(k*math.tau/16),math.sin(k*math.tau/16),0),.25)
                        if h:hits.append({'point':[round(v,3) for v in q],'object':h[2],'height':z})
            else:
                # Fits folded proxy irrespective of yaw; endpoint support checked separately.
                for dx in [-.61,0,.61]:
                    for dy in [-.61,0,.61]:
                        for dz in [-.085,.17,.41]:
                            h=ray(q+Vector((dx,dy,dz)),delta.normalized(),delta.length/steps+.001)
                            if h:hits.append({'point':[round(v,3) for v in q],'object':h[2]})
    report['routes'][name]={'samples':count,'obstacle_hits':hits,'floor_gaps':floor,'pass':not hits and not floor}
report['all_routes_pass']=all(r['pass'] for r in report['routes'].values())
report['docking_support']=[]
for label,pos in [('dispatch',data['routes']['parcel']['points'][0]),('receiving',data['routes']['parcel']['points'][-1])]:
    q=Vector(pos);h=ray(q+Vector((0,0,-.08)),(0,0,-1),.1)
    gap=(q.z-.085-h[0].z) if h else None
    report['docking_support'].append({'endpoint':label,'support':h[2] if h else None,'gap_m':gap,'pass':gap is not None and abs(gap)<.005})
report['clear_areas']={}
for label,bounds in [('trial',(4,21,8.5,24.5,.012)),('demonstration',(-24,53,-18,59,6.012))]:
    x1,y1,x2,y2,z=bounds;hits=[];count=0
    for i in range(math.ceil((x2-x1)/.25)+1):
        for j in range(math.ceil((y2-y1)/.25)+1):
            q=(x1+(x2-x1)*i/math.ceil((x2-x1)/.25),y1+(y2-y1)*j/math.ceil((y2-y1)/.25),z+.10);count+=1;h=ray(q,(0,0,1),1.7)
            if h:hits.append(h[2])
    report['clear_areas'][label]={'samples':count,'vertical_obstacles':sorted(set(hits)),'pass':not hits}
(out/'spatial-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({n:{'samples':r['samples'],'hits':len(r['obstacle_hits']),'floors':len(r['floor_gaps']),'objects':sorted(set(h['object'] for h in r['obstacle_hits']))} for n,r in report['routes'].items()},ensure_ascii=False))
