import os, threading, http.server, functools, runpy
D=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(D+'/../..')
s=open(ROOT+'/index.html',encoding='utf-8').read(); a=" function flMenuOn(id){"; assert s.count(a)==1
open(ROOT+'/ktest.html','w',encoding='utf-8').write(s.replace(a," window.__x=function(c){return eval(c);};"+a))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('',8768),functools.partial(Q,directory=ROOT)); threading.Thread(target=srv.serve_forever,daemon=True).start()
runpy.run_path(D+'/cap.py', run_name='__main__')
n=len([f for f in os.listdir(D+'/shots') if f.endswith('.png')]); print('shots',n); assert n>=23
runpy.run_path(D+'/mk.py', run_name='__main__')
os.remove(ROOT+'/ktest.html')
