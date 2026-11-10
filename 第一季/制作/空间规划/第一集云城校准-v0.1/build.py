"""v12: worldbuilding repair, additive except recorded terrain rim and local replacements."""
import bpy,bmesh,sys,json,math,hashlib,shutil,random
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(sys.argv[sys.argv.index('--')+1]);D=Path(__file__).parent
sys.path.insert(0,str(D.parent/'第一集水巷街桥-v0.1'));import geometry as G
sys.path.insert(0,str(D.parent/'第一集山水总图白模-v0.1'));import layout as L
OLD=R/'视频制作/第一集云山聚落-20261024-v0.1';O=R/'视频制作/第一集云城校准-20261024-v0.1';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OLD/'cloud-hamlet-masterplan-v11.blend'));S=bpy.context.scene
for m in bpy.data.materials:
 if ' / ' in m.name:G.M[m.name.split(' / ')[-1]]=m
if 'gold' not in G.M:
 m=G.M['wood'].copy();m.name='Retained CITY05 palette / gold';rgb=[int('c9a45a'[i:i+2],16)/255 for i in (0,2,4)];rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,);m.diffuse_color=rgba
 next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=rgba;G.M['gold']=m
if 'cloudwhite' not in G.M:
 m=G.M['terrain'].copy();m.name='Whitebox / cloudwhite';m.diffuse_color=(.87,.89,.86,1);next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=m.diffuse_color;G.M['cloudwhite']=m
def col(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
SCHOOL=col('16 Ink campus and shipping porch');ACCESS=col('17 Hillside shared access');PORT=col('18 Two height ferry pavilion');HOME=col('19 Banyuan and workshop life');ECO=col('20 Cloud ecology and water cycle');CLOUD=bpy.data.collections['05 Atmospheric envelope optional']
records={'removed':[],'features':[],'walk_links':[],'support_roots':[]};rng=random.Random(24102412)
ground=bpy.data.objects['Continuous stable cloud terrain / river bed and inhabited slopes']
def rebuild_ground():
 global gb
 gb=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[tuple(f.vertices) for f in ground.data.polygons])
rebuild_ground()
def gz(xy):
 hit=gb.ray_cast(Vector((*xy,600)),Vector((0,0,-1)),1200)
 if hit[0] is None:return None
 return hit[0].z
def loc(s,side,x,q,z):
 t,n=L.basis(s);return np.r_[L.center(s)[0]+t*x+n*side*(float(L.width(s,side))+q),z]
def angle(s):return math.atan2(*L.basis(s)[0][::-1])
def oval(name,xyz,scale,key,c,physical=True,noise=.04):
 me=bpy.data.meshes.new(name);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);c.objects.link(ob);ob.location=xyz;ob.scale=scale
 for v in me.vertices:v.co*=1+noise*math.sin(v.co.x*9+v.co.y*6+v.co.z*8)
 for f in me.polygons:f.use_smooth=True
 me.materials.append(G.M[key] if isinstance(key,str) else key);ob['physical']=physical;return ob
def beam(name,a,b,r,key,c):return G.beam(name,[a,b],r,key,c)
def grounded_post(name,xy,top,c,key='wood',r=.22):
 z=gz(xy)
 if z is None:raise ValueError(('ungrounded post',name,xy))
 beam(name,(*xy,z-.4),(*xy,top),r,key,c);records['support_roots'].append({'name':name,'xy':list(xy),'bottom':z-.4,'top':top})
