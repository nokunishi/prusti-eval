import os, json, sys, shutil
from w import wksp

non_rust_warnings = ["warning", "warnings", "prusti", "Prusti", "generated", "(lib)", "`" + os.getcwd() + "`", 
                     '(bin "run_prusti")', "`name`", "`ver`", '`cmd`']

w = wksp()

class Stats:
    us_detailed = {}
    us = 0;
    us_summary = {}
    internal = 0;
    rw_reasons = {}
    rw = 0;
    crashed =False
    ve_reasons = {}
    ve = 0;

def num_fn(crate):
    p = os.path.join(w.t_l, crate)
    try:
        for d in os.listdir(p):
            if d != "vir_program_before_foldunfold":
                shutil.rmtree(os.path.join(p, d))
        f = os.path.join(p, "vir_program_before_foldunfold")
        fns = 0
        for rust_f in os.listdir(f):
            with open(os.path.join(f, rust_f), "r") as f_:
                for l in f_:
                    if l.strip().startswith("method ") and "(...)" in l:
                        fns += 1
    except:
        return 0
    
    return fns


def parse_us(s, l):
    s.us += 1
    type = ""
    l = l.split(" ")[1:]

    for w in l:
        if "?" in w or " " in w or "Val(" in w:
            continue
        if "{impl#" in w:
            w = w.replace("{impl#", "")
            for c in w:
                if c.isnumeric():
                    w = w.replace(c, "")
            w = w.replace("}::", "")
        if "'" in w:
            w = w.replace("'", "")
        type += w + " "
    return type.strip()


def parse_us_d(words):
    w_len = len(words);
    i = 0
    while i < len(words):
        w = words[i].strip()
        if "~" in w:
            if "::" in words[i + 1]:
                crate = words[i + 1].split("::")[0]
                if "[" in crate:
                    crate = crate[:crate.index("[")]
                words = words[:i]
                words.append(crate)
            else:
                words = words[:i]
        if "{" in w: 
            words = words[:i]
        if "(" in w:
            w = w[:w.index("(")]
            words = words[:i]
            words.append(w)
        if ";" in w:
            w = w[:w.index(";")]
            words = words[:i]
            words.append(w)
        if "std::" in w:
            if "(" in w:
                w = w[:w.index("(")]
            else : 
                err_word_ = w.split("::")
                w = err_word_[0] + "::" + err_word_[1]
            words = words[:i]
            words.append(w)
        i += 1
    return words

def unsupported(s, l, detail, l_no):
    if l in s.us_detailed:
        s.us_detailed[l].append({l_no: detail})
    else: 
        s.us_detailed[l] = [{l_no: detail}]
    
    words = parse_us_d(l.split(" "))

    rsn_distinct = ""    
    for w in words:
        w = w.strip()
        if "[" in w:
            w = w.replace("[", "")
        if "]" in w:
            w = w.replace("]", "")
        rsn_distinct += w + " "
                
    rsn_distinct = rsn_distinct.strip()

    if not rsn_distinct in s.us_summary and len(rsn_distinct) > 0:
        if not rsn_distinct == "unsupported constant type" and not rsn_distinct =="unsupported constant value":
            s.us_summary[rsn_distinct] = [{l_no: detail}]
        else: 
            obj = {l_no: detail}
            s.us_summary[rsn_distinct].append(obj) 

def warning(s, line, detail, l_no):
    for warn in non_rust_warnings:
        if warn in line:
            line = ""
            break
    w_line = line.split(" ")
    w_type = ""
    for err in w_line:
        w_type += err + " "
    w_type = w_type.strip()

    if "src/bin/run_prusti.rs" not in l_no and len(w_type) > 0:
        if not w_type in s.rw_reasons:
            s.rw_reasons[w_type] = [{
                l_no: detail
                }]
        else: 
            s.rw_reasons[w_type].append({
                l_no: detail
            })
        s.rw += 1;

def parse(crate, fn_n):
    with open(os.path.join(w.d_a, crate  + ".txt"), "r") as f:
        lines = f.readlines()
        i = 0 
        crashed = False
        
        s = Stats()
        while i < len(lines) - 3:
            line = lines[i]
            l_no = lines[i+1].replace(" ", "").replace("-", "").replace(">", "").strip();
            detail = lines[i + 3]

            while detail[0].isdigit() or detail[0] == "/":
                detail = detail[1:]
            detail = detail[2:].strip()
            
            if "[Prusti: unsupported feature]" in line:
                e_line = line.replace("[Prusti: unsupported feature]", "")
                us = parse_us(s, e_line)
                unsupported(s, us, detail, l_no)

            elif "warning:" in line:
                line = line.replace("warning:", "").replace("\n", "")
                warning(s, line, detail, l_no)
            elif "[Prusti: internal error]" in line:
                s.internal += 1
            elif "error: [Prusti: verification error]" in line:
                w_type = line.replace("error: [Prusti: verification error]", "").replace("\"", "").strip()
                s.ve += 1;
                
                if  w_type not in s.ve_reasons and len(w_type) > 0:
                    s.ve_reasons[w_type] = [{
                            l_no: detail
                    }]
                else: 
                    s.ve_reasons[w_type].append({
                        l_no: detail
                    }) 
            elif "thread 'rustc' panicked at" in line and not crashed:
                with open(os.path.join(w.c_r, crate + ".txt"), "a") as c_rprt:
                    j = i
                    while j < len(lines):
                        c_rprt.write(lines[j])
                        j += 1
                    c_rprt.close()
                crashed = True
        
            i += 1
        f.close()
    if crashed:
        print("writing to panic_report for " + crate)
        
    trace = {
        "fn_total": fn_n, 
        "verification_failed_num_total": s.ve,
        "verification_failed_num_distinct": len(s.ve_reasons),
        "verification_failed_reason": s.ve_reasons,
        "unsupported_feature_total_num": s.us,
        "unsupported_summary_num": len(s.us_summary),
        "unsupported_summary": s.us_summary,
        "unsupported_detailed_num": len(s.us_detailed),
        "unsupported_detailed": s.us_detailed,
        "rust_warning_total_num":  s.rw,
        "rust_warning_num": len(s.rw_reasons),
        "rust_warning_reasons": s.rw_reasons,
        "internal_err_total_num": s.internal,
    }

    json_trace = json.dumps(trace, indent= 4)

    with open(os.path.join(w.p_err, crate + ".json")  , "w") as f:
        print("writing to json: " + crate)
        f.write(json_trace)
        f.close()

    p = os.path.join(w.t_l, crate)
    if os.path.exists(p):
        print("deleting viper log files for " + crate)
        shutil.rmtree(p)

def run(crate):
    e_rprt = os.path.join(w.p_err, crate + ".json")

    if "--reset" not in sys.argv:
        if os.path.exists(e_rprt):
            print("err report for " + crate + " exists already")
            return

    parse(crate, num_fn(crate))


def main():
    results = os.listdir(w.d_a);

    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    if "--a" in sys.argv:
        if len(results) == 0:
            print("no txt file to extract data from")
            return
        for r in results:
            crate = r.replace(".txt", "")
            if crate + ".json" not in os.listdir(w.p_err):
                parse(crate, num_fn(crate))
        return
    else:
        parse(sys.argv[1], num_fn(sys.argv[1]))


if __name__ == '__main__':
    main()
