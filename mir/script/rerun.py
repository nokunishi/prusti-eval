import os, sys, json
from pathlib import Path
import format as fm, run as rn
from w import wksp

cwd = os.getcwd()

def collect_global_var(crate):
    p = os.path.join("/tmp", crate.replace(".json", ""))
    try:
        list = rn.get_file(p, [])
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

def collect_imports(mir):
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

  
def rerun(crate):
    w = wksp()
    if not crate.strip().endswith(".json"):
        crate += ".json"

    vars = collect_global_var(crate)
    
    for var in vars:
        k = [*var.keys()][0]
        fm.set_var(k, var[k])   

    imports = collect_imports(os.path.join(w.m_rprt, crate))
    fm.fix_c_err(imports)

    if len(imports) == 0 and len(vars) == 0:
        return False
    else:
        return True

def main():
    w = wksp()
    mirs = os.listdir(w.m_report)

    try:
        args = []
        for arg in sys.argv:
            if "--" not in arg:
                args.append(arg)
        n = int(args[1])
    except:
        n = 0

    if "--a" in sys.argv:
        n = len(mirs)
    if n > 0:
        i = 0
        while i < n:
            rerun(mirs[i])
            i += 1
        return 
    else:
        for arg in sys.argv:
            if ".py" not in arg and not "--" in arg:
                if not arg.strip().endswith(".json"):
                    arg += ".json"
                rerun(arg)
        return 

if __name__ == "__main__":
    main()