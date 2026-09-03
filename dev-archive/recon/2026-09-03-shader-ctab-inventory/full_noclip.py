import os, collections, importlib.util
spec = importlib.util.spec_from_file_location("ctab",
    r"D:/claude video game stuff/github-backups-pd/flat-to-vr-RE-toolkit/tools/d3d9-ctab.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root = r"D:/Program Files (x86)/Steam/steamapps/common/Alan Wake/shaders/build/pc"
CLIP = {"g_mViewToClip","g_mLocalToClip","g_mWorldToClip"}
fct = collections.Counter(); tot=0
for fn in sorted(os.listdir(root)):
    if not fn.endswith(".obj"): continue
    _, tables = m.collect(os.path.join(root, fn))
    for k,c in tables.items():
        if k[1]=="vs_3_0" and not any(r[0] in CLIP for r in k[0]):
            fct[fn]+=c; tot+=c
print("COMPLETE list of files containing the %d no-clip vertex shaders:"%tot)
for fn,c in fct.most_common(): print("   %-28s %d"%(fn,c))
print("sum =", sum(fct.values()), "; files =", len(fct))
