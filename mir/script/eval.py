import os, sys, json
from pathlib import Path
import run 


def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

cwd = os.getcwd()

def summary():
    w = wksp()
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


def extract_summary(mir, list):
    total = 0
    reasons = []
    w = wksp()

    try:
        with open(mir, "r") as f:
            j = 0
            for l in f:
                if "fn " in l and "(" in l and ")" in l and \
                    "->" in l and "{" in l:
                    fn = l.split(" ")[1].split("(")[0]
                if l.strip().startswith("bb") and l.strip().endswith("{"):
                    j = l.strip().split(" ")[0].replace("bb", "").replace(":", "")
                if "assert(!" in l:
                    total += 1
                    if not l.split('"')[1] in reasons:
                        reasons.append(l.split('"')[1])
    except:
        raise Exception("mir file missing (likely failed to build file)")

    file_name = mir.split("/")[-1].split("-")[0]
    obj = {  
        "num_total": total,
        "num_reasons": len(reasons),
        "reasons": reasons,
        "num_blocks": j
    }

    for obj_ in list:
        if file_name in obj_:
            obj_[file_name].append({
                fn: obj
            })
            list.append(obj_)
            return list
    obj_ = {
            file_name: [{
                fn: obj
            }]
        }
    list.append(obj_)
    return list

  