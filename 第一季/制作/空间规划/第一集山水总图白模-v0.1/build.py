import bpy,sys,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent;sys.path.insert(0,str(D));import layout as L
O=R/'视频制作/第一集山水总图白模-20261024-v0.1';O.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);S=bpy.context.scene
def col(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
LAND=col('01 Continuous cloud terrain');WATER=col('02 Descending water spine');ROAD=col('03 Daily routes and crossings');ARCH=col('04 Contour courtyard clusters');CLOUD=col('05 Atmospheric envelope optional');CAM=col('06 Cameras and guides')
def rgba(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
palette={'roof':'#34494b','wall':'#e4dbc5','stone':'#a5aa99','wood':'#8b5836','redwood':'#a4533c','water':'#238c7f','pine':'#355d49','leaf':'#779550','gold':'#c9a45a','window':'#354c43'}
M={}
for k,h in palette.items():
 m=bpy.data.materials.new('Retained CITY05 palette / '+k);m.diffuse_color=rgba(h);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=rgba(h);bs.inputs['Roughness'].default_value=.7 if k!='water' else .24;M[k]=m
for k,c in [('terrain',(.62,.66,.59,1)),('cloudwhite',(.87,.89,.86,1)),('rock',(.32,.37,.33,1)),('road',(.63,.57,.43,1))]:
 m=bpy.data.materials.new('Whitebox / '+k);m.diffuse_color=c;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=c;bs.inputs['Roughness'].default_value=.9;M[k]=m
def mesh(name,vs,fs,key,c,physical=True):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);me.materials.append(M[key] if isinstance(key,str) else key);o['physical']=physical;return o
def box(name,center,size,key,c,angle=0):
 x,y,z=center;sx,sy,sz=np.array(size)/2;co=math.cos(angle);si=math.sin(angle);vs=[]
 for a,b,h in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]:vs.append((x+a*co-b*si,y+a*si+b*co,z+h))
 return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],key,c)
def strip(name,pts,w,key,c,physical=True,conform=False):
 pts=np.array(pts);vs=[]
 for i,p in enumerate(pts):
  d=pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)];n=np.array([-d[1],d[0],0]);n=n/max(np.linalg.norm(n),1e-9)*w/2
  for side in [-1,1]:
   q=p+n*side
   vs.append(q)
 if conform:
  vs=np.array(vs);vs[:,2]=L.terrain(vs[:,:2])+.15
 return mesh(name,vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pts)-1)],key,c,physical)
def beam(name,points,r,key,c):
 vs=[];fs=[]
 for i,p in enumerate(points):
  d=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)]);u=d.normalized().cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=d.normalized().cross(u)
  for j in range(6):vs.append(Vector(p)+r*(u*math.cos(j*math.tau/6)+v*math.sin(j*math.tau/6)))
 for i in range(len(points)-1):
  for j in range(6):fs.append((6*i+j,6*i+(j+1)%6,6*(i+1)+(j+1)%6,6*(i+1)+j))
 return mesh(name,vs,fs,key,c)
def roof(name,loc,size,height,ang):
 # A restrained pitched roof with lifted eave tips; blockout, not final tiles.
 length,width=size;vs=[]
 for x in [-length/2,length/2]:
  for y,z in [(-width/2,.4),(-width*.38,0),(0,height),(width*.38,0),(width/2,.4)]:
   vs.append((loc[0]+x*math.cos(ang)-y*math.sin(ang),loc[1]+x*math.sin(ang)+y*math.cos(ang),loc[2]+z))
 fs=[(i,i+1,i+6,i+5) for i in range(4)]+[(0,4,3,2,1),(5,6,7,8,9)];return mesh(name,vs,fs,'roof',ARCH)
