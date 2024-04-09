import os, sys, threading, json
import collect as c
from w import wksp

w = wksp()
lock = threading.Lock()

def equal(r, r_p):
    if "add" in r_p and "+" in r:
        return True
    if "subtract" in r_p and "-" in r:
        return True
    if "multiply" in r_p and "*" in r:
        return True
    if "divide" in r_p and "/" in r:
        return True
    if "remainder" in r_p and "remainder" in r:
        return True
    if "unreachable!(..)" in r_p and \
         'const "internal error: entered unreachable code"' in r:
        return True
    if "panic!(..)" in r_p and 'const "explicit panic"' in r:
        return True
    if "index" in r_p and "index" in r:
        return True
    else:
        return False

def print_crates(k):
    crates = []
    for e in os.listdir(w.m_eval):
        with open(os.path.join(w.m_eval, e), "r") as f_:
            f = json.load(f_)
            if len(f[k]) > 0:
                crates.append(e)

            f_.close()
    
    for c in crates:
        print(c, sep="\n")

def mir_us(mir, list):
    us = []
    other = []

    for obj in c.unsupported(mir):
        file_us = [*obj.keys()][0].split(":")[0]
        try:
            ln_us =  int([*obj.keys()][0].split(".rs:")[1].split(":")[0])
        except:
            print(mir)
            print(obj)
        
        for line in list:
            list_ = line[[*line.keys()][0]]
            
            for l_ in list_:
                fn = l_["fn"].split("-")[1]
                file = l_["path"].split(":")[0]
                start = int(l_["path"].split(".rs:")[1].split(":")[0])
                end = int(l_["path"].split(".rs:")[1].split(" ")[1].split(":")[0])

                if start == end and "={" not in fn:
                    tmp = os.path.join(w.tmp, mir.split("/")[-1].replace(".json", ""), file)
                    start, end = c.get_endlns(tmp, fn)
                
                if start <= ln_us and ln_us <= end and file_us == file:
                    o = {"fn": l_["fn"], "path": l_["path"], "l_no": ln_us, "rsn": obj[[*obj.keys()][0]]}
                    if o not in us:
                        us.append(o)    
                else:
                    o = {"fn": l_["fn"], "path": l_["path"], "mir": l_["mir"]}
                    other.append(o)

    return us, other

def mir_ve(mir, p_lines):
    eq = []
    ne = []
    mir_only = []

    with open(mir, "r") as m_:
        for obj in json.load(m_)["panicked_rn"]:
            r = [*obj.keys()][0]
            for l in obj[r]:
                file = l["path"].split(":")[0]
                fn = l["fn"].split("-")[1]
        
                start =  int(l["path"].split(".rs:")[1].split(" ")[0].split(":")[0])
                end =  int(l["path"].split(" ")[1].split(":")[0])

                if start == end and "={" not in fn:
                    tmp = os.path.join(w.tmp, mir.split("/")[-1].replace(".json", ""), file)
                    start, end = c.get_endlns(tmp, fn)

                inPrusti = False
                for p in p_lines:
                    file_p = [*p.keys()][0].split(":")[0]
                    ln_p = int([*p.keys()][0].split(":")[1])
                    r_p = p[[*p.keys()][0]]

                    if start <= ln_p and ln_p <= end and file_p == file:
                        inPrusti = True
                        if equal(r, r_p):
                            inlist = False
                            for obj in eq:
                                if [*obj.keys()][0] == r:
                                    obj[r].append({"fn": fn, "path": l["path"]})
                                    inlist = True

                            if not inlist:
                                eq.append(
                                    {r: [{"fn": l["fn"], "path": l["path"]}] })
                        else:
                            ne.append({"fn": l["fn"], "path": l["path"], "mir":r, "prusti": r_p})


                if not inPrusti:
                    inlist = False
                    for obj in mir_only:
                        if [*obj.keys()][0] == r:
                            obj[r].append({"fn": l["fn"], "path": l["path"], "mir": r})
                            inlist = True

                    if not inlist:
                        mir_only.append({r: [{"fn": l["fn"], "path": l["path"], "mir": r}] })

        m_.close()                             
    return eq, ne, mir_only                

def write(mir, eq, ne, us, other):
    with open(mir, "r") as m_:
        m = json.load(m_)
        f_total = m["fn_total"]
        ln_total = m["line_total"]
        p_total = m["p_total"]
        
    with open(os.path.join(w.r_e, mir.split("/")[-1].strip()), "w") as f:
        obj = {
            "match": eq,
            "mismatch": ne,
            "unsupported": us,
            "mir_only": other 
        }
        obj = json.dumps(obj)
        print("writing comparison rprt for " + mir)
        f.write(obj)


def run():
    mirs = os.listdir(w.m_rprt)
    m_rerun = os.listdir(w.m_rerun)
    evals = os.listdir(w.r_e)

    for mir in mirs:
        if mir in m_rerun:
            m = os.path.join(w.m_rerun, mir)
        else:
            m = os.path.join(w.m_rprt, mir)

        if not os.path.exists(os.path.join(w.p_c, mir)):
            lock.acquire()
            os.chdir(w.p)
            os.system("python3 run_x.py " + mir.replace(".json", ""))
            lock.release()
        
        eq, ne, mir_only = mir_ve(m, c.v_err(mir))
        us, other = mir_us(mir, mir_only)
        write(m, eq, ne, us, other)

def main():
    w = wksp()
    
    if "--mm" in sys.argv:
        print_crates("mismatch")
        return
    if "--mo" in sys.argv:
        print_crates("mir_only")
        return
    
    run()


if __name__ == "__main__":
    main()