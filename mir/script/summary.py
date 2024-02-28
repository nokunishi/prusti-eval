import os, sys, json, datetime
from pathlib import Path

cwd = os.getcwd()

class Stats:
    crate = 0
    fn_total = 0
    fn_mir = 0
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


def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w


def panic_rn(s, list, rerun):
    for p_obj in list:
        k = [*p_obj.keys()][0]
        k_total = 0
        for p_ in p_obj[k]:
            k_ = [*p_.keys()][0]
            k_total += p_[k_]
            
        inlist = False
        for obj in s.panicked_rn:
            if obj.getKey() == k:
                obj.inc(k_total)
                inlist = True
            
        if not inlist:
            s.panicked_rn.append(Obj(k, k_total))

def compile_err(s, list, rerun):
    if len(s.compile_err) == 0:
            s.compile_err.append(Obj("import_crates", 0))
            s.compile_err.append(Obj("module", 0)) 
            s.compile_err.append(Obj("scope", 0))  
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
                
        if "failed to resolve" in k or "import" in k:
            s.compile_err[0].inc(1)
        elif "scope" in k:
            s.compile_err[2].inc(1)
        elif "cannot find" in k and "in" in k:
            s.compile_err[1].inc(1)
        elif "associated type" in k:
            s.compile_err[3].inc(1)
        elif "attribute" in k:
            s.compile_err[4].inc(1)
        elif "bound" in k or "lifetime" in k or "size" in k:
            s.compile_err[5].inc(1)
        elif "expected" in k or "type annotations needed" in k:
            s.compile_err[6].inc(1)
        elif "Rust" in k or "experimental" in k:
            s.compile_err[7].inc(1)

def read(file, s, rerun):
    with open(file, "r") as f_:
        f = json.load(f_)
        s.crate += 1
        s.fn_total += f["fn_total"]
        s.fn_mir += f["fn_mir"]
        s.p_total += f["p_total"]
        s.p_fn_num += f["p_fn_num"]
        s.num_b0 += f["num_b0"]
        s.unreachable_bn += f["unreachable_bn_total"]
        s.compile_err_num += f["compile_err_num"]

        panic_rn(s, f["panicked_rn"], rerun)       
        compile_err(s, f["compile_err"], rerun)


def main():
    w = wksp()
    s = Stats()

    mir = os.listdir(w.m_report)
    mir_re = os.listdir(w.m_rerun)
    i = 0

    for m in mir:
        if m not in mir_re:
            read(os.path.join(w.m_report, m), s, False)  
        else:
            read(os.path.join(w.m_rerun, m), s, True)   
    
    s.compile_err.sort(key = lambda x: x.count, reverse=True)
    c_err = []
    for e in s.compile_err:
        c_err.append({e.getKey(): e.getVal()})

    s.panicked_rn.sort(key = lambda x: x.count, reverse=True)
    p_rn = []
    for p in s.panicked_rn:
        p_rn.append({p.getKey(): p.getVal()})

    obj = {
        "crate_num": s.crate,
        "fn_total": s.fn_total,
        "fn_mir": s.fn_mir,
        "p_total": s.p_total,
        "p_fn_num": s.p_fn_num,
        "panicked_rn_num": len(p_rn),
        "panicked_rn": p_rn,
        "num_b0": s.num_b0,
        "unreachable_bn": s.unreachable_bn,
        "compile_err_num": s.compile_err_num,
        "compile_err": c_err
    }
    
    obj = json.dumps(obj)
    date_ = str(datetime.datetime.now()).split(" ")
    date = date_[0] + "-" + date_[1]
    with open(os.path.join(w.m_summary, "mir-" + date +  ".json"), "w") as f:
        print("writing to mir summary...")
        f.write(obj)

if __name__ == "__main__":
    main()
  
