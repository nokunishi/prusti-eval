import os, json
from w import wksp

w = wksp()

class Stat:
    match_l = {}
    match_t = 0
    mir_l = {}
    mir_t = 0
    mmatch_t = 0
    us_l = {}
    us_t = 0

def count(acc, t, crate, list):
    for rsn in list:
        for o in list[rsn]:
            if rsn in acc:
                acc[rsn]["count"] += 1
            else:
                o_ = {
                "count": 1,
                "i.e.": {
                    "crate": crate,
                    "fn": o["fn"],
                    "path": o["path"]
                    }
                }
                acc[rsn] = o_
            t += 1
    return acc, t


def run():
    s = Stat()
    crashed = os.listdir(w.c_r)

    for r in os.listdir(w.e_c):
        if not r.replace(".json", ".txt") in crashed:
            with open(os.path.join(w.e_c, r), "r") as f_:
                f = json.load(f_)
                s.match_l, s.match_t = count(s.match_l, s.match_t, r.replace(".json", ""), f["match"])
                s.mir_l, s.mir_t = count(s.mir_l, s.mir_t, r.replace(".json", ""), f["mir_only"])
                s.us_l, s.us_t =  count(s.us_l, s.us_t, r.replace(".json", ""), f["unsupported"])
                s.mmatch_t += len(f["unevaluated"])

    
    s.match_l =  dict(sorted(s.match_l.items(),  key=lambda x: x[1]["count"], reverse=True))
    s.mir_l = dict(sorted(s.mir_l.items(),  key=lambda x: x[1]["count"], reverse=True))
    s.us_l = dict(sorted(s.us_l.items(),  key=lambda x: x[1]["count"], reverse=True))

    obj = {
        "crate": len(os.listdir(w.e_c)) - len(crashed),
        "match_total": s.match_t,
        "match": s.match_l,
        "us_total": s.us_t,
        "us": s.us_l, 
        "mismatch": s.mmatch_t,
        "mir_only_total": s.mir_t,
        "mir_only_l": s.mir_l
    }

    obj = json.dumps(obj)
    with open(os.path.join(w.e_s, w.date() + ".json"), "w") as f:
        print("writing summary")
        f.write(obj)



if __name__ == "__main__":
    run()