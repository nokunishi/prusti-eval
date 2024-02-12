import os, sys, json

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w

cwd = os.getcwd()


# TODO: import this in the mir.py file
def summary():
    mirs = os.listdir(w.m)
    
    for m in mirs:
        with open(os.path.join(w.m, m), "r") as f:
            f = json.load(f)
            t_fn = 0
            t_panic = 0
            t_rn = 0
            t_rns = [] 
            
            for f_name in f["results"].keys():
                fns = f["results"][f_name]
                
                for fn in fns:
                    name = fn["fn_name"]
                    num_total = fn["num_total"]
                    num_reasons = fn["num_reasons"]
                    reasons = fn["reasons"]





if __name__ == "__main__":
    main()