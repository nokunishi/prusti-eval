import os, sys, threading, shutil, json
from pathlib import Path
import mir, format as fm, rerun as rr

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w

cwd = os.getcwd()
root = os.path.abspath(os.path.join(cwd, os.pardir))
mir_rust = os.path.join(root, "mir-rust")
lock = threading.Lock()

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

def reset_all():
    w = wksp()
    shutil.rmtree(w.m_summary)
    shutil.rmtree(w.m_rerun)
    os.chdir(w.p)
    os.system("python3 run_x.py --rs")
    print("reset complete")

def reset(m):
    w = wksp()
    print("removing mir for " + m)
    os.remove(os.path.join(w.m, m + ".json"))
    if os.path.exists(os.path.join(w.m_summary, m + ".json")):
        os.remove(os.path.join(w.m_summary, m + ".json"))
    shutil.rmtree(os.path.join(w.tmp, m))
    os.remove(os.path.join(w.tmp, m + ".crate"))
    os.chdir(w.p)
    os.system("python3 run_x.py --e")

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

def setup_tmp():
    lock.acquire()
    os.chdir(w.p)
    os.system("python3 run_x.py --e",)
    lock.release()

def run_mir(crate, file):
    os.chdir(mir_rust);
    lock.acquire()
    os.system("cargo build")
    fm.format(crate, file)
    lock.release()

    print("extracting mir on " + file)
    e_file = file.replace(".rs", "-e.txt")
    os.system("cargo run " + file + " &> " + e_file)


def run(crate):
    if "--d" not in sys.argv:
        crate_path= os.path.join("/tmp/" + crate)
        files = get_file(crate_path, [])

        os.system("cargo clean")
        os.chdir(Path(crate_path))
        os.system("cargo build")
    else:
        files = [crate]
        mirs = []

    for f in files:
        run_mir(crate, f)

    if "--d" not in sys.argv:
        mirs = mir.get_paths(crate_path, [])

    mir.summary_tmp(crate, mirs)
    mir.summary_wksp(crate + ".json")
    
   

def main():
    if "mir" not in os.listdir(w.tmp):
        os.mkdir(w.m)
    if not os.path.exists(w.m_summary):
        os.mkdir(w.m_summary)
    if not os.path.exists(w.m_rerun):
        os.mkdir(w.m_rerun)

    tmps = os.listdir(w.tmp)
    mirs = os.listdir(w.m)

    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    if "--rs" in sys.argv:
        if "--a" in sys.argv:
            reset_all()
            return
        if "--" not in sys.argv[1]:
            crate = sys.argv[1]
        else:
            crate = sys.argv[2]
        reset(crate)
        return

    setup = True
    for tmp in tmps:
        if ".crate" in tmp:
            setup = False

    if setup:
        setup_tmp()
        os.chdir(cwd)
        tmps = os.listdir(w.tmp)

    try:
        args = []
        for arg in sys.argv:
            if "--" not in arg:
                args.append(arg)
        n = int(args[1])
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
                    if "--run" not in sys.argv and rr.rerun(crate):
                        sys.argv.append("--rerun")
                        run(crate)
                    else:
                        print("no need to rerun")
            else:
                n += 1
            if "--rerun" in sys.argv:
                sys.argv.remove("--rerun")
            i += 1
        return 
    else:
        for arg in sys.argv:
            if ".py" not in arg and not "--" in arg:
                print("Running on :" + arg)
                run(arg)
                if "--run" not in sys.argv and rr.rerun(arg):
                        sys.argv.append("--rerun")
                        run(arg)
                else:
                    print("no need to rerun")
            if "--rerun" in sys.argv:
                sys.argv.remove("--rerun")
        return 
    

if __name__ == "__main__":
    main()