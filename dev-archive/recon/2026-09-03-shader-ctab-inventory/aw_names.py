import os, collections, re, importlib.util
spec = importlib.util.spec_from_file_location("ctab",
    r"D:/claude video game stuff/github-backups-pd/flat-to-vr-RE-toolkit/tools/d3d9-ctab.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root = r"D:/Program Files (x86)/Steam/steamapps/common/Alan Wake/shaders/build/pc"
allt = collections.Counter()
for fn in sorted(os.listdir(root)):
    if fn.endswith(".obj"):
        _, tables = m.collect(os.path.join(root, fn))
        for k,c in tables.items(): allt[k]+=c

where = collections.defaultdict(collections.Counter)
for (rows,tgt),n in allt.items():
    for name,rs,ri,rc in rows: where[name][(tgt,ri,rc)] += n

rx = re.compile(r"clip|view|proj|camera|eye|world|near|far|fov", re.I)
hits = sorted(((sum(v.values()),k) for k,v in where.items() if rx.search(k)), reverse=True)
print("=== EVERY constant whose name mentions clip/view/proj/camera/eye/world/near/far/fov ===")
print("(%d distinct names)\n" % len(hits))
for tot,name in hits:
    spots = ", ".join("%s c%d x%d(%d)"%(t,r,c,k) for (t,r,c),k in where[name].most_common(4))
    print("  %-34s %-6d %s" % (name, tot, spots))
