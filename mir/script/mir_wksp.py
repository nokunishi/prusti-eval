import sys, json, os

def wksp():
    from dotenv import load_dotenv
    load_dotenv()
    sys.path.insert(1, os.getenv('ROOT'))
    from workspace import Wksp as w
    return w

def get_fn_submod(p_rn):
    root = []
    for r in p_rn:
        for obj in r[[*r.keys()][0]]:
            p = [*obj.keys()][0]

            if not p.startswith("mod") and not p.startswith("lib"):
                root.append({[*r.keys()][0]: p})

    return root


def paniced_rn(arr, key, obj):
    for a in arr:
        if key in a:
            a[key].append(obj)
            return arr
        
    o_ = {
        key: [obj]
    }
    arr.append(o_)
    return arr

def remove_duplicate(p_rn, fn_mir, p_total,  p_fn_num):
    fns_submod = get_fn_submod(p_rn)

    r_ = []
    fns = []

    for r in p_rn:
        for obj in r[[*r.keys()][0]]:
            p = [*obj.keys()][0]

            if (p.startswith("mod") or p.startswith("lib")):
                p_ = p.split("/")[1].split("::")
                
                if len(p_) > 1:
                    p_ = p_[0] + "/" + p_[1]
                    if {[*r.keys()][0]: p_} not in fns_submod:
                        r_ =  paniced_rn(r_, [*r.keys()][0], obj)
                        fns.append(p)
                    else:
                        p_total -= obj[p]
                else:
                    r_ =  paniced_rn(r_, [*r.keys()][0], obj)
                    fns.append(p)
            else:
                r_ = paniced_rn(r_, [*r.keys()][0], obj)
                fns.append(p)

    fns = list(dict.fromkeys(fns))
    fn_mir -=  p_fn_num -len(fns)
    p_fn_num = len(fns)

    return r_, fn_mir, p_total, p_fn_num




def summary_wksp(m, fn_total):
    w = wksp()
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
            
            
        for file_list in f_["result"]:
            for file_name in file_list.keys():
                for fn_lists in file_list[file_name]:
                    for fn in fn_lists.keys():
                        name = fn_lists[fn]["path"]
                        fn_mir += 1
                            
                        p_total += fn_lists[fn]["num_total"]
                        if  fn_lists[fn]["num_total"] != 0:
                            p_fn += 1
                        for r_obj in fn_lists[fn]["reasons"]:
                            r = [*r_obj.keys()][0]
                            inlist = False
                            for p_obj in p_reason:
                                if r == [*p_obj.keys()][0]:
                                    inlistf = False
                                    for p in p_obj[r]:
                                        if name == [*p.keys()][0]:
                                            p[name] += r_obj[r]
                                            inlistf = True
                                    if not inlistf:
                                        p_obj[r].append({
                                            name : r_obj[r]
                                        })
                                    inlist = True
                            if not inlist:
                                p_reason.append({
                                    r : [{
                                        name : r_obj[r]
                                    }]
                                })
                        if fn_lists[fn]["num_blocks"] == "0":
                            error.append(name)
                        if not fn_lists[fn]["num_blocks"] == "0" and fn_lists[fn]["unreachable"]:
                            unreachable.append({name: fn_lists[fn]["unreachable"]})
                            u_total += fn_lists[fn]["unreachable"]


        p_reason, fn_mir, p_total, p_fn = remove_duplicate(p_reason, fn_mir, p_total, p_fn);

                
        for e in f_["error"]:
            r = [*e.keys()][0]
            if r not in compile_e_rr:
                compile_e_rr.append(r)
            if e not in compile_e:
                compile_e.append(e)
            
        obj = {
                "fn_total": fn_total,
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
            p = os.path.join(w.m_report, m)
            o = obj
        with open(p, "w") as f_:
            print("writing summary for " + m[:-5] + " to " + p.split("/")[-2])
            o = json.dumps(o)
            f_.write(o)    
