import os, sys, shutil, shutil
from pathlib import Path

cwd = os.getcwd()

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

def handle_mod(file, mod):
    line = ""
    parent =  Path(file).parent.absolute()

    dirs = get_dirs(parent, [])

    for dir in dirs:
        if mod in dir:
            return "use super::" + mod + ";\n"
    return ""

def format(crate, file):
    with open(file, "r") as f, open("new.rs", "w") as new:
        imports = []
        for i, line in enumerate(f):
            if i == 0 and "#![feature(rustc_private)]" not in line:
                new.write("#![feature(rustc_private)] \n")
            if line.strip().startswith("use") and not comment(line):
                crate = line.split(" ")[1].split("::")[0]
                l_ = "extern crate " + crate + "; \n"
                if l_ not in imports and "std" not in crate and "core" not in crate \
                    and "crate" != crate and l_ != "":
                    imports.append(l_)
                    new.write(l_)
            if '#![cfg(feature = "std")]' in line:
                continue     
            if "use std;" == line.strip():
                continue
            if line.strip().startswith("mod"):
                mod = line.split(" ")[1].replace(";", "").strip()
                l_ = handle_mod(file, mod)
                if l_ != "":
                    new.write(l_)
                    continue
            new.write(line)
        f.close()
        new.close()
    os.rename("new.rs", file)

if __name__ == "__main__":
    format(sys.argv[1])
            

    

