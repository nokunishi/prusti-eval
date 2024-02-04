import os

class Wksp:
    p_eval = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    wksp = os.path.abspath(os.path.join(p_eval, os.pardir))
    dir = os.path.join(wksp, "workspace")

    a = os.path.join(dir, "archive")
    err = os.path.join(dir, "err_report")
    eval = os.path.join(dir, "eval_summary")
    l = os.path.join(dir, "line_summary")
    p_report = os.path.join(dir, "panic_report")
    p_summary = os.path.join(dir, "panic_summary")
    r = os.path.join(dir, "rerun_archive")
    z = os.path.join(dir, "zipped")