def walkway(name,pts,width,c,key='stone',rails=True,support=True):
 pts=np.array(pts,float);vs=[]
 for i,p in enumerate(pts):
  d=pts[min(i+1,len(pts)-1),:2]-pts[max(0,i-1),:2];n=np.array([-d[1],d[0]])/np.linalg.norm(d)
  for off,dz in [(-width/2,-.28),(width/2,-.28),(-width/2,0),(width/2,0)]:vs.append((* (p[:2]+off*n),p[2]+dz))
 fs=[]
 for i in range(len(pts)-1):
  a=i*4;b=a+4;fs.extend([(a+2,a+3,b+3,b+2),(a,b,b+1,a+1),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 fs.extend([(0,1,3,2),(len(vs)-4,len(vs)-2,len(vs)-1,len(vs)-3)]);G.mesh(name,vs,fs,key,c)
 if rails:
  for side in [-1,1]:
   line=[]
   for i,p in enumerate(pts):
    d=pts[min(i+1,len(pts)-1),:2]-pts[max(0,i-1),:2];n=np.array([-d[1],d[0]])/np.linalg.norm(d);line.append(np.r_[p[:2]+n*side*width/2,p[2]+1.1])
   G.beam(name+' edge rail',line,.065,'wood',c)
 if support:
  for i,p in enumerate(pts):
   d=pts[min(i+1,len(pts)-1),:2]-pts[max(0,i-1),:2];n=np.array([-d[1],d[0]])/np.linalg.norm(d)
   for side in [-1,1]:
    xy=p[:2]+n*side*(width/2+.3);z=gz(xy)
    if z is not None and p[2]-z>.5:grounded_post(name+' side support '+str(i),xy,p[2]-.15,c,r=.18)
 records['walk_links'].append({'name':name,'points':pts.tolist(),'width':width})

# Freeze the middle flight; school now travels outside the pedestrian arcade.
poses=json.loads((OLD/'route-poses.json').read_text('utf8'));oldpos=np.array([p['position'] for p in poses]);positions=oldpos.copy();stations=L.nearest(oldpos[:,:2])[0]
def smooth(x):x=np.clip(x,0,1);return x*x*x*(10+x*(-15+6*x))
for i,s in enumerate(stations):
 if s<.145:positions[i,:2]-=L.basis(float(s))[1]*12*(1-smooth((s-.10)/.045))
 if s<.155:positions[i,2]+=9*smooth((s-.055)/.04)*(1-smooth((s-.115)/.04))
endcourt=next(p for p in L.COURTS if p['id']=='Repair-workshop');t=np.array(endcourt['tangent']);out=np.array(endcourt['outward']);entry_scale=endcourt['half_size'][1]/18.5
arrival_xy=np.array(endcourt['center'])-out*(18*entry_scale+4)+t*7
arrival_z=endcourt['floor']+4.5;delta=np.r_[arrival_xy-out*6-t*2,arrival_z]-positions[-1]
for i in range(len(poses)):
 if i>1300:positions[i]+=delta*smooth((i-1300)/(1391-1300))
quats=[Quaternion(p['quaternion']) for p in poses]
for i in range(len(poses)):
 if i<210:
  direction=Vector(positions[min(i+10,1391)]-positions[max(0,i-3)]);direction.z-=.035*math.hypot(direction.x,direction.y)
  if direction.length>.01:quats[i]=direction.to_track_quat('-Z','Y').slerp(quats[i],float(smooth((i-165)/45)))
  if i<72:
   look=Vector(loc(.018,1,0,12.5,102)-positions[i]);quats[i]=look.to_track_quat('-Z','Y').slerp(quats[i],float(smooth(i/72)))
 if i>1300:
  target=np.r_[arrival_xy,endcourt['floor']+1.4];direction=Vector(target-positions[i]);quats[i]=quats[i].slerp(direction.to_track_quat('-Z','Y'),float(smooth((i-1300)/91)))
 if i and quats[i].dot(quats[i-1])<0:quats[i].negate()
for i,p in enumerate(poses):p['position']=positions[i].tolist();p['quaternion']=list(quats[i])
(O/'route-poses.json').write_text(json.dumps(poses),encoding='utf8')

# Open only uninhabited outer valley shoulders; preserve every inhabited inner bench.
xyz=np.array([v.co[:] for v in ground.data.vertices]);ss,dd,_=L.nearest(xyz[:,:2]);sides=np.where(dd>=0,1,-1);qq=np.abs(dd)-np.where(dd>=0,L.width(ss,1),L.width(ss,-1));changed=[]
cut=142-48*np.exp(-((ss-.245)/.034)**2)-46*np.exp(-((ss-.365)/.025)**2)
active=(ss>.155)&(ss<.415)&(qq>80)
for i in np.where(active)[0]:
 fade=min(1,(ss[i]-.155)/.022,(.415-ss[i])/.022)*smooth((qq[i]-80)/27)
 dz=-.70*fade*max(0,xyz[i,2]-float(L.water_z(ss[i]))+6)
 ground.data.vertices[int(i)].co.z+=dz;changed.append(int(i))
notch=(dd>0)&(ss>.23)&(ss<.34)&(qq>58)
for i in np.where(notch)[0]:
 fade=smooth((ss[i]-.23)/.025)*(1-smooth((ss[i]-.315)/.025))*smooth((qq[i]-58)/18)
 target=float(L.water_z(ss[i]))+3+(qq[i]-58)*.045;v=ground.data.vertices[int(i)];v.co.z+=(min(v.co.z,target)-v.co.z)*fade;changed.append(int(i))
cut=np.where((dd>0)&(ss>.255)&(ss<.315),np.minimum(cut,90),cut)
# Scalloped windows are outward of all current mountain homes and paths.
remove_faces=[f.index for f in ground.data.polygons if all(active[i] and qq[i]>cut[i] for i in f.vertices)]
bm=bmesh.new();bm.from_mesh(ground.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in remove_faces],context='FACES_ONLY');bm.to_mesh(ground.data);bm.free();ground.data.update();rebuild_ground()
records['terrain']={'changed_vertex_count':len(set(changed)),'removed_outer_face_count':len(remove_faces),'scope':'outer s .155-.415 q>80 plus uninhabited left s .23-.34 q>58; no housing bench moved'}
# Existing exposed-rock seams follow the changed ground, retaining their surface relief.
oldgb=BVHTree.FromPolygons([Vector(p) for p in xyz],[tuple(f.vertices) for f in ground.data.polygons])
for ob in bpy.data.collections['15 Terrain rooted rock seams'].objects:
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co;before=oldgb.ray_cast(Vector((p.x,p.y,600)),Vector((0,0,-1)),1200)[0];after=gz((p.x,p.y))
  if before is not None and after is not None:v.co.z+=after-before.z
print('CLOUD_RIM',len(changed),len(remove_faces),flush=True)
# Cloud material copies: density variation makes soft edges and internal pockets.
base=bpy.data.materials['Ordinary cloud / local soft enclosure']
def cloudmat(name,density):
 m=base.copy();m.name=name;ns=m.node_tree.nodes;lk=m.node_tree.links
 for node in ns:
  if node.type=='MAP_RANGE':node.inputs['To Min'].default_value=density
 vo=next(n for n in ns if n.type=='PRINCIPLED_VOLUME');old=vo.inputs['Density'].links[0].from_socket
 tex=ns.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3.6;tex.inputs['Detail'].default_value=2
 coord=next(n for n in ns if n.type=='TEX_COORD');lk.new(coord.outputs['Generated'],tex.inputs['Vector']);mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';lk.new(old,mul.inputs[0]);lk.new(tex.outputs['Fac'],mul.inputs[1]);lk.new(mul.outputs[0],vo.inputs['Density']);return m
rim=cloudmat('Ordinary cloud / broken soft rim v12',.028);veil=cloudmat('Ordinary cloud / ink exit veil v12',.021)
for j,s in enumerate([.175,.225,.272,.325,.371,.405]):
 for side in [-1,1]:
  p=loc(s,side,0,87,float(L.water_z(s))+5);o=oval('Breathing cloud shoulder',p,(46,25,14),rim,CLOUD,False,.07);o.rotation_euler.z=angle(s)
for dx in [-25,0,25]:
 p=loc(.122,1,0,dx-float(L.width(.122,1)),108);o=oval('Ink campus exit atmospheric veil',p,(11,24,15),veil,CLOUD,False);o.rotation_euler.z=angle(.122)

# Add functional departure platform off the walking lane and a private warm room.
s=.018;floor=98.26;a=angle(s);G.ARCH=SCHOOL
startxy=positions[0,:2]
walkway('Dorm shipping jetty',[loc(s,1,0,4,floor),loc(s,1,0,-5,floor)],3.4,SCHOOL,rails=False)
G.box('Dorm parcel berth',(*startxy,floor-.16),(4,4,.32),'stone',SCHOOL,a)
for x in [-1.6,1.6]:
 for q in [-6.6,-3.4]:grounded_post('Dorm jetty foot',loc(s,1,x,q,0)[:2],floor,SCHOOL)
def perch(name,xy,floor,c,a):
 G.box(name+' stem',(*xy,floor+.62),(.28,.28,1.24),'wood',c,a);G.box(name+' load tray',(*xy,floor+1.26),(1.3,.9,.12),'stone',c,a)
 for side in [-1,1]:beam(name+' guide',(* (xy+np.array([math.cos(a),math.sin(a)])*side*.65),floor+1.28),(* (xy+np.array([math.cos(a),math.sin(a)])*side*.65),floor+1.52),.045,'gold',c)
 records['features'].append({'id':name,'kind':'parcel interface proposal','xy':list(xy),'tray_top':floor+1.32})
perch('Dorm departure perch',startxy,floor,SCHOOL,a)
rf=99.5
roomxy=loc(s,1,0,16,rf)[:2];rt,rn=L.basis(s)
def rp(x,y,z):return np.r_[roomxy+rt*x+rn*y,z]
warm=G.M['wall'].copy();warm.name='Private dorm warm wall exempt from public ink';G.M['private']=warm
for x in [-5,5]:G.box('Dorm private side wall',rp(x,0,rf+2.8),(.25,7,5.6),'private',SCHOOL,a)
G.box('Dorm private rear wall',rp(0,3.5,rf+2.8),(10,.3,5.6),'private',SCHOOL,a)
G.box('Dorm private rf',rp(0,0,rf-.12),(10,7,.24),'wood',SCHOOL,a)
G.roof('Dorm doorway light canopy',rp(0,0,rf+5.8),(12,9),1.8,a)
G.box('Dorm open door left',rp(-3.7,-3.5,rf+2.8),(2.6,.25,5.6),'wall',SCHOOL,a);G.box('Dorm open door right',rp(3.7,-3.5,rf+2.8),(2.6,.25,5.6),'wall',SCHOOL,a)
G.box('Dorm packing desk',rp(0,-.4,rf+1.1),(3,1.3,.16),'wood',SCHOOL,a)
for x in [-1.2,1.2]:grounded_post('Dorm desk leg',rp(x,-.4,0)[:2],rf+1.05,SCHOOL,r=.07)
G.box('Dorm spare shoe box',rp(.45,-.4,rf+1.4),(.8,.5,.4),'private',SCHOOL,a)
walkway('Dorm door approach',[loc(.018,1,0,7,98.26),loc(.018,1,0,10,98.26),loc(.018,1,0,12.5,rf)],3,SCHOOL,rails=False)
for k in range(8):
 p=loc(.018,1,0,10+(k+.5)*2.5/8,0);top=98.26+(rf-98.26)*(k+1)/8;bottom=min(top-.25,gz(p[:2])-.2);G.box('Dorm threshold stone step',(*p[:2],(top+bottom)/2),(3,2.5/8+.015,top-bottom),'stone',SCHOOL,angle(.018))
# A single open learning pavilion across the water distinguishes the school from shops.
s=.065;f=98.26;a=angle(s);p=loc(s,-1,0,-4,f)
G.box('Open practice hall platform',p-np.array([0,0,.18]),(22,12,.36),'stone',SCHOOL,a)
for x in [-10,10]:
 for q in [-9,1]:grounded_post('Practice hall slender frame',loc(s,-1,x,q,0)[:2],f+7.5,SCHOOL,r=.16)
G.roof('Practice hall floating eaves',p+np.array([0,0,7.5]),(26,15),1.1,a)
beam('Practice barre',loc(s,-1,-8,0,f+1.1),loc(s,-1,8,0,f+1.1),.065,'wood',SCHOOL)
for x in [-8,8]:beam('Practice barre foot',loc(s,-1,x,0,f),loc(s,-1,x,0,f+1.1),.055,'wood',SCHOOL)
walkway('Practice hall shore access',[loc(s,-1,0,2,f),loc(s,-1,0,7,f)],3,SCHOOL,rails=False)
records['features'].append({'id':'campus','kind':'public ink environment, private color dorm and actual outdoor parcel berth','boundary':'atmospheric visual transition only'})

# Hillside access: each pair shares a two-stop lift and upper connecting gallery.
data=json.loads((OLD/'landscape-data.json').read_text('utf8'));access_bounds=[]
glass=G.M['window'].copy();glass.name='Shared lift lightly glazed sides';glass.diffuse_color=(.25,.39,.35,.23)
bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.25,.39,.35,1);bs.inputs['Alpha'].default_value=.23;G.M['glass']=glass
for j in range(3):
 low,up=data['houses'][j*2:j*2+2];s=low['s'];side=low['side'];a=angle(s);lx=max(low['length']/2,up['xoffset']+up['length']/2)+7;lf=low['floor'];uf=up['floor'];q=31
 def lp(x,q,z):return loc(s,side,x,q,z)
 center=lp(lx,q,0)[:2]
 for x in [-1.8,1.8]:
  for y in [-1.8,1.8]:grounded_post(f'H{j+1} lift frame',lp(lx+x,q+y,0)[:2],uf+3,ACCESS,r=.13)
 for x in [-1.9,1.9]:G.box(f'H{j+1} lift glazed side',lp(lx+x,q,(lf+uf+2.7)/2),(.08,3.8,uf+2.7-lf),'glass',ACCESS,a)
 G.box(f'H{j+1} lift roof',lp(lx,q,uf+3),(4.4,4.4,.22),'roof',ACCESS,a)
 G.box(f'H{j+1} lift cabin at lower stop',lp(lx,q,lf-.12),(3.4,3.4,.24),'stone',ACCESS,a)
 walkway(f'H{j+1} lower access',[lp(low['length']/2,38,lf),lp(lx,38,lf),lp(lx,q+1.65,lf)],2.5,ACCESS)
 walkway(f'H{j+1} upper gallery',[lp(up['xoffset']+up['length']/2,61,uf),lp(lx,61,uf),lp(lx,q+1.65,uf)],2.5,ACCESS)
 records['features'].append({'id':f'H{j+1} shared lift','kind':'two stop candidate, static cabin lower; operation not animated','center':center.tolist(),'lower':lf,'upper':uf})

