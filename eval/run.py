import os
from w import wksp

def setup():
    if not os.path.exists(w.r_dir):
        os.mkdir(w.r_dir)
    if not os.path.exists(w.r_e):
        os.mkdir(w.r_e)
    if not os.path.exists(w.r_s):
        os.mkdir(w.r_s)

if __name__ == "__main__":
    w = wksp()
    setup()