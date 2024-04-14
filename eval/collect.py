import os, sys, json
from w import wksp

w = wksp()

def v_err(crate):
    with open(os.path.join(w.p_c, crate), "r") as f_:
        f = json.load(f_)
        v_err = f["verification_failed_reason"]
        v_e_new = []
        for rsn in v_err:
            if  "the asserted expression might not hold" in rsn:
                for l in v_err[rsn]:
                    line = [*l.keys()][0]
                    if "," in l[line]:
                        a = l[line].split("!")[2].split(",")[0]
                    else:
                        a = l[line].split("!")[1].split(";")[0]
                    v_e_new.append({line: a})
            for l in v_err[rsn]:
                line = [*l.keys()][0]
                v_e_new.append({line: rsn})
        f_.close()
        return v_e_new

def unsupported(crate):
    with open(os.path.join(w.p_c, crate), "r") as f_:
        f = json.load(f_)
        us = f["unsupported_detailed"]
        us_ = []

        for k in us.keys():
            for rsn in us[k]:
                l =[*rsn.keys()][0]      
                if l != "" and l not in us_:
                    us_.append({l: k})

        f_.close()
        return us_


def get_endlns(crate, fn):
    if "::" in fn:
        fn = fn.split("::")[1]

    with open(crate, "r") as f_:
        f = f_.readlines()
        i = 0

        while i < len(f):
            if "fn " + fn + "(" in f[i] or "fn " + fn + "<" in f[i]:
                 start, j = i, i

                 while j < len(f):
                     if "}" in f[j]:
                         end = j + 1
                         break
                     else:
                         j += 1
            i += 1
        f_.close()
    try:
        return start, end
    except:
        print(fn)
        print(crate)
