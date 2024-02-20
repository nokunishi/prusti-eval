import os, sys
from dotenv import load_dotenv
load_dotenv()

class Wksp:
    tmp = "/tmp"
    m = os.path.join(tmp, "mir")

    p_eval = os.getenv('ROOT')

    p = os.path.join(p_eval, "prusti")
    root = os.path.abspath(os.path.join(p_eval, os.pardir))
    dir = os.path.join(root, "workspace")

    a = os.path.join(dir, "archive")
    err = os.path.join(dir, "err_report")
    eval = os.path.join(dir, "eval_summary")
    l = os.path.join(dir, "line_summary")
    c_report = os.path.join(dir, "crash_msg")
    c_summary = os.path.join(dir, "crash_summary")
    r = os.path.join(dir, "rerun_archive")
    z = os.path.join(dir, "zipped")
    m_summary = os.path.join(dir, "mir_summary")

