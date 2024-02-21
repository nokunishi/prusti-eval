import os, sys, json
from pathlib import Path
import format as fm

cwd = os.getcwd()

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w


def collect_imports(mir):
    with open(mir, "r") as f_:
        f = json.load(f_)
        imports = []
        files = []

        for err in f["compile_err"]:
            e = [*err][0]
            if len(err[e]["help"]) > 0:
                for help in err[e]["help"]:
                    if  "consider importing" in help:
                        where = err[e]["where"].split(":")[0]
                        help = help.split("importing:")[1].strip()
                            
                        if where in files:
                            i = 0
                            while i < len(imports):
                                k = [*imports[i]][0]
                                if k == where:
                                    imports[i][k].append(help)
                                    break
                                i+= 1
                        else:
                            imports.append({where: [help]})
                            files.append(where)
                
        f_.close()
        return imports
    
def rerun(crate):
     w = wksp()
     imports = collect_imports(os.path.join(w.m_summary, crate))

def main():
    w = wksp()
    mirs = os.listdir(w.m_summary)

    try:
        args = []
        for arg in sys.argv:
            if "--" not in arg:
                args.append(arg)
        n = int(args[1])
    except:
        n = 0

    if "--a" in sys.argv:
        n = len(mirs)
    if n > 0:
        i = 0
        while i < n:
            rerun(mirs[i])
            i += 1
        return 
    else:
        for arg in sys.argv:
            if not arg == "rerun.py" and not "--" in arg:
                rerun(arg)
        return 

main()