def local(p,x,y,z):return np.r_[np.array(p['center'])+np.array(p['tangent'])*x+np.array(p['outward'])*y,z]
def house(p,name,x,y,sx,sy,h,turn=False):
 z=p['floor'];xy=local(p,x,y,z);ang=math.atan2(p['tangent'][1],p['tangent'][0]);a=ang+(math.pi/2 if turn else 0)
 if p['id']=='Two-level-water-court' and name=='back hall':
  box(p['id']+' lower hall',xy+np.array([0,0,4.1]),(sx,sy,8.2),'wall',ARCH,a)
  for xx in [-9.05,9.05]:box(p['id']+' middle storey pier',local(p,xx,y,z+11.9),(14.9,sy,7.4),'wall',ARCH,a)
  box(p['id']+' upper door lintel',xy+np.array([0,0,14.1]),(sx,sy,4.8),'wall',ARCH,a)
  box(p['id']+' through passage floor',xy+np.array([0,0,8.3]),(3.2,sy,.2),'stone',ARCH,a)
 else:box(p['id']+' / '+name,xy+np.array([0,0,h/2]),(sx,sy,h),'wall',ARCH,a)
 roof(p['id']+' / '+name+' roof',xy+np.array([0,0,h]),(sx+2,sy+2),3,a)
 # Dark recess markers on the court-facing facade convey openings without fine detailing.
 for shift in ([-.3,.3] if p['id']=='Two-level-water-court' and name=='back hall' else [-.3,0,.3]):
  pos=xy+np.array([math.cos(a)*sx*shift-math.sin(a)*sy/2,math.sin(a)*sx*shift+math.cos(a)*sy/2,2.8]);box(p['id']+' / '+name+' opening',pos,(sx*.19,.12,2.7),'window',ARCH,a)
print('BUILD terrain',flush=True)
xs=np.arange(-530,640,2.5);ys=np.arange(-800,960,2.5);grid=np.array([(x,y) for y in ys for x in xs]);known=L.nearest(grid);z=L.terrain(grid,known);st,dd,ids=known
valid=(np.abs(dd)<np.where(dd>=0,L.extent(st,1),L.extent(st,-1))) & (np.linalg.norm(grid-L.XY[ids],axis=1)<np.where(dd>=0,L.extent(st,1),L.extent(st,-1)))
index={int(i):j for j,i in enumerate(np.flatnonzero(valid))};vs=[(grid[i,0],grid[i,1],z[i]) for i in index];fs=[];nx=len(xs)
for iy in range(len(ys)-1):
 for ix in range(nx-1):
  q=[iy*nx+ix,iy*nx+ix+1,(iy+1)*nx+ix+1,(iy+1)*nx+ix]
  if all(i in index for i in q):fs.append(tuple(index[i] for i in q))
ground=mesh('Continuous stable cloud terrain / river bed and inhabited slopes',vs,fs,'terrain',LAND)
for p in ground.data.polygons:p.use_smooth=True
# Water is one continuous ribbon, with asymmetric width and monotone elevation.
water_s=np.linspace(0,1,1001);wv=[]
for s in water_s:
 for side in [-1,1]:wv.append(L.point(s,side*L.width(s,side)))
mesh('Main water spine / upstream to downstream collection',wv,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(water_s)-1)],'water',WATER,False)
paths=[];connections=[]
for side in [-1,1]:
 pts=L.pathline(np.linspace(.006,.974,1001),side);strip('Continuous bank lane '+str(side),pts,4.8,'road',ROAD,conform=True);paths.append({'id':'bank-'+str(side),'type':'daily-bank-route','points':pts.tolist(),'width':4.8})
print('BUILD courts',flush=True)
for p in L.COURTS:
 floor=p['floor'];a=math.atan2(p['tangent'][1],p['tangent'][0]);box(p['id']+' court floor',(*p['center'],floor+.04),(37,37,.16),'stone',ARCH,a)
 house(p,'back hall',0,13,33,9,16.5 if p['id']=='Two-level-water-court' else (9.5 if p['group']=='School' else 7.5))
 house(p,'left wing',-13,-1,23,8,6.8,True);house(p,'right wing',13,-1,23,8,6.8,True)
 # Front wall has an actual 5m entry gap, not a painted door.
 for x in [-10.5,10.5]:box(p['id']+' front wall',local(p,x,-17,floor+1.6),(15,1,3.2),'wall',ARCH,a)
 gate=local(p,0,-18,floor+.18);start=L.point(p['s'],p['side']*(L.width(p['s'],p['side'])+7));start[2]=L.terrain(start[:2])[0]+.17
 source='bank-'+str(p['side'])
 if p['group']=='Slope-neighbourhood':
  start=L.point(p['s'],p['side']*(L.width(p['s'],p['side'])+72));start[2]=L.terrain(start[:2])[0]+.17;source='hill-'+str(p['side'])
 pts=np.linspace(start,gate,41);pts[:,2]=L.terrain(pts[:,:2])+.17;strip(p['id']+' entry connection',pts,3,'road',ROAD,conform=True);paths.append({'id':p['id']+'-entry','type':'entry-ramp','points':pts.tolist(),'width':3});connections.append({'from':source,'to':p['id'],'start':start.tolist(),'end':gate.tolist()})
 p['entry']=gate.tolist()
 # Each court is a coherent local plan with its own footprint, rather than repeated equal lots.
 sc=np.array(p['half_size'])/18.5;origin=np.array(p['center']);tt=np.array(p['tangent']);nn=np.array(p['outward'])
 for ob in list(ARCH.objects):
  if ob.name.startswith(p['id']+' ') and ob.type=='MESH':
   for v in ob.data.vertices:
    delta=np.array(v.co[:2])-origin;v.co.x,v.co.y=origin+tt*np.dot(delta,tt)*sc[0]+nn*np.dot(delta,nn)*sc[1]
 # Rebuild the short entry after scaling the court; keep a 3m walking width.
 end=local(p,0,-18*sc[1],floor+.18);entryob=bpy.data.objects.get(p['id']+' entry connection');bpy.data.objects.remove(entryob,do_unlink=True)
 pts=np.linspace(start,end,41);pts[:,2]=L.terrain(pts[:,:2])+.17;strip(p['id']+' entry connection',pts,3,'road',ROAD,conform=True);paths[-1]['points']=pts.tolist();connections[-1]['end']=end.tolist();p['entry']=end.tolist()
