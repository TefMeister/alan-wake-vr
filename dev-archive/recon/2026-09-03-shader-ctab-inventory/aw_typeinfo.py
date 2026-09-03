import os, re, struct, collections
root = r"D:/Program Files (x86)/Steam/steamapps/common/Alan Wake/shaders/build/pc"
CLS = {0:"SCALAR",1:"VECTOR",2:"MATRIX_ROWS",3:"MATRIX_COLUMNS",4:"OBJECT",5:"STRUCT"}
TYP = {1:"BOOL",2:"INT",3:"FLOAT",4:"STRING",5:"TEXTURE",
       6:"TEXTURE1D",7:"TEXTURE2D",8:"TEXTURE3D",9:"TEXTURECUBE",
       10:"SAMPLER",11:"SAMPLER1D",12:"SAMPLER2D",13:"SAMPLER3D",14:"SAMPLERCUBE"}
WANT = {"g_mViewToClip","g_mLocalToView","g_mViewToWorld","g_mWorldToClip",
        "g_mLocalToClip","g_mClipToView","GPU_skinning_matrices"}

def cstr(d,a):
    e=d.find(b"\0",a); return d[a:e].decode("latin-1","replace") if e>=0 else ""

out = collections.Counter()
for fn in sorted(os.listdir(root)):
    if not fn.endswith(".obj"): continue
    d = open(os.path.join(root,fn),"rb").read()
    for m in re.finditer(b"CTAB", d):
        base = m.start()+4
        try:
            size,creator,ver,nconst,cinfo,flags,target = struct.unpack_from("<7I",d,base)
        except struct.error: continue
        if size!=0x1C or not (0<nconst<512): continue
        if base+cinfo+nconst*20 > len(d): continue
        tgt = cstr(d, base+target) if base+target<len(d) else "?"
        if not re.match(r"^(vs|ps)_\d_\d$", tgt): continue
        for i in range(nconst):
            o = base+cinfo+i*20
            name_off,regset,regidx,regcount,_res,ti,_dv = struct.unpack_from("<IHHHHII",d,o)
            if base+name_off>=len(d): continue
            nm = cstr(d, base+name_off)
            if nm not in WANT: continue
            if base+ti+12 > len(d): continue
            cl,ty,rows,cols,elems,smem = struct.unpack_from("<6H", d, base+ti)
            out[(nm, tgt, regidx, regcount, CLS.get(cl,cl), TYP.get(ty,ty), rows, cols, elems)] += 1

print("%-24s %-7s %-6s %-16s %-6s %-4s %-5s %-7s %s" %
      ("constant","stage","reg","class","type","rows","cols","elements","shaders"))
for k,n in sorted(out.items(), key=lambda kv:(kv[0][0], -kv[1])):
    nm,tgt,ri,rc,cl,ty,rows,cols,el = k
    print("%-24s %-7s c%-5d %-16s %-6s %-4d %-5d %-7d %d" % (nm,tgt,ri,cl,ty,rows,cols,el,n))
