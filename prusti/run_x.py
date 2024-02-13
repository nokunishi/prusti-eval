import os, sys, shutil
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w


cwd = os.getcwd()

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
        os.mkdir(w.c_report)

    if "eval_summary" not in log_dir:
        os.mkdir(w.eval)
    
    if "line_summary" not in log_dir:
        os.mkdir(w.l)
    
    if "panic_summary" not in log_dir:
        os.mkdir(w.c_summary)

    if "rerun_archive" not in log_dir:
        os.mkdir(w.r)

    if "zipped" not in log_dir:
        os.mkdir(w.z)


    if len(sys.argv) < 2:
        print("incorrect number of args")
        exit()
    print("setup complete")

def reset_tmp_default():
    tmp_dir = os.listdir(w.tmp)

    for tmp in tmp_dir:
        if ".crate" in tmp:
            os.remove('/tmp/' + tmp)
            if tmp[:-6] in tmp_dir:
                shutil.rmtree('/tmp/' + tmp[:-6])

def reset_tmp_failed_tar():
    tmp_dir = os.listdir(w.tmp)
    tmp_key = os.getenv('TMP_KEY')

    for tmp in tmp_dir:
        if tmp not in tmp_key:
            shutil.rmtree('/tmp/' + tmp)

def main():

    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    setup()

    if not os.getcwd() == w.p_eval:
        os.chdir(w.p_eval)
    
    if "--e":
        os.system("python3 ./x.py run --bin setup_crates err_report")
    if "--cl":
        os.system("python3 ./x.py run --bin setup_crates cratelist" )  
    
    os.chdir(cwd)
    
    if "--r" in sys.argv: 
        reset_tmp_default()
    
    if "--rt" in sys.argv: 
        reset_tmp_failed_tar()

    if "--z" in sys.argv: 
        zip()
    
    if "--a" in sys.argv:
        tmp = os.listdir(w.tmp)
        archive = os.listdir(w.a)
        err_reports = os.listdir(w.err)

        i = 0
        num = int(sys.argv[1])

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
        else:
            crate = sys.argv[1]
            if ".txt" not in crate:
                crate += ".txt"
            os.system("python3 ./x.py run --bin run_prusti clippy &> " + w.a + "/" + crate + " " + crate)

    if "--log" in sys.argv:
        import err_log


if __name__ == '__main__':
    main()



          

