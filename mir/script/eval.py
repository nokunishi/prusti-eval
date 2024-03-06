import os, sys, threading, json
from run import prusti_panicked

cwd = os.getcwd()
lock = threading.Lock()

unreachable = 'const "internal error: entered unreachable code")'

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w


def get_lns(crate, fn):

    with open(crate, "r") as f_:
        f = f_.readlines()
        i = 0

        while i < len(f):
            if "fn " + fn + "(" in f[i] or "fn " + fn + "<" in f[i] :
                 start, j = i, i

                 while j < len(f):
                     if "}" in f[j]:
                         end = j + 1
                         break
                     else:
                         j += 1
            i += 1
        f_.close()
    return start, end

def equal(r, r_p):
    if "add" in r_p and "+" in r:
        return True
    if "subtract" in r_p and "-" in r:
        return True
    if "multiply" in r_p and "*" in r:
        return True
    if "divide" in r_p and "/" in r:
        return True
    if "remainder" in r_p and "remainder" in r:
        return True
    if "unreachable!(..)" in r_p and unreachable in r:
        return True
    if "panic!(..)" in r_p and 'const "explicit panic"' in r:
        return True
    if "index" in r_p and "index" in r:
        return True
    else:
        return False


def prusti_err(err):
    p_lines = []

    with open(err, "r") as e:
        prusti_errs = json.load(e)["verification_failed_reason"]

        for k in prusti_errs:
            for line in  prusti_errs[k]:
                p_lines.append({
                    [*line.keys()][0]: k
                })
        e.close()
    return p_lines


def compare(mir, p_lines):
    w = wksp()
    eq = []
    ne = []

    with open(mir, "r") as m:
        mir_panics = json.load(m)["panicked_rn"]

        for obj in mir_panics:
            r = [*obj.keys()][0]
            for l in obj[r]:
                file = l["path"].split(":")[0]
                fn = l["fn"].split("-")[1]
        
                start =  int(l["path"].split(file + ":")[1].split(" ")[0].split(":")[0])
                end =  int(l["path"].split(" ")[1].split(":")[0])

                if start == end:
                    tmp = os.path.join(w.tmp, mir.split("/")[-1].replace(".json", ""), file)
                    start, end = get_lns(tmp, fn)

                for p in p_lines:
                    file_p = [*p.keys()][0].split(":")[0]
                    line = int([*p.keys()][0].split(":")[1])
                    r_p = p[[*p.keys()][0]]

                    if start <= line and line <= end and file_p == file:
                        if equal(r, r_p):
                            inlist = False
                            for obj in eq:
                                if [*obj.keys()][0] == r:
                                    obj[r].append({"fn": fn, "path": l["path"]})
                                    inlist = True

                            if not inlist:
                                eq.append(
                                    {r: [{"fn": fn, "path": l["path"]}] })
                        else:
                            ne.append({"fn": fn, "path": l["path"], "mir":r, "prusti": r_p})

                                              

        m.close()
   # with open(os.path.join(w.m_eval, w.date()), "w") as f:
        

                

def run():
    w = wksp()
    mirs = os.listdir(w.m_rprt)
    m_rerun = os.listdir(w.m_rerun)
    panicked = prusti_panicked()

    for mir in mirs:
        if mir in panicked:
            if mir in m_rerun:
                m = os.path.join(w.m_rerun, mir)
            else:
                m = os.path.join(w.m_rprt, mir)

            err = os.path.join(w.p_err, mir)
            if not os.path.exists(err):
                lock.acquire()
                os.chdir(w.p)
                os.system("python3 run_x.py " + mir.replace(".json", ""))
                lock.release()
            
            if 'adler32-1.0.4.json' in mir:
                p_lines = prusti_err(err)
                compare(m, p_lines)
def main():
    w = wksp()

    if not os.path.exists(w.m_eval):
        os.mkdir(w.m_eval)
    run()



if __name__ == "__main__":
    main()