import os
import pandas as pd
import csv


parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir = os.path.join(parent_dir, "./log")
err_report_dir = os.path.join(log_dir, "./err_report")
summary_csv_path = os.path.join(log_dir, "summary.csv")

def download():
    os.system("python3 ./x.py run --bin setup_crates err_report") 


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
def count_num_fn(name, paths):
    total_fns = 0;
    total_num_lines = 0;

    for path in paths:
        with open(path, "r") as f:
            for l_no, line in enumerate(f):
                if "fn" in line:
                    total_fns += 1;

            total_num_lines += l_no
            
    
    data = {"Crate-Version": name, 
            "Total Number of Lines": total_num_lines, 
            "Total Number of Functions": total_fns}

    df = pd.DataFrame([data])
    df.to_csv(summary_csv_path, mode = "a", index=False, header = not os.path.isfile(summary_csv_path))
    

def run():
    crates = os.listdir(err_report_dir);
    for crate in crates:  
        crate = crate[:-5]  
        
        count_num_fn(crate, get_file("./" + crate, []))


download()
