import os
import sys
import shutil
import asyncio
import uuid

tmp_dir = os.listdir("/tmp")
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir = os.path.join(parent_dir, "log")
log = os.listdir(log_dir)
archive_dir = os.path.join(log_dir, "archive")
archive = os.listdir(archive_dir)

""" python3 run_x.py num rerun"""

def zip():
    if (len(archive) > 100) :   
        zipped_dist = os.path.join(log_dir, "zipped", 'archive_' + str(len(archive)))
        shutil.make_archive(base_name=zipped_dist, format='zip', root_dir=os.path.join(log_dir, "archive"))

        if os.path.exists(zipped_dist + ".zip"):
            shutil.rmtree(archive_dir)
            os.mkdir(archive_dir)


def setup():
    err_dir = ""
    err_reports = []  

    if "err_report" in log:
        err_dir = os.path.join(log_dir, "err_report")
        err_reports = os.listdir(err_dir)

    if len(sys.argv) < 2:
        print("incorrect number of args")
        exit()

    os.system("python3 ./x.py run --bin setup_crates" ) 
    print("setup complete")
    return err_reports

def reset_tmp():
    for tmp in tmp_dir:
        if ".crate" in tmp:
            os.remove('/tmp/' + tmp)
            if tmp[:-6] in tmp_dir:
                shutil.rmtree('/tmp/' + tmp[:-6])

def main():
    
    if "reset" in sys.argv: 
        reset_tmp()
        return 

    zip()
    err_reports = setup()
    
    i = 0
    num = int(sys.argv[1])

    while i < num and i < len(tmp_dir): 
        crate_name = tmp_dir[i][:-6] + ".txt" 
        report_name = tmp_dir[i][:-6] + ".json"

        if crate_name in archive or report_name in err_reports:
            print("Prusti already ran on crate:" + tmp_dir[i])
            os.remove('/tmp/' + tmp_dir[i])
            shutil.rmtree('/tmp/' + tmp_dir[i][:-6])
            num += 1
    
        else:
            if ".crate" in tmp_dir[i]:
                print("running on: " + tmp_dir[i])
                try: 
                    os.system("python3 ./x.py run --bin run_prusti clippy &> " + archive_dir + "/" + crate_name + " " + crate_name)
                except:
                    print("failed to run Prusti on " + crate_name)
            else:
                num += 1
        i += 1

    import err_log


if __name__ == '__main__':
    main()



          