# Three bridges, located in narrow reaches. Flying route stays above them.
for s in [.18,.51,.91]:
 ends=[L.point(s,side*(L.width(s,side)+9)) for side in [-1,1]]
 for q in ends:q[2]=L.terrain(q[:2])[0]+.25
 pts=np.linspace(ends[0],ends[1],31);pts[:,2]+=1*np.sin(np.linspace(0,math.pi,31))**2;strip('Cross-water bridge '+str(s),pts,5,'stone',ROAD)
 for q in pts[::5]:beam('Bridge railing post',[q+np.array([0,2,0]),q+np.array([0,2,1.1])],.08,'wood',ROAD)
 paths.append({'id':'bridge-'+str(s),'type':'cross-bank-bridge','points':pts.tolist(),'width':5});connections.append({'from':'bank--1','to':'bank-1','via':'bridge-'+str(s)})
# Two banks each have a continuous hill street behind the waterside courts.
p=next(x for x in L.COURTS if x['id']=='Two-level-water-court');upper_z=p['floor']+8.4;door=local(p,0,17.6,upper_z);landing=local(p,0,23,upper_z)
for side,a,b in [(1,.42,.76),(-1,.43,.86)]:
 street=L.pathline(np.linspace(a,b,401),side,72)
 # Hill street follows the deliberately cut continuous bench.
 strip('Upper slope street '+str(side),street,4.2,'road',ROAD);paths.append({'id':'hill-'+str(side),'type':'upper-daily-route','points':street.tolist(),'width':4.2})
 if side==1:upper_street=street
 for cs in ([.423,.752] if side==1 else [.433,.568,.852]):
  xx=np.linspace(L.width(cs,side)+7,L.width(cs,side)+72,101);cross=np.array([L.point(cs,side*x) for x in xx]);cross[:,2]=L.terrain(cross[:,:2])+.18
  strip('Bank to slope connector '+str(side)+' '+str(cs),cross,3.6,'road',ROAD,conform=True);paths.append({'id':'slope-link-'+str(side)+'-'+str(cs),'type':'slope-connection','points':cross.tolist(),'width':3.6});connections.append({'from':'bank-'+str(side),'to':'hill-'+str(side),'via':paths[-1]['id']})
q=upper_street[np.argmin(np.linalg.norm(upper_street[:,:2]-landing[:2],axis=1))];ramp=np.vstack([q,landing,door,local(p,0,7,upper_z),local(p,6,7,upper_z)]);strip('Second-level through passage and gallery',ramp,3,'wood',ROAD);paths.append({'id':'middle-entry','type':'upper-entry','points':ramp.tolist(),'width':3})
for pp in [landing,local(p,0,7,upper_z),local(p,6,7,upper_z)]:box('Middle-floor turning platform',pp-np.array([0,0,.12]),(3.6,3.6,.24),'wood',ROAD,math.atan2(p['tangent'][1],p['tangent'][0]))
for pp in [q,landing]:
 bottom=L.terrain(pp[:2])[0];beam('Upper street support',[np.r_[pp[:2],bottom],pp],.3,'wood',ROAD)
