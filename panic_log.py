import os 
import datetime
import json

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
panic_report_dir = os.path.join(parent_dir, "log", "panic_report")
panic_reports = os.listdir(panic_report_dir)

date_ = str(datetime.datetime.now()).split(" ")
date = date_[0] + "-" + date_[1]
panic_summary_dir = os.path.join(parent_dir, "log", "panic_summary")
print(panic_summary_dir )
panic_summary_path = panic_summary_dir + "/" + date + ".json"

class Stats:
    reason = {}


def eval():
    s = Stats()

    for panic in panic_reports:
        with open(os.path.join(panic_report_dir, panic), "r") as f: 
            lines = f.readlines()
            i = 0

            while i < len(lines) - 3:
                line = lines[i]
                
                if "thread 'rustc' panicked at" in line:
                    crate = {
                            "name": panic[:-4],
                            "line": "todo"
                    }
                    
                    if lines[i+1] not in s.reason:
                        s.reason[lines[i+1]] = {
                            "num": 0,
                            "crate": []
                        }
                    else:
                        if crate not in s.reason[lines[i+1]]["crate"]:
                            s.reason[lines[i+1]]["num"] += 1
                            s.reason[lines[i+1]]["crate"].append(crate)

                i += 1

    stats = {
        "total_num_crates_paniced": len(panic_reports),
        "reason_num": len(s.reason),
        "reason": s.reason
    }

    json_stats = json.dumps(stats, indent= 8)
    with open(panic_summary_path, "w") as f:
        print("writing to summary")
        f.write(json_stats)

if __name__ == '__main__':
    eval()