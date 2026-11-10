"""Replace the visible slab skin with volumetric cloud masses; preserve the exact recorded flight."""
import bpy,math,json,sys,argparse,ast,hashlib,random,time
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--render',default='preview');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root);PREV=ROOT/'视频制作/第一集无人机试飞-20261022-v0.1';OUT=ROOT/'视频制作/第一集无人机试飞-20261022-v0.2';OUT.mkdir(exist_ok=True,parents=True)
SOURCE=PREV/'episode1-drone-rehearsal-v01.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene
layout=json.loads((ROOT/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text(encoding='utf8'));old=json.loads((PREV/'flight-checks.json').read_text(encoding='utf8'))
helper=ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py';names={'section','group','ell','surf'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
COL={};G=None;M={};rng=random.Random(220502)
protected={o.name:(tuple(v for row in o.matrix_world for v in row),len(o.data.vertices) if o.type=='MESH' else -1) for o in S.objects}
def volume(name,density,scale,fade=True):
    m=bpy.data.materials.new(name);m.use_nodes=True;ns=m.node_tree.nodes;ls=m.node_tree.links;ns.clear();out=ns.new('ShaderNodeOutputMaterial');v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Color'].default_value=(.83,.87,.88,1);v.inputs['Anisotropy'].default_value=.25;v.inputs['Emission Color'].default_value=(.83,.87,.88,1);v.inputs['Emission Strength'].default_value=.035
    tc=ns.new('ShaderNodeTexCoord');noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.65;ls.new(tc.outputs['Generated'],noise.inputs['Vector'])
    rem=ns.new('ShaderNodeMapRange');rem.clamp=True;rem.inputs['From Min'].default_value=.22;rem.inputs['From Max'].default_value=.72;rem.inputs['To Min'].default_value=0;rem.inputs['To Max'].default_value=density;ls.new(noise.outputs['Fac'],rem.inputs['Value'])
    if fade:
        sub=ns.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5);ls.new(tc.outputs['Generated'],sub.inputs[0]);length=ns.new('ShaderNodeVectorMath');length.operation='LENGTH';ls.new(sub.outputs[0],length.inputs[0])
        edge=ns.new('ShaderNodeMapRange');edge.clamp=True;edge.interpolation_type='SMOOTHERSTEP';edge.inputs['From Min'].default_value=.26;edge.inputs['From Max'].default_value=.51;edge.inputs['To Min'].default_value=1;edge.inputs['To Max'].default_value=0;ls.new(length.outputs['Value'],edge.inputs['Value'])
        mult=ns.new('ShaderNodeMath');mult.operation='MULTIPLY';ls.new(rem.outputs['Result'],mult.inputs[0]);ls.new(edge.outputs['Result'],mult.inputs[1]);ls.new(mult.outputs[0],v.inputs['Density'])
    else:ls.new(rem.outputs['Result'],v.inputs['Density'])
    # Density-weighted ambient fill approximates multiple scattering without emitting in empty margins.
    fill=ns.new('ShaderNodeMath');fill.operation='MULTIPLY';fill.inputs[1].default_value=.12;ls.new(v.inputs['Density'].links[0].from_socket,fill.inputs[0]);ls.new(fill.outputs[0],v.inputs['Emission Strength'])
    ls.new(v.outputs['Volume'],out.inputs['Volume']);return m
M['puff']=volume('V06 cloud lobe with feathered boundary',.32,5.5)
M['body']=volume('V06 dense cloud interior',.24,11)
M['wisp']=volume('V06 translucent trailing cloud',.075,7)
section('V06_CLOUD_EDGE_REFINEMENT');hidden=[];cores=[];count=0
for o in list(S.objects):
    if o.name.startswith('Soft structural cloud fringe'):
        o.hide_render=True;o.hide_set(True);hidden.append(o.name)
