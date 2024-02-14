import os, sys, threading, json
from pathlib import Path
import  eval

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w

cwd = os.getcwd()
root = os.path.abspath(os.path.join(cwd, os.pardir))
mir_rust = os.path.join(root, "mir-rust")
lock = threading.Lock()



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

def run_mir(file):
    try:
        os.chdir(mir_rust);
        lock.acquire()
        os.system("cargo build")
        lock.release()

        print("extracting mir on " + file)
        os.system("cargo run " + file)
    except:
        print("his")
        fm.format(file)
        raise Exception("debug")

def read_mir(crate, file):
    eval.extract_summary(crate, file)

def run(crate):
    crate_path= os.path.join("/tmp/" + crate)
    os.system("cargo clean")
    os.chdir(Path(crate_path))
    os.system("cargo build")

    files = get_file(crate_path, [])

    for f in files:
        try: 
            run_mir(f)
            read_mir(crate, f)
        except Exception as str:
            print(str)
            return

    os.chdir(cwd)

def debug(f):
    try: 
        run_mir(f)
        read_mir("debug", f)
    except Exception as str:
        print(str)
        return

def main():
    tmps = os.listdir(w.tmp)
    mirs = os.listdir(w.m)

    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    if "mir" not in os.listdir(w.dir):
        os.mkdir(w.m)

    if "--tmp" in sys.argv:
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
        if "--d" not in sys.argv:
            run(crate)
        else:
            debug(crate)
        return
    

if __name__ == "__main__":
    main()