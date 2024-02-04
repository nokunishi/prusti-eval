import os, shutil, sys

cwd = os.getcwd()


def get_file(path, file_lists):
    dir_list = os.listdir(path)

    for dir in dir_list:
        dir_path = os.path.join(path, dir)

        if os.path.isdir(dir_path):
            get_file(dir_path, file_lists)
        if ".rs" in dir and dir_path not in file_lists:
            file_lists.append(dir_path)

    return file_lists

def run(crate):
    crate_path= os.path.join("/tmp/" + crate)

    fns = []
    main = False

    files = get_file(crate_path, [])

    for file in files:
        paths = file.split("/")

        for i in range(0, len(paths)):
            if ".rs" in paths[i]:
                file_ = paths[i]
                break
        
        path = crate_path + "/" +  paths[i-1]
        if not os.getcwd() == path:
            os.chdir(path)
            os.system("cargo clean")

        print(os.getcwd())
        with open(file_, "r") as f:
            for l_no, line in enumerate(f):
                if "fn" in line:
                    names = line.split(" ")
                    for name in names:
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
            with open(file_, "a") as f: 
                f.write("fn main(){}")

        for fn in fns:
            os.system("cargo clean")
            os.system('rustc -Z dump-mir="' + fn + ' & built" ' + file_)

def read_mir(crate):
    mir_dump = path + "/mir_dump"

    panic = []
    panic_reason = []

    mir_files = get_file(mir_dump, [])

    for m in mir_files:
        with open(mir_dump, "r") as f:
            for l_no, line in enumerate(f):
                if "assert!(" in line:
                    panic.append(line)

                    reasons = line.split('"')
                    print(reasons[1])

    obj = {
        "name": crate,
        "num_lines": len(crate),
        "panic": panic,
    }
    return
    with open(cwd + "/mir_dump", "w") as f:
        print("hi")


def main():
    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    if "-a" in sys.argv:
        print("hi")
    else: 
        run(sys.argv[1])


if __name__ == "__main__":
    main()