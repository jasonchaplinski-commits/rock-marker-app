import os, subprocess, wave, html
import numpy as np
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__)); S = D + '/shots/'; C = D + '/cards3/'
O = os.path.abspath(D + '/../../videos') + '/'
os.makedirs(C, exist_ok=True); os.makedirs(O, exist_ok=True)

# scene order (benefit captions come from cap.py BEN)
SC = ['map6', 'map2', 'p_crop', 'p_rain', 'field1', 'field3', 'p_heat', 'harv3', 'harv1',
      'p_stl', 'p_sos', 's1', 'p_jl', 'harv4', 'o4', 'o1']
BEN = {
 'map6': ('📍', 'Never lose a rock again', 'Hold up your phone. It points to every marked rock.'),
 'map2': ('🪨', 'Pick rocks in fewer trips', 'Every rock shows its closest pile.'),
 'p_crop': ('🛰', 'Spot problem areas from space', 'Satellite crop health for every field, all season.'),
 'p_rain': ('🌧', 'Weather right on your fields', 'Rain, snow and fog show up where they are falling.'),
 'field1': ('☀️', 'Know what needs doing today', 'Jobs, weather, bins and service on one screen.'),
 'field3': ('🗣', 'Just ask', '“How full is bin 1?”<br>“Mark a big rock here.”'),
 'p_heat': ('🌽', 'Know when it will be ready', 'Crop stage and harvest dates from your own weather.'),
 'harv3': ('🚜', 'Every load accounted for', 'Grain cart loads checked against the combine.'),
 'harv1': ('🌡', 'Catch warm grain early', 'Log bin checks. It warns before grain goes bad.'),
 'p_stl': ('📄', 'Catch settlement mistakes', 'Snap the elevator sheet. It checks every ticket and price.'),
 'p_sos': ('📦', 'Store or sell? See the math', 'Later bids minus storage and interest, side by side.'),
 's1': ('🔧', 'Service on time, every machine', 'Hours, parts and what is coming due.'),
 'p_jl': ('🔗', 'Send a job, not a phone call', 'Outside help gets the field, the map and the job.'),
 'harv4': ('🎬', 'Your season, like a movie', 'Rocks, planting and harvest play back day by day.'),
 'o4': ('💰', 'See which fields make money', 'Profit for every field, right on the map.'),
 'o1': ('🛡', 'Insurance papers in one place', 'Your agent sends PDFs to a private link.'),
}
EMAIL = 'jasonchaplinski@gmail.com'
FPS = 30; XF = 0.4

CSS = """*{box-sizing:border-box}body{margin:0;font-family:'Liberation Sans',Arial,Helvetica,sans-serif;color:#fff;overflow:hidden}
.bg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 38%,#3d6b35 0%,#1f3a1d 48%,#0e160b 100%)}
.dk{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,#2b2b2b 0%,#141414 60%,#070707 100%)}
.wrap{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 7%}
.y{color:#f5d40f}.e{line-height:1}.t{font-weight:900;line-height:1.08}.s{line-height:1.35;opacity:.95}
.pill{display:inline-block;background:#f5d40f;color:#1f3a1d;font-weight:900;border-radius:999px}
.sm{opacity:.8}
.blur{position:absolute;inset:-60px;background-size:cover;background-position:center;filter:blur(38px) brightness(.38) saturate(1.1)}
.phone{position:absolute;border-radius:46px;border:12px solid #0b0b0b;box-shadow:0 30px 80px rgba(0,0,0,.65),0 0 0 2px #333;overflow:hidden;background:#000}
.phone img{width:100%;height:100%;display:block}
.L{position:absolute;text-align:left}
.brand{position:absolute;font-weight:900;color:#f5d40f;opacity:.9}
.bar{width:90px;height:8px;background:#f5d40f;border-radius:4px}
"""