for bank in layout['platforms']:
    cx,cy,z=bank['center'];rx,ry=bank['radii'];depth=bank['depth'];core=S.objects[bank['name']+' structural cloud']
    core.data.materials.clear();core.data.materials.append(M['body']);core['visual_revision']='Volumetric cloud interior; original physical support mesh retained';cores.append(core.name)
    # Follow the actual irregular shore contour, not a different analytic ellipse.
    contour=[core.matrix_world@v.co for v in core.data.vertices[:64]]
    for i in range(0,64,3):
        q=contour[i];rad=Vector((q.x-cx,q.y-cy,0)).normalized();tangent=Vector((-rad.y,rad.x,0));size=rng.uniform(.8,1.25)
        center=q-rad*rng.uniform(1,4)+Vector((0,0,-depth*rng.uniform(.55,.95)))
        lobex=min(rx*.13,22)*size;lobey=min(ry*.16,21)*size;lobez=depth*rng.uniform(.75,1.15)
        o=ell('Billowing cloud margin',center,(lobex,lobey,lobez),'puff');o['physical']=False;o['semantic_role']='Soft visible cloud material around unchanged support core';count+=1
        # Uneven lower lobes interrupt the straight underside without filling the sky gaps.
        if i%2==0:
            c=center-rad*rng.uniform(2,6)+tangent*rng.uniform(-3,3)+Vector((0,0,-depth*rng.uniform(.3,.6)))
            o=ell('Pendant cloud lobe',c,(lobex*.65,lobey*.70,lobez*rng.uniform(.5,.8)),'puff');o['physical']=False;count+=1
        if i%9==0:
            c=center+rad*rng.uniform(5,12)+Vector((0,0,-depth*rng.uniform(.5,1.4)))
            o=ell('Detached soft cloud wisp',c,(lobex*.7,lobey*.6,lobez*.35),'wisp');o['physical']=False;count+=1
# The support strips below the bridges should also dissolve into cloud, leaving the real bridge readable.
for o in S.objects:
    if o.type=='MESH' and o.name.startswith('Load-bearing cloud ribbon'):
        o.data.materials.clear();o.data.materials.append(M['wisp'])
unchanged=[]
for name,(matrix,nverts) in protected.items():
    o=S.objects[name]
    if tuple(v for row in o.matrix_world for v in row)!=matrix or (o.type=='MESH' and len(o.data.vertices)!=nverts):unchanged.append(name)
assert not unchanged,unchanged
cam=S.camera;drone=S.objects['Same carrier ROOT placeholder'];pose_errors=[]
for r in old['records']:
    S.frame_set(r['frame'])
    if (drone.location-Vector(r['drone'])).length>.0001 or (cam.location-Vector(r['camera'])).length>.0001:pose_errors.append(r['frame'])
assert not pose_errors
S.frame_set(1);S.cycles.samples=8;S.cycles.max_bounces=3;S.cycles.volume_bounces=0;S.cycles.volume_step_rate=8;S.cycles.volume_max_steps=64
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S['episode_scope']='Same 24s flight as v01, volumetric cloud silhouette refinement only'
audit={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'protected_object_transforms_and_vertex_counts':len(protected),'unexpected_changes':unchanged,'same_flight_camera_frames':len(old['records']),'pose_errors':pose_errors,'structural_cloud_cores':cores,'old_fringe_hidden':len(hidden),'new_cloud_lobes_and_wisps':count,'change_scope':'Only cloud appearance changed. Original support geometry, garden tops, buildings, drone and camera animation preserved. New lobes are cloud material visualization, no new hard obstacles. Prior collision report applies to unchanged physical geometry; optical occlusion must be judged in rendered frames.'}
(OUT/'cloud-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
old['appearance_revision']='Cloud v02, same original geometry and exact flight';old['appearance_source_sha256']=audit['source_sha256'];(OUT/'flight-checks.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'episode1-drone-rehearsal-v02.blend'))
preview=OUT/'preview';preview.mkdir(exist_ok=True)
for f in ([1,200,384,576] if a.render=='preview' else []):
    S.frame_set(f);S.render.filepath=str(preview/f'{f:04d}.png');t=time.time();bpy.ops.render.render(write_still=True);print('CLOUD_PREVIEW',f,round(time.time()-t,2),flush=True)
print('CLOUD_REFINEMENT_COMPLETE',count,flush=True)
