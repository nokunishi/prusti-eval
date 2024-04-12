import os, json, sys
from w import wksp

w = wksp()

class Stat:
    fn_total = 0
    unsupported_total = 0
    rust_warning = 0;
    internal_error = 0;

    us = ["arg", "cast", "unsizing", "slice", "lifetime", "ref", "val", "type"]
    us_summary = {}
    unsupported = {}
    unsupported_detailed = {}
    rust_reason = {}

    failed_total = 0;
    failed_reason = {};

    crashed = []
    i = 0

    omit = 0
    omit_c = []

    def __init__(self):
        for u in self.us:
            if u not in self.us_summary:
                 self.us_summary[u] = {
                    "num": 0,
                    "i.e.": {
                        "crate": "",
                        "msg": ""
                    }
                }

    def us_obj(self, u, err, crate):
        if  self.us_summary[u]["num"] == 0:
            self.us_summary[u]["i.e."]["crate"]=  crate
            self.us_summary[u]["i.e."]["msg"]=  err
        self.us_summary[u]["num"] += 1
    
    def cat(self, err, crate):
        if "use a local variable as argument" in err:
            self.us_obj("arg", err, crate)
        elif "cast" in err:
            self.us_obj("cast", err, crate)
        elif "unsizing " in err:
            self.us_obj("unsizing", err, crate)
        elif "slice" in err or "slicing" in err:
            self.us_obj("slice", err, crate)
        elif "lifetime" in err:
            self.us_obj("lifetime", err, crate)
        elif "reference" in err:
            self.us_obj("ref", err, crate)
        elif "unsupported type" in err or "unsupported constant type" in err:
            self.us_obj("type", err, crate)
        elif "unsupported value" in err or "unsupported constant value" in err:
            self.us_obj("val", err, crate)

def eval(report, s):
    s.i += 1;
    with open(os.path.join(w.p_c, report), "r") as f_:
        f = json.load(f_)

        if f["fn_total"] == 0:
            return (1, report)

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
            s.cat(err, report[:-5])

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
    return (0, "")


def extract(s):
    crashed = os.listdir(w.c_r)

    for report in os.listdir(w.p_c):
         if report.replace(".json", ".txt") in crashed:
             continue
         (o, c)= eval(report, s)
         s.omit += o
         if c != "":
            s.omit_c.append(c.replace(".json", ""))


    s.us_summary =  dict(sorted(s.us_summary.items(),  key=lambda x: x[1]["num"], reverse=True))
    s.unsupported  = dict(sorted(s.unsupported.items(),  key=lambda x: x[1]['num'], reverse=True))
    s.unsupported_detailed = dict(sorted(s.unsupported_detailed.items(), key=lambda x: x[1]['num'], reverse=True))
    s.rust_reason  = dict(sorted(s.rust_reason.items(),  key=lambda x: x[1]['num'], reverse=True))
    s.failed_reason  = dict(sorted(s.failed_reason.items(), key=lambda x: x[1]['num'], reverse=True))

    for c in os.listdir(w.c_r):
        s.crashed.append(c.replace(".txt", ""))


def run():
    s = Stat()
    extract(s)

    stats = {
        "crates_total": s.i,
        "crates_num": s.i - s.omit,
        "fn_total": s.fn_total,
        "ve_total": s.failed_total,
        "ve_distinct_num": len(s.failed_reason),
        "ve": s.failed_reason,
        "us_total": s.unsupported_total,
        "us_rsn_num": len(s.unsupported),
        "us_by_cat": s.us_summary,
        "ie_num": s.internal_error,
        "crashed_num": len(s.crashed),
        "crahsed": s.crashed,
        "omitted_num": s.omit,
        "omitted": s.omit_c
    }

    with open(os.path.join(w.r_s, w.date() + ".json"), "w") as f:
        print("writing eval")
        f.write(json.dumps(stats, indent= 8))
        f.close()

    us_d = {
        "crates": s.i,
        "us_total": s.unsupported_total,
        "us_rsn_num": len(s.unsupported_detailed),
        "rsn":s.unsupported_detailed
    }

    with open(os.path.join(w.u_d, w.date() + ".json"), "w") as f:
        print("dumping us features (verbose)")
        f.write(json.dumps(us_d, indent= 4))
        f.close()

    us_s = {
        "crates": s.i,
        "us_total": s.unsupported_total,
        "us_rsn_num": len(s.unsupported),
        "rsn": s.unsupported
    }

    with open(os.path.join(w.u_s, w.date() + ".json"), "w") as f:
        print("dumping us features (summary)")
        f.write(json.dumps(us_s, indent= 4))
        f.close()

    rust = {
        "crates": s.i,
        "rw_total": s.rust_warning,
        "rw_rsn_num": len(s.rust_reason),
        "rw": s.rust_reason,
    }

    with open(os.path.join(w.r_r, w.date() + ".json"), "w") as f:
        print("dumping rust warnings")
        f.write(json.dumps(rust, indent= 4))
        f.close()


def reset():
    for d in os.listdir(w.r_dir):
        for f in os.listdir(os.path.join(w.r_dir, d)):
            os.remove(f)


def main():
    if "--r" in sys.argv:
        reset()
        return
    else:
        run()


if __name__ == '__main__':
    main()