# Two-height public landing; the same floating ferry is the recurring bay landmark.
s=.635;side=1;a=angle(s);w=float(L.water_z(s));G.ARCH=PORT
def pp(x,q,z):return loc(s,side,x,q,z)
publicfloor=max(gz(pp(x,q,0)[:2]) for x in [-9,-7,-5] for q in [13,15,17])+.2
walkway('Ferry lower bank entry',[pp(-7,7,w+2.26),pp(-7,10,w+2.26),pp(-7,13.10,publicfloor),pp(-7,15,publicfloor)],3.2,PORT,rails=False)
walkway('Ferry upper landing',[pp(-7,15,w+11.3),pp(-7,0,w+11.3),pp(7,0,w+11.3)],3.5,PORT,rails=False)
for x in [-9,-5]:
 for q in [13,17]:grounded_post('Public lift frame',pp(x,q,0)[:2],w+14,PORT,r=.16)
for x in [-9.1,-4.9]:G.box('Public lift glazed side',pp(x,15,w+7.8),(.1,4.2,11.1),'glass',PORT,a)
G.box('Public lift lower cabin',pp(-7,15,publicfloor-.16),(3.7,3.7,.32),'stone',PORT,a)
G.box('Public lift cap',pp(-7,15,w+14.1),(4.8,4.8,.25),'roof',PORT,a)
walkway('Upper boarding bridge',[pp(7,0,w+11.3),pp(7,-11,w+11.3)],2.5,PORT,rails=False,support=False)
boat=pp(7,-15,w+11.3);length=19;breadth=5.8;vs=[]
for z,scale in [(-1.7,.6),(0,1)]:
 for x,y in [(-length/2,0),(-length*.32,-breadth/2),(length*.32,-breadth/2),(length/2,0),(length*.32,breadth/2),(-length*.32,breadth/2)]:
  t,n=L.basis(s);vs.append((* (boat[:2]+t*x*scale+n*side*y*scale),boat[2]+z))
