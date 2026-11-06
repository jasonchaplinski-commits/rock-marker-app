import os, subprocess
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__)); S=D+'/shots/'; C=D+'/cards/'; O=os.path.abspath(D+'/../../videos')+'/'
os.makedirs(C,exist_ok=True)
SC=['map1','map2','map6','p_rain','p_snow','p_crop','p_cropf','map5','field1','field3','field2','field4','harv1','harv2','harv3','harv4','harv5','s1','s2','o1','o2','n1']
FEAT=['🪨 Mark rocks, find piles','📷 Rock camera','🌧 Weather on the map','🌱 Crop health from satellite','🗣 Hey Farm voice','🌱 Planting and tillage','🌾 Bins, grain checks, dryer','🎬 Season replay','🔧 Shop and service','🛡 Insurance papers','⭐ Your own favorites']
CSS="""body{margin:0;font-family:Arial,Helvetica,sans-serif;color:#fff}
.card{width:720px;height:1280px;background:radial-gradient(ellipse at 50% 38%,#3d6b35 0%,#1f3a1d 45%,#111a0e 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.e{font-size:120px;line-height:1}.t{color:#f5d40f;font-weight:900;font-size:76px;margin:26px 30px 16px}.s{font-size:32px;margin:0 60px;line-height:1.35}.u{display:inline-block;margin-top:26px;background:#f5d40f;color:#1f3a1d;font-weight:900;font-size:24px;padding:8px 18px;border-radius:20px}.c{font-size:22px;opacity:.85;margin-top:34px}
.side{width:1280px;height:720px;position:relative;background:transparent}.L{position:absolute;left:40px;top:230px;width:380px}.L .e{font-size:64px}.L .t{font-size:52px;margin:10px 0 10px;text-align:left}.L .s{font-size:21px;margin:0;text-align:left}.L .c{font-size:15px;margin-top:20px;text-align:left}
.R{position:absolute;left:880px;top:150px;width:390px;font-size:23px;font-weight:800;line-height:1.7}.ci{font-size:20px;line-height:1.35;margin:9px 0;font-weight:700}"""
def shot(pg,html,path,w,h,transparent=False):
    pg.set_viewport_size({'width':w,'height':h})
    pg.set_content('<html><head><meta charset=utf-8><style>'+CSS+'</style></head><body style="background:transparent">'+html+'</body></html>')
    pg.wait_for_timeout(200); pg.screenshot(path=path,omit_background=transparent)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    shot(pg,'<div class=card><div class=e>🪨🌾</div><div class=t>Rock Marker</div><div class=s>The farm app built on the farm,<br>for the people who run it.</div><div class=u>New · Nov 2026</div><div class=c>Created by Jason Chaplinski</div></div>',C+'p_title.png',720,1280)
    shot(pg,'<div class=card><div class=e>🚜</div><div class=t>Rock Marker</div><div class=s>Planning · Field · Harvest<br>Shop · Office · Crew</div><div class=s style="margin-top:26px;font-size:27px">Every farm gets its own logo,<br>app icon and data.</div><div class=c>Created by Jason Chaplinski</div></div>',C+'p_end.png',720,1280)
    shot(pg,'<div class=side><div class=L><div class=e>🪨🌾</div><div class=t style="color:#f5d40f">Rock<br>Marker</div><div class=s>The farm app built on the farm, for the people who run it.</div><div class=c>Created by Jason Chaplinski</div></div><div class=R style="top:120px"><div style="color:#f5d40f;font-size:30px;font-weight:900;margin-bottom:10px">🛰️ Crop health<br>from satellite</div><div class=ci>🌱 Green is strong, red is weak or bare</div><div class=ci>📅 New pictures every few clear days</div><div class=ci>◀ ▶ Step back through the whole season</div><div class=ci>📊 Tap any field for its season chart</div><div class=ci>⚠️ Spot drowned-out or thin areas early</div><div class=ci>💲 Free. No account, no extra cost</div><div style="font-size:14px;font-weight:600;opacity:.75;margin-top:12px">Sentinel-2 satellite pictures, about 30 ft per pixel</div></div></div>',C+'p_side_crop.png',1280,720,True)
    shot(pg,'<div class=side><div class=L><div class=e>🪨🌾</div><div class=t style="color:#f5d40f">Rock<br>Marker</div><div class=s>The farm app built on the farm, for the people who run it.</div><div class=c>Created by Jason Chaplinski</div></div><div class=R>'+'<br>'.join(FEAT)+'</div></div>',C+'p_side.png',1280,720,True)
    b.close()
