import os
import json
import sys
from pathlib import Path

run_prusti_file = '(bin "run_prusti")'
unsupported_feature = "[Prusti: unsupported feature]"
internal_errors = "[Prusti: internal error]"
warning = "warning:"
non_rust_warnings = ["warning", "warnings", "prusti", "Prusti", "generated", "(lib)", "`" + os.getcwd() + "`", 
                     run_prusti_file, "`name`", "`ver`", '`cmd`']
verification_error = "error: [Prusti: verification error]"

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir = os.path.join(parent_dir, "log")
archive_dir = os.path.join(log_dir, "archive")
archivedir_list = os.listdir(os.path.join(log_dir, "archive"))

def setup():
    logdir_list = os.listdir(log_dir)

    if "err_report" in logdir_list:
        logdir_list.remove("err_report")
    else:
        os.mkdir(os.path.join(logdir_list, "err_report"))

    panic_reports = []
    if "panic_report" in logdir_list:
        logdir_list.remove("panic_report")
    else:
        os.mkdir(os.path.join(logdir_list, "panic_report"))

    if not "archive" in logdir_list:
        print("No file to extract error report from")        


def parse():
    for log in archivedir_list:
        err_file = log[:-4] + ".json"
        err_file_path = os.path.join(archive_dir, "err_report",  err_file)

        if "reset" not in sys.argv:
            if os.path.exists(err_file_path):
                print("err report for " + log + " exists already")
                continue

        with open(os.path.join(archive_dir, log), "r") as f:
            lines = f.readlines()

            us_detailed = {}
            us = 0;
            us_summary = {}
            internal = 0;
            rw_reasons = {}
            rw = 0;
            panic_report =False
            ve_reasons = {}
            ve = 0;
        
            i = 0 
        
        
            while i < len(lines) - 3:
                line = lines[i]
                if unsupported_feature in line:
                    us += 1
                    err_line = line.replace("warning:", "").replace(unsupported_feature, "").split(" ")
                    err_type = ""

                    for word in err_line: 
                        index = err_line.index(word)
                        err_word = ""
                        if len(word) == 0:
                            continue
                        if word not in err_line:
                            break
                        if "?" in word or " " in word:
                            word = ""
                        if "{impl#" in word:
                            word = word.replace("{impl#", "")
                            for c in word:
                                if c.isnumeric():
                                    word = word.replace(c, "")
                            word = word.replace("}::", "")
                        if ":" in word and not "::" in word:
                            if not word.endswith(":"):
                                word = ""
                            else: 
                                word = word[:-1]
                        if "Val(" in word:
                            word = ""
                        if "'" in word:
                            word = word.replace("'", "")
                        err_line[index] = word
                        err_type += word + " "

                    err_type = err_type.strip()
                    err_l_no = lines[i + 1].replace(" ", "").replace("-", "").replace(">", "").strip()
                    err_l_detailed = lines[i + 3]

                    while err_l_detailed[0].isdigit() or err_l_detailed[0] == "/":
                        err_l_detailed = err_l_detailed[1:]
                    err_l_detailed = err_l_detailed[2:].strip()

                    if not err_type in us_detailed:
                        us_detailed[err_type] = [{
                            err_l_no: err_l_detailed
                        }]
                    else: 
                        us_detailed[err_type].append({
                            err_l_no: err_l_detailed
                        })
                
                    err_line_summary = err_line

                    for err_word in err_line_summary:
                        if err_word in err_line_summary:
                            index =err_line_summary.index(err_word)
                            err_word = err_word.strip()
                            if "~" in err_word:
                                if "::" in err_line_summary[index + 1]:
                                    crate = err_line_summary[index + 1].split("::")[0]
                                    if "[" in crate:
                                        crate = crate[:crate.index("[")]
                                    err_line_summary = err_line_summary[:index]
                                    err_line_summary.append(crate)
                                else:
                                    err_line_summary = err_line_summary[:index]
                            if "{" in err_word: 
                                err_line_summary = err_line_summary[:index]
                            if "(" in err_word:
                                err_word = err_word[:err_word.index("(")]
                                err_line_summary = err_line_summary[:index]
                                err_line_summary.append(err_word)
                            if ";" in err_word:
                                err_word = err_word[:err_word.index(";")]
                                err_line_summary = err_line_summary[:index]
                                err_line_summary.append(err_word)
                            if "std::" in err_word:
                                if "(" in err_word:
                                    err_word = err_word[:err_word.index("(")]
                                else : 
                                    err_word_ = err_word.split("::")
                                    err_word = err_word_[0] + "::" + err_word_[1]
                                err_line_summary = err_line_summary[:index]
                                err_line_summary.append(err_word)

                    err_type_distinct = ""    
                    for err_word in err_line_summary:
                        err_word = err_word.strip()
                        if "[" in err_word:
                            err_word = err_word.replace("[", "")
                        if "]" in err_word:
                            err_word = err_word.replace("]", "")
                        if not err_word == '':
                            err_type_distinct += err_word + " "
                
                    err_type_distinct = err_type_distinct.strip()
                    err_l_no_distinct = lines[i + 1].replace(" ", "").replace("-", "").replace(">", "").strip()
                    err_l_detailed_distinct = lines[i + 3]

                    while err_l_detailed_distinct[0].isdigit() or  err_l_detailed_distinct[0] == "/":
                        err_l_detailed_distinct = err_l_detailed_distinct[1:]
                    err_l_detailed_distinct = err_l_detailed_distinct[2:].strip()

                    if not err_type_distinct in us_summary:
                        if not err_type_distinct == "unsupported constant type" and not err_type_distinct =="unsupported constant value":
                            us_summary[err_type_distinct] = [{
                                err_l_no_distinct: err_l_detailed_distinct
                            }]
                    else: 
                        obj = {
                            err_l_no_distinct: err_l_detailed_distinct
                        }
                        us_summary[err_type_distinct].append(obj) 

                if warning in line and not unsupported_feature in line:
                    line = line.replace("warning:", "").replace("\n", "")
                    for warn in non_rust_warnings:
                        if warn in line:
                            line = ""
                            break
                    if len(line) > 0:
                        err_line = line.split(" ")
                        err_type = ""
                        for err in err_line:
                            err_type += err + " "
                        err_type = err_type.strip()
                        err_l_no = lines[i + 1].replace(" ", "").replace("-", "").replace(">", "").strip()
                        err_l_detailed = lines[i + 3]

                        while err_l_detailed[0].isdigit() or  err_l_detailed[0] == "/":
                            err_l_detailed = err_l_detailed[1:]
                        err_l_detailed = err_l_detailed[2:].strip()
                        if not err_type in rw_reasons:
                            rw_reasons[err_type] = [{
                                err_l_no: err_l_detailed
                            }]
                        else: 
                            rw_reasons[err_type].append({
                                err_l_no: err_l_detailed
                            })
                        rw += 1;
                if internal_errors in line:
                    internal += 1
                if "thread 'rustc' panicked at" in line:
                    panic_report = True
                if panic_report:
                    filename = os.path.join(log_dir, "panic_report", log)
                    with open(filename, "a") as crash_report:
                        crash_report.write(line)
                if verification_error in line:
                    err_type = line.replace(verification_error, "").replace("\"", "").strip()
                    ve += 1;
                
                    err_l_no = lines[i + 1].replace(" ", "").replace("-", "").replace(">", "").strip()
                    err_l_detailed = lines[i + 3]

                    while err_l_detailed[0].isdigit() or  err_l_detailed[0] == "/":
                        err_l_detailed = err_l_detailed[1:]
                    err_l_detailed = err_l_detailed[2:].strip()

                    if  err_type not in ve_reasons:
                        ve_reasons[err_type] = [{
                                err_l_no: err_l_detailed
                        }]
                    else: 
                        ve_reasons[err_type].append({
                            err_l_no: err_l_detailed
                        }) 
        
                i += 1
        if panic_report:
            print("writing to panic_report: " + log)
        
        trace = {
        "verification_failed_num_total": ve,
        "verification_failed_num_distinct": len(ve_reasons),
        "verification_failed_reason": ve_reasons,
        "unsupported_feature_total_num": us,
        "unsupported_summary_num": len(us_summary),
        "unsupported_summary": us_summary,
        "unsupported_detailed_num": len(us_detailed),
        "unsupported_detailed": us_detailed,
        "rust_warning_total_num":  rw,
        "rust_warning_num": len(rw_reasons),
        "rust_warning_reasons": rw_reasons,
        "internal_err_total_num": internal,
        "has_panic_reports": panic_report
        }

        json_trace = json.dumps(trace, indent= 4)
        with open(os.path.join(log_dir, "err_report", log[:-4] + ".json"), "w") as outfile:
            print("writing to json: " + log)
            outfile.write(json_trace)

        filename = os.path.join(log_dir, "panic_report", log)
        if panic_report and os.path.getsize(filename) == 0:
            os.remove(filename)
    


def main():
    setup()
    print("hello")
    parse()


main()