lift_xy=local(p,6,4,p['floor']);box('Vertical access reserved shaft',lift_xy+np.array([0,0,4.2]),(3.4,3.4,8.4),'wood',ROAD,math.atan2(p['tangent'][1],p['tangent'][0]));box('Lift upper landing',lift_xy+np.array([0,0,8.3]),(5,5,.25),'stone',ROAD)
connections.extend([{'from':'hill-1','to':p['id']+'-middle-floor','via':'middle-entry'},{'from':p['id'],'to':'hill-1','via':'Vertical access reserved shaft','status':'connected landings, reserved lift; no operating lift simulation'}])
# Upstream framing bridge: a wide circular opening aligned with the river flight direction.
gs=.105;gc=L.point(gs,0,float(L.water_z(gs)+19));t,n=L.basis(gs);gv=[];gf=[]
for depth in [-.6,.6]:
 for r in [7,10]:
  for j in range(72):
   a=j*math.tau/72;gv.append(gc+np.r_[n*r*math.cos(a)+t*depth,r*math.sin(a)])
for j in range(72):
 k=(j+1)%72;gf.extend([(j,k,72+k,72+j),(144+j,216+j,216+k,144+k),(j,144+j,144+k,k),(72+j,72+k,216+k,216+j)])
mesh('School valley framing aperture',gv,gf,'wall',ARCH)
gate_ends=[L.point(gs,side*(L.width(gs,side)+9)) for side in [-1,1]]
for q in gate_ends:q[2]=L.terrain(q[:2])[0]+.2
gate_deck=np.linspace(gate_ends[0],gate_ends[1],61);strip('Framing bridge supported bank to bank',gate_deck,4,'stone',ROAD);paths.append({'id':'framing-bridge','type':'cross-bank-bridge','points':gate_deck.tolist(),'width':4})
for side in [-1,1]:
 foot=L.point(gs,side*9);foot[2]=float(np.mean(gate_deck[:,2]));beam('Framing gate pier',[foot,np.r_[foot[:2],gc[2]]],.7,'stone',ARCH)
# Visible downstream receiving basin is the last section of the water spine; engineered return is a buried schematic.
returnline=[L.point(s,0,float(L.water_z(s)-5)) for s in np.linspace(1,0,101)];beam('Buried return conduit / diagram only',returnline,.7,'water',WATER).hide_render=True
# Shared quay and garden clearings are attached to bank routes between court clusters.
for cs,side,ln in [(.419,1,20),(.557,-1,18),(.743,-1,19),(.90,1,18)]:
 q=L.point(cs,side*(L.width(cs,side)+17));q[2]=L.terrain(q[:2])[0]+.2;tt,nn=L.basis(cs);ang=math.atan2(tt[1],tt[0]);box('Shared waterside landing '+str(cs),q,(ln,17,.3),'stone',ROAD,ang)
 for xx in [-ln*.35,ln*.35]:
  pos=q+np.r_[tt*xx,1.1];box('Quay seating',pos,(3,1.2,.45),'wood',ROAD,ang)
# A small valley resting pavilion uses a natural shoulder; no residential row in the gorge.
cs=.405;q=L.point(cs,L.width(cs,1)+28);q[2]=L.terrain(q[:2])[0]+.2;tt,nn=L.basis(cs);aa=math.atan2(tt[1],tt[0]);box('Valley pavilion base',q,(12,10,.35),'stone',ARCH,aa)
for x in [-5,5]:
 for y in [-4,4]:
  vv=q+np.r_[tt*x+nn*y,0];beam('Pavilion post',[vv,vv+np.array([0,0,5])],.2,'redwood',ARCH)
roof('Valley pavilion roof',q+np.array([0,0,5]),(14,12),3,aa)
# Broad planting reservation bands, without inventing new species.
for side in [-1,1]:
 for a,b in [(.17,.23),(.36,.42),(.72,.76)]:
  pts=[]
  for s in np.linspace(a,b,30):
   q=L.point(s,side*(L.width(s,side)+62));q[2]=L.terrain(q[:2])[0]+.12;pts.append(q)
  strip('Planting reserve '+str(side)+' '+str(a),pts,14,'leaf',LAND,False,True)
