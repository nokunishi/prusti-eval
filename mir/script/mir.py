import os, sys, json, shutil
import mir_tmp as mt, mir_wksp as mw

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

def write_all():
    w = wksp()
   
    mir_dir = os.listdir(w.m)
    
    for m in mir_dir:
        if os.path.exists(os.path.join(w.m_report, m)):
            print("mir report for " + m + " already exists")
            continue
        else:
            print("writing mir report for " + m + "...")
            mw.summary_wksp(m)    


def main():
    args = []
    for arg in sys.argv:
        if "--" not in arg:
            args.append(arg)

    if "--wr" in sys.argv and "--a" in sys.argv:
        write_all()
        return
    if "--r" in sys.argv:
        mirs = mt.get_paths("/tmp/" + args[1], [])
        mt.summary_tmp(args[1], mirs)
    else:
        mirs = mt.get_paths("/tmp/" + args[1], [])
        mt.summary_tmp(args[1], mirs)
        mw.summary_wksp(args[1] + ".json", -1)

if __name__ == "__main__":
    main()
  
