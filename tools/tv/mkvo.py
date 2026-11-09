import subprocess, wave, sys, os, json
import numpy as np
# Makes one WAV per voiceover line with the free Piper voice (runs offline).
# Output: tools/tv/vo3/l00.wav ... and lines.json. promo3.py times the scenes to these.
# AI voice (Piper, free, runs offline). Jason can swap in his own recordings later.
D = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(D, 'voices')
os.makedirs(VO, exist_ok=True)
voice = sys.argv[1] if len(sys.argv) > 1 else 'en_US-ryan-high'
outd = sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, 'vo3')
ls = float(sys.argv[3]) if len(sys.argv) > 3 else 0.97
os.makedirs(outd, exist_ok=True)
import urllib.request
for e in ('onnx', 'onnx.json'):
    p = os.path.join(VO, voice + '.' + e)
    if not os.path.exists(p):
        loc, spk, q = voice.split('-')
        urllib.request.urlretrieve('https://huggingface.co/rhasspy/piper-voices/resolve/main/en/%s/%s/%s/%s.%s' % (loc, spk, q, voice, e), p)
L = [
 "Rock piles you can't find. Bin levels on scraps of paper. Notes in five different places.",
 "There's a better way.",
 "This is Rock Marker. Your whole farm, in one app.",
 "Mark a rock once, and your phone points you right back to it. It even shows the closest pile.",
 "Spot weak areas from satellite, and see the weather right on your fields.",
 "Open it in the morning to see what needs doing. Or just ask it.",
 "Know when every field will be ready.",
 "Every load gets counted. Log your bin checks, and it flags warm grain and reminds you when the next check is due.",
 "Snap the elevator sheet, and it checks every ticket. Store or sell? It shows you the math.",
 "Service on time, for every machine.",
 "Send outside help the field, the map, and the job. No more phone calls.",
 "Replay your season. See which fields make money. And keep your insurance papers in one place.",
 "It is built and used every day on Chaplinski Farms. Twenty-five hundred acres in Middle River, Minnesota.",
 "Want to see it on your farm? Ask Jason for a free demo.",
]
meta = []
for i, txt in enumerate(L):
    f = os.path.join(outd, 'l%02d.wav' % i)
    subprocess.run([sys.executable, '-m', 'piper', '-m', os.path.join(VO, voice + '.onnx'), '--length-scale', '%.3f' % ls,
                    '--sentence-silence', '0.3', '-f', f], input=txt.encode(), check=True, capture_output=True)
    w = wave.open(f); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768; w.close()
    nz = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, nz[0] - 200): nz[-1] + 1500]
    a = a * (0.89 / max(1e-6, np.abs(a).max()))
    w = wave.open(f, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype('<i2').tobytes()); w.close()
    meta.append({'f': 'l%02d.wav' % i, 'dur': round(len(a) / sr, 3), 'text': txt})
    print('%2d %.2fs %s' % (i, len(a) / sr, txt))
json.dump({'voice': voice, 'lines': meta}, open(os.path.join(outd, 'lines.json'), 'w'), indent=1)
print('total speech %.1fs' % sum(m['dur'] for m in meta))
