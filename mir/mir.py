import os, sys, json, datetime, shutil
from pathlib import Path
import pandas as pd, csv
import threading

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w

cwd = os.getcwd()


date_ = str(datetime.datetime.now()).split(" ")
date = date_[0] + "-" + date_[1]

lock = threading.Lock()

class Stat:
    file_names = {}



def get_file(path, file_lists):
    dir_list = os.listdir(path)

    for dir in dir_list:
        dir_path = os.path.join(path, dir)

        if not os.path.isfile(dir_path):
            file_lists = get_file(dir_path, file_lists)
        elif ".rs" in dir_path and dir_path not in file_lists:
            file_lists.append(dir_path)

    return file_lists

def setup_tmp():
    lock.acquire()
    os.chdir(w.p_eval)
    os.system("python3 run_x.py --e",)
    lock.release()

def setup(crate, file):
    crate_path= os.path.join("/tmp/" + crate)
    paths = file.split("/")

    for i in range(0, len(paths)):
        if ".rs" in paths[i]:
            file_ = paths[i]

    parent = Path(file).parent.absolute()

    if not os.getcwd() == parent:
        os.chdir(parent)
    return parent, file_

def format(line):
    if "use" in line:
        if "crate::Builder" in line:
            line = line.replace("crate::Builder", "std::thread::Builder")
        if "crate::error" in line:
            line = line.replace("crate::error", "core::error")
    if "try" in line:
        line = line.replace("try!", "#rtry!")

    return line

def get_fns(file):
    fns = []

    with open(file, "r") as f, open("new", "w") as f_:
        for l_no, line in enumerate(f):
            if l_no == 0 and "#![feature(rustc_private)]" not in line:
                f_.write("#![feature(rustc_private)]\n")

            if "//" in line or "/*" in line or "*/" in line:
                continue
            if "fn " in line:
                names = line.split(" ")

                for i in range(0, len(names)):
                    if "fn" == names[i]:
                        break

                try:
                    name = names[i+1]
                except:
                    raise Exception(names[i+1] + " out of bounds at: " + (name, file))

                if "<" in name:
                    name = name.split("<")[0]
                    if not name in fns:
                        fns.append(name)
                elif "(" in name:
                    name = name.split("(")[0]
                    if not name in fns:
                        fns.append(name)
            line = format(line)
            f_.write(line + "\n")
        if not "main" in fns:
            f_.write("fn main(){} \n")
            fns.append("main")
        f.close()
        f_.close()
    shutil.move("new", file)
    return fns

def extract(file):
    failed = []
    fns = get_fns(file)
    for fn in fns:
        print("extracting mir on " + file + " for " + fn)
        try:
            os.system('rustc --edition 2021 -Z dump-mir="' + fn + ' & built" ' + file) 
        except:
            print("failed to build " + file)
            failed.push(file)

        """
        mir_dump = os.path.join(os.getcwd(), "mir_dump")
        shutil.move(mir_dump, os.path.join(cwd, "mir_dump"))
        """
    return failed

def read(crate, root_path, s):
    mir_dump = os.path.join(root_path, "mir_dump")
    panic = []
    reasons = []

    if not Path(mir_dump).exists():
        print("mir_dump does not exist")
        return

    mir_files = os.listdir(mir_dump)

    if len(mir_files) == 0:
        print("no mir files produced")
        return

    i = 0

    for m in mir_files:
        m = os.path.join(mir_dump,  m)
        with open(m, "r") as f:
            for l_no, line in enumerate(f):
                if "assert(!" in line:
                    panic.append(line)
                    
                    w = line.split('"')[1]
                    if not w in reasons:
                        reasons.append(w)

        m_ = m.split("/")
        for c in m_:
            if ".mir" in c:
                c = c.split(".")
                file_name = c[0]
                fn_name = c[1]

        obj = {
            "fn_name": fn_name,
            "num_total": len(panic),
            "num_reasons": len(reasons),
            "reasons": reasons
        }

        p = os.path.join(w.m, crate + ".json")

        if os.path.exists(p):
            with open(p, "r") as f:
                f = json.load(f)
                if file_name in f["results"]:
                   if obj not in f["results"][file_name]:
                       f["results"][file_name].append(obj)
                else:
                    f["results"] = {
                        file_name: [obj]
                    }
        else:
            f = {
                "results": {
                    file_name: [obj]
                }
            }
        with open(p, "w") as f_:
            json.dump(f, f_)


    

def run(crate):
    crate_path= os.path.join("/tmp/" + crate)
    os.system("cargo clean")
    os.chdir(Path(crate_path))
  
    lock.acquire()
    os.system("cargo build &> error.txt")  #this might be slowing the program down?
    lock.release()
    os.chdir(cwd)

    files = get_file(crate_path, [])
    s = Stat()

    for f_ in files:
        p, f = setup(crate, f_)
        
        """TODO: test dir have complex import statements"""
        if p == "" or f == "" or p == "test" or p == "tests":
            continue
        if "--r" not in sys.argv:
            try: 
                extract(f)
            except Exception as str:
                print(str)
                p = os.path.join(w.m, crate + ".json")
                if os.path.exists(p):
                    os.remove(p)
        read(crate, p, s)



def main():
    tmps = os.listdir("/tmp")
    mirs = os.listdir(w.m)

    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    if "mir" not in os.listdir(wk_dir):
        os.mkdir(os.path.join(wk_dir, "mir"))

    if "--b" in sys.argv:
        setup_tmp()
        os.chdir(cwd)

    try:
        n = int(sys.argv[1])
    except:
        n = 0
    
    if "--a" in sys.argv:
        n = len(tmps)
    
    if n > 0:
        i = 0
        while i < n:
            if ".crate" in tmps[i]:
                crate = tmps[i][:-6]
                if  crate + ".json" in mirs:
                    print("mir file for " + crate + " already exists")
                    n += 1
                else:
                    print("Running on :" + crate)
                    run(crate)
            else:
                n += 1
            i += 1
        return
    else:
        for arg in sys.argv:
            if not arg == "mir.py" and not "--" in arg:
                crate = arg
        run(crate)
        return
    

            

    


if __name__ == "__main__":
    main()