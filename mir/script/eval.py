import os, sys, json
from pathlib import Path


def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

cwd = os.getcwd()

# TODO: count number of lines / fns
def summary():
    mirs = os.listdir(w.m)
    
    for m in mirs:
        with open(os.path.join(w.m, m), "r") as f:
            f = json.load(f)
            t_fn = 0
            t_panic = 0
            t_rn = 0
            t_rns = [] 
            
            for f_name in f["results"].keys():
                fns = f["results"][f_name]
                
                for fn in fns:
                    name = fn["fn_name"]
                    num_total = fn["num_total"]
                    num_reasons = fn["num_reasons"]
                    reasons = fn["reasons"]


def extract_summary(crate, file):
    total = 0
    reasons = []
    w = wksp()

    mir = file.replace(".rs", ".txt")
    try:
        with open(mir, "r") as f:
            for l in f:
                if "assert(!" in l:
                    total += 1
                    if not l.split('"')[1] in reasons:
                        reasons.append(l.split('"')[1])
    except:
        raise Exception("mir file missing (likely failed to build file)")

    file_name = mir.split("/")[-1]
    obj = {
        "num_total": total,
        "num_reasons": len(reasons),
        "reasons": reasons
    }

    p = os.path.join(w.m, crate + ".json")

    if os.path.exists(p):
        with open(p, "r") as f:
            f = json.load(f)
            if file_name in f["results"]:
                if obj not in f["results"][file_name]:
                    f["results"][file_name].append(obj)
            else:
                f["results"] = {
                    file_name: [obj]
                }
    else:
        f = {
            "results": {
                file_name: [obj]
            }
        }
    with open(p, "w") as f_:
        json.dump(f, f_)
    return

  