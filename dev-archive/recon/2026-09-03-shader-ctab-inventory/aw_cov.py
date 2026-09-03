import os, collections, importlib.util
spec = importlib.util.spec_from_file_location("ctab",
    r"D:/claude video game stuff/github-backups-pd/flat-to-vr-RE-toolkit/tools/d3d9-ctab.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root = r"D:/Program Files (x86)/Steam/steamapps/common/Alan Wake/shaders/build/pc"
allt = collections.Counter()
per_file = collections.defaultdict(collections.Counter)
for fn in sorted(os.listdir(root)):
    if not fn.endswith(".obj"): continue
    seen, tables = m.collect(os.path.join(root, fn))
    for k, c in tables.items():
        allt[k] += c; per_file[fn][k] += c

vs = {k:v for k,v in allt.items() if k[1]=="vs_3_0"}
ps = {k:v for k,v in allt.items() if k[1]=="ps_3_0"}
nvs, nps = sum(vs.values()), sum(ps.values())
print("vertex shaders: %d (%d layouts) ; pixel shaders: %d (%d layouts)" % (nvs,len(vs),nps,len(ps)))

CLIP = {"g_mViewToClip","g_mLocalToClip","g_mWorldToClip"}
have_vtc = sum(n for (rows,t),n in vs.items() if any(r[0]=="g_mViewToClip" for r in rows))
have_any = sum(n for (rows,t),n in vs.items() if any(r[0] in CLIP for r in rows))
print("\nVS carrying g_mViewToClip : %d / %d  (%.1f%%)" % (have_vtc,nvs,100*have_vtc/nvs))
print("VS carrying ANY *ToClip    : %d / %d  (%.1f%%)" % (have_any,nvs,100*have_any/nvs))

# register distribution of g_mViewToClip
dist = collections.Counter()
for (rows,t),n in vs.items():
    for name,rs,ri,rc in rows:
        if name=="g_mViewToClip": dist[(ri,rc)] += n
print("\ng_mViewToClip register distribution (vs_3_0):")
for (ri,rc),n in dist.most_common():
    print("   c%-4d x%-3d : %5d shaders" % (ri,rc,n))

# what do the VS WITHOUT any clip matrix look like?
print("\n=== VS with NO *ToClip matrix: what are they? ===")
noclip = [(rows,t,n) for (rows,t),n in vs.items() if not any(r[0] in CLIP for r in rows)]
noclip.sort(key=lambda x:-x[2])
tot = sum(x[2] for x in noclip)
print("total %d shaders in %d layouts" % (tot, len(noclip)))
namect = collections.Counter()
for rows,t,n in noclip:
    for r in rows: namect[r[0]] += n
for nm,n in namect.most_common(12): print("   %-34s %d" % (nm,n))
print("\n  which files:")
fct = collections.Counter()
for fn,tabs in per_file.items():
    for k,c in tabs.items():
        if k[1]=="vs_3_0" and not any(r[0] in CLIP for r in k[0]): fct[fn]+=c
for fn,c in fct.most_common(12): print("   %-28s %d" % (fn,c))
