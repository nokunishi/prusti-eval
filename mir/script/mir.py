import os, sys, json
from pathlib import Path
import run 


cwd = os.getcwd()

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

def get_paths(path, mirs):
    dir_list = os.listdir(path)

    for dir in dir_list:
        dir_path = os.path.join(path, dir)

        if not os.path.isfile(dir_path):
            mirs = get_paths(dir_path, mirs)
        elif ".txt" in dir_path and dir_path not in mirs:
            mirs.append(dir_path)
    return mirs

def reset(m):
    w = wksp()
    print("removing mir for " + m)
    os.remove(os.path.join(w.m, m))
    if os.path.exists(os.path.join(w.m_summary, m)):
        os.remove(os.path.join(w.m_summary, m))

def summary(m):
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
                "fn_total": fn_total,
                "p_total": p_total,
                "p_fn_num": len(p_fns),
                "p_fn": p_fns,
                "panicked_rn_num": len(p_reason),
                "panicked_rn": p_reason,
                "num_error": len(error),
                "fn_error": error
        }

        with open(os.path.join(w.m_summary, m), "w") as f_:
            f = json.dumps(obj)
            f_.write(f)    

def write_all():
    w = wksp()
   
    mir_dir = os.listdir(w.m)
    
    for m in mir_dir:
        if os.path.exists(os.path.join(w.m_summary, m)):
            print("mir summary for " + m + " already exists")
            continue
        else:
            print("writing mir summary for " + m + "...")
            summary(m)    

def extract(mir, list):
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
                    print(fn)
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

def read(crate, mirs):
    w = wksp()
    list = []
    for mir in mirs:
        list = extract(mir, list)

    if os.path.exists(os.path.join(w.m, crate + ".json")):
        print("mir for this file exists already")
        if input("Do you want to overwrite it?: (y or n)") == "n":
            return
    with open(os.path.join(w.m, crate + ".json"), "w") as f_:
        f = {"result": []}
        for obj in list:
            f["result"].append(obj)
        f = json.dumps(f)
        f_.write(f)

def main():
    args = []
    for arg in sys.argv:
        if "--" not in arg:
            args.append(arg)

    if "--rs" in sys.argv:
        reset(args[1] + ".json")
        return
    if "--wr" in sys.argv and "--a" in sys.argv:
        write_all()
        return
    if "--r" in sys.argv:
        mirs = get_paths("/tmp/" + args[1], [])
        read(args[1], mirs)
    else:
        mirs = get_paths("/tmp/" + args[1], [])
        read(args[1], mirs)
        summary(args[1] + ".json")

if __name__ == "__main__":
    main()
  
