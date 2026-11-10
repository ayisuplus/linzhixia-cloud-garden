"""A reviewable garden-city design candidate; preserves source and adopted interiors."""
import bpy, sys, argparse, json, ast, math, random, hashlib, heapq
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root);OUT=ROOT/'视频制作/第一集园城设计-20261023-v0.1';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'视频制作/第一集全程快飞-20261023-v0.2/episode1-full-route-58s-v02.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene;S.frame_set(1)
layout=json.loads((ROOT/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text(encoding='utf8'))
flight=json.loads((SOURCE.parent/'flight-checks.json').read_text(encoding='utf8'))
helper=ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py'
names={'section','group','box','ell','rod','surf','slab','road'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
COL={};G=None;random.seed(2310)
mn={'wood':'Warm timber / reference-derived family','wall':'Warm mineral plaster','stone':'Warm gray garden stone','green':'Garden leaves','roof':'Gray clay roof','ink':'School ink timber','paper':'School paper plaster','gray':'School gray stone','inkleaf':'School ink vegetation','water':'Longzhou water','inkwater':'School monochrome water'}
M={k:bpy.data.materials[v] for k,v in mn.items()}
palette={k:list(next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value) for k,m in M.items()}
hidden=[];added_courts=[];roof_count=0
original_objects=list(S.objects)
def hide(o):
    if not o.hide_render:hidden.append(o.name)
    o.hide_render=True;o.hide_set(True);o['design_v01_replaced']=True
def center(o):return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
def linecurve(n,pts,r,key):
    cv=bpy.data.curves.new(n,'CURVE');cv.dimensions='3D';cv.resolution_u=1;sp=cv.splines.new('POLY');sp.points.add(len(pts)-1)
    for q,pt in zip(sp.points,pts):q.co=(*pt,1)
    cv.bevel_depth=r;cv.bevel_resolution=1;cv.materials.append(M[key]);ob=bpy.data.objects.new(n,cv);G.objects.link(ob);ob['physical']=True;return ob
def nearroute(x,y,r=12):
    for pts in [layout['walk_points'],[q['position'] for q in flight['records'][::6]]]:
        for aa,bb in zip(pts,pts[1:]):
            ax,ay=aa[:2];dx,dy=bb[0]-ax,bb[1]-ay;t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/max(.001,dx*dx+dy*dy)))
            if math.hypot(x-ax-t*dx,y-ay-t*dy)<r:return True
    return False
# Remove the repeated ring of 40 equal courts. Named story locations stay in place.
blocks=[b for b in layout['blocks'] if b['name'].startswith('Garden neighbourhood')]
oldcourts=[]
for i in range(0,len(blocks),3):
    bb=blocks[i:i+3];oldcourts.append((sum(b['center'][0] for b in bb)/3,bb[0]['center'][1],bb[0]['center'][2]-3))
for o in original_objects:
    if o.name.startswith('Ink distant terrain PROXY'):hide(o)
    if o.name.startswith(('Garden neighbourhood','Garden winding path','Cloud garden tree')):hide(o)
    if o.name.startswith(('Roof ridge cap','Readable timber eave','Filled roof gable')):hide(o)
    if o.name.startswith(('Inset facade glazing','Window vertical timber','Window sill lintel','House door','Door center seam','Filled roof gable','Roof ridge cap','Readable timber eave')):
        c=center(o)
        if any(abs(c.x-x)<17 and abs(c.y-y)<15 and z-.7<c.z<z+15 for x,y,z in oldcourts):hide(o)
# Derived leaf meshes/core copies have generic names; use their source markers and exact centers.
removed_canopies=[o for o in original_objects if o.hide_render and o.name.startswith(('Garden neighbourhood','Cloud garden tree')) and 'canopy' in o.name]
canopy_centers={tuple(round(v,3) for v in o.location) for o in removed_canopies}
for o in original_objects:
    if o.name.startswith('Leaf cluster ') and o.name[len('Leaf cluster '):] in {q.name for q in removed_canopies}:hide(o)
    if o.name.startswith('Irregular foliage core') and tuple(round(v,3) for v in o.location) in canopy_centers:hide(o)

