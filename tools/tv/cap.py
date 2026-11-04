import os, sys, json, traceback
from playwright.sync_api import sync_playwright
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots')
os.makedirs(OUT, exist_ok=True)
SP = os.path.dirname(os.path.abspath(__file__)) + '/'
CAPJS = """(function(t,s){ var c=document.getElementById('tvcap'); if(!c){ c=document.createElement('div'); c.id='tvcap'; document.body.appendChild(c); }
c.style.cssText='position:fixed;left:12px;right:12px;top:9%;z-index:2147483647;background:rgba(18,20,18,.88);color:#fff;border-radius:14px;padding:11px 14px 11px 16px;border-left:6px solid #f2c94c;box-shadow:0 6px 20px rgba(0,0,0,.45);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;pointer-events:none';
c.innerHTML='<div style="font-weight:900;font-size:18px;line-height:1.2">'+t+'</div>'+(s?'<div style="font-size:13px;opacity:.9;margin-top:3px;line-height:1.3">'+s+'</div>':''); })"""
def x(pg, c): return pg.evaluate("c=>__x(c)", c)
def snap(pg, name, t, s, pos=None):
    pg.evaluate(CAPJS + "(%s,%s)" % (json.dumps(t), json.dumps(s)))
    if pos: pg.evaluate("document.getElementById('tvcap').style.top=%s" % json.dumps(pos))
    pg.evaluate("document.querySelectorAll('.show').forEach(function(e){ if(/Menu switched/.test(e.textContent||'')) e.classList.remove('show'); })")
    pg.wait_for_timeout(250)
    pg.screenshot(path=os.path.join(OUT, name + '.png'))
    pg.evaluate("var c=document.getElementById('tvcap'); if(c) c.remove()")
    print('snap', name)
def fresh(p, geo=None):
    args = ['--use-fake-ui-for-media-stream']
    b = p.chromium.launch(args=args)
    kw = dict(viewport={'width': 405, 'height': 720}, device_scale_factor=720/405)
    if geo: kw.update(permissions=['geolocation'], geolocation=geo)
    ctx = b.new_context(**kw); pg = ctx.new_page()
    pg.on('pageerror', lambda z: print('PAGEERR', str(z)[:200]))
    pg.add_init_script("localStorage.setItem('rockMarkerInstallDismissed','1');localStorage.setItem('rmTodayAuto','0');localStorage.setItem('rmUpBan_mn-weight-2026_'+new Date().toISOString().slice(0,10),'1')")
    pg.goto('http://localhost:8768/ktest.html?demo=1', wait_until='domcontentloaded'); pg.wait_for_timeout(7000)
    x(pg, "try{ var db=document.querySelector('#demo-bar, .demo-bar, #demo-pill'); if(db) db.style.display='none'; }catch(e){} 1")
    return b, ctx, pg
def hide_demo(pg):
    pg.add_style_tag(content="#demo-banner,#demo-bar,.demo-bar,#demo-pill,.demo-pill,[id^=demo-]{display:none !important}")
def step(fn, name):
    try: fn()
    except Exception as e: print('FAIL', name, str(e)[:300])

PILES = """var by={}; activeRocks().forEach(function(r){by[r.field]=(by[r.field]||0)+1;}); var F=Object.keys(by).sort(function(a,b){return by[b]-by[a];})[0]; window.__F=F; var R=activeRocks().filter(function(r){return r.field===F;}); var la=R.map(function(r){return r.lat;}), ln=R.map(function(r){return r.lng;}); var mnA=Math.min.apply(0,la),mxA=Math.max.apply(0,la),mnN=Math.min.apply(0,ln),mxN=Math.max.apply(0,ln);
rocks.push({id:'pA',kind:'pile',lat:mxA+0.0008,lng:mnN-0.0008,field:F,note:'NW corner',createdAt:'2026-01-01'}); rocks.push({id:'pB',kind:'pile',lat:mxA+0.0008,lng:mxN+0.0008,field:F,note:'East approach',createdAt:'2026-01-02'}); rocks.push({id:'pC',kind:'pile',lat:mnA-0.0008,lng:(mnN+mxN)/2,field:F,note:'South ditch',createdAt:'2026-01-03'}); saveData(); renderAll(); 1"""

