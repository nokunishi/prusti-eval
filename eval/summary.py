import os, json
from w import wksp

w = wksp()

class Stat:
    match_l = {}
    match_t = 0
    mir_l = {}
    mir_t = 0
    us = 0

def count_match(s, crate, list):
    for obj in list:
        rsn = [*obj.keys()][0]

        if rsn in s.match_l:
            s.match_l[rsn]["count"] += len(obj[rsn])
        else:
            o = {
                "crate": crate,
                "fn": obj[rsn][0]["fn"],
                "path": obj[rsn][0]["path"],
            }

            s.match_l[rsn] = {
                "count": len(obj[rsn]),
                "i.e.": o,
            }

        s.match_t += len(obj[rsn])
    return s.match_l, s.match_t

def count_mir(s, crate, list):
    for obj in list:
        rsn = obj["mir"]

        if rsn in s.mir_l:
            s.mir_l[rsn]["count"] += 1
        else:
            o = {
                "count": 1,
                "i.e.": {
                    "crate": crate,
                    "fn": obj["fn"],
                    "path": obj["path"]
                }
            }
            s.mir_l[rsn] = o
        s.mir_t += 1
    return s.mir_l, s.mir_t


def run():
    s = Stat()

    for r in os.listdir(w.e_c):
        with open(os.path.join(w.e_c, r), "r") as f_:
            f = json.load(f_)
            s.match_l, s.match_t = count_match(s, r.replace(".json", ""), f["match"])
            s.mir_l, s.mir_t = count_mir(s, r.replace(".json", ""), f["mir_only"])
            s.us += len(f["unsupported"])

    
    s.match_l =  dict(sorted(s.match_l.items(),  key=lambda x: x[1]["count"], reverse=True))
    s.mir_l = dict(sorted(s.mir_l.items(),  key=lambda x: x[1]["count"], reverse=True))

    obj = {
        "crate": len(os.listdir(w.e_c)),
        "unsupported": s.us,
        "match_total": s.match_t,
        "match": s.match_l,
        "mir_only_total": s.mir_t,
        "mir_only_l": s.mir_l
    }

    obj = json.dumps(obj)
    with open(os.path.join(w.e_s, w.date() + ".json"), "w") as f:
        print("writing summary")
        f.write(obj)



if __name__ == "__main__":
    run()