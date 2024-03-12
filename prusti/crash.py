import os, json, sys
from w import wksp

class Stats:
    reason = {}
    fn = {}


def eval():
    s = Stats()
    w = wksp()
    c_reports = os.listdir(w.c_report)

    for c in c_reports:
        with open(os.path.join(w.c_report, c), "r") as f: 
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
                            "crates": [c[:-4]]
                        }
                    else:
                        if c.replace(".txt", "") not in s.reason[lines[i+1]]["crates"]:
                            s.reason[lines[i+1]]["num"] += 1
                            s.reason[lines[i+1]]["crates"].append(c.replace(".txt", ""))

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
        "total_num_crates_paniced": len(c_reports),
        "reason_num": len(s.reason),
        "reason": s.reason,
        "panicky_fns": s.fn
    }

    json_stats = json.dumps(stats, indent= 8)
    with open(os.path.join(w.c_summary, w.date() + ".json"), "w") as f:
        print("writing summary")
        f.write(json_stats)

if __name__ == '__main__':
    eval()