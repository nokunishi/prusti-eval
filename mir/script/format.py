import os, sys, shutil, shutil
from pathlib import Path

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


def fix_c_err1(crate, imports):
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
                
                new.write(line)
            f.close()
            new.close()
        os.rename("new.rs", file)

def format(crate, file):
    with open(file, "r") as f, open("new.rs", "w") as new:
        imports = []
        for i, line in enumerate(f):
            if i == 0 and "#![feature(rustc_private)]" not in line:
                new.write("#![feature(rustc_private)] \n")
            if line.strip().startswith("extern crate"):
                if "as" in line:
                    i1 = line.split(" as ")[0].strip() + "\n"
                    i2 = "extern crate " + line.split(" as ")[1].strip() + "\n"
                    print(i2)
                    imports.append(i1)
                    imports.append(i2)
                else:
                    imports.append(line.strip() + "\n")
            if line.strip().startswith("use") and not comment(line):
                if "::" not in line:
                    continue
                else:
                    crate = line.split(" ")[1].split("::")[0]
                    l_ = "extern crate " + crate + ";\n"
                    if l_ not in imports and "std" not in crate and "core" not in crate \
                        and "crate" != crate and crate != "" and crate :
                        imports.append(l_)
                        new.write(l_)
            if '#![cfg(feature = "std")]' in line:
                continue     
            if "use std;" == line.strip():
                continue
            if not line.strip().startswith(";"):
                new.write(line)
        f.close()
        new.close()
    os.rename("new.rs", file)
    return imports

if __name__ == "__main__":
    format(sys.argv[1])
            

    