section('DESIGN_V01_ROOF_GRAMMAR')
def curved_roof(n,x,y,z,w,d,ink=False,hip=False,rise=None):
    global roof_count
    key='ink' if ink else 'roof';long_y=d>w;L=max(w,d)/2;W=min(w,d)/2
    rise=rise or min(4.8,W*.6);nu=16;nv=16;vs=[];fs=[]
    def point(u,v):
        if hip:
            inward=min(1-abs(v),max(0,(1-abs(u))*L/W));zz=rise*inward**1.45+.28*(abs(u)*abs(v))**5
        else:zz=rise*(1-abs(v))**1.65+.23*abs(v)**9+.28*(abs(u)*abs(v))**6
        xx,yy=(v*W,u*L) if long_y else (u*L,v*W)
        return (x+xx,y+yy,z+zz)
    for i in range(nu+1):
        for j in range(nv+1):vs.append(point(-1+2*i/nu,-1+2*j/nv))
    for i in range(nu):
        for j in range(nv):k=i*(nv+1)+j;fs.append((k,k+nv+1,k+nv+2,k+1))
    ob=surf(n+' curved tiled roof',vs,fs,key);sol=ob.modifiers.new('Tile thickness','SOLIDIFY');sol.thickness=.18
    for v in [-1,1]:linecurve(n+' eave', [point(-1+2*i/24,v) for i in range(25)],.12,key)
    linecurve(n+' ridge',[point(-.95+1.9*i/24,0) for i in range(25)],.14,key)
    for i in range(max(5,int(L*2/1.2))):
        u=-.98+1.96*i/max(4,int(L*2/1.2)-1)
        linecurve(n+' tile course',[(xx,yy,zz+.025) for xx,yy,zz in [point(u,-1+2*j/16) for j in range(17)]],.035,key)
    if not hip:
        for u in [-.97,.97]:
            pts=[point(u,-1+2*j/16) for j in range(17)];pts += [(pts[-1][0],pts[-1][1],z),(pts[0][0],pts[0][1],z)]
            surf(n+' gable infill',pts,[tuple(range(len(pts)))],'paper' if ink else 'wall')
    roof_count+=1;return ob
# Replace only generated exterior roof surfaces and matching original trim, not adopted buildings.
targets=[]
for o in original_objects:
    if o.hide_render or o.type!='MESH' or len(o.data.vertices)!=6:continue
    if not any(c.name.startswith('V03_') for c in o.users_collection) or 'roof' not in o.name.lower():continue
    if not any(m.type=='SOLIDIFY' for m in o.modifiers) or 'coping' in o.name:continue
    targets.append(o)
for o in targets:
    vs=[o.matrix_world@v.co for v in o.data.vertices];x1=min(v.x for v in vs);x2=max(v.x for v in vs);y1=min(v.y for v in vs);y2=max(v.y for v in vs);z=min(v.z for v in vs)
    ink=any('ink' in m.name.lower() for m in o.data.materials);hip=any(s in o.name.lower() for s in ['pavilion','observatory'])
    for q in original_objects:
        if q.name.startswith(o.name+' '):hide(q)
    hide(o);curved_roof('Refined '+o.name,(x1+x2)/2,(y1+y2)/2,z,x2-x1,y2-y1,ink,hip)

