import os
import sys
import shutil
from workspace import Wksp as w

def zip():
    archive = os.listdir(w.a)   

    if (len(archive) > 100) :   
        zipped_dist = os.path.join(w.dir, "zipped", 'archive_' + str(len(archive)))
        shutil.make_archive(base_name=zipped_dist, format='zip', root_dir=os.path.join(w.dir, "archive"))

        if os.path.exists(zipped_dist + ".zip"):
            shutil.rmtree(w.a)
            os.mkdir(w.a)


def setup():
    log_dir = os.listdir(w.dir)

    if "err_report" not in log_dir:
        os.mkdir(w.err)

    if "panic_report" not in log_dir:
        os.mkdir(w.p_report)

    if "eval_summary" not in log_dir:
        os.mkdir(w.eval)
    
    if "line_summary" not in log_dir:
        os.mkdir(w.l)
    
    if "panic_summary" not in log_dir:
        os.mkdir(w.p_summary)

    if "rerun_archive" not in log_dir:
        os.mkdir(w.r)

    if "zipped" not in log_dir:
        os.mkdir(w.z)


    if len(sys.argv) < 2:
        print("incorrect number of args")
        exit()

    os.system("python3 ./x.py run --bin setup_crates cratelist" ) 
    print("setup complete")

def reset_tmp():
    tmp_dir = os.listdir(w.tmp)

    for tmp in tmp_dir:
        if ".crate" in tmp:
            os.remove('/tmp/' + tmp)
            if tmp[:-6] in tmp_dir:
                shutil.rmtree('/tmp/' + tmp[:-6])

def main():

    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    if "--r" in sys.argv: 
        reset_tmp()
        return 

    if "--z" in sys.argv: 
        zip()
        return 
    
    i = 0
    num = int(sys.argv[1])

    tmp = os.listdir(w.tmp)
    archive = os.listdir(w.a)
    err_reports = os.listdir(w.err)

    while i < num and i < len(tmp): 
        crate = tmp[i][:-6] + ".txt" 
        report_name = tmp[i][:-6] + ".json"

        if crate in archive or report_name in err_reports:
            print("Prusti already ran on crate:" + tmp[i])
            os.remove('/tmp/' + tmp[i])
            shutil.rmtree('/tmp/' + tmp[i][:-6])
            num += 1
    
        else:
            if ".crate" in tmp[i]:
                print("running on: " + tmp[i])
                try: 
                    os.system("python3 ./x.py run --bin run_prusti clippy &> " + w.a + "/" + crate + " " + crate)
                except:
                    print("failed to run Prusti on " + crate)
            else:
                num += 1
        i += 1

    import err_log


if __name__ == '__main__':
    main()



          

