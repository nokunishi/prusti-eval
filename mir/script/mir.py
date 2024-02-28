import os, sys, json, shutil
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


def extract(mir, list):
    total = 0
    reasons = []
    r_tmp = []
    w = wksp()
    unreachable = 0
    try:
        fn = mir.split("/")[-1].split("-")[1]
    except:
        return list

    try:
        with open(mir, "r") as f:
            j = 0
            for l in f:
                if l.strip().startswith("bb") and l.strip().endswith("{"):
                    j = l.strip().split(" ")[0].replace("bb", "").replace(":", "")
                if "assert(!" in l:
                    total += 1
                    if l.split('"')[1] in r_tmp:
                        for reason in reasons:
                            if [*reason.keys()][0] == l.split('"')[1]:
                                reason[l.split('"')[1]] += 1
                    else:
                        reasons.append({l.split('"')[1]: 1})
                        r_tmp.append(l.split('"')[1])
                if "unreachable;" in l:
                    unreachable += 1

            f.close()
    except:
        raise Exception("mir file missing (likely failed to build file)")

    file_name = mir.split("/")[-1].split("-")[0]
    obj = {  
        "num_total": total,
        "num_reasons": len(reasons),
        "reasons": reasons,
        "num_blocks": j,
        "unreachable": unreachable
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
    if os.path.exists(os.path.join(w.m, crate + ".json")) and "--rerun" not in sys.argv:
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

def summary_wksp(m, fn_total):
    w = wksp()
    with open(os.path.join(w.m, m), "r") as f:
        crate = m.replace(".json", "")
        f_ = json.load(f)
        fn_mir = 0
        p_total = 0
        p_reason = []
        error = []
        p_fn = 0

        compile_e = []
        compile_e_rr = []
        unreachable = []
        u_total = 0
            
            
        for file_list in f_["result"]:
            for file_name in file_list.keys():
                for fn_lists in file_list[file_name]:
                    for fn in fn_lists.keys():
                        name = file_name + "/" + fn
                        fn_mir += 1
                            
                        p_total += fn_lists[fn]["num_total"]
                        if  fn_lists[fn]["num_total"] != 0:
                            p_fn += 1
                        for r_obj in fn_lists[fn]["reasons"]:
                            r = [*r_obj.keys()][0]
                            inlist = False
                            for p_obj in p_reason:
                                if r == [*p_obj.keys()][0]:
                                    p_obj[r].append({
                                        name : r_obj[r]
                                    })
                                    inlist = True
                            if not inlist:
                                p_reason.append({
                                    r : [{
                                        name : r_obj[r]
                                    }]
                                })
                        if fn_lists[fn]["num_blocks"] == "0":
                            error.append(name)
                        if not fn_lists[fn]["num_blocks"] == "0" and fn_lists[fn]["unreachable"]:
                            unreachable.append({name: fn_lists[fn]["unreachable"]})
                            u_total += fn_lists[fn]["unreachable"]
        for e in f_["error"]:
            r = [*e.keys()][0]
            if r not in compile_e_rr:
                compile_e_rr.append(r)
            if e not in compile_e:
                compile_e.append(e)
            
        obj = {
                "fn_total": fn_total,
                "fn_mir": fn_mir,
                "p_total": p_total,
                "p_fn_num": p_fn,
                "panicked_rn_num": len(p_reason),
                "panicked_rn": p_reason,
                "num_b0": len(error),
                "fn_b0": error,
                "unreachable_bn_total": u_total,
                "unreachable_bn": unreachable,
                "compile_err_num": len(compile_e),
                "compile_err": compile_e
        }

        obj_rr = {
                "fn_total": fn_total,
                "fn_mir": fn_mir,
                "p_total": p_total,
                "p_fn_num": p_fn,
                "panicked_rn_num": len(p_reason),
                "panicked_rn": p_reason,
                "num_b0": len(error),
                "fn_b0": error,
                "unreachable_bn_total": u_total,
                "unreachable_bn": unreachable,
                "compile_err_num": len(compile_e),
                "compile_err": compile_e_rr
        }

        f.close()

        if "--rerun" in sys.argv:
            p = os.path.join(w.m_rerun, m)
            o = obj_rr
        else:
            p = os.path.join(w.m_report, m)
            o = obj
        with open(p, "w") as f_:
            print("writing summary for " + m[:-5] + " to " + p.split("/")[-2])
            o = json.dumps(o)
            f_.write(o)    


def write_all():
    w = wksp()
   
    mir_dir = os.listdir(w.m)
    
    for m in mir_dir:
        if os.path.exists(os.path.join(w.m_report, m)):
            print("mir report for " + m + " already exists")
            continue
        else:
            print("writing mir report for " + m + "...")
            summary_wksp(m)    


def main():
    args = []
    for arg in sys.argv:
        if "--" not in arg:
            args.append(arg)

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
  
