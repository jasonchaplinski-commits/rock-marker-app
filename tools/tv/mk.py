import os, subprocess, json
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__)); S=D+'/shots/'; C=D+'/cards/'; O=os.path.abspath(D+'/../../videos')+'/'
os.makedirs(C,exist_ok=True); os.makedirs(O,exist_ok=True)
CLIPS={
 'clip_map_v2':('🗺','The farm map','Rocks, piles, map pictures and weather',['map1','map2','map3','map4','map5','map6']),
 'clip_field_v2':('🚜','In the field · Today','Jobs, planting, Hey Farm and tillage',['field1','field2','field3','field4']),
 'clip_harvest_v2':('🌾','Harvest, loads & bins','Grain checks, dryer, cart loads and replay',['harv1','harv2','harv3','harv4','harv5']),
 'clip_shop_v2':('🔧','The shop','Machines, your own service items and alerts',['s1','s2','s3']),
 'clip_office_v2':('💼','The office','Agent papers, plan types, crop value and USDA dates',['o1','o2','o3','o4','o5']),
 'clip_new':('🆕',"What's new",'The latest changes in 30 seconds',['n1','map2','map3','map5','field2','field3','harv1','harv4','map6','s2']),
}
CSS="""body{margin:0;width:720px;height:1280px;background:radial-gradient(ellipse at 50% 38%,#3d6b35 0%,#1f3a1d 45%,#111a0e 100%);font-family:Arial,Helvetica,sans-serif;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.e{font-size:130px;line-height:1}.t{color:#f5d40f;font-weight:900;font-size:62px;margin:28px 40px 14px}.s{font-size:30px;margin:0 50px;line-height:1.35}.u{display:inline-block;margin-top:26px;background:#f5d40f;color:#1f3a1d;font-weight:900;font-size:24px;padding:8px 18px;border-radius:20px}.c{font-size:22px;opacity:.85;margin-top:34px}"""
def card(pg,name,html):
    pg.set_content('<html><head><meta charset=utf-8><style>'+CSS+'</style></head><body>'+html+'</body></html>')
    pg.wait_for_timeout(200); pg.screenshot(path=C+name+'.png')
def seg(img,dur,out):
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-t',str(dur),'-i',img,'-vf','scale=720:1280:flags=lanczos,format=yuv420p,fps=25','-c:v','libx264','-preset','medium','-crf','20',out],check=True)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':720,'height':1280})
    card(pg,'end','<div class=e>🚜</div><div class=t>Rock Marker</div><div class=s>Planning · Field · Harvest<br>Shop · Office · Crew</div><div class=c>Created by Jason Chaplinski</div>')
    for k,(e,t,s,_) in CLIPS.items():
        card(pg,k,'<div class=e>'+e+'</div><div class=t>'+t+'</div><div class=s>'+s+'</div><div class=u>Updated Nov 2026</div><div class=c>Created by Jason Chaplinski</div>')
    b.close()
XF=0.4
for k,(e,t,s,sc) in CLIPS.items():
    items=[(C+k+'.png',2.4)]+[(S+n+'.png',3.3) for n in sc]+[(C+'end.png',2.4)]
    segs=[]
    for i,(img,d) in enumerate(items):
        f=O+'_%s_%d.mp4'%(k,i); seg(img,d,f); segs.append((f,d))
    args=['ffmpeg','-v','error','-y']
    for f,_ in segs: args+=['-i',f]
    fc=[];last='[0:v]';off=0
    for i in range(1,len(segs)):
        off+=segs[i-1][1]-XF; lab='[v%d]'%i
        fc.append('%s[%d:v]xfade=transition=fade:duration=%s:offset=%.2f%s'%(last,i,XF,off,lab)); last=lab
    total=off+segs[-1][1]
    args+=['-f','lavfi','-t','%.2f'%total,'-i','anullsrc=r=44100:cl=stereo','-filter_complex',';'.join(fc),'-map',last,'-map','%d:a'%len(segs),
           '-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-r','25','-c:a','aac','-b:a','64k','-shortest','-movflags','+faststart',O+k+'.mp4']
    subprocess.run(args,check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',C+k+'.png','-vf','scale=720:1280','-q:v','4',O+k+'.jpg'],check=True)
    for f,_ in segs: os.remove(f)
    print(k,'%.1fs'%total,os.path.getsize(O+k+'.mp4')//1024,'KB')
