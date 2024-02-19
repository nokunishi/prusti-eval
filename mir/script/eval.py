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

def get_summary(m, list):
    w = wksp()
    with open(os.path.join(w.m, m), "r") as f:
        crate = m.replace(".json", "")
        f = json.load(f)
        fn_total = 0
        p_total = 0
        p_fns = []
        p_reason = []
        error = []
            
            
        for file_list in f["result"]:
            for file_name in file_list.keys():
                for fn_lists in file_list[file_name]:
                    for fn in fn_lists.keys():
                        name = file_name + "/" + fn
                        fn_total += 1
                            
                        p_total += fn_lists[fn]["num_total"]
                        if fn_lists[fn]["num_total"] != 0:
                            p_fns.append(name)
                        for r in fn_lists[fn]["reasons"]:
                            if r not in p_reason:
                                p_reason.append(r)
                        if fn_lists[fn]["num_blocks"] == "0":
                            error.append(name)
            
        obj = {
            crate: {
                "fn_total": fn_total,
                "p_total": p_total,
                "p_fn_num": len(p_fns),
                "p_fn": p_fns,
                "panicked_rn_num": len(p_reason),
                "panicked_rn": p_reason,
                "num_error": len(error),
                "fn_error": error
            }
        }
        list.append(obj)
        return list




def write_summary():
    w = wksp()
    mir_dir = os.listdir(w.m)
    list = []
    
    for m in mir_dir:
        list = get_summary(m, list)    

    with open(os.path.join(w.m_summary, m), "a") as f_:
        f = {"summary": []}
        for obj in list:
            f["summary"].append(obj)
        f = json.dumps(f)
        f_.write(f)        


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
            return list
    obj_ = {
        file_name: [{
            fn: obj
        }]
    }
    list.append(obj_)
    return list


if __name__ == "__main__":
    write_summary()
  