def card_html(kind, w, h):
    W = w > h  # wide
    k = (h / 1920.0) if not W else 1.3
    def px(v): return '%dpx' % int(v * k)
    if kind == 'prob1':
        rows = [('🪨', 'Rock piles you can’t find.'), ('📝', 'Bin levels on scraps of paper.'), ('📱', 'Notes in five different places.')]
        r = ''.join('<div style="display:flex;align-items:center;gap:%s;margin:%s 0;font-size:%s;font-weight:800;text-align:left"><span style="font-size:%s">%s</span><span>%s</span></div>' % (px(28), px(22), px(58 if not W else 62), px(84), e, t) for e, t in rows)
        return '<div class=dk></div><div class=wrap><div>%s</div></div>' % r
    if kind == 'prob2':
        return '<div class=bg></div><div class=wrap><div class="t y" style="font-size:%s">There’s a better way.</div></div>' % px(104 if not W else 110)
    if kind == 'title':
        return ('<div class=bg></div><div class=wrap><div class=e style="font-size:%s">🪨🌾</div><div class="t y" style="font-size:%s;margin-top:%s">Rock Marker</div>'
                '<div class=s style="font-size:%s;margin-top:%s;font-weight:700">Your whole farm in one app.</div>'
                '<div class=s style="font-size:%s;margin-top:%s">Planning · Field · Harvest · Shop · Office</div></div>') % (
                px(170), px(130), px(30), px(56), px(26), px(36), px(30))
    if kind == 'proof':
        return ('<div class=bg></div><div class=wrap><div class=e style="font-size:%s">🚜</div>'
                '<div class=s style="font-size:%s;margin-top:%s">Built and used on</div>'
                '<div class="t y" style="font-size:%s;margin-top:%s">Chaplinski Farms</div>'
                '<div class=s style="font-size:%s;margin-top:%s;font-weight:700">Middle River, Minnesota · 2,500 acres</div>'
                '<div class="s sm" style="font-size:%s;margin-top:%s">Every screen in this video is the real app.</div></div>') % (
                px(150), px(44), px(30), px(100), px(12), px(46), px(22), px(32), px(48))
    if kind == 'end':
        return ('<div class=bg></div><div class=wrap><div class=e style="font-size:%s">🪨🌾</div>'
                '<div class="t y" style="font-size:%s;margin-top:%s">Rock Marker</div>'
                '<div class=s style="font-size:%s;margin-top:%s">Every farm gets its own logo, app icon and data.</div>'
                '<div class=pill style="font-size:%s;padding:%s %s;margin-top:%s">Ask for a free demo</div>'
                '<div style="font-size:%s;margin-top:%s;font-weight:800">%s</div>'
                '<div class="s sm" style="font-size:%s;margin-top:%s">Created by Jason Chaplinski</div></div>') % (
                px(130), px(110), px(18), px(36), px(20), px(54), px(20), px(44), px(54), px(50), px(36), EMAIL, px(32), px(46))