G.mesh('Cloud ferry hull',vs,[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]+[tuple(range(6,12))],'wood',PORT)
for x in [-5.8,0,5.8]:
 for q in [-17.2,-12.8]:beam('Ferry canopy column',pp(7+x,q,w+11.3),pp(7+x,q,w+14.7),.10,'gold',PORT)
G.roof('Ferry light curved canopy',boat+np.array([0,0,3.6]),(15,6.7),1.1,a)
for x in [-5,5]:G.box('Ferry passenger bench',pp(7+x,-15,w+11.85),(3,1,.4),'wood',PORT,a)
records['features'].append({'id':'bay-ferry','kind':'one physical docked public vehicle and two height landing, form candidate','center':boat.tolist(),'station':s})

# Banyuan work/life identity; front porches are attached to actual court entry heights.
for kind in ['Repair-workshop','Zhixia-home']:
 p=next(p for p in L.COURTS if p['id']==kind);t=np.array(p['tangent']);n=np.array(p['outward']);c=np.array(p['center']);f=p['floor'];a=math.atan2(t[1],t[0]);sc=np.array(p['half_size'])/18.5
 def hp(x,y,z):return np.r_[c+t*x+n*y,z]
 front=-18*sc[1]
 if kind=='Repair-workshop':
  start=hp(1.5,front-4,f+.18);start[2]=gz(start[:2])+.16
  walkway('Workshop receiving porch',[start,hp(7,front-4,f+.18)],3.2,HOME,rails=False)
  perch('Workshop arrival perch',arrival_xy,f+.18,HOME,a)
  G.box('Workshop open workbench',hp(-6,front-1,f+1.08),(4,1.5,.16),'wood',HOME,a)
  for x in [-7.5,-4.5]:grounded_post('Workshop bench leg',hp(x,front-1,0)[:2],f+1,HOME,r=.10)
  for j in range(5):G.box('Workshop repair tray',hp(-7+j*.52,front-1,f+1.24),(.35,.5,.17),'stone' if j%2 else 'wood',HOME,a)
  # Local repair identity: spare timber, small cabinet, unfinished lattice panel.
  for j in range(4):
   pstock=hp(8+j*.27,front-2.5,0);pstock[2]=gz(pstock[:2])+.45;G.box('Workshop timber stock',pstock,(.18,1.8,.9),'wood',HOME,a)
  for j in range(4):beam('Unfinished lattice panel',hp(-9+j*.45,front-1.7,f+.3),hp(-9+j*.45,front-1.7,f+2.6),.06,'wood',HOME)
 else:
  # Courtyard objects remain small and usable, with an open front-to-room axis.
  G.box('Banyuan shallow pond rim',hp(4,-2,f+.18),(3,4,.36),'stone',HOME,a)
  G.box('Banyuan courtyard pond water',hp(4,-2,f+.38),(2.4,3.4,.05),'water',HOME,a)
  for y in [-5,0]:
   G.box('Banyuan earth gardening bed',hp(-4,y,f+.3),(2,3,.6),'wood',HOME,a)
   oval('Banyuan cultivated shrub',hp(-4,y,f+1.3),(1.1,1.25,1.2),'leaf',HOME)
  walkway('Banyuan small front sitting terrace',[hp(6,front-3,f+.17),hp(10,front-3,f+.17)],2.5,HOME,rails=False)
  G.box('Banyuan resting bench',hp(8,front-3,f+.65),(3,.75,.3),'wood',HOME,a)
  for j in range(3):G.box('Banyuan repaired timber patch',hp(-5+j*.8,front-1.3,f+1.6),(.5,.16,1.7),'wood',HOME,a)
 records['features'].append({'id':kind,'kind':'retained two-bank identity with exterior use cues','center':c.tolist()})

