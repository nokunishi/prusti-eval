import os, sys, json, shutil
from pathlib import Path
import run as rn

cwd = os.getcwd()

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

def get_dirs(path, dirs):
    root_dir = os.listdir(path)

    for dir in root_dir:
        dir = os.path.join(path, dir)
        if not os.path.isfile(dir):
            dirs.append(dir)
            dirs = get_dirs(dir, dirs)

    return dirs

def comment(line):
    line = line.strip()
    return line.startswith("//") or line.startswith("/*") or line.endswith("*/")


def fix_c_err(imports):
    if len(imports) == 0:
        return

    w = wksp()

    for i in imports:
        file = [*i][0]
        deps = []
        with open(file, "r") as f:
            j = 0
            for l_no, line in enumerate(f):
                if "extern crate " in line:
                    j = l_no
                if "use " in line and not comment(line):
                    deps.append(line.strip())
            j+= 1
            f.close()
        with open(file, "r") as f, open("new.rs", "w") as new:
            for l_no, line in enumerate(f):
                if j == l_no:
                    for i_ in i[file]:
                        if i_ not in deps:
                            new.write(i_ + "\n")
                            deps.append(i_)
                
                if not line.strip().startswith(";"):
                    new.write(line) 
            f.close()
            new.close()
        os.rename("new.rs", file)


def set_var(path, vars):
    if len(vars) == 0:
        return 

    dir = os.path.abspath(os.path.join(path, os.pardir))
    files =  rn.get_file(dir, [])

    for p in files:
        if path == p:
            continue
        
        const = []
        set = False
        with open(p, "r") as f:
            for l_no, line in enumerate(f):
                line = line.strip()
                if line.startswith("const"):
                    const.append(line) 
        with open(p, "r") as f, open("new.rs", "w") as new:
            for l_no, line in enumerate(f):
                if not line.strip().startswith("#!") and not line.strip().startswith("use") \
                    and not line.strip().startswith("extern crate") and not set:
                    for v in vars:
                        if v not in const:
                            new.write(v + "\n")
                    set = True
                new.write(line)
            f.close()
            new.close()
        os.rename("new.rs", p)         

def format(file):
    fn_total = 0
    with open(file, "r") as f, open("new.rs", "w") as new:
        for i, line in enumerate(f):
            if i == 0 and "#![feature(rustc_private)]" not in line:
                new.write("#![feature(rustc_private)] \n")
            if not line.strip().startswith(";"):
                new.write(line) 
            if line.strip().startswith("fn") or line.strip().startswith("pub fn") \
                or line.strip().startswith("unsafe fn"):
                if "(" in line:
                    fn_total += 1
        f.close()
        new.close()
    os.rename("new.rs", file)
    return fn_total

def count_total_fns():
    w = wksp()
    crates = os.listdir(w.m_report)

    for crate in crates:
        crate = crate.replace(".json", "")
        tmp = os.path.join(w.tmp, crate)

        fn_total = 0
        for file in rn.get_file(tmp, []):
            fn_total += format(file)
        
        with open(os.path.join(w.m_report, crate + ".json"), "r") as f_, open("new.rs", "w") as new:
            f = json.load(f_)
            f["fn_total"] = fn_total

            f = json.dumps(f)
            new.write(f)
            f_.close()
            new.close()
        os.rename("new.rs", os.path.join(w.m_report, crate + ".json"))

    
    for crate in os.listdir(w.m_rerun):
        os.remove(os.path.join(w.m_report, crate))

if __name__ == "__main__":
    count_total_fns()
            

    

