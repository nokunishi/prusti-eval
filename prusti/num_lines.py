import os, sys, json
import pandas as pd
import csv, datetime

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w


header = "Crate-Version,Number of Lines,Number of Functions";
line_index = 1;
fn_index = 2;

date_ = str(datetime.datetime.now()).split(" ")
date = date_[0] + "-" + date_[1]

summary_csv_path = w.dir + "/line_summary" + "/summary-" + date + ".csv"

def get_file(path, file_lists):
    dir_list = os.listdir(path)

    for dir in dir_list:
        dir_path = os.path.join(path, dir)

        if os.path.isdir(dir_path):
            get_file(dir_path, file_lists)
        if ".rs" in dir and dir_path not in file_lists:
            file_lists.append(dir_path)

    return file_lists


# call get_file first
def count_num_fn(name, paths, report):
    num_fn = 0;
    num_lines = 0;
    fns = panicky_fns(report)
    num_fn_calls = {}
    for fn in fns:
        num_fn_calls[fn] = 0;

    for path in paths:
        with open(path, "r") as f:
            for l_no, line in enumerate(f):
                if "fn" in line:
                    num_fn += 1;
            
                for fn in fns:
                    fn_ = "." + fn
                    if fn_ in line and line.strip().startswith("//"):
                        num_fn_calls[fn] += 1

            num_lines += l_no
   
    data = {"Crate-Version": name, 
            "Number of Lines": num_lines, 
            "Number of Functions": num_fn}
    
    merge = dict()
    merge.update(data)
    merge.update(num_fn_calls)

    df = pd.DataFrame([merge]) 
    row_csv = name + "," + str(num_lines) + "," + str(num_fn)
    
    row_exists = False
    with open(summary_csv_path, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for l_no, line in enumerate(reader):
            if row_csv in line[0]:
                print("summary for " + name + " already exists")
                row_exists = True

    if not row_exists:
        df.to_csv(summary_csv_path, mode = "a", index=False, header = os.path.getsize(summary_csv_path) == 0)

def summary():
    total_num_lines = 0;
    total_num_fns = 0;
    fn_calls = [];
    fn_calls_crates = [];
    
    i = 0

    with open(summary_csv_path, "r") as f:
        reader = csv.reader(f, delimiter="\t")

        for l_no, line in enumerate(reader):
            if l_no == 0:
                cols = line[0].split(",")
                fn_calls = [0] * len(cols)
                fn_calls_crates = [0] * len(cols)
            else:
                if not line == []:
                    row = line[0].split(",")

                    total_num_lines += int(row[line_index])
                    total_num_fns += int(row[fn_index])

                    for j in range(fn_index+1, len(row)):
                        fn_calls[j] += int(row[j])
                        
                        if int(row[j]) > 0:
                            fn_calls_crates[j] += 1
                    i+=1

    merge = dict()
    data = {"Total Number of Crates": i -1,
            "Total Number of Lines": total_num_lines, 
            "Number of Functions": total_num_fns}
    
    merge.update(data)
    for j in range(fn_index+1, len(cols)):
        obj = {cols[j] + ":total": fn_calls[j]}
        merge.update(obj)

    for j in range(fn_index+1, len(cols)):
        obj = {cols[j] + ":num_crates": fn_calls_crates[j]}
        merge.update(obj)

    df = pd.DataFrame([merge])
    df.to_csv(summary_csv_path, mode = "a", index=False, header = True)
    

def panicky_fns(report):
    panicked_fns = [];

    with open(os.path.join(w.p_eval, report), "r") as f:
        f = json.load(f)

        for key in f["panicky_fns"]:
            msgs = f["panicky_fns"][key]["type"]
        
            for msg in msgs:
                fn = msg.split()[1].replace("`", "").split("::")[1]

                if fn not in panicked_fns:
                    panicked_fns.append(fn)
    return panicked_fns
    
def run():
    if len(sys.argv) < 2:
        print("invalid number of args")
        return

    os.system("python3 ./x.py run --bin setup_crates err_report") 

    if not os.path.isfile(summary_csv_path):
        with open(summary_csv_path, "w"):
            print("summary.csv created")

    if "-a" in sys.argv:
        crates = os.listdir("/tmp");
        for crate in crates:  
            if ".crate" not in crate:
                crate_ = crate + ".crate"

                if crate_ in crates: 
                    count_num_fn(crate, get_file("/tmp/" + crate, []), 
                            "log/panic_summary/2024-01-28-12:56:14.194899.json")
    else:
        count_num_fn(sys.argv[2], get_file("/tmp/" + sys.argv[2], []), 
                            "workspace/panic_summary/2024-01-28-12:56:14.194899.json")
        
    summary()
        
run()

