import os, json, datetime, sys, csv
from w import wksp

w = wksp()
err_reports = os.listdir(w.err)

class Stat:
    unsupported_total = 0
    rust_warning = 0;
    internal_error = 0;
    panicked = 0;

    unsupported = {}
    unsupported_detailed = {}
    rust_reason = {}

    failed_total = 0;
    failed_reason = {};
    i = 0
    
    crates_ommitted = [];
        


def sync(crate, s):
    report_path = sys.argv[2]

     with open(os.path.join(w.p_eval, report_path), "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for l_no, line in enumerate(reader):
            rows_csv = line[0].split(",")[0]

            if rows_csv == crate:      
                return True

        print(crate + " not found in line summary")
        s.crates_ommitted.append(crate)
        return False

def eval(report, s):
    s.i += 1;
    with open(os.path.join(w.err, report), "r") as f:
        f = json.load(f)
    
        s.unsupported_total += f["unsupported_feature_total_num"]
        try:
            s.rust_warning += f["rust_warning_total_num"]
            s.internal_error += f["internal_err_total_num"]
        except:
            print(report)
        s.failed_total += f["verification_failed_num_total"]
        if f["has_panic_reports"] == True:
            s.panicked += 1

        unsuppported_errs = f["unsupported_summary"]

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

def run():
    s = Stat()

    for report in err_reports:
        if "-s" in sys.argv:
            report_name = report[:-5]
            if sync(report_name, s):
                eval(report, s)
        else:
            eval(report, s)
                
    if "-s" in sys.argv:
        report_path = sys.argv[2]

        with open(os.path.join(w.p_eval, report_path), "r") as f:
            lines = f.read().splitlines()
            lastline = lines[-1]
            if not int(lastline.split(",")[0]) == s.i:
                print("inconsistent number of crates")
                print("# of crates in line summary: " + lastline.split(",")[0])
                print("# of crates in error reports: " + s.i)
                return

    s.unsupported  = dict(sorted(s.unsupported.items(),  key=lambda x: x[1]['num'], reverse=True))
    s.unsupported_detailed = dict(sorted(s.unsupported_detailed.items(), key=lambda x: x[1]['num'], reverse=True))
    s.rust_reason  = dict(sorted(s.rust_reason.items(),  key=lambda x: x[1]['num'], reverse=True))
    s.failed_reason  = dict(sorted(s.failed_reason.items(), key=lambda x: x[1]['num'], reverse=True))

    stats = {
        "number_of_crates": s.i,
        "panicked_total": s.panicked,
        "verification_failed_total": s.failed_total,
        "verification_failed_distinct_num": len(s.failed_reason),
        "verification_failed_reason": s.failed_reason,
        "unsupported_features_total": s.unsupported_total,
        "unsupported_feature_grouped_num": len(s.unsupported),
        "unsupported_feature_summary": s.unsupported,
        "unsupported_feature_distinct_num": len(s.unsupported_detailed),
        "unsupported_feature_detailed": s.unsupported_detailed,
        "rust_warning_total": s.rust_warning,
        "rust_warning_distinct_num": len(s.rust_reason),
        "rust_warning_summary": s.rust_reason,
        "internal_errors_total": s.internal_error,
        "crates_ommitted_num": len(s.crates_ommitted),
        "crates_ommitted": s.crates_ommitted
    }

    json_stats = json.dumps(stats, indent= 8)
    with open(os.path.join(w.eval, "summary-" + w.date() + ".json"), "w") as outfile:
        print("writing to summary")
        outfile.write(json_stats)

if __name__ == '__main__':
    run()


