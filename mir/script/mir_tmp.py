import os, sys, json
from w import wksp

cwd = os.getcwd()

def get_paths(path, mirs):
    dir_list = os.listdir(path)

    for dir in dir_list:
        dir_path = os.path.join(path, dir)

        if not os.path.isfile(dir_path):
            mirs = get_paths(dir_path, mirs)
        elif ".txt" in dir_path and dir_path not in mirs:
            mirs.append(dir_path)
    return mirs

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

def e_extract(mir, error):
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
                if  j < len(f_) and "note" in f_[j]:
                    note.append(f_[j].replace("= note:", "").replace("note:", "").strip())
                if j + 1 < len(f_) and "note" in f_[j + 1]:
                    note.append(f_[j + 1].replace("= note:", "").replace("note:", "").strip())

                if  j < len(f_) and "help" in f_[j]:
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

def m_extract(mir, crate, list):
    total = 0
    reasons = []
    r_tmp = []
    path = ""
    unreachable = 0
    try:
        fn = mir.split("/")[-1].split("-")[1]
    except:
        return list

    try:
        with open(mir, "r") as f:

            j = 0
            for l in f:
                if l.strip().startswith("path:"):
                    path = l.strip().replace("/tmp/" + crate + "/", "").split("path:")[1].strip()
                if l.strip().startswith("bb") and l.strip().endswith("{"):
                    j = l.strip().split(" ")[0].replace("bb", "").replace(":", "")
                if 'assert(move' in l or 'assert(!move' in l:
                    total += 1
                    if l.split('"')[1] in r_tmp:
                        for reason in reasons:
                            if [*reason.keys()][0] == l.split('"')[1]:
                                reason[l.split('"')[1]] += 1
                    else:
                        reasons.append({l.split('"')[1]: 1})
                        r_tmp.append(l.split('"')[1])
                if ("core::panicking::" in l and  "(move" in l) \
                    or '(const "explicit panic")' in l \
                    or "core::panicking::panic(const " in l:
                    total += 1
                    if '"' in l:
                        l_ = l.split('"')[1]
                    else:
                        l_ = l.split("::")[2]
                    if l.split('(')[1] in r_tmp:
                        for reason in reasons:
                            if [*reason.keys()][0] == l_:
                                reason[l_] += 1
                    else:
                        reasons.append({l_: 1})
                        r_tmp.append(l_)

                if "unreachable;" in l:
                    unreachable += 1

            f.close()
    except:
        raise Exception("mir file missing (likely failed to build file)")

    file_name = mir.split("/")[-1].split("-")[0]
    fn_name = mir.replace("/tmp/" + crate + "/", "").replace(".txt", "")
    obj = {  
        "fn_name": fn_name,
        "path": path,
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

def summary_tmp(crate, mirs):
    w = wksp()
    list = []
    error = []
    for mir in mirs:
        if "-e" not in mir:
            list = m_extract(mir, crate, list)
        else:
            error = e_extract(mir, error)
    with open(os.path.join(w.m, crate + ".json"), "w") as f_:
        f = {"result": [], "error": error}
        for obj in list:
            f["result"].append(obj)
        f = json.dumps(f)
        f_.write(f)
        f_.close()

    
def fix(crate):
    w = wksp()
    p = os.path.join(w.tmp, crate)
    summary_tmp(crate, get_paths(p,[]))


if __name__ == "__main__":
    w = wksp()
    for m in os.listdir(w.m_rprt):
        fix(m.replace(".json", ""))