# A small cloud-root garden candidate sits beside, not inside, the flight corridor.
s=.245;side=-1;a=angle(s);rootp=loc(s,side,0,90,0);rootp[2]=gz(rootp[:2])+1
oval('Stable cloud root garden shoulder',rootp,(14,10,2.4),'cloudwhite',ECO,True,.08)
for j in range(3):
 p=loc(s,side,-6+j*6,90,rootp[2]+2);beam('Cloud garden rooted trunk',p,p+np.array([0,0,8+j]),.18,'wood',ECO)
 oval('Cloud garden crown candidate',p+np.array([0,0,8+j]),(3.5,2.8,1.4),'pine' if j!=1 else 'leaf',ECO)
 for k in range(3):
  t,n=L.basis(s);q=p+np.r_[t*(k-1)+n*side*7,0];G.beam('Cloud exposed root candidate',[q,q+np.r_[n*side*2,-3],q+np.r_[n*side*3,-7-k]],.09,'wood',ECO)
records['features'].append({'id':'cloud-root-garden','kind':'ecological form candidate, no species name or mechanism adopted','position':rootp.tolist()})
# Visible rain/recirculation node: upper collection basin, drop, lower catchment, closed return housing.
s=.42;side=-1;a=angle(s);w=float(L.water_z(s));p=loc(s,side,0,18,0);basez=gz(p[:2]);
for name,z,sx,sy in [('upper rain basin',basez+5,7,5),('lower catchment',basez+.4,9,7)]:
 G.box(name,(*p[:2],z),(sx,sy,.55),'stone',ECO,a);G.box(name+' clean water',(*p[:2],z+.3),(sx-.6,sy-.6,.06),'water',ECO,a)
