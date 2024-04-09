import os, sys, json
from w import wksp

w = wksp()

def count_match(list, acc, t):
    for obj in list:
        rsn = [*obj.keys()][0]

        inList = False
        for match in acc:
            if [*match.keys()][0] == rsn:
                match[rsn] += 1
        if not inList:
            acc.append({rsn: 1})
            inList = True

        t += 1
    return acc, t

def count_mir(list, acc, t):
    for obj in list:
        rsn = obj["mir"]

        inList = False
        for match in acc:
            if [*match.keys()][0] == rsn:
                match[rsn] += 1
                inList = True
        if not inList:
            acc.append({rsn: 1})
            inList = True

        t += 1
    return acc, t


def main():
    match_l = []
    match_t = 0
    mir_l = []
    mir_t = 0
    us = 0

    for r in os.listdir(w.r_e):
        with open(os.path.join(w.r_e, r), "r") as f_:
            f = json.load(f_)
            
            match_l, match_t = count_match(f["match"], match_l, match_t)
            mir_l, mir_t = count_mir(f["mir_only"], mir_l, mir_t)
            us += len(f["unsupported"])
    obj = {
        "crate": len(os.listdir(w.r_e)),
        "unsupported": us,
        "match_total": match_t,
        "match": match_l,
        "mir_only_total": mir_t,
        "mir_only_l": mir_l
    }

    obj = json.dumps(obj)
    with open(os.path.join(w.r_s, w.date() + ".json"), "w") as f:
        print("writing summary")
        f.write(obj)


if __name__ == "__main__":
    main()