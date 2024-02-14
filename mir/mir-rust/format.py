import os, sys, shutil, shutil
from pathlib import Path

cwd = os.getcwd()

def format(file):
    with open(file, "r") as f, open("new.rs", "w") as new:
        cfg = False
        imports = []

        for i, line in enumerate(f):
            if i == 0 and "#![feature(rustc_private)]" not in line:
                new.write("#![feature(rustc_private)] \n")
            if cfg:
                if "use" in line:
                    words = line.split(" ")[1].split("::")
                    crate = words[0]
                    l_ = "extern crate " + crate + "; \n"
                    if l_ not in imports:
                        imports.append(l_)
                        new.write(l_)
            if '#![cfg(feature = "std")]' in line:
                cfg = True    
                continue        
            new.write(line)
        f.close()
        new.close()
    os.rename("new.rs", file)

if __name__ == "__main__":
    format(sys.argv[1])
            

    

