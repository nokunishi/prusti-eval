import os
import json
import operator
import datetime


parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
err_report_dir = os.path.join(parent_dir, "log", "err_report")
err_reports = os.listdir(err_report_dir)
stat_report_dir =  os.path.join(parent_dir, "log", "eval_summary")

{
  "unsupported_feature_err_num": 3,
  "unsupported_distinct_detailed_num": 3,
  "unsupported_distinct_detailed": [],
  "unsupported_distinct_summary_num": 3,
  "unsupported_distinct_summary": [],
  "rust_warning_num": 5,
  "rust_warning_distinct_num": 4,
  "rust_warning_reasons": [],
  "internal_err_num": 0,
  "has_panic_reports": False,
  "verification_failed_num_total": 0,
  "verification_failed_num_distinct": 0,
  "verification_failed_reason": []
}

unsupported_total = 0;

rust_warning = 0;
internal_error = 0;
panicked = 0;

unsupported = {}
unsupported_detailed = {}
rust_reason = {}

failed_total = 0;
failed_reason = {}

num_reports = len(err_reports)

for report in err_reports:
    with open(os.path.join(err_report_dir, report), "r") as f:
        f = json.load(f)
        unsupported_total += f["unsupported_feature_total_num"]
        try:
            rust_warning += f["rust_warning_total_num"]
            internal_error += f["internal_err_total_num"]
        except:
            print(report)
        failed_total += f["verification_failed_num_total"]
        if f["has_panic_reports"] == True:
            panicked += 1

        unsuppported_errs = f["unsupported_summary"]

        for err in f["unsupported_detailed"]:
            if err in unsupported_detailed:
                unsupported_detailed[err]["num"] += 1
            else:
                unsupported_detailed[err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }
        
        for err in f["unsupported_summary"]:
            if err in unsupported:
                unsupported[err]["num"] += 1
            else:
                unsupported[err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }

        for rust_err in f["rust_warning_reasons"]:
            if rust_err in rust_reason:
                rust_reason[rust_err]["num"] += 1
            else:
                rust_reason[rust_err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }

        for err in f["verification_failed_reason"]:
            if err in failed_reason:
                failed_reason[err]["num"] += 1
            else:
                failed_reason[err] = {
                    "num": 1,
                    "i.e.": report[:-5]
                }

unsupported = sorted_dict = dict(sorted(unsupported.items(),  key=lambda x: x[1]['num'], reverse=True))
unsupported_detailed = sorted_dict = dict(sorted(unsupported_detailed.items(), key=lambda x: x[1]['num'], reverse=True))
rust_reason = sorted_dict = dict(sorted(rust_reason.items(),  key=lambda x: x[1]['num'], reverse=True))
failed_reason = sorted_dict = dict(sorted(failed_reason.items(), key=lambda x: x[1]['num'], reverse=True))
stats = {
    "number_of_crates": num_reports,
    "panicked_total": panicked,
    "verification_failed_total": failed_total,
    "verification_failed_distinct_num": len(failed_reason),
    "verification_failed_reason": failed_reason,
    "unsupported_features_total": unsupported_total,
    "unsupported_feature_grouped_num": len(unsupported),
    "unsupported_feature_summary": unsupported,
    "unsupported_feature_distinct_num": len(unsupported_detailed),
    "unsupported_feature_detailed": unsupported_detailed,
    "rust_warning_total": rust_warning,
    "rust_warning_distinct_num": len(rust_reason),
    "rust_warning_summary": rust_reason,
    "internal_errors_total": internal_error,
}

json_stats = json.dumps(stats, indent= 8)
with open(os.path.join(stat_report_dir, "summary-" + str(datetime.datetime.now()) + ".json"), "w") as outfile:
    print("writing to summary")
    outfile.write(json_stats)





