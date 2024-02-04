import os, shutil

mir_dir = os.getcwd()

if os.getcwd() == mir_dir:
    os.chdir(os.path.join("/tmp/adler32-1.0.4/src"))
    os.system("cargo clean")
    print(os.getcwd())

fns = []
main = False

with open("lib.rs", "r") as f:
    for l_no, line in enumerate(f):
        if "fn" in line:
            names = line.split(" ")
            for name in names:
                print(name)
                if "(" in name in name:
                    for i in range(0, len(name)):
                        if name[i] == "(":
                            break
                    
                    index = len(name) - i
                    name = name[:-index] 
                    
                    if name not in fns:
                        fns.append(name)
                    if "main" in name:
                        main = True

if not main:
    with open("lib.rs", "a") as f: 
        f.write("fn main(){}")

for fn in fns:
    os.system("cargo clean")
    os.system('rustc -Z dump-mir="' + fn + ' & built" lib.rs')

shutil.move("/tmp/adler32-1.0.4/src/mir_dump", mir_dir + "/mir_dump")


"""
try:
    os.system('rustc -Z dump-mir="update_buffer & built" lib.rs')
except:
    print("hello")

"""
"""
with open("lib.rs", "a") as f: 

    for l_no, line in enumerate(f):
        if "fn" in line:
            names = line.split(" ")
            
            for name in names:
                if "(" in name and ":" in name:
                    for i in range(0, len(name)):
                        if name[i] == "(":
                            break
                    
                    index = len(name) - i
                    name = name[:-index] 

                    os.system('rustc -Z dump-mir="' + name + ' & built" lib.rs')

"""