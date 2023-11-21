import os
import json

run_prusti_file = '(bin "run_prusti")'
cwd =  "`" + os.getcwd() + "`"

unsupported_feature = "[Prusti: unsupported feature]"
internal_errors = "[Prusti: internal error]"
warning = "warning:"
non_rust_warnings = ["warning", "warnings", "prusti", "Prusti", "generated", "(lib)", cwd, run_prusti_file]


parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir = os.path.join(parent_dir, "log")
logs = os.listdir(log_dir)


if "err_report" in logs:
    logs.remove("err_report")
else:
    os.mkdir(os.path.join(log_dir, "err_report"))

for log in logs:
    err_file = log[:-4] + ".json"
    err_file_path = os.path.join(log_dir, "err_report",  err_file)
    
    """
    if os.path.exists(err_file_path):
        print("err report for " + log + " exists already")
        continue
    """

    with open(os.path.join(log_dir, log), "r") as f:
        unsupported_reasons = []
        unsupported = 0;
        unsupported_distinct = []
        internal = 0;
        rust_warnings_reasons = []
        rust_warnings = 0;

        for l_no, line in enumerate(f):
            if unsupported_feature in line:
                unsupported += 1
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
                if not err_type in unsupported_reasons:
                    unsupported_reasons.append(err_type)
                
                err_line_distinct = err_line

                for err_word in err_line_distinct:
                    if err_word in err_line_distinct:
                        index =err_line_distinct.index(err_word)
                        err_word = err_word.strip()
                        if "~" in err_word:
                            if "::" in err_line_distinct[index + 1]:
                                crate = err_line_distinct[index + 1].split("::")[0]
                                if "[" in crate:
                                    crate = crate[:crate.index("[")]
                                err_line_distinct = err_line_distinct[:index]
                                err_line_distinct.append(crate)
                            else:
                                err_line_distinct = err_line_distinct[:index]
                        if "{" in err_word: 
                            err_line_distinct = err_line_distinct[:index]
                        if "(" in err_word:
                            err_word = err_word[:err_word.index("(")]
                            err_line_distinct = err_line_distinct[:index]
                            err_line_distinct.append(err_word)
                        if ";" in err_word:
                            err_word = err_word[:err_word.index(";")]
                            err_line_distinct = err_line_distinct[:index]
                            err_line_distinct.append(err_word)
                        if "std::" in err_word:
                            if "(" in err_word:
                                err_word = err_word[:err_word.index("(")]
                            else : 
                                err_word_ = err_word.split("::")
                                err_word = err_word_[0] + "::" + err_word_[1]
                            err_line_distinct = err_line_distinct[:index]
                            err_line_distinct.append(err_word)
                            
                err_type_distinct = ""    
                for err_word in err_line_distinct:
                    err_word = err_word.strip()
                    if "[" in err_word:
                        err_word = err_word.replace("[", "")
                    if "]" in err_word:
                        err_word = err_word.replace("]", "")
                    if not err_word == '':
                        err_type_distinct += err_word + " "
                
                err_type_distinct = err_type_distinct.strip()
                if not err_type_distinct in unsupported_distinct:
                    if not err_type_distinct == "unsupported constant type" and not err_type_distinct =="unsupported constant value":
                        unsupported_distinct.append(err_type_distinct)

            else:
                if warning in line:
                    err_line = line.replace("warning:", "").split(" ")
                    err_type = ""
                    rust = True
                    for warn in non_rust_warnings:
                        if warn in err_line:
                            rust = False
                            break
                    if rust:
                        for err in err_line:
                            err_type += err + " "
                        err_type = err_type.strip()
                        if not err_type in rust_warnings_reasons:
                            rust_warnings_reasons.append(err_type)
                        rust_warnings += 1;
            if internal_errors in line:
                internal += 1

    trace = {
        "unsupported_feature_err_num": unsupported,
        "unsupported_distinct_detailed_num": len(unsupported_reasons),
        "unsupported_distinct_detailed": unsupported_reasons,
        "unsupported_distinct_summary_num": len(unsupported_distinct),
        "unsupported_distinct_summary": unsupported_distinct,
        "rust_warning_num":  rust_warnings,
        "rust_warning_distinct_num": len(rust_warnings_reasons),
        "rust_warning_reasons": rust_warnings_reasons,
        "internal_err_num": internal,
    }

    json_trace = json.dumps(trace, indent= 4)
    with open(os.path.join(log_dir, "err_report", log[:-4] + ".json"), "w") as outfile:
        outfile.write(json_trace)
    

