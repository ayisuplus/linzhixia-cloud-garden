"""Validate saved spatial changes and routes; no claims of continuous physics or final shots."""
import bpy,json,sys,argparse,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(a.root);out=root/'视频制作/第一集航线空间-20261022-v0.2';data=json.loads((out/'route-layout.json').read_text(encoding='utf8'))
school={'E01_SCHOOL_GROUND','E01_DORM','E01_DANCE_HALL'}
local={'E01_HOME_EXTENSION','E01_WATER_LANE','E01_WORKSHOP'}
bpy.ops.wm.open_mainfile(filepath=str(root/data['source']));expected={}
for o in bpy.context.scene.objects:
    cats={c.name for c in o.users_collection}
    if o.type=='MESH' and (cats&school or cats&local or any(c.startswith('HOME_') for c in cats)):
        mat=o.matrix_world.copy()
        if cats&school:mat.translation+=Vector(data['school_translation_m'])
        expected[o.name]={'matrix':[v for row in mat for v in row],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)}
bpy.ops.wm.open_mainfile(filepath=str(out/'episode1-delivery-corridor-v02.blend'));S=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
verts=[];faces=[];names=[]
for o in S.objects:
    if o.type!='MESH' or o.get('physical',True)==False or any(c.name=='E01_FLIGHT_PROXY' for c in o.users_collection):continue
    ev=o.evaluated_get(dg);m=ev.to_mesh();base=len(verts);verts.extend([ev.matrix_world@v.co for v in m.vertices]);faces.extend([tuple(base+i for i in f.vertices) for f in m.polygons]);names.extend([o.name]*len(m.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces)
def ray(q,d,dist):
    p,n,i,t=bvh.ray_cast(Vector(q),Vector(d),dist)
    return (p,n,names[i],t) if i is not None else None
report={'scope':'Flight: 27 sampled offset rays, <=0.5m increments, not complete swept volume. Walk: <=0.25m sampling, three height radial probes, floor support. Not final animation or navigation validation.','routes':{},'source_unchanged':hashlib.sha256((root/data['source']).read_bytes()).hexdigest()==data['source_sha256']}
changed=[]
for name,v in expected.items():
    o=S.objects.get(name)
    if o is None or len(o.data.vertices)!=v['vertices'] or len(o.data.polygons)!=v['polygons'] or any(abs(a-b)>.001 for a,b in zip([q for row in o.matrix_world for q in row],v['matrix'])):changed.append(name)
report['preserved_scene_objects']={'checked':len(expected),'unexpected_changes':changed,'scope':'Existing room/campus mesh counts and expected world transforms; school translation allowed'}
for name,pts in [('parcel',data['flight_points']),('regional_walk',data['walk_points'])]:
    hits=[];floor=[];count=0
    for av,bv in zip(pts,pts[1:]):
        av,bv=Vector(av),Vector(bv);delta=bv-av;steps=max(1,math.ceil(delta.length/(.5 if name=='parcel' else .25)))
        for j in range(steps+1):
            q=av.lerp(bv,j/steps);count+=1
            if name=='parcel':
                for dx in [-.61,0,.61]:
                    for dy in [-.61,0,.61]:
                        for dz in [-.085,.17,.41]:
                            h=ray(q+Vector((dx,dy,dz)),delta.normalized(),delta.length/steps+.001)
                            if h:hits.append({'point':[round(v,3) for v in q],'object':h[2]})
            else:
                h=ray(q+Vector((0,0,.15)),(0,0,-1),.35)
                if not h or abs(h[0].z-q.z)>.10:floor.append({'point':list(q),'object':h[2] if h else None})
                for z in [.2,.9,1.65]:
                    for k in range(12):
                        h=ray(q+Vector((0,0,z)),(math.cos(k*math.tau/12),math.sin(k*math.tau/12),0),.25)
                        if h:hits.append({'point':[round(v,3) for v in q],'object':h[2]})
    report['routes'][name]={'samples':count,'obstacle_hits':hits,'floor_gaps':floor,'pass':not hits and not floor}
report['docks']=[]
for q in [data['flight_points'][0],data['flight_points'][-1]]:
    h=ray(Vector(q)+Vector((0,0,-.08)),(0,0,-1),.10);gap=q[2]-.085-h[0].z if h else None
    report['docks'].append({'support':h[2] if h else None,'gap_m':gap,'pass':gap is not None and abs(gap)<.005})
report['old_adjacent_ramp_removed']=not any(o.name.startswith('Terraced long ramp') for o in S.objects)
report['walk_distance_m']=data['walking_route_distance_m'];report['flight_distance_m']=data['flight_distance_m'];report['building_mass_count']=len(data['blocks'])
(out/'route-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({n:{'samples':r['samples'],'hits':len(r['obstacle_hits']),'floor':len(r['floor_gaps']),'objects':sorted(set(h['object'] for h in r['obstacle_hits']))} for n,r in report['routes'].items()},ensure_ascii=False))