def scene_wide(n):
    e, t, s = BEN[n]
    img = S + n + '_nc.png'
    ph_h = 990; ph_w = int(ph_h * 9 / 16)
    return ('<div class=blur style="background-image:url(\'file://%s\')"></div>'
            '<div class=L style="left:150px;top:0;bottom:0;width:900px;display:flex;flex-direction:column;justify-content:center">'
            '<div style="font-size:130px;line-height:1">%s</div><div class=bar style="margin:36px 0 32px"></div>'
            '<div class=t style="font-size:96px">%s</div><div class=s style="font-size:46px;margin-top:28px">%s</div></div>'
            '<div class=phone style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"><img src="file://%s"></div>'
            '<div class=brand style="left:150px;bottom:54px;font-size:30px">🪨 Rock Marker</div>') % (
            img, e, t, s, 1920 - 230 - ph_w, (1080 - ph_h) // 2, ph_w, ph_h, img)

def render_all():
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        def shot(body, path, w, h):
            f = C + '_tmp.html'
            open(f, 'w', encoding='utf-8').write('<html><head><meta charset=utf-8><style>' + CSS + '</style></head><body style="width:%dpx;height:%dpx;position:relative;background:#111">' % (w, h) + body + '</body></html>')
            pg.set_viewport_size({'width': w, 'height': h}); pg.goto('file://' + f); pg.wait_for_timeout(250)
            pg.screenshot(path=path)
        for k in ['prob1', 'prob2', 'title', 'proof', 'end']:
            shot(card_html(k, 1080, 1920), C + k + '_p.png', 1080, 1920)
            shot(card_html(k, 1920, 1080), C + k + '_w.png', 1920, 1080)
        for n in SC:
            if os.path.exists(S + n + '_nc.png') and os.path.exists(S + n + '.png'):
                shot(scene_wide(n), C + n + '_w.png', 1920, 1080)
                out.append(n)
            else:
                print('MISSING', n)
        b.close()
    return out

def seg(img, dur, out, w, h, zoom=0.035):
    n = int(round(dur * FPS))
    vf = ("scale=%d:%d:flags=lanczos,zoompan=z='1+%s*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=%d,format=yuv420p"
          % (int(w * 1.5), int(h * 1.5), zoom, n, n, w, h, FPS))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', img, '-vf', vf, '-frames:v', str(n),
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', out], check=True)

# ---------- original music (synthesized here, no samples, no license) ----------
SR = 44100
def music(total, t_go, t_end, path):
    N = int(total * SR) + SR; t = np.arange(N) / SR
    L = np.zeros(N); R = np.zeros(N)
    bpm = 92.0; beat = 60 / bpm; bar = beat * 4
    def hz(m): return 440.0 * 2 ** ((m - 69) / 12.0)
    prog = [(62, [62, 66, 69]), (57, [61, 64, 69]), (59, [62, 66, 71]), (55, [59, 62, 67])]  # D A Bm G
    clen = bar * 2
    # pad
    i = 0; st = 0.0
    while st < total:
        root, notes = prog[i % 4]
        a = int(st * SR); ln = int((clen + 1.2) * SR); b2 = min(N, a + ln); tt = np.arange(b2 - a) / SR
        env = np.minimum(1, tt / 0.9) * np.clip((clen + 1.2 - tt) / 1.2, 0, 1)
        sig = np.zeros(b2 - a)
        for m in notes + [notes[0] + 12]:
            for dt in (-0.0035, 0.0035):
                f = hz(m - 12) * (1 + dt)
                for k in range(1, 6):
                    sig += np.sin(2 * np.pi * f * k * tt + k * 0.7) / (k ** 1.6)
        sig *= env * 0.022
        L[a:b2] += sig; R[a:b2] += np.roll(sig, 220)
        # bass on beats 1 and 3
        for bb in range(0, 8, 2):
            s0 = st + bb * beat
            if s0 >= total: break
            a3 = int(s0 * SR); l3 = int(beat * 1.8 * SR); b3 = min(N, a3 + l3); t3 = np.arange(b3 - a3) / SR
            fb = hz(root - 24)
            bs = (np.sin(2 * np.pi * fb * t3) + 0.3 * np.sin(4 * np.pi * fb * t3)) * np.exp(-t3 * 2.2) * np.minimum(1, t3 / 0.02) * 0.10
            if s0 < t_go: bs *= 0.5
            L[a3:b3] += bs; R[a3:b3] += bs
        st += clen; i += 1
    # arpeggio + light drums after "a better way"
    pat = [0, 1, 2, 3, 2, 1, 2, 3]
    arpL = np.zeros(N); arpR = np.zeros(N)
    s0 = t_go; k8 = 0
    while s0 < t_end + bar:
        ci = int(s0 // clen) % 4; root, notes = prog[ci]
        tones = notes + [notes[0] + 12]
        m = tones[pat[k8 % 8]] + 12
        a = int(s0 * SR); ln = int(0.9 * SR); b2 = min(N, a + ln); tt = np.arange(b2 - a) / SR
        f = hz(m)
        pl = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt) + 0.08 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 5.5) * np.minimum(1, tt / 0.004)
        g = 0.055 * (1.0 if k8 % 2 == 0 else 0.75)
        pan = 0.5 + 0.25 * np.sin(k8 * 0.7)
        arpL[a:b2] += pl * g * (1 - pan) * 2; arpR[a:b2] += pl * g * pan * 2
        if s0 < t_end:
            if k8 % 4 == 0:  # kick on 1 and 3
                l4 = int(0.35 * SR); b4 = min(N, a + l4); t4 = np.arange(b4 - a) / SR
                ph = 2 * np.pi * (45 * t4 + (110 - 45) / 18.0 * (1 - np.exp(-18 * t4)))
                kk = np.sin(ph) * np.exp(-t4 * 9) * 0.16
                L[a:b4] += kk; R[a:b4] += kk
            if k8 % 2 == 1:  # soft shaker on off-beats
                l5 = int(0.06 * SR); b5 = min(N, a + l5); t5 = np.arange(b5 - a) / SR
                nz = np.random.RandomState(k8).randn(b5 - a); nz = nz - np.convolve(nz, np.ones(6) / 6, 'same')
                hh = nz * np.exp(-t5 * 70) * 0.018
                L[a:b5] += hh * 0.8; R[a:b5] += hh * 1.1
        s0 += beat / 2; k8 += 1
    d = int(beat * 0.75 * SR)  # dotted-eighth echo
    for rep, gg in ((1, 0.35), (2, 0.16), (3, 0.07)):
        arpL[d * rep:] += arpR[:-d * rep] * gg; arpR[d * rep:] += arpL[:-d * rep] * gg * 0.9
    L += arpL; R += arpR
    # fades
    fin = np.minimum(1, t / 1.2); fout = np.clip((total - t) / 3.0, 0, 1)
    L *= fin * fout; R *= fin * fout
    pk = max(np.abs(L).max(), np.abs(R).max()); L *= 0.45 / pk; R *= 0.45 / pk
    n2 = int(total * SR); pcm = (np.stack([L[:n2], R[:n2]], 1) * 32767).astype('<i2')
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()

