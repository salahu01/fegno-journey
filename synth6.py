# soundtrack for the website timeline (index.html): D≈58.5s
import numpy as np
from scipy.signal import butter,sosfilt
from scipy.io import wavfile
SR=48000;D=59;N=SR*D;rng=np.random.default_rng(9)
L=np.zeros(N);R=np.zeros(N)
def add(sig,t,g=1.0,pan=0.0):
    i=int(t*SR);n=min(len(sig),N-i)
    if n<=0 or i<0:return
    L[i:i+n]+=sig[:n]*g*(1-pan)*.7;R[i:i+n]+=sig[:n]*g*(1+pan)*.7
lp=lambda x,f:sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
hp=lambda x,f:sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
bp=lambda x,a,b:sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
hz=lambda m:440*2**((m-69)/12);tt=lambda d:np.arange(int(d*SR))/SR
def piano(m,d=3.5):
    s=tt(d);f=hz(m);return sum(a*np.sin(2*np.pi*f*r*s)*np.exp(-s*k) for r,a,k in[(1,1,1.4),(2,.45,2.2),(3,.2,3.2),(4,.1,4.5)])*np.minimum(1,s/.004)
def bell(f,d=1.8):
    s=tt(d);return sum(a*np.sin(2*np.pi*f*r*s)*np.exp(-s*k) for r,a,k in[(1,1,2.6),(2.76,.3,4),(5.4,.12,7)])*np.minimum(1,s/.002)
def click():return hp(rng.standard_normal(int(.02*SR)),3000)*np.exp(-tt(.02)*300)
def step():s=tt(.12);return bp(rng.standard_normal(len(s)),150,2500)*np.exp(-s*45)+np.sin(2*np.pi*90*s)*np.exp(-s*60)*.8
def air(d):x=tt(d);return lp(rng.standard_normal(len(x)),900)*np.sin(np.pi*x/d)**2
tg=np.arange(N)/SR
# city ambience (quieter once inside the climb)
amb=lp(rng.standard_normal(N),220)*1.2+bp(rng.standard_normal(N),300,1200)*.25
lev=np.clip(tg/1.0,0,1)*(1-.5*np.clip((tg-6)/2,0,1))
L+=amb*.1*lev;R+=np.roll(amb,4000)*.1*lev
# opening: lamp + neon flicker, footsteps, door
for k,on in enumerate([1,0,1,1,0,1]):
    if on:add(click(),.3+k*.1,.2,pan=-.5)
x=tt(D);add(bp(np.sign(np.sin(2*np.pi*120*x)),200,3000)*.012*(tg>1.1)*(tg<6),0,pan=.3)
add(bp(rng.standard_normal(int(.05*SR)),800,4000)*np.exp(-tt(.05)*80),.6,.3,pan=.3)
t=.8+1/1.8*0
while t<3.2:add(step(),t,.2,pan=-.2+.4*(t-.8)/2.4);t+=1/1.8
add(piano(84,2),3.1,.07);add(piano(79,2.5),3.35,.07);add(air(.6),3.0,.12)
s=tt(3.2);add(lp(sum(np.sin(2*np.pi*hz(m)*s) for m in[57,64,69,72])*np.minimum(1,s/2)*np.exp(-np.maximum(0,s-2.4)*1.5),1600)*.05,3.2)
# events
E0,DT=6.0,1.6
kinds=['p','ph','p','ph','ph','p','ph','p','ph','p','ph','ph','ph','p','burst','p','ph','p','ph','p','ph','p','p','ph']
CH=[[48,55,60,64],[43,55,59,62],[45,52,57,60],[41,53,57,60]]
for i,k in enumerate(kinds):
    t0=E0+i*DT;c=CH[i%4]
    for j,m in enumerate([c[0],c[1],c[2],c[3],c[2]]):add(piano(m+12,2.0),t0+j*.32,.045 if j else .06,pan=.3*np.sin(j+i))
    add(piano(c[0]-12,2.4),t0,.06)
    tl=t0+.45
    if k=='ph':add(bell(hz([84,86,88,91][i%4])),tl,.07,pan=.3)
    elif k=='p':add(click(),tl,.25,pan=-.2);add(piano(79+(i%3)*2,1.4),tl+.02,.06)
    else:
        for q in range(7):add(click(),tl+.05+q*.06,.2,pan=np.sin(q))
        s=tt(3);add(lp(sum(np.sin(2*np.pi*hz(m)*s) for m in[57,64,69,76])*np.minimum(1,s/.3)*np.exp(-s*.8),2200)*.07,tl)
    if i+1<len(kinds):add(air(.6),t0+1.05,.05)
# pull back + end card
EEND=E0+len(kinds)*DT;PB=EEND+.4;FIN=PB+6.2
s=tt(7);add(lp(sum(np.sin(2*np.pi*hz(m)*s*(1+d)) for m in[36,48,55,60,64,67] for d in(-.002,.002))*np.minimum(1,s/2.5)*np.minimum(1,(7-s)/1.5),1800)*.05,PB)
s=tt(6);add(lp(sum(np.sin(2*np.pi*hz(m)*s) for m in[48,55,60,64,67,72])*np.exp(-s*.5)*np.minimum(1,s/.02),2600)*.09,FIN)
for j,m in enumerate([72,76,79,84]):add(piano(m,3),FIN+1+j*.45,.08)
fade=np.ones(N);fade[-int(1.5*SR):]=np.linspace(1,0,int(1.5*SR))
S=np.stack([L,R],1)*fade[:,None];S/=np.abs(S).max()/0.85
wavfile.write('/private/tmp/claude-501/-Users-salahu/c0c8ade3-eb1b-42a5-9ee6-528b86f6eba5/scratchpad/site.wav',SR,(S*32767).astype(np.int16))
