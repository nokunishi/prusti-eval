import os, shutil
from w import wksp

w = wksp()


#  TODO: automate installing Prusti when not found in target/debug
def no_prusti():
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

if __name__ == "__main__":
    for c in no_prusti():
        os.remove(os.path.join(w.d_a, c))
        print("removing " + c + " in data/archive")


        p = os.path.join(w.p_c, c.replace(".txt", ".json"))
        if os.path.exists(p):
            os.remove(p)
            print("removing " + c + " in prusti/crates")






        