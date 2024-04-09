import os, json
from w import wksp

w = wksp()

class Stat:
    fn_total = 0
    unsupported_total = 0
    rust_warning = 0;
    internal_error = 0;

    unsupported = {}
    unsupported_detailed = {}
    rust_reason = {}

    failed_total = 0;
    failed_reason = {};

    crashed = []
    i = 0
    
def eval(report, s):
    s.i += 1;
    with open(os.path.join(w.p_c, report), "r") as f_:
        f = json.load(f_)

        if f["fn_total"] == 0:
            return 1

        s.fn_total += f["fn_total"]
        s.unsupported_total += f["unsupported_feature_total_num"]
        s.rust_warning += f["rust_warning_total_num"]
        s.internal_error += f["internal_err_total_num"]
        s.failed_total += f["verification_failed_num_total"]

        for err in f["unsupported_detailed"]:
            if err in s.unsupported_detailed:
                s.unsupported_detailed[err]["num"] += 1
            else:
                s.unsupported_detailed[err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }
        
        for err in f["unsupported_summary"]:
            if err in s.unsupported:
                s.unsupported[err]["num"] += 1
            else:
                s.unsupported[err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }

        for rust_err in f["rust_warning_reasons"]:
            if rust_err in s.rust_reason:
                s.rust_reason[rust_err]["num"] += 1
            else:
                s.rust_reason[rust_err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }

        for err in f["verification_failed_reason"]:
            if err in s.failed_reason:
                s.failed_reason[err]["num"] += 1
            else:
                s.failed_reason[err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }
        f_.close()
    return 0

def run():
    s = Stat()
    omit = 0
    for report in os.listdir(w.p_c):
        omit = eval(report, s)

    s.unsupported  = dict(sorted(s.unsupported.items(),  key=lambda x: x[1]['num'], reverse=True))
    s.unsupported_detailed = dict(sorted(s.unsupported_detailed.items(), key=lambda x: x[1]['num'], reverse=True))
    s.rust_reason  = dict(sorted(s.rust_reason.items(),  key=lambda x: x[1]['num'], reverse=True))
    s.failed_reason  = dict(sorted(s.failed_reason.items(), key=lambda x: x[1]['num'], reverse=True))

    for c in os.listdir(w.c_r):
        s.crashed.append(c.replace(".txt", ""))

    stats = {
        "crates_num": s.i,
        "fn_total": s.fn_total,
        "ve_total": s.failed_total,
        "ve_distinct_num": len(s.failed_reason),
        "ve_rsn": s.failed_reason,
        "us_total": s.unsupported_total,
        "us_rsn_num": len(s.unsupported),
        "us_rsn": s.unsupported,
        "us_rsn_detailed_num": len(s.unsupported_detailed),
        "us_rsn_detailed": s.unsupported_detailed,
        "rw_total": s.rust_warning,
        "rw_distinct_num": len(s.rust_reason),
        "rw_rsn": s.rust_reason,
        "ie_num": s.internal_error,
        "crashed_num": len(s.crashed),
        "crahsed_crates": s.crashed,
        "crates_omitted": omit
    }

    json_stats = json.dumps(stats, indent= 8)
    with open(os.path.join(w.p_s, w.date() + ".json"), "w") as f:
        print("writing to summary")
        f.write(json_stats)

if __name__ == '__main__':
    run()


