import os 
import datetime
import json
from workspace import Wksp as w

p_reports = os.listdir(w.p_report)
date_ = str(datetime.datetime.now()).split(" ")
date = date_[0] + "-" + date_[1]
summaries = os.listdir(w.p_summary)
summary_path = summaries + "/" + date + ".json"


class Stats:
    reason = {}
    fn = {}


def eval():
    s = Stats()

    for panic in p_reports:
        with open(os.path.join(w.p_report, panic), "r") as f: 
            lines = f.readlines()
            i = 0

            while i < len(lines) - 3:
                line = lines[i]
                
                if "thread 'rustc' panicked at" in line:        
                    lines[i+1] = lines[i+1].strip()    
                    if  "called `Result::unwrap()` on an `Err` value:" in lines[i+1]:
                        lines[i+1] =  "called `Result::unwrap()` on an `Err` value:"
                    if lines[i+1] not in s.reason:
                        s.reason[lines[i+1]] = {
                            "num": 1,
                            "crates": [panic[:-4]]
                        }
                    else:
                        if panic[:-4] not in s.reason[lines[i+1]]["crates"]:
                            s.reason[lines[i+1]]["num"] += 1
                            s.reason[lines[i+1]]["crates"].append(panic[:-4])

                if "called" in line:
                    words = line.split(" ");
                    fn_key = [];

                    for word in words:
                        if "`" in word and "::" in word:
                            word = word.replace("`", "")
                            module = word.split("::")[0]

                            if module not in s.fn:
                                s.fn[module] = {
                                    "num_panicked_fns": 1,
                                    "type": [line.strip()]
                                }
                            else:
                                if not line.strip() in s.fn[module]["type"]:
                                    s.fn[module]["num_panicked_fns"] += 1
                                    s.fn[module]["type"] = line.strip()

                i += 1

    stats = {
        "total_num_crates_paniced": len(p_reports),
        "reason_num": len(s.reason),
        "reason": s.reason,
        "panicky_fns": s.fn
    }

    json_stats = json.dumps(stats, indent= 8)
    with open(summary_path, "w") as f:
        print("writing to summary")
        f.write(json_stats)

if __name__ == '__main__':
    eval()