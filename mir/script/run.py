import os, sys, threading, shutil, json
from pathlib import Path
import mir_tmp as mt, mir_wksp as mw
import format as fm,  collect as c
from w import wksp


cwd = os.getcwd()
w = wksp()
lock = threading.Lock()

def setup():
    if not os.path.exists(w.m):
        os.mkdir(w.m)
    if not os.path.exists(w.m_dir):
        os.mkdir(w.m_dir)
    if not os.path.exists(w.m_s):
        os.mkdir(w.m_s)
    if not os.path.exists(w.m_rprt):
        os.mkdir(w.m_rprt)
    if not os.path.exists(w.m_rerun):
        os.mkdir(w.m_rerun)

def setup_tmp():
    lock.acquire()
    os.chdir(w.p)
    os.system("python3 run_x.py --cr",)
    lock.release()

def reset_all():
    shutil.rmtree(w.m_rprt)
    shutil.rmtree(w.m_rerun)
    os.chdir(w.p)
    os.system("python3 run_x.py --rs")
    print("reset complete")

def reset(m):
    print("removing mir for " + m)
    os.remove(os.path.join(w.m, m + ".json"))
    if os.path.exists(os.path.join(w.m_rprt, m + ".json")):
        os.remove(os.path.join(w.m_rprt, m + ".json"))
    shutil.rmtree(os.path.join(w.tmp, m))
    os.remove(os.path.join(w.tmp, m + ".crate"))
    os.chdir(w.p)
    os.system("python3 run_x.py --e")

def get_mir(file):
    p = os.path.abspath(os.path.join(cwd, os.pardir))
    os.chdir(os.path.join(p, "mir-rust"))
    lock.acquire()
    os.system("cargo build")
    fn, line = fm.format(file)
    lock.release()

    print("extracting mir on " + file)
    e_file = file.replace(".rs", "-e.txt")
    os.system("cargo run " + file + " &> " + e_file)

    return fn, line

def mir(crate):
    crate_path= os.path.join("/tmp/" + crate)
    files = c.get_file(crate_path, [])

    os.system("cargo clean")
    os.chdir(Path(crate_path))
    os.system("cargo build")

    fn_total = 0
    ln_total = 0

    for f in files:
        fn, ln = get_mir(f)
        fn_total += fn
        ln_total += ln

    mirs = mt.get_paths(crate_path, [])
    mt.summary_tmp(crate, mirs)
    mw.summary_wksp(crate + ".json", fn_total, ln_total)

  
def rerun(crate):
    w = wksp()
    if not crate.strip().endswith(".json"):
        crate += ".json"

    vars = c.global_var(crate)
    
    for var in vars:
        k = [*var.keys()][0]
        fm.set_var(k, var[k])   

    imports = c.imports(os.path.join(w.m_rprt, crate))
    fm.fix_c_err(imports)

    if len(imports) == 0 and len(vars) == 0:
        return False
    else:
        return True
   
def run(n, list): 
    mirs = os.listdir(w.m_rprt)
    
    if n > 0:
        i = 0
        while i < n:
            if "--pr" in sys.argv or "--cr" in sys.argv:
                crate = list[i].replace(".json", "")
                run = True
                rerun = False
            elif ".crate" in list[i]:
                crate = list[i].replace(".crate", "")
                run = True
                rerun = False
            else:
                crate = list[i]
                run = True
                rerun = True
            if run:
                if  crate + ".json" in mirs and not rerun:
                    print("mir file for " + crate + " already exists")
                    n += 1
                else:
                    print("Running on :" + crate)
                    mir(crate)
                    #if "--run" not in sys.argv and rerun(crate):
                    #    sys.argv.append("--rerun")
                    #    mir(crate)
                    #else:
                    #    print("no need to rerun")
            else:
                n += 1
            #if "--rerun" in sys.argv:
            #    sys.argv.remove("--rerun")
            i += 1
        return 
    else:
        for arg in sys.argv:
            if ".py" not in arg and not "--" in arg:
                print("Running on :" + arg)
                mir(arg)
                #if "--run" not in sys.argv and rerun(arg):
                #    sys.argv.append("--rerun")
                #    mir(arg)
                #else:
                #    print("no need to rerun")
            #if "--rerun" in sys.argv:
            #    sys.argv.remove("--rerun")
        return 

def main():
    if len(sys.argv) < 2 or sys.argv[1].isdigit():
        print("num of mir " + str(len(os.listdir(w.m_rprt))))
        print("num of prusti " + str(len(os.listdir(w.p_c))))
        return
    
    setup()
    tmps = os.listdir(w.tmp)
    
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

    if "--cl":
        setup_tmp()

    j = 0
    while j < len(sys.argv):
        try:
            n = int(sys.argv[j])
            break
        except:
            j += 1
            n = 0

    if "--pr" in sys.argv:
        if n == 0:
            run(len(c.prusti_err()), c.prusti_err())
            return
        else:
            run(n, c.prusti_err())
            return

    if "--tmp" in sys.argv:
        if "--a" in sys.argv:
            run(len(tmps), tmps)
            return
        else:
            run(n, tmps)
            return
    if "--cr" in sys.argv:
        fs = os.listdir(w.p_c)
        if "--a" in sys.argv:
            run(len(fs), fs)
            return
        else:
            run(n, fs)
            return
    else:
        run(1, [sys.argv[1]])

if __name__ == "__main__":
    main()