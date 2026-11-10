"""Resolve independently identified support gaps, preserving the rejected objects hidden."""
import bpy,sys,json,math,ast
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(sys.argv[sys.argv.index('--')+1]);out=root/'视频制作/第一集园城航线重排-20261023-v0.1'
plan=json.loads((out/'space-plan.json').read_text(encoding='utf8'))
badcourts=['Replan 00 compound 03','Replan 04 compound 10'];badgroves=[26,70,71,124,153,157]
for file in ['garden-city-space-v01.blend','garden-city-flight-58s-v04.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(out/file));S=bpy.context.scene;S.frame_set(1)
    if S.get('replan_support_refined'):continue
    hidden=[]
    for o in S.objects:
        if any(o.name.startswith(n+' ') for n in badcourts):o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    # Match each grove by its actual trunk base; generic shrubs/rocks remain linked by local footprint.
    for idx in badgroves:
        x,y,z,h=plan['new_groves'][idx];prefix=None
        for o in S.objects:
            if o.name.startswith('Replan grove ') and 'leaning trunk' in o.name:
                vs=[o.matrix_world@v.co for v in o.data.vertices]
                low=min(v.z for v in vs);near=[v for v in vs if v.z<low+.6]
                c=sum(near,Vector())/len(near)
                if abs(c.x-x)<.4 and abs(c.y-y)<.4:prefix=o.name.split(' leaning trunk')[0];break
        for o in S.objects:
            if prefix and o.name.startswith(prefix+' '):o.hide_render=True;o.hide_set(True);hidden.append(o.name)
            elif o.name.startswith(('Replan low shrub','Replan grove rock')):
                vs=[o.matrix_world@Vector(v) for v in o.bound_box];c=sum(vs,Vector())/8
                if abs(c.x-x)<7 and abs(c.y-y)<7 and abs(c.z-z)<6:o.hide_render=True;o.hide_set(True);hidden.append(o.name)
    helper=root/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py';names={'surf','box','slab','road'}
    exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
    G=bpy.data.collections.new('REPLAN_V01_CANAL_FOUNDATIONS');S.collection.children.link(G);M={'stone':bpy.data.materials['Warm gray garden stone']}
    for i,(x,y,z,w,d) in enumerate(plan['new_canal_houses']):
        if y<0:
            transform=Matrix.Translation((x,y,z))@Matrix.Rotation(math.pi,4,'Z')@Matrix.Translation((-x,-y,-z))
            for o in S.objects:
                if not o.name.startswith('Replan canal house'):continue
                vs=[o.matrix_world@Vector(v) for v in o.bound_box];c=sum(vs,Vector())/8
                if abs(c.x-x)<w/2+2 and abs(c.y-y)<d/2+3:o.matrix_world=transform@o.matrix_world
        # Ground is at -3.465 m; this is a visible stone riverbank podium, not an unsupported floor.
        ymin=-26 if i==0 else -24.9 if i==5 else y-d/2-5
        xmax=-50.2 if i==5 else x+w/2+5
        slab(f'Replan canal {i} stone retaining podium',x-w/2-3,ymin,xmax,y+d/2+5,.02,'stone',3.62)
    S['replan_support_refined']=True
    bpy.ops.wm.save_as_mainfile(filepath=str(out/file))
    (out/'support-fixes.json').write_text(json.dumps({'hidden_courts':badcourts,'hidden_grove_indices':badgroves,'hidden_object_count':len(set(hidden)),'canal_stone_podiums':len(plan['new_canal_houses']),'south_canal_facades_face_water':True},ensure_ascii=False,indent=2),encoding='utf8')
print('SUPPORT_REFINED')
