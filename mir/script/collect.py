import os, json
from w import wksp

w = wksp()

def get_file(path, file_lists):
    dir_list = os.listdir(path)

    for dir in dir_list:
        dir_path = os.path.join(path, dir)

        if not os.path.isfile(dir_path):
            file_lists = get_file(dir_path, file_lists)
        elif ".rs" in dir_path and dir_path not in file_lists:
            if "lib.rs" in dir_path or "mod.rs" in dir_path:
                file_lists.insert(0, dir_path)
            else:
                file_lists.append(dir_path)

    return file_lists

def prusti_err():
    list = []
    for file in os.listdir(w.p_c):
         with open(os.path.join(w.p_c, file), "r") as f_:
            f = json.load(f_)

            if f["verification_failed_num_total"] > 0 and file not in list:
                for r in f["verification_failed_reason"]:
                    if "assertion might fail" in r or "might be reachable" in r or \
                        "bounds" in r or "range" in r:
                        list.append(file)
    return list

def global_var(crate):
    p = os.path.join("/tmp", crate.replace(".json", ""))
    try:
        list = get_file(p, [])
    except:
        list = [p]
    roots = []
    vars = []
    
    for l in list:
        if "lib.rs" in l or "mod.rs" in l:
            p = os.path.abspath(os.path.join(l, os.pardir))
            if p not in roots:
                roots.append(p)
                vars.append({
                    l: []
                })
                with open(l, "r") as f:
                    for l_no, line in enumerate(f):
                        line = line.strip()
                        if line.startswith("const") and line not in vars[-1]:
                             vars[-1][l].append(line)   
                    f.close()    
    for v in vars:
        k = [*v.keys()][0]
        if len(v[k]) == 0:
            vars.remove(v)   
    return vars   

def imports(mir):
    with open(mir, "r") as f_:
        f = json.load(f_)
        imports = []
        files = []

        for err in f["compile_err"]:
            e = [*err][0]
            if len(err[e]["help"]) > 0:
                for help in err[e]["help"]:
                    if  "consider importing" in help:
                        where = err[e]["where"].split(":")[0]
                        try:
                            help = help.split("importing:")[1].strip()
                        except:
                            continue
                        if where in files:
                            i = 0
                            while i < len(imports):
                                k = [*imports[i]][0]
                                if k == where:
                                    imports[i][k].append(help)
                                    break
                                i+= 1
                        else:
                            imports.append({where: [help]})
                            files.append(where)
                
        f_.close()
        return imports