import pandas as pd, os, sys
from w import wksp

w = wksp()

def csv_rust(dir):
    d = os.path.join(w.r_r)
    recent = os.listdir(d)[0]
    df = pd.read_json(os.path.join(d, recent))



def main():
    csv_rust()
            

if __name__ == "__main__":
    main()