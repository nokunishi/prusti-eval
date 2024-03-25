import sys, json, os
import collect as c
from w import wksp

w = wksp()

def summary_wksp(m, fn_total, line_total):
    with open(os.path.join(w.m, m), "r") as f:
        crate = m.replace(".json", "")
        f_ = json.load(f)
        fn_mir = 0
        p_total = 0
        p_reason = []
        error = []
        p_fn = 0

        compile_e = []
        compile_e_rr = []
        unreachable = []
        u_total = 0
            
        for f_list in f_["result"]:
            for f_name in f_list.keys():
                for txts in f_list[f_name]:
                    for txt_name in txts.keys():
                        name = txts[txt_name]["fn_name"]
                        fn_mir += 1
                        p_total += txts[txt_name]["num_total"]

                        if  txts[txt_name]["num_total"] != 0:
                            p_fn += 1
                        for r_obj in txts[txt_name]["reasons"]:
                            r = [*r_obj.keys()][0]
                            inlist = False
                            for p_obj in p_reason:
                                if r == [*p_obj.keys()][0]:
                                    p_obj[r].append({
                                        "fn": name,
                                        "path": txts[txt_name]["path"], 
                                        "count": r_obj[r]
                                    })
                                    inlist = True
                            if not inlist:
                                p_reason.append({
                                    r : [{
                                        "fn": name,
                                        "path": txts[txt_name]["path"], 
                                        "count": r_obj[r]
                                    }]
                                })
                        if txts[txt_name]["num_blocks"] == "0":
                            fn_mir -= 1
                            error.append(name)
                        if not txts[txt_name]["num_blocks"] == "0" and txts[txt_name]["unreachable"]:
                            unreachable.append({name: txts[txt_name]["unreachable"]})
                            u_total += txts[txt_name]["unreachable"]
        for e in f_["error"]:
            r = [*e.keys()][0]
            if r not in compile_e_rr:
                compile_e_rr.append(r)
            if e not in compile_e:
                compile_e.append(e)
            
        obj = {
                "fn_total": fn_total,
                "line_total": line_total,
                "fn_mir": fn_mir,
                "p_total": p_total,
                "p_fn_num": p_fn,
                "panicked_rn_num": len(p_reason),
                "panicked_rn": p_reason,
                "num_b0": len(error),
                "fn_b0": error,
                "unreachable_bn_total": u_total,
                "unreachable_bn": unreachable,
                "compile_err_num": len(compile_e),
                "compile_err": compile_e
        }

        obj_rr = {
                "fn_total": fn_total,
                "line_total": line_total,
                "fn_mir": fn_mir,
                "p_total": p_total,
                "p_fn_num": p_fn,
                "panicked_rn_num": len(p_reason),
                "panicked_rn": p_reason,
                "num_b0": len(error),
                "fn_b0": error,
                "unreachable_bn_total": u_total,
                "unreachable_bn": unreachable,
                "compile_err_num": len(compile_e),
                "compile_err": compile_e_rr
        }

        f.close()

        if "--rerun" in sys.argv:
            p = os.path.join(w.m_rerun, m)
            o = obj_rr
        else:
            p = os.path.join(w.m_rprt, m)
            o = obj
        with open(p, "w") as f_:
            print("writing summary for " + m[:-5] + " to " + p.split("/")[-2])
            o = json.dumps(o)
            f_.write(o)    



def fix(crate):
    with open(os.path.join(w.m_rprt, crate)) as f_:
        f = json.load(f_)
        summary_wksp(crate, f["fn_total"], f["line_total"])


if __name__ == "__main__":
    for m in os.listdir(w.m_rprt):
        if not os.path.exists(os.path.join(w.r_e, m)):
            fix(m)