def seg(img,dur,out):
    n=int(dur*25)
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',img,'-vf',"scale=1080:1920:flags=lanczos,zoompan=z='1+0.035*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=720x1280:fps=25,format=yuv420p"%(n,n),'-frames:v',str(n),'-c:v','libx264','-preset','medium','-crf','20',out],check=True)
XF=0.45
items=[(C+'p_title.png',3.2)]+[(S+n+'.png',3.2) for n in SC if os.path.exists(S+n+'.png')]+[(C+'p_end.png',3.8)]
segs=[]
for i,(img,d) in enumerate(items):
    f=O+'_pr_%d.mp4'%i; seg(img,d,f); segs.append((f,d))
args=['ffmpeg','-v','error','-y']
for f,_ in segs: args+=['-i',f]
fc=[];last='[0:v]';off=0
for i in range(1,len(segs)):
    off+=segs[i-1][1]-XF; lab='[v%d]'%i
    fc.append('%s[%d:v]xfade=transition=fade:duration=%s:offset=%.2f%s'%(last,i,XF,off,lab)); last=lab
total=off+segs[-1][1]
args+=['-f','lavfi','-t','%.2f'%total,'-i','anullsrc=r=44100:cl=stereo','-filter_complex',';'.join(fc),'-map',last,'-map','%d:a'%len(segs),'-c:v','libx264','-preset','medium','-crf','26','-pix_fmt','yuv420p','-r','25','-c:a','aac','-b:a','64k','-shortest','-movflags','+faststart',O+'promo_phone_v2.mp4']
subprocess.run(args,check=True)
for f,_ in segs: os.remove(f)
names=['p_title']+[n for n in SC if os.path.exists(S+n+'.png')]+['p_end']
st=[0.0]
for i in range(1,len(segs)): st.append(st[-1]+segs[i-1][1]-XF)
c0=st[names.index('p_crop')]+0.2 if 'p_crop' in names else 0
c1=(st[names.index('p_cropf')]+segs[names.index('p_cropf')][1]-0.2) if 'p_cropf' in names else 0
subprocess.run(['ffmpeg','-v','error','-y','-i',O+'promo_phone_v2.mp4','-i',C+'p_side.png','-i',C+'p_side_crop.png','-filter_complex',"[0:v]split[a][b];[a]scale=1280:-2,crop=1280:720,boxblur=24:3,eq=brightness=-0.32[bg];[b]scale=-2:680[ph];[bg][ph]overlay=(W-w)/2:20[m];[m][1:v]overlay=0:0:enable='not(between(t,%.2f,%.2f))'[m2];[m2][2:v]overlay=0:0:enable='between(t,%.2f,%.2f)',format=yuv420p"%(c0,c1,c0,c1),'-map','0:a','-c:v','libx264','-preset','medium','-crf','26','-r','25','-c:a','copy','-movflags','+faststart',O+'promo_wide_v2.mp4'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-ss','1.5','-i',O+'promo_wide_v2.mp4','-frames:v','1','-q:v','4',O+'promo_poster_v2.jpg'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',C+'p_title.png','-vf','scale=720:1280','-q:v','4',O+'promo_poster_phone_v2.jpg'],check=True)
print('promo %.1fs'%total, os.path.getsize(O+'promo_phone_v2.mp4')//1024, os.path.getsize(O+'promo_wide_v2.mp4')//1024)
