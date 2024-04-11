import os, json, sys, shutil
from w import wksp

w = wksp()

class Stats:
    reason = {}
    fn = []

def zip():
    size = str(len(os.listdir(w.c_r)))

    zip_dist = os.path.join(w.c_dir, w.date() + "-" +  size)
    shutil.make_archive(base_name=zip_dist, format='zip', root_dir=w.c_r)

    if os.path.exists(zip_dist + ".zip"):
        shutil.rmtree(w.c_r)
        os.mkdir(w.c_r)

def summarize():
    s = Stats()
    c_reports = os.listdir(w.c_r)

    for c in c_reports:
        with open(os.path.join(w.c_r, c), "r") as f: 
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
                i += 1
            f.close()
    for r in s.reason.keys():
        if "called" in r:
            for word in r.split(" "):
                if "`" in word and "::" in word:
                    fn = word.replace("`", "").strip()
                    inList = False
                    for obj in s.fn:
                        if fn == [*obj.keys()][0]:
                            obj[fn] += s.reason[r]["num"]
                            inList = True
                    if not inList:
                        s.fn.append({fn: s.reason[r]["num"]})

    s.reason = dict(sorted(s.reason.items(),  key=lambda x: x[1]["num"], reverse=True))
    s.fn.sort(key=lambda x: x.items(), reverse=True)
    stats = {
        "total_num_crates_paniced": len(c_reports),
        "reason_num": len(s.reason),
        "reason": s.reason,
        "crashed_fns": s.fn
    }

    json_stats = json.dumps(stats, indent= 8)
    with open(os.path.join(w.c_s, w.date() + ".json"), "w") as f:
        print("writing summary")
        f.write(json_stats)


def main():
    if "--z" in sys.argv:
        zip()
        return
    summarize()

if __name__ == '__main__':
    main()