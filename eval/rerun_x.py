import os, sys, shutil, json, datetime

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w

def rerun_all():
    tmp = os.listdir(w.tmp)
    crates = [];

    c_reports = os.listdir(w.c_report)
    reran_crates = os.listdir(w.r)

    for paniced in c_reports:
        paniced_ = paniced[:-3] + "crate"
        if paniced_ not in tmp and ".DS" not in paniced_:
            print(paniced_ + " not in /tmp file")
        else:
            if paniced not in reran_crates:
                crates.append(paniced)

    i = 0
    num = int(sys.argv[1])

    while i < num and i < len(crates):
        print("rerunning on: " +  crates[i])
        os.system("python3 ./x.py run --bin run_prusti clippy &> " + w.r + "/" + crates[i] + " " + crates[i])
        i += 1

def rerun():
    for arg in sys.argv:
        if ".txt" in arg:  
            print("rerunning on: " +  arg)
            os.system("python3 ./x.py run --bin run_prusti  -- --Z dump-mir=with_ordinal clippy &> " + 
                      w.r + "/" + arg + " " + arg)


def truncate_p():
    c_reports = os.listdir(w.c_report)
    date = str(datetime.datetime.now())
    panicked = []
    sampled = False

    for p in c_reports:
        if ".DS" not in p:
            panicked.append(p)
        if not sampled:
            os.rename(os.path.join(w.c_report, p), os.path.join(w.c_summary, "sample-" + date + ".txt"))
            sampled = True

    with open(os.path.join(w.c_summary, "sample-" + date + ".json"), "a") as outfile:
        print("truncating panic_report dir ..")
        obj = {
            "paniced_crates": panicked,
            "num_crates": len(panicked)
        }
        outfile.write(json.dumps(obj))

def replace_err():
    archived = os.listdir(w.a)
    reran_crates = os.listdir(w.r)

    for crate in reran_crates:
        if crate in archived:
            print("replacing old error report for " + crate[:-3] + " with new")
            os.rename(os.path.join(w.r, crate), os.path.join(w.a, crate))

def main():
    if len(sys.argv) < 2:
        print("incorrect number of args")
        return
    
    if "--d" in sys.argv:
       shutil.rmtree(w.c_report)
       os.mkdir(w.c_report)
       return
    if "--t" in sys.argv:
        truncate_p()
        return
    if "--rp" in sys.argv:
        response = input("Truncate panic_report dir? (y or n) :")

        if "y" == response:
            truncate_p()
            replace_err()
        if "n" == response:
            replace_err()
        return

    if "--report" in sys.argv:
        panic_dir = os.listdir(w.c_report)
        reran_crates = os.listdir(w.r)
        print(str(len(panic_dir) - len(reran_crates)) + " more crates to rerun")
        return

    if "--z" in sys.argv:
        archived = os.listdir(w.a)
        zipped_dist = os.path.join(w.z, 'archive_' + str(len(archived)) + "_" + str(datetime.datetime.now()))
        shutil.make_archive(base_name=zipped_dist, format='zip', root_dir= w.a)
        return

    if "--s" in sys.argv:
        rerun()
        return

    if "--a" in sys.argv:
        rerun_all()
        return
  
if __name__ == '__main__':
    main()

