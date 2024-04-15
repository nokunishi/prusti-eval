import os, json
from w import wksp

class Stats:
    crate = 0
    fn_total = 0
    ln_total = 0
    fn_mir = 0
    fn_multiple_p = 0
    p_total = 0
    p_fn_num = 0
    panicked_rn_num = 0
    panicked_rn = []
    num_b0 = 0
    unreachable_bn = 0
    compile_err_num = 0
    compile_err = []

class Obj:
    def __init__(self, key, count):
        self.key = key
        self.count = count

    def __repr__(self):
        return "{" + self.key + ": " + str(self.count) + "}"
    
    def getKey(self):
        return self.key

    def getVal(self):
        return self.count

    def inc(self, val):
        self.count += val


def compile_err(s, list, rerun):
    if len(s.compile_err) == 0:
            s.compile_err.append(Obj("import/dependencies", 0))
            s.compile_err.append(Obj("associated_type", 0))  
            s.compile_err.append(Obj("attribute", 0))  
            s.compile_err.append(Obj("rule", 0)) 
            s.compile_err.append(Obj("syntax", 0))  
            s.compile_err.append(Obj("rust", 0))

    for e in list:
        if not rerun:
            k = [*e.keys()][0]
        else:
            k = e
                
        if "failed to resolve" in k or "import" in k or "dependency" in k:
            s.compile_err[0].inc(1)
        elif "scope" in k:
            s.compile_err[0].inc(1)
        elif "cannot find" in k and "in" in k:
            s.compile_err[0].inc(1)
        elif "associated type" in k:
            s.compile_err[1].inc(1)
        elif "attribute" in k:
            s.compile_err[2].inc(1)
        elif "bound" in k or "lifetime" in k or "size" in k:
            s.compile_err[3].inc(1)
        elif "expected" in k or "type annotations needed" in k:
            s.compile_err[4].inc(1)
        elif "Rust" in k or "experimental" in k:
            s.compile_err[5].inc(1)



def to_list(arr, key, obj):
    for a in arr:
        if key in a:
            a[key].append(obj)
            return arr
        
    o_ = {
        key: [obj]
    }
    arr.append(o_)
    return arr


def panic_rn(s, list):
    fns = {}
    j = 0

    for p_obj in list:
        k = [*p_obj.keys()][0]
        k_total = 0
        for p_ in p_obj[k]:
            k_total += p_["count"]

            p = p_["path"]
            if p in fns:
                fns[p] += p_["count"]
            else:
                fns[p] = p_["count"]

        inlist = False
        for obj in s.panicked_rn:
            if obj.getKey() == k:
                obj.inc(k_total)
                inlist = True
            
        if not inlist:
            s.panicked_rn.append(Obj(k, k_total))

    for fn in fns:
        if fns[fn] > 1:
            j += 1

    return j


def rm_duplicate(p_rn, fn_mir):
    r_new = []
    p_total_ = 0
    fns = []

    i = 0
    j = 0

    for r in p_rn:
        rsn = [*r.keys()][0]
        for obj in r[rsn]:
            fn = obj["fn"]
            p = obj["path"]
            c = obj["count"]


            fn_ = fn
            if "=" in fn_:
                fn_ = fn_.split("=")[0]
            fn_ = fn_.split("-")[0] + ".rs"

            inlist = False
            for obj_ in r_new:
                r = [*obj_.keys()][0]
                if r == rsn:
                    for o in obj_[r]:
                        if o["path"] == p:
                            inlist = True
                    
                    if not inlist and fn_ in obj["path"]:
                        obj_[r].append({
                            "fn": fn,
                            "path": p,
                            "count": c
                        })
                        if fn not in fns:
                            fns.append(fn)
                        p_total_ += c
                    else:
                        i += 1
                        j += c
                    inlist= True
            if not inlist and fn_ in obj["path"]:
                r_new.append({
                    rsn: [{
                        "fn": fn,
                        "path": p,
                        "count": c
                    }]
                })
                if fn not in fns:
                    fns.append(fn)
                p_total_ += c

    fn_mir -= i
    return r_new, fn_mir, p_total_, len(fns)

def read_fix(file, s, rerun):
    with open(file, "r") as f_, open("new.json", "w") as new:
        f = json.load(f_)

        r, fn_m, p, p_fn = rm_duplicate(f["panicked_rn"], f["fn_mir"])
        s.crate += 1
        s.fn_total += f["fn_total"]
        s.ln_total += f["line_total"]
        s.fn_mir += fn_m
        s.p_total += p
        s.p_fn_num += p_fn
        s.num_b0 += f["num_b0"]
        s.unreachable_bn += f["unreachable_bn_total"]
        s.compile_err_num += f["compile_err_num"]

        mul_p = panic_rn(s, r)  
        s.fn_multiple_p += mul_p  
        compile_err(s, f["compile_err"], rerun)

        obj = {
            "fn_total": f["fn_total"],
            "line_total": f["line_total"],
            "fn_mir":  fn_m,
            "fn_multiple_p": mul_p,
            "p_total": p,
            "p_fn_num":  p_fn,
            "panicked_rn_num": len(r),
            "panicked_rn": r,
            "num_b0": f["num_b0"],
            "fn_b0": f["fn_b0"] ,
            "unreachable_bn_total": f["unreachable_bn_total"],
            "unreachable_bn": f["unreachable_bn"],
            "compile_err_num": f["compile_err_num"],
            "compile_err": f["compile_err"],
        }

        obj = json.dumps(obj)
        new.write(obj)

        f_.close()
        new.close()
        os.rename("new.json", file)


def parse_p_rn(s):
    p_rn = {}
    for p in s.panicked_rn:
        p_ = p.getKey()
        if "assertion failed:" in p_:
            p_ = "assert_failed"
        if "panic_fmt" in p_:
            p_ = "panic_fmt"
        if "cell was filled by closure" in p_:
            p_ = "cell was filled by closure"
        if p_ not in p_rn:
            p_rn[p_] = p.getVal()
        else:
            p_rn[p_] += p.getVal()
    return p_rn

def write_summary():
    s = Stats()
    w = wksp()

    mir = os.listdir(w.m_rprt)
    mir_re = os.listdir(w.m_rerun)
    crashed = os.listdir(w.c_r)
    i = 0

    for m in mir:
        if m.replace(".json", ".txt") in crashed:
            continue
        if m not in mir_re:
            read_fix(os.path.join(w.m_rprt, m), s, False)  
        else:
            read_fix(os.path.join(w.m_rerun, m), s, True)   
    s.compile_err.sort(key = lambda x: x.count, reverse=True)
    c_err = []
    for e in s.compile_err:
        c_err.append({e.getKey(): e.getVal()})

    p_rn = parse_p_rn(s)
    p_rn = dict(sorted(p_rn.items(), key = lambda x: x[1], reverse=True))

    obj = {
        "crate_num": s.crate,
        "fn_total":  s.fn_mir + s.num_b0,
        "line_total": s.ln_total,
        "fn_mir": s.fn_mir,
        "p_total": s.p_total,
        "p_fn": s.p_fn_num,
        "multiple_p_fn": s.fn_multiple_p,
        "panicked_rn_num": len(p_rn),
        "panicked_rn": p_rn,
        "num_b0": s.num_b0,
        "unreachable_bn": s.unreachable_bn,
        "compile_err_num": s.compile_err_num,
        "compile_err": c_err
    }
    
    obj = json.dumps(obj)
    with open(os.path.join(w.m_s, w.date() +  ".json"), "w") as f:
        print("writing to mir summary...")
        f.write(obj)

if __name__ == "__main__":
    write_summary()
  