# Optional ordinary cloud forms wrap the same terrain from below, sides and above.
cm=bpy.data.materials.new('Ordinary cloud / local soft enclosure');cm.use_nodes=True;nd=cm.node_tree.nodes;lk=cm.node_tree.links;nd.clear();tc=nd.new('ShaderNodeTexCoord');sub=nd.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5);lk.new(tc.outputs['Generated'],sub.inputs[0]);le=nd.new('ShaderNodeVectorMath');le.operation='LENGTH';lk.new(sub.outputs[0],le.inputs[0]);mp=nd.new('ShaderNodeMapRange');mp.inputs['From Min'].default_value=.18;mp.inputs['From Max'].default_value=.49;mp.inputs['To Min'].default_value=.035;mp.inputs['To Max'].default_value=0;lk.new(le.outputs['Value'],mp.inputs['Value']);vo=nd.new('ShaderNodeVolumePrincipled');lk.new(mp.outputs[0],vo.inputs['Density']);vo.inputs['Color'].default_value=(.9,.95,1,1);em=nd.new('ShaderNodeMath');em.operation='MULTIPLY';em.inputs[1].default_value=.6;lk.new(mp.outputs[0],em.inputs[0]);lk.new(em.outputs[0],vo.inputs['Emission Strength']);out=nd.new('ShaderNodeOutputMaterial');lk.new(vo.outputs['Volume'],out.inputs['Volume'])
for i,s in enumerate(np.linspace(.02,.98,14)):
 for side in [-1,1]:
  q=L.point(s,side*(L.width(s,side)+155));q[2]=float(L.water_z(s)+35)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=q);ob=bpy.context.object;ob.name=f'Enclosing side cloud {i} {side}';ob.scale=(115,130,90)
  for cc in list(ob.users_collection):cc.objects.unlink(ob)
  CLOUD.objects.link(ob);ob.data.materials.append(cm);ob['physical']=False
for i,s in enumerate(np.linspace(.05,.95,7)):
 q=L.point(s,0,float(L.water_z(s)+175));bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=q);o=bpy.context.object;o.name='Upper cloud canopy '+str(i);o.scale=(230,150,62)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 CLOUD.objects.link(o);o.data.materials.append(cm);o['physical']=False
CLOUD.hide_render=True
world=bpy.data.worlds.new('Bright reference sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.63,.73,.83,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55;S.world=world
ld=bpy.data.lights.new('Sun','SUN');lo=bpy.data.objects.new('Sun',ld);S.collection.objects.link(lo);ld.energy=2.5;ld.angle=.2;lo.rotation_euler=(.45,-.55,-.6)
S.render.engine='BLENDER_EEVEE';S.eevee.taa_render_samples=24;S.eevee.volumetric_samples=64;S.eevee.use_volume_custom_range=True;S.eevee.volumetric_start=.3;S.eevee.volumetric_end=5000;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.view_settings.view_transform='AgX';S.render.image_settings.file_format='PNG';S.render.fps=24;S.frame_end=1392
def camera(name,loc,target,lens=35,ortho=None):
 d=bpy.data.cameras.new(name);c=bpy.data.objects.new(name,d);CAM.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=10000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 return c
views=[('01-masterplan',(30,50,1900),(30,50,0),40,1850),('02-valley-overview',(1660,-1850,1510),(30,60,65),42,None),('03-school-to-valley',L.point(.075,38,float(L.water_z(.075)+5)),L.point(.21,0,float(L.water_z(.21)+20)),28,None),('04-water-bay',L.point(.535,-35,float(L.water_z(.535)+12)),L.point(.66,0,float(L.water_z(.66)+8)),28,None),('05-two-level-court',local(p,0,-12,p['floor']+1.7),local(p,0,13,p['floor']+9),24,None),('06-home-workshop',L.point(.91,0,float(L.water_z(.91)+8)),L.point(.97,0,float(L.water_z(.97)+6)),28,None)]
for name,loc,target,lens,ortho in views:camera(name,loc,target,lens,ortho)
S.camera=bpy.data.objects['02-valley-overview'];S['status']='Landscape-first spatial blockout; inferred dimensions; cloud-free inspection default; not adopted final art.'
report={'river_length_m':L.LENGTH,'water_samples':[{'s':float(s),'center':L.point(s).tolist(),'left_width':float(L.width(s,1)),'right_width':float(L.width(s,-1))} for s in water_s],'courts':L.COURTS,'paths':paths,'connections':connections,'gate':{'s':gs,'center':gc.tolist(),'normal':t.tolist(),'radius':7},'upper_entry':{'court':p['id'],'floor':p['floor'],'middle_floor':upper_z,'door':door.tolist(),'landing':landing.tolist()},'views':[{'name':v[0],'location':list(v[1]),'target':list(v[2])} for v in views],'scope':'New layout; existing source unchanged. Precise positions are this blockout design, not surveyed data. Water circulation and lift represented, not simulated.'}
(O/'layout-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');bpy.ops.wm.save_as_mainfile(filepath=str(O/'landscape-masterplan-v08.blend'));print('MASTERPLAN_READY',len(L.COURTS),len(S.objects),flush=True)