beam('Enclosed return service housing',(* (p[:2]+L.basis(s)[0]*3),basez),(* (p[:2]+L.basis(s)[0]*3),basez+5),.35,'stone',ECO)
fallxy=p[:2]+L.basis(s)[1]*2.2;G.box('Contained cascade into lower basin',(*fallxy,basez+2.9),(3,.18,4.3),'water',ECO,a)
records['features'].append({'id':'water-cycle-node','kind':'clean-water collection/drop/catch/return topology candidate, not flow simulation or sewage route'})

# Remove whole original plant groups intersecting new access/functional geometry.
trees=bpy.data.collections['12 Contour woodland and understory'];roots=np.array([r['xy'] for r in data['roots']]);newobs=[ob for c in [ACCESS,PORT,SCHOOL,HOME,ECO] for ob in c.objects if ob.type=='MESH']
newbounds=[]
for ob in newobs:
 v=np.array([ob.matrix_world@Vector(p) for p in ob.bound_box]);newbounds.append((v.min(0),v.max(0)))
lo=np.array([x[0] for x in newbounds]);hi=np.array([x[1] for x in newbounds]);prune=set();groups={}
for ob in trees.objects:
 v=np.array([ob.matrix_world@Vector(p) for p in ob.bound_box]);center=v.mean(0);r=int(np.argmin(np.linalg.norm(roots-center[:2],axis=1)));groups.setdefault(r,[]).append(ob)
 if np.any(np.all(v.max(0)>=lo,axis=1)&np.all(hi>=v.min(0),axis=1)):prune.add(r)
