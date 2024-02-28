import os, sys, threading

cwd = os.getcwd()
lock = threading.Lock()

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

def eval(p):
    with open(p, "r") as f:
        for l_no, line in enumerate(f):
            

def mir_to_prusti():
    w = wksp()
    mirs = os.listdir(w.m_report)
    m_rerun = os.listdir(w.m_rerun)

    for mir in mirs:
        e_report = os.path.join(w.err, mir)
        if not os.path.exists(e_report):
            os.chdir(w.p)
            lock.acquire()
            os.system("python3 run_x.py " + mir.replace(".json", ""))
            lock.release()

        if mir in m_rerun:
            p = os.path.join(w.m_rerun, mir)
        else:
            p = os.path.join(w.m_report, p)

        eval(p)
        
        
           

def main():
    mir_to_prusti()



if __name__ == "__main__":
    main()