# Rebuild the public static site from the artifact export + the artifact page source.
import json,glob,os,re,sys
EXP="/home/claude/site_export"; SRC="/home/claude/lounge/library.html"; OUT="/home/claude/site/public"
os.makedirs(OUT,exist_ok=True)
data={"cafes":{},"meta":{}}
for f in glob.glob(EXP+"/cafes/*.json"):
    d=json.load(open(f)); d.pop("photos",None); data["cafes"][os.path.basename(f)[:-5]]=d
for f in glob.glob(EXP+"/meta/*.json"):
    data["meta"][os.path.basename(f)[:-5]]=json.load(open(f))
json.dump(data,open(OUT+"/data.json","w"),ensure_ascii=False,separators=(",",":"))
s=open(SRC).read()
title=re.search(r"<title>.*?</title>",s).group(0); s=s.replace(title,"",1)
# replace the claude runtime boot with a static fetch
start=s.index("(async()=>{\n  const db=window.claude"); end=s.index("})();",start)+5
boot='''(async()=>{
  try{const d=JSON.parse(document.getElementById("libdata").textContent);
    S.cafes=d.cafes;S.frameworks=d.meta.frameworks?.list||[];S.insights=d.meta.insights?.list||[];S.canvas=d.meta.canvas||null;S.compare=d.meta.compare||null;
    const n=Object.keys(S.cafes).length;$("#sync").innerHTML=`<b>${n} cafes</b> · updated ${esc(d.updated||"")}`;
    const h=(location.hash||"").replace("#","");S.route=S.cafes[h]?h:"compare";render(true);
  }catch(e){$("#sync").textContent="Could not load the library data.";$("#view").innerHTML='<div class="empty" style="margin-top:28px">Could not load the library. Refresh the page.</div>';}
})();'''
s=s[:start]+boot+s[end:]
s=s.replace('+`<a href="#add" class="cmp" ${S.route==="add"?\'aria-current="page"\':""}>+ Add a cafe</a>`;',';')
s=s.replace('S.route=h==="add"?"add":S.cafes[h]?h:"compare";render(true);','S.route=S.cafes[h]?h:"compare";render(true);')
s=s.replace('${secHead("08","Your ratings","Tap after you visit. Tap the same dot again to clear it.")}','${secHead("08","Ratings after a visit","Sawaschin\'s own scores, out of 5.")}')
s=s.replace(":\"Links to every photo guests have posted online. Open this page as its owner to add your own photos.\"",":\"Links to every photo guests have posted online: outside, food and inside.\"")
assert "claude.use" not in s.split("<script>")[1].split("(async()=>{")[-1]
html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{title}<meta name="description" content="Market research library for Lounge at the Edge of the Universe: cafes of Bhubaneswar, side by side.">
<meta name="theme-color" content="#0d0a14"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='14' fill='%23ff8fcf'/%3E%3Cellipse cx='32' cy='32' rx='29' ry='9' fill='none' stroke='%23b89cff' stroke-width='4' transform='rotate(-20 32 32)'/%3E%3C/svg%3E">
<style>body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}</style>
</head><body>
{s}
</body></html>'''
d3=json.load(open(OUT+"/data.json"));import datetime;d3["updated"]=datetime.date.today().strftime("%d %b %Y")
emb=json.dumps(d3,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
html=html.replace("</head><body>\n",'</head><body>\n<script id="libdata" type="application/json">'+emb+'</script>\n',1)
open(OUT+"/index.html","w").write(html)
open(OUT+".nojekyll","w").close() if False else open(OUT+"/.nojekyll","w").close()
d2=json.load(open(OUT+"/data.json"));import datetime;d2["updated"]=datetime.date.today().strftime("%d %b %Y");json.dump(d2,open(OUT+"/data.json","w"),ensure_ascii=False,separators=(",",":"))
print("built",len(data["cafes"]),"cafes")