def build(tag, items, w, h, outmp4):
    segs = []
    for i, (img, d) in enumerate(items):
        f = O + '_p3%s_%d.mp4' % (tag, i); seg(img, d, f, w, h); segs.append((f, d))
    st = [0.0]
    for i in range(1, len(segs)): st.append(st[-1] + segs[i - 1][1] - XF)
    total = st[-1] + segs[-1][1]
    wav = O + '_p3music.wav'
    if not os.path.exists(wav):
        music(total, st[1], st[-1], wav)
    args = ['ffmpeg', '-v', 'error', '-y']
    for f, _ in segs: args += ['-i', f]
    fc = []; last = '[0:v]'
    for i in range(1, len(segs)):
        lab = '[v%d]' % i
        fc.append('%s[%d:v]xfade=transition=fade:duration=%s:offset=%.3f%s' % (last, i, XF, st[i], lab)); last = lab
    args += ['-i', wav, '-filter_complex', ';'.join(fc), '-map', last, '-map', '%d:a' % len(segs),
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p', '-r', str(FPS),
             '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', outmp4]
    subprocess.run(args, check=True)
    for f, _ in segs: os.remove(f)
    return total, st

names = render_all()
DUR = {'prob1': 3.6, 'prob2': 2.0, 'title': 3.0, 'proof': 3.4, 'end': 5.0}
order = ['prob1', 'prob2', 'title'] + names + ['proof', 'end']
def pick(n, wide):
    if n in DUR: return C + n + ('_w.png' if wide else '_p.png'), DUR[n]
    return (C + n + '_w.png') if wide else (S + n + '.png'), 3.1
w_items = [pick(n, True) for n in order]; p_items = [pick(n, False) for n in order]
if os.path.exists(O + '_p3music.wav'): os.remove(O + '_p3music.wav')
tot, st = build('p', p_items, 1080, 1920, O + 'promo_phone_v3.mp4')
build('w', w_items, 1920, 1080, O + 'promo_wide_v3.mp4')
os.remove(O + '_p3music.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', C + 'title_w.png', '-vf', 'scale=1280:720', '-q:v', '3', O + 'promo_poster_v3.jpg'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', C + 'title_p.png', '-vf', 'scale=720:1280', '-q:v', '3', O + 'promo_poster_phone_v3.jpg'], check=True)
print('promo3 %.1fs scenes=%d' % (tot, len(names)), os.path.getsize(O + 'promo_phone_v3.mp4') // 1024, os.path.getsize(O + 'promo_wide_v3.mp4') // 1024)
print('starts', ' '.join('%s=%.1f' % (n, s) for n, s in zip(order, st)))
