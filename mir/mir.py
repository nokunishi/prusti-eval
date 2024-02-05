import os, sys, json, datetime, shutil
from pathlib import Path
import threading

p_eval = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
eval_dir = os.path.join(p_eval, "eval")
cwd = os.getcwd()

wk = os.path.abspath(os.path.join(p_eval, os.pardir))
wk_dir = os.path.join(wk, "workspace")
mir_dir = os.path.join(wk_dir, "mir")


date_ = str(datetime.datetime.now()).split(" ")
date = date_[0] + "-" + date_[1]

lock = threading.Lock()


def get_file(path, file_lists):
    dir_list = os.listdir(path)

    for dir in dir_list:
        dir_path = os.path.join(path, dir)

        if os.path.isdir(dir_path):
            file_lists = get_file(dir_path, file_lists)
        if ".rs" in dir and dir_path not in file_lists:
            file_lists.append(dir_path)

    return file_lists

def setup_tmp():
    lock.acquire()
    os.chdir(eval_dir)
    os.system("python3 run_x.py --e",)
    lock.release()

def setup(crate, file):
    crate_path= os.path.join("/tmp/" + crate)
    paths = file.split("/")

    for i in range(0, len(paths)):
        if ".rs" in paths[i]:
            file_ = paths[i]
            break

    path = crate_path + "/" +  paths[i-1]
    if not Path(path).exists():
        print(path)
        print("path does not exists")
        return "", ""

    if not os.getcwd() == path:
        os.chdir(path)
    return Path(file).parent.absolute(), file_


def get_fns(file):
    lock.acquire()
    fns = []

    with open(file, "r") as f, open("new", "w") as f_:
        for line in f:
            if "fn" in line:
                names = line.split(" ")
                for name in names:
                    if "(" in name in name:
                        for i in range(0, len(name)):
                            if name[i] == "(":
                                break
                    
                        index = len(name) - i
                        name = name[:-index] 

                        if name not in fns:
                            fns.append(name)
                        
            if "try!" in line and "r#try!" not in line:
                words = line.split(" ")

                if 
            else:
                f_.write()

        if "main" not in fns:
            f_.write("fn main(){} \n")
            fns.append("main")
        f.close()
        f_.close()
    shutil.move(file, "new")
    lock.release()
    return fns

def extract(file):
    fns = get_fns(file)
    lock.acquire()
    for fn in fns:
        print("extracting mir on " + file + " for " + fn)
        os.system('rustc --edition 2021 -Z dump-mir="' + fn + ' & built" ' + file) 

        mir_dump = os.path.join(os.getcwd(), "mir_dump")
        shutil.move(mir_dump, os.path.join(cwd, "mir_dump"))
    lock.release()

def read(crate, path):
    mir_dump = os.path.join(path, "mir_dump")
    panic = []
    reasons = []

    if not Path(mir_dump).exists():
        print("mir_dump does not exist")
        return

    mir_files = os.listdir(mir_dump)

    if len(mir_files) == 0:
        print("no mir files produced")
        return

    for m in mir_files:
        m = os.path.join(mir_dump,  m)
        with open(m, "r") as f:
            for l_no, line in enumerate(f):
                if "assert(!" in line:
                    panic.append(line)
                    
                    w = line.split('"')[1]
                    if not w in reasons:
                        reasons.append(w)

    obj = {
        "num_total": len(panic),
        "num_reasons": len(reasons),
        "reasons": reasons
    }

    m_fs = os.listdir(mir_dir)
    m_f = os.path.join(mir_dir, date + ".json")
    if m_f in m_fs:
        with open(os.path.join(mir_dir, date + ".json")  , "r") as f:
            f = json.load(f)
            if crate in f["results"]:
                f["results"] = obj
            else:
                f["results"][crate] = obj
    else:
        f = {}
        results = {}
        results[crate] = obj
        f["results"] = results
    
    f = json.dumps(f)
    with open(os.path.join(mir_dir, date + ".json")  , "a") as f_:
        print("writing to jsons...")
        f_.write(f)
        return
    

def run(crate):
    crate_path= os.path.join("/tmp/" + crate)
    os.system("cargo clean")
    os.chdir(Path(crate_path))

    lock.acquire()
    os.system("cargo build")
    lock.release()
    os.chdir(cwd)

    files = get_file(crate_path, [])

    for f_ in files:
        p, f = setup(crate, f_)
        
        if p == "" or f == "":
            continue
        if "--r" not in sys.argv:
            extract(f)
        read(crate, p)  


def main():
    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    if "mir" not in os.listdir(wk_dir):
        os.mkdir(os.path.join(wk_dir, "mir"))

    setup_tmp()
    os.chdir(cwd)

    try:
        n = int(sys.argv[1])
    except:
        n = 0
    
    if n != 0:
        tmps = os.listdir("/tmp")

        for i in range(0, n):
            if ".crate" in tmps[i]:
                crate = tmps[i][:-6]
                print("Running on :" + crate)
                run(crate)
        return
    if "--a" in sys.argv:
        tmps = os.listdir("/tmp")
        for tmp in tmps:
            if ".crate" in tmp:
                crate = tmp[:-6]
                print("Running on :" + crate)
                run(crate)
        return
    else:
        for arg in sys.argv:
            if not arg == "mir.py" and not "--" in arg:
                crate = arg
        run(crate)
        return
    

            

    


if __name__ == "__main__":
    main()