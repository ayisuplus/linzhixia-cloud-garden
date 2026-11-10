"""Explicit 3D school-to-workshop reference route. Metres are creative inference."""
import numpy as np
POINTS=np.array([
 [-249,151,132],[-216,152,132],[-193,137,134],[-177,104,135],
 [-183,71,116],[-169,57,96],[-149,65,87.5],[-126,75,87.5],
 [-106,57,91],[-85,30,92],[-70,5,72],[-55,-17,46],[-45,-28,38],[-21,-30,38],
 [7,-37,52],[43,-48,74],[78,-48,78],[115,-49,79],[147,-67,81],
 [170,-103,79],[191,-130,72],[222,-129,70],[260,-125,69],
 [280,-126,69],[301,-130,71],[310,-119,58],[323,-103,53],[344,-90,51]
],float)
def smooth(t):
 t=np.clip(t,0,1);return t*t*t*(10+t*(-15+6*t))
def raw_route():
 p=POINTS;segments=np.linalg.norm(np.diff(p,axis=0),axis=1)
 tang=np.zeros_like(p);tang[0]=(p[1]-p[0])/segments[0];tang[-1]=(p[-1]-p[-2])/segments[-1]
 for j in range(1,len(p)-1):tang[j]=(p[j+1]-p[j-1])/(segments[j-1]+segments[j])
 raw=[]
 for j,L in enumerate(segments):
  for t in np.linspace(0,1,max(30,int(L*8)),endpoint=False):
   raw.append((2*t**3-3*t*t+1)*p[j]+(t**3-2*t*t+t)*tang[j]*L+(-2*t**3+3*t*t)*p[j+1]+(t**3-t*t)*tang[j+1]*L)
 raw=np.array(raw+[p[-1]]);k=np.arange(-16,17);kernel=np.exp(-.5*(k/5.5)**2);kernel/=kernel.sum()
 for j in range(3):
  pad=np.r_[raw[0,j]+(raw[0,j]-raw[1,j])*np.arange(16,0,-1),raw[:,j],raw[-1,j]+(raw[-1,j]-raw[-2,j])*np.arange(1,17)]
  raw[:,j]=np.convolve(pad,kernel,'valid')
 return raw
def timed_route():
 raw=raw_route();arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(raw,axis=0),axis=1))]
 vec=np.gradient(raw,axis=0);unit=vec/np.maximum(np.linalg.norm(vec,axis=1)[:,None],1e-8)
 curv=np.linalg.norm(np.gradient(unit,axis=0),axis=1)/np.maximum(np.linalg.norm(vec,axis=1),1e-8)
 speed=np.minimum(25,np.sqrt(5/np.maximum(curv,1e-6)));speed[:1]=speed[-1:]=1.5
 for i in range(1,len(speed)):speed[i]=min(speed[i],np.sqrt(speed[i-1]**2+2*5*(arc[i]-arc[i-1])))
 for i in range(len(speed)-2,-1,-1):speed[i]=min(speed[i],np.sqrt(speed[i+1]**2+2*5*(arc[i+1]-arc[i])))
 ts=np.r_[0,np.cumsum(2*np.diff(arc)/(speed[:-1]+speed[1:]))];ts*= (1391/24)/ts[-1]
 dist=np.interp(np.arange(1392)/24,ts,arc)
 pos=np.column_stack([np.interp(dist,arc,raw[:,j]) for j in range(3)])
 return raw,arc,dist,pos
