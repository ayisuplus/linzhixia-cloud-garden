import bpy,math,numpy as np
from mathutils import Vector
M={}
ARCH=None
def mesh(name,vs,fs,key,c,physical=True):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);me.materials.append(M[key] if isinstance(key,str) else key);o['physical']=physical;return o

def box(name,center,size,key,c,angle=0):
 x,y,z=center;sx,sy,sz=np.array(size)/2;co=math.cos(angle);si=math.sin(angle);vs=[]
 for a,b,h in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]:vs.append((x+a*co-b*si,y+a*si+b*co,z+h))
 return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],key,c)

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