section('DESIGN_V01_COURTYARD_GROUPS')
def hall(n,x,y,z,w,d,h,ink=False):
    wall='paper' if ink else 'wall';wood='ink' if ink else 'wood';stone='gray' if ink else 'stone'
    box(n+' wall',(x,y,z+h/2),(w,d,h),wall,0);slab(n+' plinth',x-w/2-.5,y-d/2-.5,x+w/2+.5,y+d/2+.5,z+.2,stone,.45)
    curved_roof(n,x,y,z+h,w+2.4,d+2.6,ink)
    # Timber bays are silhouette and shadow cues, readable in a fast wide shot.
    bays=max(3,round(w/3.5));yy=y-d/2-.22
    for i in range(bays+1):
        xx=x-w/2+w*i/bays;rod(n+' bay post',(xx,yy,z+.2),(xx,yy,z+h),.14,wood)
    box(n+' lintel',(x,yy,z+h-.45),(w+.35,.25,.28),wood,0)
    for i in range(bays):
        xx=x-w/2+w*(i+.5)/bays;ww=w/bays-.5;box(n+' dark lattice',(xx,yy+.05,z+h*.48),(ww,.08,h*.52),wood,0)
        for k in [-.3,0,.3]:box(n+' lattice stile',(xx+ww*k,yy-.03,z+h*.48),(.055,.06,h*.5),wall,0)
        for zz in [-.17,.17]:box(n+' lattice rail',(xx,yy-.03,z+h*(.48+zz)),(ww,.06,.06),wall,0)
def pine(n,x,y,z,h=9,ink=False):
    wood='ink' if ink else 'wood';green='inkleaf' if ink else 'green'
    rod(n+' leaning trunk',(x,y,z),(x+h*.12,y,z+h*.78),.24,wood)
    for i in range(4):
        ang=i*2.3;xx=x+math.cos(ang)*h*.23;yy=y+math.sin(ang)*h*.18;zz=z+h*(.55+i*.11)
        rod(n+' layered branch',(x+h*.08,y,z+h*.48),(xx,yy,zz),.11,wood)
        for j in range(3):ell(n+' flat needle mass',(xx+(j-1)*h*.14,yy+math.sin(j)*h*.08,zz),(h*.22,h*.19,h*.075),green)
def rocks(n,x,y,z,scale=1,ink=False):
    for i,(dx,dy,h) in enumerate([(-1.5,0,2.8),(.3,.1,4),(2,1,1.8),(.5,-1.5,.9)]):
        ob=ell(n+' weathered garden stone',(x+dx*scale,y+dy*scale,z+h*scale*.4),(scale*(1.1 if i!=1 else .8),scale*.7,h*scale*.55),'gray' if ink else 'stone')
        for v in ob.data.vertices:v.co*=random.uniform(.78,1.18)
def courtyard(n,x,y,z,w=30,d=24,ink=False):
    added_courts.append({'name':n,'center':[x,y,z],'size':[w,d],'ink':ink})
    stone='gray' if ink else 'stone';wall='paper' if ink else 'wall'
    slab(n+' paved court',x-w/2,y-d/2,x+w/2,y+d/2,z+.12,stone,.25)
    hall(n+' principal hall',x,y+d/2-4,z,w,8,6.8,ink)
    hall(n+' side study',x-w/2+3,y-1,z,6,d-9,4.5,ink)
    # Front wall leaves a full passage; no single isolated screen billboard.
    for xx,ww in [(x-w*.3,w*.4),(x+w*.3,w*.4)]:
        box(n+' enclosing wall',(xx,y-d/2,z+1.6),(ww,.4,3.2),wall,0)
        box(n+' wall coping',(xx,y-d/2,z+3.2),(ww+.2,.7,.2),'ink' if ink else 'roof',0)
    box(n+' east garden wall',(x+w/2,y-1,z+1.3),(.4,d-8,2.6),wall,0)
    pine(n+' court pine',x+w*.22,y-d*.27,z,6,ink);rocks(n+' court rock',x+w*.22,y-3,z,.7,ink)
    # This connector terminates on the existing retained outer walk, not at a floating door.
    road(n+' entrance path',[(x,y-d/2,z+.13),(x,y-d/2-8,z+.13)],2.8,stone)

# Deliberately small number of unequal groups. Named original courts remain anchors.
new_specs=[('Academy north study',-1360,1034,35.85,36,28,True),('Academy west study',-1450,990,35.85,27,23,True),
('Upper west annex',-862,805,58.15,24,20,False),('Upper east annex',-690,740,58.15,25,20,False),
('Middle south court',-685,560,23.15,34,27,False),('Middle north study',-690,647,23.15,25,20,False),
('Quiet west study',-1100,492,-14.85,25,20,False),('Quiet east residence',-975,530,-14.85,32,25,False),
('East waterside court',-326,296,4.15,30,24,False),('West bamboo court',-560,132,-7.85,30,24,False)]
for spec in new_specs:courtyard(*spec)