for r in prune:
 for ob in groups[r]:records['removed'].append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
records['plant_groups_pruned_for_access']=len(prune)

# Public campus ink shader, with subtle directional grain in world coordinates.
# Material copies protect adopted city palettes and the private warm dorm wall.
material_copies={}
def ink_copy(m):
 if m.name.startswith('Private dorm'):return m
 if m.name in material_copies:return material_copies[m.name]
 if not m.use_nodes:return m
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if bs is None:return m
 new=m.copy();new.name=m.name+' [campus ink region v12]';ns=new.node_tree.nodes;lk=new.node_tree.links;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
 base=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].links else None
 if base is None:
  rgb=ns.new('ShaderNodeRGB');rgb.outputs[0].default_value=bs.inputs['Base Color'].default_value;base=rgb.outputs[0]
 geo=ns.new('ShaderNodeNewGeometry');sep=ns.new('ShaderNodeSeparateXYZ');lk.new(geo.outputs['Position'],sep.inputs[0]);fade=ns.new('ShaderNodeMapRange');fade.interpolation_type='SMOOTHSTEP';fade.inputs['From Min'].default_value=622;fade.inputs['From Max'].default_value=655;lk.new(sep.outputs['Y'],fade.inputs['Value'])
 bw=ns.new('ShaderNodeRGBToBW');lk.new(base,bw.inputs[0]);grain=ns.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=.32;grain.inputs['Detail'].default_value=2;vec=ns.new('ShaderNodeVectorMath');vec.operation='MULTIPLY';vec.inputs[1].default_value=(.5,.5,3.5);lk.new(geo.outputs['Position'],vec.inputs[0]);lk.new(vec.outputs[0],grain.inputs['Vector'])
 gr=ns.new('ShaderNodeMapRange');gr.inputs['To Min'].default_value=.75;gr.inputs['To Max'].default_value=1.12;lk.new(grain.outputs['Fac'],gr.inputs['Value']);mult=ns.new('ShaderNodeMath');mult.operation='MULTIPLY';lk.new(bw.outputs[0],mult.inputs[0]);lk.new(gr.outputs[0],mult.inputs[1]);mix=ns.new('ShaderNodeMixRGB');lk.new(fade.outputs[0],mix.inputs[0]);lk.new(base,mix.inputs[1]);lk.new(mult.outputs[0],mix.inputs[2]);lk.new(mix.outputs[0],bs.inputs['Base Color']);material_copies[m.name]=new;return new
