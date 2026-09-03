#!/usr/bin/env python3
"""ビルド済みサイト（site/）の内部リンクとアンカーを総当たりで確認する。

Markdown側のリンクは GitHub上とサイト上で意味が変わることがある
（`use_directory_urls: true` でページのURLが1段深くなるため）。
生成後のHTMLを実際にたどって、404とアンカー切れを出荷前に落とす。
"""
import os, re, urllib.parse, html, sys
SITE="site"; BASE="/getting-started-vibecoding/"   # site_url のパス部分
href=re.compile(r'(?:href|src)="([^"]+)"')
pages={}; ids={}
for dp,dn,fn in os.walk(SITE):
    for n in fn:
        if n.endswith(".html"):
            p=os.path.join(dp,n); t=open(p,encoding="utf-8",errors="ignore").read()
            pages[p]=t; ids[os.path.relpath(p,SITE)]=set(re.findall(r'id="([^"]+)"',t))
bad=[]
for p,t in pages.items():
    rel=os.path.relpath(p,SITE); base=os.path.dirname(rel)
    for h in href.findall(t):
        h=html.unescape(h)
        if h.startswith(("http://","https://","mailto:","data:","#","//")): continue
        u=urllib.parse.urlparse(h); path=urllib.parse.unquote(u.path); frag=urllib.parse.unquote(u.fragment)
        if not path: continue
        if path.startswith("/"):
            if not path.startswith(BASE): bad.append((rel,h,"base外")); continue
            tgt=os.path.normpath(path[len(BASE):] or ".")
        else:
            tgt=os.path.normpath(os.path.join(base,path))
        if tgt.startswith(".."): bad.append((rel,h,"サイト外")); continue
        fs=os.path.join(SITE,tgt)
        if os.path.isdir(fs) or path.endswith("/"):
            tgt=os.path.normpath(os.path.join(tgt,"index.html")); fs=os.path.join(SITE,tgt)
        if not os.path.exists(fs): bad.append((rel,h,"404 -> "+tgt)); continue
        if frag and tgt in ids and frag not in ids[tgt]: bad.append((rel,h,"アンカー無し #"+frag))
for b in bad: print("NG", b)
print(f"ページ {len(pages)} 枚 / 壊れたリンク {len(bad)} 件")
sys.exit(1 if bad else 0)
