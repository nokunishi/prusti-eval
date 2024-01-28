import os
import pandas as pd
import csv
import datetime



header = ["Crate-Version,Number of Lines,Number of Functions"];
line_index = 1;
fn_index = 2;

date_ = str(datetime.datetime.now()).split(" ")
date = date_[0] + "-" + date_[1]
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir = os.path.join(parent_dir, "./log")
err_report_dir = os.path.join(log_dir, "./err_report")
summary_csv_path = log_dir + "/lines_summary" + "/summary-" + date + ".csv"


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
    num_fn = 0;
    num_lines = 0;

    for path in paths:
        with open(path, "r") as f:
            for l_no, line in enumerate(f):
                if "fn" in line:
                    num_fn += 1;

            num_lines += l_no
            
    
    data = {"Crate-Version": name, 
            "Number of Lines": num_lines, 
            "Number of Functions": num_fn}
    df = pd.DataFrame([data]) 
    row_csv = [name + "," + str(num_lines) + "," + str(num_fn)]
    
    row_exists = False
    with open(summary_csv_path, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for l_no, line in enumerate(reader):
            if line == row_csv:
                print("summary for " + name + " already exists")
                row_exists = True

    if not row_exists:
        df.to_csv(summary_csv_path, mode = "a", index=False, header = os.path.getsize(summary_csv_path) == 0)

def summary():
    total_num_lines = 0;
    total_num_fns = 0;
    i = 0

    with open(summary_csv_path, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for l_no, line in enumerate(reader):
            if not line == header and not line == []:
                row = line[0].split(",")

                total_num_lines += int(row[line_index])
                total_num_fns += int(row[fn_index])
                i+=1

    data = {"Total Number of Crates": i -1,
            "Total Number of Lines": total_num_lines, 
            "Number of Functions": total_num_fns}

    df = pd.DataFrame([data])
    df.to_csv(summary_csv_path, mode = "a", index=False, header = True)
    


def run():
    os.system("python3 ./x.py run --bin setup_crates err_report") 

    if not os.path.isfile(summary_csv_path):
        with open(summary_csv_path, "w"):
            print("summary.csv created")

    crates = os.listdir("/tmp");
    for crate in crates:  
        if ".crate" not in crate:
            crate_ = crate + ".crate"

            if crate_ in crates: 
                count_num_fn(crate, get_file("/tmp/" + crate, []))

    summary()


if __name__ == '__main__':
    run()

