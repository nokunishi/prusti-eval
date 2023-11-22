import os
import sys
import shutil
import asyncio
import uuid

tmp = os.listdir("/tmp")
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir = os.path.join(parent_dir, "log")
log = os.listdir(log_dir)
archive_dir = os.path.join(log_dir, "archive")
archive = os.listdir(archive_dir)

zipped_dist = os.path.join(log_dir, "zipped", 'archive_' + str(len(archive)) + "-" + str(uuid.uuid4()))
shutil.make_archive(base_name=zipped_dist, format='zip', root_dir=os.path.join(log_dir, "archive"))

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

    if len(sys.argv) != 2:
        print("incorrect number of args")
        exit()

    os.system("python3 ./x.py run --bin setup_crates" ) 
    print("setup complete")
    return err_reports


async def run_prusti(crate_name):
    os.system("python3 ./x.py run --bin run_prusti clippy &> " + archive_dir + "/" + crate_name + " crate:" + crate_name)

if __name__ == '__main__':
    zip()
    err_reports = setup()
    
    i = 0
    num = int(sys.argv[1])

    while i < num and i < len(tmp): 
        crate_name = tmp[i][:-6] + ".txt" 
        report_name = tmp[i][:-6] + ".json"

        if crate_name in archive or report_name in err_reports:
            print("Prusti already ran on crate:" + tmp[i])
            os.remove('/tmp/' + tmp[i])
            shutil.rmtree('/tmp/' + tmp[i][:-6])
            num += 1
    
        else:
            if ".crate" in tmp[i]:
                print("running on: " + tmp[i])
                try: 
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(asyncio.wait_for(run_prusti(crate_name), 180))
                except:
                    print("failed to run Prusti on " + crate_name)
            else:
                num += 1
        i += 1

    import err_log




          