with sync_playwright() as p:
    # ---------- MAP ----------
    b, ctx, pg = fresh(p, geo={'latitude': 0, 'longitude': 0}); hide_demo(pg)
    step(lambda: snap(pg, 'map1', '🗺 Your farm map', 'Fields, rocks and bins, live for the whole crew.'), 'map1')
    def m2():
        x(pg, PILES); x(pg, "startPicking(window.__F); 1"); pg.wait_for_timeout(800)
        x(pg, "document.getElementById('btn-pick-bypile').click(); 1"); pg.wait_for_timeout(1200)
        snap(pg, 'map2', '🎨 Rocks by pile', 'Each rock shows the closest pile. Mark a pile full and they move.')
        x(pg, "rbpOff(); document.getElementById('btn-pick-exit').click(); 1"); pg.wait_for_timeout(600)
    step(m2, 'map2')
    def m3():
        x(pg, "map.setView([48.402,-96.10],15); 1"); pg.wait_for_timeout(2500)
        pg.click('#btn-layer'); pg.wait_for_timeout(500)
        snap(pg, 'map3', '🛩 Pick the map picture', 'Satellite, or the USDA aerial photo when there are clouds.', '62%')
        pg.click('[data-mpk=cmp]'); pg.wait_for_timeout(2500)
        snap(pg, 'map4', '⇆ Compare them', 'Drag the line. Fields and rocks stay put.', '62%')
        x(pg, "mpkCmpOff(); mpkSet('esri'); 1"); pg.wait_for_timeout(500)
    step(m3, 'map3')
    def m5():
        x(pg, "fitAllFields && fitAllFields(); 1") if False else None
        x(pg, "var B=L.latLngBounds([]); fields.forEach(function(f){ if(f.points) f.points.forEach(function(q){B.extend(q);}); }); map.fitBounds(B,{padding:[20,20]}); 1"); pg.wait_for_timeout(2000)
        x(pg, "WXM.test={obs:{st:{name:'Thief River Falls'},vis:400,txt:'Fog',at:Date.now()},al:[{id:'a1',event:'Dense Fog Advisory',ends:new Date(Date.now()+3*3600000).toISOString()}],wx:{hours:[]}}; wxmApply(); 1"); pg.wait_for_timeout(800)
        snap(pg, 'map5', '🌫 Fog and rain show up', 'Haze, how far you can see, and weather warnings.', '40%')
        x(pg, "WXM.test=null; wxmApply(); document.body.classList.remove('wxm-fog1','wxm-fog2'); var w=document.getElementById('wxm'); if(w) w.innerHTML=''; 1")
    step(m5, 'map5')
    def m6():
        r0 = x(pg, "var r=activeRocks()[0]; [r.lat,r.lng]")
        ctx.set_geolocation({'latitude': r0[0]-0.0015, 'longitude': r0[1]-0.0004})
        x(pg, "arOpen(); 1"); pg.wait_for_timeout(2500)
        x(pg, "var o=document.getElementById('ar-ov'); o.style.background='linear-gradient(#9cc5ea 0%,#d8e9f5 40%,#a89b6b 41%,#8a7f52 70%,#6e6640 100%)'; var v=document.getElementById('ar-vid'); if(v) v.style.display='none'; var m=document.getElementById('ar-msg'); if(m) m.classList.add('hidden'); 1")
        for k in range(12):
            x(pg, "var b=rpBear(AR.pos.lat,AR.pos.lng,%f,%f); window.dispatchEvent(new DeviceOrientationEvent('deviceorientationabsolute',{alpha:(360-b+8)%%360,beta:88,gamma:0,absolute:true})); 1" % (r0[0], r0[1])); pg.wait_for_timeout(60)
        pg.wait_for_timeout(600)
        x(pg, "var m=document.getElementById('ar-msg'); if(m) m.classList.add('hidden'); 1")
        snap(pg, 'map6', '📷 Rock camera', 'Hold your phone up. Rock tags float over the field.', '14%')
        x(pg, "arClose(); 1")
    step(m6, 'map6')
    b.close()

    # ---------- FIELD / TODAY ----------
    b, ctx, pg = fresh(p); hide_demo(pg)
    def f1():
        x(pg, "WXM.test={obs:{st:{name:'Thief River Falls'},vis:16000,txt:'Cloudy',at:Date.now()},al:[],wx:{hours:[{startTime:new Date(Date.now()+3600000).toISOString(),endTime:new Date(Date.now()+7200000).toISOString(),probabilityOfPrecipitation:{value:80},shortForecast:'Rain'}]}}; 1")
        x(pg, "openToday(); 1"); pg.wait_for_timeout(2500)
        snap(pg, 'field1', '☀️ Today', 'What needs doing: jobs, weather, bins, service, rain.', '62%')
        x(pg, "hideSheet('today-modal','today-backdrop'); 1"); pg.wait_for_timeout(400)
    step(f1, 'field1')
    def f2():
        x(pg, "applySeason('plant'); 1"); pg.wait_for_timeout(800)
        x(pg, "var f=fields.find(function(f){return !f.plantedOn && f.points && f.points.length>2;}); openFieldLabelActions(f.id); 1"); pg.wait_for_timeout(1000)
        x(pg, "document.getElementById('field-label-fert').scrollIntoView(); 1"); pg.wait_for_timeout(300)
        snap(pg, 'field2', '🌱 Planted? One tap', 'Today, yesterday or pick a date. Variety fills in from last time.', '6%')
        x(pg, "closeFieldLabelActions(); applySeason('all'); 1"); pg.wait_for_timeout(500)
    step(f2, 'field2')
    def f3():
        x(pg, "hfOpen(); HF.chat=[{r:'u',t:'Mark a big rock here'},{r:'a',t:'Okay. Marking a big rock where you are. Check it and tap Save.'},{r:'u',t:'How full is bin 1?'},{r:'a',t:hfBinLine(bins[0])}]; hfRender(); 1"); pg.wait_for_timeout(800)
        snap(pg, 'field3', '🗣 Hey Farm', 'Ask questions, or say “mark a big rock here” or “open the time clock”.', '62%')
        x(pg, "hfClose(); 1")
    step(f3, 'field3')
    def f4():
        x(pg, "applySeason('tillage'); 1"); pg.wait_for_timeout(1000)
        snap(pg, 'field4', '🚜 Tillage at any angle', 'Mark where you stopped, even on an angle. Fall % counts partial passes.')
        x(pg, "applySeason('all'); 1")
    step(f4, 'field4')
    b.close()

    # ---------- HARVEST ----------
    b, ctx, pg = fresh(p); hide_demo(pg)
    def h1():
        x(pg, "var bb=bins.filter(function(b){return b.currentBu>0;}); window.__bid=(bb[0]||bins[0]).id; openBinActions(window.__bid); 1"); pg.wait_for_timeout(600)
        x(pg, "document.querySelector('[data-gck=open]').click(); 1"); pg.wait_for_timeout(300)
        x(pg, "document.getElementById('gck-top').value='58'; document.getElementById('gck-mid').value='54'; document.getElementById('gck-air').value='41'; document.querySelector('[data-gck=save]').click(); 1"); pg.wait_for_timeout(400)
        x(pg, "document.getElementById('bin-gck').scrollIntoView(); 1"); pg.wait_for_timeout(300)
        snap(pg, 'harv1', '🌡 Grain checks', 'Grain and air temps, smell. Warns when grain is warming up.', '70%')
        x(pg, "closeBinActions(); 1"); pg.wait_for_timeout(300)
    step(h1, 'harv1')
    def h2():
        x(pg, "document.getElementById('menu-item-dfl').click(); 1"); pg.wait_for_timeout(1000)
        x(pg, "document.querySelector('[data-dfl=new]').click(); var s=function(i,v){document.getElementById(i).value=v;}; s('dfl-bu','4200'); s('dfl-gal','720'); s('dfl-min','22.5'); s('dfl-mout','15'); s('dfl-hrs','13.5'); document.querySelector('[data-dfl=save]').click(); 1"); pg.wait_for_timeout(300)
        x(pg, "document.querySelector('[data-dfl=new]').click(); var s=function(i,v){document.getElementById(i).value=v;}; s('dfl-date','2026-10-28'); s('dfl-bu','3800'); s('dfl-gal','610'); s('dfl-min','21'); s('dfl-mout','15'); document.querySelector('[data-dfl=save]').click(); 1"); pg.wait_for_timeout(400)
        snap(pg, 'harv2', '⛽ Dryer fuel log', 'Gallons per bushel per point, and a report for grants.', '64%')
        x(pg, "hideSheet('dfl-modal','dfl-backdrop'); 1"); pg.wait_for_timeout(300)
    step(h2, 'harv2')
    def h3():
        x(pg, "var Y=JH.d[jhY()]={}; fields.forEach(function(f){ Y[jhK(f.name)]={ac:100,bu:f.crop==='Wheat'?2050:f.crop==='Soybeans'?950:15000,final:true,crop:gbCrop(f.crop)}; }); var i=document.createElement('input'); i.type='file'; i.id='cart-file'; i.style.display='none'; document.body.appendChild(i); 1")
        pg.set_input_files('#cart-file', SP + 'cart_test.csv'); pg.wait_for_timeout(4000)
        snap(pg, 'harv3', '🚜 Grain cart report', 'Bring in UHarvest loads and check them against the combine.', '6%')
        x(pg, "var o=document.getElementById('cart-ov'); if(o) o.remove(); 1")
    step(h3, 'harv3')
    def h4():
        x(pg, """var y=String(currentYear); var F=fields.filter(function(f){return f.points&&f.points.length>2;}); F.forEach(function(f,i){ f.plantedOn=y+'-05-'+String(5+i).padStart(2,'0'); }); var R=activeRocks(); R.forEach(function(r,i){ r.createdAt=y+'-04-'+String(10+(i%10)).padStart(2,'0')+'T15:00:00'; if(i%2===0) r.pickedAt=y+'-04-'+String(22+(i%5)).padStart(2,'0')+'T15:00:00'; }); 1""")
        x(pg, "hrOpen(); 1"); pg.wait_for_timeout(1500); x(pg, "hrStop(); 1")
        x(pg, "var i=HR.days.indexOf(String(currentYear)+'-05-10'); hrShow(i,false); 1"); pg.wait_for_timeout(1200)
        snap(pg, 'harv4', '🎬 Season replay', 'Rocks, planting, tillage and harvest play back like a movie.', '24%')
        x(pg, "hrShow(HR.days.length-1,false); 1"); pg.wait_for_timeout(1200)
        snap(pg, 'harv5', '🎬 …through harvest', 'Bins fill and trucks run. Owners get the season wrap-up.', '24%')
        x(pg, "hrClose(); 1")
    step(h4, 'harv4')
    b.close()

    # ---------- SHOP ----------
    b, ctx, pg = fresh(p); hide_demo(pg)
    def s1():
        x(pg, "openEquipmentListSheet(); 1"); pg.wait_for_timeout(1000)
        snap(pg, 's1', '🔧 Your machines', 'Hours, parts, filters and what is coming due.', '62%')
    step(s1, 's1')
    def s2():
        x(pg, "hideSheet('equipment-list-modal','equipment-list-backdrop'); var e=equipment[0]; openServiceSheet(e.id); 1"); pg.wait_for_timeout(600)
        x(pg, "document.getElementById('input-service-hours').value='2148'; document.getElementById('input-service-hours').dispatchEvent(new Event('input',{bubbles:true})); 1"); pg.wait_for_timeout(200)
        x(pg, "document.getElementById('cs-name').value='Flip feed accelerator knives'; document.getElementById('cs-int').value='400'; document.querySelector('[data-cs=add]').click(); 1"); pg.wait_for_timeout(300)
        x(pg, "document.querySelector('.cs-item [data-action=done-now]').click(); document.querySelector('.cs-item').scrollIntoView({block:'center'}); 1"); pg.wait_for_timeout(400)
        snap(pg, 's2', '➕ Add your own items', 'Service anything by hours, like flipping the accelerator knives.', '6%')
        x(pg, "saveServiceSheet(); 1"); pg.wait_for_timeout(300)
    step(s2, 's2')
    def s3():
        x(pg, "openToday(); 1"); pg.wait_for_timeout(2000)
        x(pg, "var t=[].slice.call(document.querySelectorAll('#today-body *')).find(function(e){return /service due|due in/.test(e.textContent) && e.children.length<4;}); if(t) t.scrollIntoView({block:'center'}); 1"); pg.wait_for_timeout(300)
        snap(pg, 's3', '🔔 Service due on Today', 'Coming-due service shows up for the whole crew.', '8%')
    step(s3, 's3')
    b.close()

    # ---------- OFFICE ----------
    b, ctx, pg = fresh(p); hide_demo(pg)
    def o1():
        x(pg, "insLoad(function(){ INS.d.units=[{id:'u1',crop:'Corn',plan:'Revenue Protection',cov:80,iy:160},{id:'u2',crop:'Soybeans',plan:'RP',cov:75,iy:45}]; }); 1"); pg.wait_for_timeout(400)
        x(pg, "jdOpen('pol'); 1"); pg.wait_for_timeout(1000)
        x(pg, "DRP.inbox=[{id:'x1',demo:true,st:'new',name:'Mike Hanson, Farmers Union',note:'2027 coverage',files:[{n:'2027 Schedule of Insurance.pdf',t:'application/pdf',s:1800000,p:1}],at:Date.now(),tok:'T'}]; jdDraw(); 1"); pg.wait_for_timeout(500)
        snap(pg, 'o1', '📥 Papers from your agent', 'Send a private link. Their PDFs wait for you to approve.', '66%')
    step(o1, 'o1')
    def o2():
        x(pg, "jdOpen('cards'); 1"); pg.wait_for_timeout(900)
        x(pg, "var d=document.querySelector('.ipt'); d.open=true; d.scrollIntoView(); 1"); pg.wait_for_timeout(400)
        snap(pg, 'o2', '🛡 Plan types', 'RP, YP, SCO, ECO in plain words. Your plan is tagged.', '66%')
        x(pg, "hideSheet('jd-modal','jd-backdrop'); 1")
    step(o2, 'o2')
    def o3():
        x(pg, "moneyLoad(function(){}); var Y=moneyYear(); Y.crops.Wheat={seed:40,rent:120,chem:40,mach:60,fert:80}; Y.crops.Soybeans={seed:70,rent:120,chem:50,mach:50}; Y.crops.Corn={seed:110,rent:120,fert:150,mach:90}; Y.crops.Canola={seed:60,rent:120,fert:90,mach:60}; showSheet('money-modal','money-backdrop'); moneyTab='value'; moneyRender(); 1"); pg.wait_for_timeout(2500)
        snap(pg, 'o3', '💲 Crop value', 'Your bushels at today’s prices, with how it’s figured.', '66%')
        x(pg, "moneyTab='pfield'; moneyRender(); 1"); pg.wait_for_timeout(2000)
        snap(pg, 'o4', '🗺 Profit by field', 'Which fields made money, on a map.', '66%')
        x(pg, "hideSheet('money-modal','money-backdrop'); 1")
    step(o3, 'o3')
    def o5():
        x(pg, "jdOpen('pol'); 1"); pg.wait_for_timeout(800)
        x(pg, "var e=[].slice.call(document.querySelectorAll('#jd-body *')).find(function(el){return /USDA|sales closing|final planting/i.test(el.textContent) && el.children.length<3;}); if(e) e.scrollIntoView({block:'center'}); 1"); pg.wait_for_timeout(400)
        snap(pg, 'o5', '📅 USDA dates by county', 'Deadlines for every county you farm, checked every week.', '8%')
    step(o5, 'o5')
    b.close()

    # ---------- WHAT'S NEW (menu) ----------
    b, ctx, pg = fresh(p, geo={'latitude': 0, 'longitude': 0}); hide_demo(pg)
    def n1():
        x(pg, "openSideMenu(); 1"); pg.wait_for_timeout(800)
        pg.click('#menu-item-today', button='right'); pg.wait_for_timeout(400)
        snap(pg, 'n1', '⭐ Favorites your way', 'Long-press any tile to add it to favorites. It stays in its section too.', '74%')
        x(pg, "var p=document.getElementById('mnp'); if(p) p.remove(); closeSideMenu(); 1")
    step(n1, 'n1')
    b.close()
print('done')
