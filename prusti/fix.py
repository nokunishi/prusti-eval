import os, sys, json
from w import wksp

w = wksp()


#  TODO: automate installing Prusti when not found in target/debug
def prusti_not_found():
    delete = []

    for a in os.listdir(w.d_a):
        if a == ".DS_Store":
            continue
        
        with open(os.path.join(w.d_a, a), "r") as f:
            for line in f.readlines():
                if "assertion failed: prusti.exists()" in line and a not in delete:
                    delete.append(a)
            f.close()
    return delete

def fix_prusti():
    for c in prusti_not_found():
        os.remove(os.path.join(w.d_a, c))
        print("removing " + c + " in data/archive")


        p = os.path.join(w.p_c, c.replace(".txt", ".json"))
        if os.path.exists(p):
            os.remove(p)
            print("removing " + c + " in prusti/crates")


def txt_not_found():
    delete = []
    a = os.listdir(w.d_a)
    for c in os.listdir(w.p_c):
        c_a = c.replace(".json", ".txt")
        if c_a not in a:
            delete.append(c)
    return delete

def fix_crates():
    for c in txt_not_found():
        print("deleting crate file for " + c)
        os.remove(os.path.join(w.p_c, c))



def json_not_found():
    delete = []
    c = os.listdir(w.p_c)
    for a in os.listdir(w.d_a):
        a_c = a.replace(".txt", ".json")
        if a_c not in c:
            delete.append(a)
            print(a)

    return delete

def fix_archive():
    for a in json_not_found():
        print("removing " + a)
        os.remove(os.path.join(w.d_a, a))


def fn_zero():
    rprts = os.listdir(w.p_c)
    rerun = []
    for r in rprts:
        with open(os.path.join(w.p_c, r), "r") as f_:
            f = json.load(f_)
            if f["fn_total"] == 0:
                rerun.append(r)

    return rerun

def fix_fn_zero():
    rerun = fn_zero()

    for r in rerun:
        os.remove(os.path.join(w.d_a, r.replace(".json", ".txt")))
        os.remove(os.path.join(w.p_c, r))


def main():
    if len(sys.argv) < 2:
        print("size of w/data/archive: " + str(len(os.listdir(w.d_a))))
        print("size of w/prusti/crates: " + str(len(os.listdir(w.p_c))))
        return
    if "--p" in sys.argv:
        fix_prusti()
        return 
    if "--c" in sys.argv:
        fix_crates()
        return
    if "--a" in sys.argv:
        fix_archive()
        return
    if "--z" in sys.argv:
        print(len(fn_zero()))
        return

if __name__ == "__main__":
    main()



        