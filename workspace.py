import os, datetime
from dotenv import load_dotenv
load_dotenv()

class Wksp:
    tmp = "/tmp"
    m = os.path.join(tmp, "mir")
    t_l = os.path.join(tmp, "log")

    root = os.getenv('ROOT')
    p = os.path.join(root, "prusti")
    parent = os.path.abspath(os.path.join(root, os.pardir))
    dir = os.path.join(parent, "workspace")

    d_dir = os.path.join(dir, "data")
    d_a = os.path.join(d_dir, "archive")
    d_r = os.path.join(d_dir, "rerun_archive")
    d_z = os.path.join(d_dir, "zipped")


    p_dir = os.path.join(dir, "prusti")
    p_c = os.path.join(p_dir, "crates")
    p_s = os.path.join(p_dir, "summary")

    c_dir = os.path.join(p_dir, "crash")
    c_s = os.path.join(c_dir, "summary")
    c_r = os.path.join(c_dir, "report")


    m_dir = os.path.join(dir, "mir")
    m_s = os.path.join(m_dir, "summary")
    m_rprt = os.path.join(m_dir, "report")
    m_rerun = os.path.join(m_dir, "rerun")
    m_eval = os.path.join(m_dir, "eval")

    r_dir = os.path.join(dir, "result")
    r_e = os.path.join(r_dir, "eval")
    r_s = os.path.join(r_dir, "summary")


    def date():
        date_ = str(datetime.datetime.now()).split(" ")
        date = date_[0] + "." + date_[1].split(".")[0]
        return date

    