for ob in S.objects:
 if ob.type!='MESH':continue
 for slot in ob.material_slots:
  if slot.material:slot.material=ink_copy(slot.material)
# Neutral campus sky smoothly returns to the existing city sky at the cloud boundary.
with bpy.data.libraries.load(str(OLD/'cloud-hamlet-route-58s-v11.blend'),link=False) as (src,dst):dst.objects=['FPV landscape route']
cam=dst.objects[0];S.collection.objects.link(cam);cam.animation_data_clear();S.camera=cam
for i,p in enumerate(poses):
 cam.location=p['position'];cam.rotation_quaternion=Quaternion(p['quaternion']);cam.keyframe_insert('location',frame=i+1);cam.keyframe_insert('rotation_quaternion',frame=i+1)
bg=S.world.node_tree.nodes.get('Background');origsky=list(bg.inputs[0].default_value)
for i in range(3):
 fc=bg.inputs[0].driver_add('default_value',i);dr=fc.driver;v=dr.variables.new();v.name='cy';v.type='TRANSFORMS';v.targets[0].id=cam;v.targets[0].transform_type='LOC_Y';v.targets[0].transform_space='WORLD_SPACE';dr.expression=f'{origsky[i]}+({.82-origsky[i]})*min(1,max(0,(cy-622)/33))'
S.frame_start=1;S.frame_end=1392;S.render.fps=24;S.frame_set(1);CLOUD.hide_render=False
records['route']={'duration':58,'frames':1392,'changed_frame_indices':[int(i+1) for i in np.where(np.max(abs(positions-oldpos),axis=1)>1e-5)[0]],'source_poses_sha256':hashlib.sha256((OLD/'route-poses.json').read_bytes()).hexdigest(),'scope':'school outside arcade, last arrival beside workshop; middle route retained'}
records['source_sha256']=hashlib.sha256((OLD/'cloud-hamlet-masterplan-v11.blend').read_bytes()).hexdigest();records['material_copies']=list(material_copies)
(O/'world-repair-data.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'cloud-city-route-58s-v12.blend'))
print('WORLD_REPAIR_READY',len(S.objects),'new features',len(records['features']),'plant groups pruned',len(prune),flush=True)
