import os, sys, threading, json

cwd = os.getcwd()

# should get incoporated into mir.py when extracting mir

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w


def get_fn_submod(f):
    root = []
    for r in f["panicked_rn"]:
        for obj in r[[*r.keys()][0]]:
            p = [*obj.keys()][0]

            if not p.startswith("mod") and not p.startswith("lib"):
                root.append({[*r.keys()][0]: p})

    return root


def recreate(arr, key, obj):
    for a in arr:
        if key in a:
            a[key].append(obj)
            return arr
        
    o_ = {
        key: [obj]
    }
    arr.append(o_)
    return arr

def remove_duplicate(f):
    fns_submod = get_fn_submod(f)

    r_ = []
    fns = []

    for r in f["panicked_rn"]:
        for obj in r[[*r.keys()][0]]:
            p = [*obj.keys()][0]

            if (p.startswith("mod") or p.startswith("lib")):
                p_ = p.split("/")[1].split("::")
                
                if len(p_) > 1:
                    p_ = p_[0] + "/" + p_[1]
                    if {[*r.keys()][0]: p_} not in fns_submod:
                        r_ = recreate(r_, [*r.keys()][0], obj)
                        fns.append(p)
                    else:
                        f["p_total"] -= obj[p]
                else:
                    r_ = recreate(r_, [*r.keys()][0], obj)
                    fns.append(p)
            else:
                r_ = recreate(r_, [*r.keys()][0], obj)
                fns.append(p)

    fns = list(dict.fromkeys(fns))
    f["fn_mir"] -=  f["p_fn_num"] -len(fns)
    f["p_fn_num"] = len(fns)

    for r in r_:
        pass
        #print(f["p_total"])
        #print(r, sep= "\n")

def main():
    w = wksp()
    mirs = os.listdir(w.m_report)
    m_rerun = os.listdir(w.m_rerun)

    for mir in mirs:
        if mir == "tokio-timer-0.3.0-alpha.6.json":
        #if mir == "ucd-util-0.1.7.json":
            with open(os.path.join(w.m_report, mir)) as f_:
                f = json.load(f_)
                remove_duplicate(f)
                
main()