# Existing named courts receive the same timber bay grammar as the new annexes.
for b in layout['blocks']:
    ob=S.objects.get(b['name'])
    if not ob or ob.hide_render:continue
    x,y,zc=b['center'];w,d,h=b['size'];z=zc-h/2;ink='LEARNING' in b['district'];wood='ink' if ink else 'wood'
    for side in [-1,1]:
        yy=y+side*(d/2+.14);count=max(2,round(w/3.6))
        for i in range(count+1):
            xx=x-w/2+w*i/count;rod('Retained court timber bay',(xx,yy,z+.15),(xx,yy,z+h-.1),.13,wood)
        box('Retained court beam',(x,yy,z+h-.35),(w+.2,.24,.3),wood,0)
    if 'court' in b['name'].lower() or 'Learning' in b['name']:
        # Stone base and one horizontal sill tie isolated windows into a facade.
        box('Retained court stone footing',(x,y,z+.18),(w+.3,d+.3,.36),'gray' if ink else 'stone',0)

section('DESIGN_V01_WATER_AND_PLANTING')
ponds=[]
def pond(n,x,y,z,rx,ry,ink=False):
    count=64;ring=[]
    for i in range(count):
        t=i*math.tau/count;f=1+.12*math.sin(t*3+.6);ring.append((x+rx*f*math.cos(t),y+ry*f*math.sin(t),z+.15))
    surf(n+' water',ring,[tuple(range(count))],'inkwater' if ink else 'water',False)
    linecurve(n+' stone bank',ring+[ring[0]],.22,'gray' if ink else 'stone')
    ponds.append({'name':n,'center':[x,y,z],'radii':[rx,ry]})
    rocks(n+' bank rocks',x-rx*.65,y+ry*.6,z,1.4,ink);pine(n+' bank pine',x-rx*.7,y-ry*1.3,z,9,ink)
for spec in [('Academy ink pond',-1315,985,35.8,28,17,True),('Upper moon pool',-784,759,58.1,46,28,False),('Middle garden pond',-637,581,23.1,31,16,False),('Quiet garden pond',-1035,485,-14.9,32,18,False),('Lower east pond',-370,320,4.1,24,15,False),('Lower west pond',-512,159,-7.9,27,17,False)]:pond(*spec)
# Curved paths connect local courts; blank land now has a garden center and deliberate sightline.
for bank in layout['platforms'][:7]:
    x,y,z=bank['center'];rx,ry=bank['radii'];ink='School' in bank['name']
    if bank['name']=='School gate garden':continue
    for j in range(6):
        t=.35+j*math.tau/6;xx=x+rx*.75*math.cos(t);yy=y+ry*.73*math.sin(t)
        clear_courts=not any(abs(xx-c['center'][0])<c['size'][0]/2+6 and abs(yy-c['center'][1])<c['size'][1]/2+6 and abs(z-c['center'][2])<2 for c in added_courts)
        if clear_courts and not nearroute(xx,yy,16):pine('Shore pine group',xx,yy,z+.1,8+(j%3)*2,ink)


