import os
import sys
import shutil
import uuid
import json

tmp_dir = os.listdir("/private/tmp")
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir_path = os.path.join(parent_dir, "log")
archive_dir_path = os.path.join(log_dir_path, "archive")
rerun_dir_path = os.path.join(log_dir_path, "rerun_archive")
panic_dir_path = os.path.join(log_dir_path, "panic_report")
err_dir_path = os.path.join(log_dir_path, "err_report")

def rerun():
    if len(sys.argv) < 2:
        print("incorrect number of args")
        return

    rerun_crates = [];

    panic_dir = os.listdir(panic_dir_path)
    reran_archive = os.listdir(rerun_dir_path)
    archived = os.listdir(archive_dir_path)

    for paniced in panic_dir:
        paniced_ = paniced[:-3] + "crate"
        if paniced_ not in tmp_dir and ".DS" not in paniced_:
            print(paniced_ + " not in /tmp file")
        else:
            if paniced not in reran_archive:
                rerun_crates.append(paniced)
    
    """rerun on a specific crate"""
    done = False
    for arg in sys.argv:
        if ".txt" in arg:  
            print("rerunning on: " +  arg)
            os.system("python3 ./x.py run --bin run_prusti clippy &> " + rerun_dir_path + "/" + arg + " " + arg)
            done = True

    if done:
        return

    i = 0
    num = int(sys.argv[1])

    while i < num and i < len(rerun_crates):
        print("rerunning on: " +  rerun_crates[i])
        os.system("python3 ./x.py run --bin run_prusti clippy &> " + rerun_dir_path + "/" + rerun_crates[i] + " " + rerun_crates[i])
        i += 1

def truncate_panic_dir():
    panic_dir = os.listdir(panic_dir_path)
    panic_summary_path = os.path.join(log_dir_path, "panic_summary")
    uuid_str = str(uuid.uuid4())
    paniced_crates = []
    sampled = False
    for panic in panic_dir:
        if ".DS" not in panic:
            paniced_crates.append(panic)
        if not sampled:
            os.rename(os.path.join(panic_dir_path, panic), os.path.join(panic_summary_path, "sample-" + uuid_str + ".txt"))
            sampled = True

    with open(os.path.join(panic_summary_path, "sample-" + uuid_str + ".json"), "a") as outfile:
        print("truncating panic_report dir ..")
        obj = {
            "paniced_crates": paniced_crates,
            "num_crates": len(paniced_crates)
        }
        outfile.write(json.dumps(obj))

def replace_err_report():
    archived = os.listdir(archive_dir_path)
    reran_crates = os.listdir(rerun_dir_path)

    for crate in reran_crates:
        if crate in archived:
            print("replacing old error report for " + crate[:-3] + " with new")
            os.rename(os.path.join(rerun_dir_path, crate), os.path.join(archive_dir_path, crate))

def main():
    if "--d" in sys.argv:
       shutil.rmtree(panic_dir_path)
       os.mkdir(panic_dir_path)
       return
    if "--t" in sys.argv:
        truncate_panic_dir()
        return
    if "--rp" in sys.argv:
        if len(sys.argv) <= 2:
            print("incorrect number of arg for --rp")
            return
        if "-y" in sys.argv:
            truncate_panic_dir()
            replace_err_report()
        if "-n" in sys.argv:
            replace_err_report()
        return

    if "--quick" in sys.argv:
        panic_dir = os.listdir(panic_dir_path)
        reran_crates = os.listdir(rerun_dir_path)
        print(str(len(panic_dir) - len(reran_crates)) + " more crates to rerun")
        return

    if "--z" in sys.argv:
        archived = os.listdir(archive_dir_path)
        zipped_dist = os.path.join(log_dir_path, "zipped", 'archive_' + str(len(archived)) + "_" + str(uuid.uuid4()))
        shutil.make_archive(base_name=zipped_dist, format='zip', root_dir=archive_dir_path)
        return

    rerun()
  
if __name__ == '__main__':
    main()

