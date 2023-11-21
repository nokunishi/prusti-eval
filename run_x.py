import os
import sys
import shutil
import time
import asyncio

tmp = os.listdir("/tmp")
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
log_dir = os.path.join(parent_dir, "log")
log = os.listdir(log_dir)

err_dir = ""
err_reports = []
if "err_report" in log:
    err_dir = os.path.join(log_dir, "err_report")
    err_reports = os.listdir(err_dir)

def setup():
    if len(sys.argv) != 2:
        print("incorrect number of args")
        exit()

    os.system("python3 ./x.py run --bin setup_crates" ) 
    print("setup complete")


async def run_prusti(crate_name):
    os.system("python3 ./x.py run --bin run_prusti clippy &> " + log_dir + "/" + crate_name + " crate:" + crate_name)

if __name__ == '__main__':
    setup()
    
    i = 0
    num = int(sys.argv[1])

    while i < num: 
        crate_name = tmp[i][:-6] + ".txt" 
        report_name = tmp[i][:-6] + ".json"

        if crate_name in log or report_name in err_reports:
            print("Prusti already ran on crate:" + tmp[i])
            os.remove('/tmp/' + tmp[i])
            shutil.rmtree('/tmp/' + tmp[i][:-6])
            num += 1
    
        else:
            if ".crate" in tmp[i]:
                start = time.time()
                open(log_dir + "/" + crate_name, "w")
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




          

