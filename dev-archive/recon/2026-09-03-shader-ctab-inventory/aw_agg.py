import sys, os, collections, importlib.util
spec = importlib.util.spec_from_file_location("ctab",
    r"D:/claude video game stuff/github-backups-pd/flat-to-vr-RE-toolkit/tools/d3d9-ctab.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

root = r"D:/Program Files (x86)/Steam/steamapps/common/Alan Wake/shaders/build/pc"
# per distinct layout: (rows, target) -> count, and which files it came from
allt = collections.Counter()
origin = collections.defaultdict(set)
for fn in sorted(os.listdir(root)):
    if not fn.endswith(".obj"): continue
    seen, tables = m.collect(os.path.join(root, fn))
    for k, c in tables.items():
        allt[k] += c
        origin[k].add(fn)

print("TOTAL distinct layouts: %d ; total shaders: %d" % (len(allt), sum(allt.values())))

# --- where do the camera matrices land, globally, by stage ---
where = collections.defaultdict(collections.Counter)
for (rows, tgt), n in allt.items():
    for name, rs, ri, rc in rows:
        where[name][(tgt, ri, rc)] += n

print("\n=== CAMERA / PROJECTION CONSTANTS, all files ===")
for nm in ["g_mViewToClip","g_mLocalToView","g_mViewToWorld","g_mLocalToClip",
           "g_mWorldToView","g_mLocalToWorld","GPU_skinning_matrices",
           "g_vCameraPos","g_mPrevLocalToClip","g_mViewToPrevClip"]:
    if nm in where:
        tot = sum(where[nm].values())
        spots = ", ".join("%s c%d x%d (%d)" % (t,r,c,k) for (t,r,c),k in where[nm].most_common(6))
        print("  %-28s total %-6d %s" % (nm, tot, spots))

# --- the correlation test: skinning palette <-> camera relocated to c192 ---
print("\n=== CORRELATION: GPU_skinning_matrices vs g_mViewToClip register ===")
tab = collections.Counter()
for (rows, tgt), n in allt.items():
    if tgt != "vs_3_0": continue
    d = {r[0]: r for r in rows}
    if "g_mViewToClip" not in d: continue
    vc = d["g_mViewToClip"][2]
    skin = "GPU_skinning_matrices" in d
    skinreg = d["GPU_skinning_matrices"][2:4] if skin else None
    tab[(skin, skinreg, vc)] += n
for (skin, skinreg, vc), n in sorted(tab.items(), key=lambda kv:-kv[1]):
    print("  skinning=%-5s %-12s g_mViewToClip c%-4d : %d shaders"
          % (skin, ("c%d x%d"%skinreg) if skinreg else "-", vc, n))
