import os, sys, threading, json
import collect as c
from w import wksp

w = wksp()
lock = threading.Lock()


def setup():
    if not os.path.exists(w.e_dir):
        os.mkdir(w.e_dir)
    if not os.path.exists(w.e_s):
        os.mkdir(w.e_s)
    if not os.path.exists(w.e_c):
        os.mkdir(w.e_c)

def equal(r, r_p):
    # arithmetic
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
    
    # bitwise 
    if "Shl" in r_p and "shift left" in r:
        return True
    if "Shr" in r_p and "shift right" in r:
        return True
    
    # explicit panic
    if "unreachable!(..)" in r_p and \
         'internal error: entered unreachable code' in r:
        return True
    if "panic!(..)" in r_p and 'explicit panic' in r:
        return True
    if "unimplemented!(..)" in r_p and 'not implemented' in r:
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
    us = {}
    other = {}

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
                fn = l_["fn"].split("-")[-1].split("::")[-1]
                file = l_["path"].split(":")[0]
                start = int(l_["path"].split(".rs:")[1].split(":")[0])
                end = int(l_["path"].split(".rs:")[1].split(" ")[1].split(":")[0])

                if start == end and "={" not in fn:
                    tmp = os.path.join(w.tmp, mir.split("/")[-1].replace(".json", ""), file)
                    start, end = c.get_endlns(tmp, fn)
                
                if start <= ln_us and ln_us <= end and file_us == file:
                    rsn =  obj[[*obj.keys()][0]]
                    o = {"fn": l_["fn"], "path": l_["path"], "l_no": ln_us}
                    if rsn in us:
                        if o not in us[rsn]:
                            us[rsn].append(o)
                    else:
                        us[rsn] = [o]    
                else:
                    o = {"fn": l_["fn"], "path": l_["path"]}
                    if [*line.keys()][0] in other:
                        if o not in other[[*line.keys()][0]]:
                            other[[*line.keys()][0]].append(o)
                    else:
                        other = {
                            [*line.keys()][0]: [o]
                        }
    return us, other

def mir_ve(mir, p_lines):
    eq = {}
    ne = []
    mir_only = []

    with open(mir, "r") as m_:
        for obj in json.load(m_)["panicked_rn"]:
            r = [*obj.keys()][0]
            for l in obj[r]:
                file = l["path"].split(":")[0]
                fn = l["fn"].split("-")[-1].split("::")[-1]
        
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
                            if r in eq:
                                eq[r].append({"fn": fn, "path": l["path"]})
                            else:
                                eq[r] =  [{"fn": l["fn"], "path": l["path"]}] 
                        else:
                            ne.append({"fn": l["fn"], "path": l["path"], "mir":r, "prusti": r_p})


                if not inPrusti:
                    inlist = False
                    for obj in mir_only:
                        if [*obj.keys()][0] == r:
                            obj[r].append({"fn": l["fn"], "path": l["path"]})
                            inlist = True

                    if not inlist:
                        mir_only.append({r: [{"fn": l["fn"], "path": l["path"]}] })

        m_.close()                             
    return eq, ne, mir_only                

def write(mir, eq, ne, us, other):
    eq = dict(sorted(eq.items(),  key=lambda x: len(x), reverse=True))
    us = dict(sorted(us.items(),  key=lambda x: len(x), reverse=True))
    other = dict(sorted(other.items(),  key=lambda x: len(x), reverse=True))
    
    with open(mir, "r") as m_:
        m = json.load(m_)
        f_total = m["fn_total"]
        ln_total = m["line_total"]
        p_total = m["p_total"]
        m_.close()
        
    with open(os.path.join(w.e_c, mir.split("/")[-1].strip()), "w") as f:
        obj = {
            "fn_total": f_total,
            "ln_total":ln_total,
            "panic_total":p_total,
            "match": eq,
            "mismatch": ne,
            "unsupported": us,
            "mir_only": other 
        }
        obj = json.dumps(obj)
        print("writing comparison rprt for " + mir.split("/")[-1].replace(".json", ""))
        f.write(obj)


def run():
    mirs = os.listdir(w.m_rprt)
    m_rerun = os.listdir(w.m_rerun)

    if "--a" in sys.argv:
        setMIR = True
        n = len(os.listdir(w.m_rprt))
    elif sys.argv[1].isdigit():
        setMIR = True
        n = int(sys.argv[1])
    else:
        setMIR = False
        if ".json" not in sys.argv[1]:
            sys.argv[1] += ".json"
        mir = sys.argv[1]
        n = 1

    i = 0
    while i < n and i < len(mirs):
        if setMIR:
            mir = mirs[i]

        #if mir in os.listdir(w.e_c):
        #    print("comparison report already exists for "+ mir)
        #    i += 1
        #    continue
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
        i += 1

def main():
    w = wksp()
    
    if "--mm" in sys.argv:
        print_crates("mismatch")
        return
    if "--mo" in sys.argv:
        print_crates("mir_only")
        return
    
    setup()
    run()


if __name__ == "__main__":
    main()