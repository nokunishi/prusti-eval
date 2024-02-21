import os, sys, json
from pathlib import Path

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

def summary_wksp(m):
    w = wksp()
    with open(os.path.join(w.m, m), "r") as f:
        crate = m.replace(".json", "")
        f_ = json.load(f)
        fn_total = 0
        p_total = 0
        p_fns = []
        p_reason = []
        error = []

        compile_e = []
            
            
        for file_list in f_["result"]:
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

        for lines in f_["error"]:
            if lines not in compile_e:
                compile_e.append(lines)
            
        obj = {
                "fn_total": fn_total,
                "p_total": p_total,
                "p_fn_num": len(p_fns),
                "p_fn": p_fns,
                "panicked_rn_num": len(p_reason),
                "panicked_rn": p_reason,
                "num_err": len(error),
                "fn_er": error,
                "compile_err_num": len(compile_e),
                "compile_err": compile_e
        }

        f.close()

        with open(os.path.join(w.m_summary, m), "w") as f_:
            o = json.dumps(obj)
            f_.write(o)    

def write_all():
    w = wksp()
   
    mir_dir = os.listdir(w.m)
    
    for m in mir_dir:
        if os.path.exists(os.path.join(w.m_summary, m)):
            print("mir summary for " + m + " already exists")
            continue
        else:
            print("writing mir summary for " + m + "...")
            summary_wksp(m)    


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
                if l.strip().startswith("bb") and l.strip().endswith("{"):
                    j = l.strip().split(" ")[0].replace("bb", "").replace(":", "")
                if "assert(!" in l:
                    total += 1
                    if not l.split('"')[1] in reasons:
                        reasons.append(l.split('"')[1])
            f.close()
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


def parse_help_mgs(f_, j, help):
    try:
        if "help: consider importing this" in f_[j] and j + 2 < len(f_):
            word = "consider importing: " + f_[j+2].split("+")[1].strip()
        elif "help: a trait with a similar name exists" in f_[j] and j + 6 < len(f_):
            word = "consider importing: " + f_[j+6].split("+")[1].strip()
        else:
            word = f_[j + 1].replace("= help:", "").strip()
    except:
        word = f_[j + 1].replace("= help:", "").strip()
    help.append(word)
    return help

def error_extract(mir, error):
    with open(mir, "r") as f:
        f_ = f.readlines()
        i = 0

        while i < len(f_):
            if f_[i].strip().startswith("error"):
                where = ""
                note = []
                help = []

                j = 1
                e = ""
                while j < len(f_[i].split(":")):
                    e += f_[i].split(":")[j].strip() + ", "
                    j+= 1
                e = e.strip()[:(len(e) - 2)].replace(", , ", "::")

                j = i + 1

                if i +1 < len(f_) and "-->" in f_[i+1]:
                    where = f_[i+1].replace("-->", "").strip();
                    j += 1
                
                while j < len(f_):
                    if f_[j].strip().startswith("|") or f_[j][0].isdigit():
                        j += 1
                    else:
                        break
                if "note" in f_[j]:
                    note.append(f_[j].replace("= note:", "").replace("note:", "").strip())
                if j + 1 < len(f_) and "note" in f_[j + 1]:
                    note.append(f_[j + 1].replace("= note:", "").replace("note:", "").strip())

                if "help" in f_[j]:
                    help = parse_help_mgs(f_, j, help)

                if j + 1 < len(f_) and "help" in f_[j + 1]:
                    help = parse_help_mgs(f_, j+1, help)

                if e not in error and "aborting due to " not in e:
                    obj = {
                        e: {
                        "where": where,
                        "note": note,
                        "help": help
                    }
                    }   
                    error.append(obj)
            i += 1
        f.close()
    return error

def summary_tmp(crate, mirs):
    w = wksp()
    list = []
    if os.path.exists(os.path.join(w.m, crate + ".json")):
        print("mir for this file exists already")
        if input("Do you want to overwrite it?: (y or n) ") == "n":
            return
    
    error = []
    for mir in mirs:
        if "-e" not in mir:
            list = extract(mir, list)
        else:
            error = error_extract(mir, error)

    with open(os.path.join(w.m, crate + ".json"), "w") as f_:
        f = {"result": [], "error": error}
        for obj in list:
            f["result"].append(obj)
        f = json.dumps(f)
        f_.write(f)
        f_.close()

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
        summary_tmp(args[1], mirs)
    else:
        mirs = get_paths("/tmp/" + args[1], [])
        summary_tmp(args[1], mirs)
        summary_wksp(args[1] + ".json")

if __name__ == "__main__":
    main()
  