# Plan local paths against actual ground-level walls, trunks and pond footprints.
# Grid cells are temporary planning data, not extra production deliverables.
walk_plans=[]
bpy.context.view_layer.update()
for bank in layout['platforms'][:7]:
    if bank['name']=='School gate garden':continue
    cx,cy,z=bank['center'];rx,ry=bank['radii'];ink='School' in bank['name'];step=2.;obstacles=[]
    for ob in list(S.objects):
        if ob.hide_render or ob.type not in {'MESH','CURVE'}:continue
        vv=[ob.matrix_world@Vector(v) for v in ob.bound_box]
        lo=[min(v[j] for v in vv) for j in range(3)];hi=[max(v[j] for v in vv) for j in range(3)]
        if hi[0]<cx-rx or lo[0]>cx+rx or hi[1]<cy-ry or lo[1]>cy+ry:continue
        water=(' water' in ob.name.lower() or ' pool' in ob.name.lower()) and abs((lo[2]+hi[2])/2-z)<1
        solid=ob.get('physical',True) and lo[2]<z+.7 and hi[2]>z+1.5
        if solid or water:obstacles.append((lo[0]-1.6,hi[0]+1.6,lo[1]-1.6,hi[1]+1.6))
    nx=int(rx*.82/step);ny=int(ry*.82/step);free=set()
    for i in range(-nx,nx+1):
        for j in range(-ny,ny+1):
            x=cx+i*step;y=cy+j*step
            if ((x-cx)/(rx*.82))**2+((y-cy)/(ry*.82))**2>1:continue
            if not any(a<x<b and c<y<d for a,b,c,d in obstacles):free.add((i,j))
    def nearest(x,y):return min(free,key=lambda q:(cx+q[0]*step-x)**2+(cy+q[1]*step-y)**2)
    def route(a,b):
        queue=[(0,a)];cost={a:0};parent={}
        while queue:
            _,q=heapq.heappop(queue)
            if q==b:
                result=[q]
                while q in parent:q=parent[q];result.append(q)
                return list(reversed(result))
            for di,dj in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                v=(q[0]+di,q[1]+dj)
                if v not in free or (di and dj and ((q[0]+di,q[1]) not in free or (q[0],q[1]+dj) not in free)):continue
                value=cost[q]+math.hypot(di,dj)
                if value<cost.get(v,1e12):cost[v]=value;parent[v]=q;heapq.heappush(queue,(value+math.hypot(v[0]-b[0],v[1]-b[1]),v))
        raise RuntimeError('No clear garden walk '+bank['name'])
    def emit(n,points):
        # Merge collinear grid edges. Keep sufficient width clearance at bends.
        simple=[]
        for q in points:
            while len(simple)>1 and (q[0]-simple[-1][0])*(simple[-1][1]-simple[-2][1])==(q[1]-simple[-1][1])*(simple[-1][0]-simple[-2][0]):simple.pop()
            simple.append(q)
        world=[(cx+i*step,cy+j*step,z+.13) for i,j in simple]
        road(n,world,2.4,'gray' if ink else 'stone');walk_plans.append({'name':n,'points':world})
    ring=[nearest(cx+rx*.71*math.cos(t),cy+ry*.71*math.sin(t)) for t in [math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4]]
    ringnodes=[]
    for k in range(4):
        nodes=route(ring[k],ring[(k+1)%4]);ringnodes+=nodes;emit(bank['name']+' garden circuit',nodes)
    for c in added_courts:
        x,y,cz=c['center'];w,d=c['size']
        assigned=min(layout['platforms'][:7],key=lambda b:(b['center'][0]-x)**2+(b['center'][1]-y)**2+100*(b['center'][2]-cz)**2)
        if assigned['name']!=bank['name']:continue
        start=nearest(x,y-d/2-8);target=min(ringnodes,key=lambda q:(q[0]-start[0])**2+(q[1]-start[1])**2)
        nodes=route(start,target);emit(c['name']+' walk link',nodes)
        actual=(cx+start[0]*step,cy+start[1]*step,z+.13)
        road(c['name']+' entrance join',[(x,y-d/2-8,cz+.13),actual],2.4,'gray' if ink else 'stone')

section('DESIGN_V01_SCREEN_CONTEXT')
# Side returns stitch the three moon windows into garden boundaries, away from the open flight bore.
for label,x,y,z,ink in [('A',-1203,859,42,True),('B',-910,639,48,False),('C',-210,0,0,False)]:
    wall='paper' if ink else 'wall';wood='ink' if ink else 'wood';rr={'A':11,'B':17,'C':10}[label]
    for side in [-1,1]:
        yy=y+side*rr;box('Moon '+label+' return wall',(x-7,yy,z+1.8),(14,.45,3.6),wall,0)
        box('Moon '+label+' return coping',(x-7,yy,z+3.6),(14.4,.8,.22),'ink' if ink else 'roof',0)
    rocks('Moon '+label+' rock composition',x-5 if label=='C' else x+4,y-16 if label=='C' else y+rr-3,z,1.2,ink)
    pine('Moon '+label+' framing pine',x-8 if label=='C' else x+6,y-20 if label=='C' else y+rr-1,z,9,ink)
# Human scale roof beams and short bracket pairs only at the focal pavilion.
for x,y,z,w,d in [(-810,678,58,23,18),(-810,678,68,15,12)]:
    h=8 if z==58 else 6
    for yy in [y-d/2,y+d/2]:
        box('Observatory deep eave beam',(x,yy,z+h-.5),(w+.8,.45,.5),'wood',0)
        for xx in [x-w/2,x,x+w/2]:
            box('Observatory bracket lower',(xx,yy,z+h-.8),(.6,1.3,.24),'wood',0)
            box('Observatory bracket upper',(xx,yy,z+h-.55),(1.4,.6,.20),'wood',0)

section('DESIGN_V01_GALLERY_GRAMMAR')
# Retain every existing gallery deck; give its thin roof a curved section and readable beams.
for oldroof in original_objects:
    if oldroof.hide_render or 'folded roof' not in oldroof.name or oldroof.type!='MESH' or len(oldroof.data.vertices)!=6:continue
    pts=[oldroof.matrix_world@v.co for v in oldroof.data.vertices];ink=any('ink' in m.name.lower() for m in oldroof.data.materials);wood='ink' if ink else 'wood';tile='ink' if ink else 'roof'
    vertices=[];faces=[]
    for i in range(5):
        t=i/4;left=pts[0].lerp(pts[3],t);right=pts[2].lerp(pts[5],t);ridge=pts[1].lerp(pts[4],t)
        for j in range(13):
            u=j/12;q=left.lerp(right,u);q.z+=(ridge.z-q.z)*(1-abs(2*u-1))**1.5;vertices.append(q)
    for i in range(4):
        for j in range(12):k=i*13+j;faces.append((k,k+13,k+14,k+1))
    hide(oldroof);roofob=surf('Gallery curved tile section',vertices,faces,tile);roofob.modifiers.new('Gallery tile thickness','SOLIDIFY').thickness=.13
    for ia,ib in [(0,3),(2,5)]:
        u,v=pts[ia],pts[ib];rod('Gallery eave beam',u-Vector((0,0,.18)),v-Vector((0,0,.18)),.16,wood)
        q=u.lerp(v,.5);rod('Gallery intermediate edge column',q-Vector((0,0,4.2)),q-Vector((0,0,.15)),.16,wood)
    rod('Gallery ridge tile',pts[1],pts[4],.10,tile)

# A few matching static before/after views; no palette or lighting change between the pair.
section('DESIGN_V01_REVIEW_CAMERAS')
views=[('01-school',(-1460,824,165),(-1320,967,40),48),('02-upper',(-970,480,180),(-775,735,53),48),('03-middle',(-814,380,150),(-655,600,25),48),('04-lower',(-530,120,105),(-360,325,5),48),('05-moon',(-944,602,58),(-903,641,53),35),('06-canal',(-247,-45,24),(-165,18,3),38)]
for name,loc,target,lens in views:
    ca=bpy.data.cameras.new('DESIGN '+name);ca.lens=lens;ca.clip_end=6000;ob=bpy.data.objects.new(ca.name,ca);G.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
S.camera=S.objects['FAST_ROUTE_FPV'];S['design_candidate']='Chinese garden massing study v01; existing adopted art and 58-second animation remain authoritative; review pending.'
report={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'palette_linear_rgba':palette,'hidden_old_objects':hidden,'removed_repeated_court_count':len(oldcourts),'new_courtyards':added_courts,'new_ponds':ponds,'refined_roofs':roof_count,'review_views':views,'local_walk_plans':walk_plans,'animation_changed':False,'status':'design candidate, not adopted; flight revalidation pending after added geometry'}
(OUT/'design-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'garden-city-design-v01.blend'))
print('DESIGN_CANDIDATE_READY',len(hidden),roof_count,flush=True)
