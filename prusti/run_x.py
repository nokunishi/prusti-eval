import os, sys, shutil, threading
from w import wksp
import crates

w = wksp()
lock = threading.Lock()

def setup():
    if not os.path.exists(w.t_l):
        os.mkdir(w.t_l)
    if not os.path.exists(w.d_dir):
        os.mkdir(w.d_dir)
    if not os.path.exists(w.d_a):
        os.mkdir(w.d_a)
    if not os.path.exists(w.d_r):
        os.mkdir(w.d_r)
    if not os.path.exists(w.d_z):
        os.mkdir(w.d_z)

    if not os.path.exists(w.p_dir):
        os.mkdir(w.p_dir)
    if not os.path.exists(w.p_c):
        os.mkdir(w.p_c)
    if not os.path.exists(w.p_s):
        os.mkdir(w.p_s)
    if not os.path.exists(w.c_dir):
        os.mkdir(w.c_dir)
    if not os.path.exists(w.c_s):
        os.mkdir(w.c_s)
    if not os.path.exists(w.c_r):
        os.mkdir(w.c_r)

def zip():
    size = str(len(os.listdir(w.d_a)))

    zipped_dist = os.path.join(w.d_z, 'archive_' + size)
    shutil.make_archive(base_name=zipped_dist, format='zip', root_dir=w.d_a)

    if os.path.exists(zipped_dist + ".zip"):
        shutil.rmtree(w.d_a)
        os.mkdir(w.d_a)


def reset_tmp_default():
    shutil.rmtree(w.m)

    for tmp in os.listdir(w.tmp):
        if ".crate" in tmp:
            os.remove('/tmp/' + tmp)
            if tmp[:-6] in os.listdir(w.tmp):
                shutil.rmtree('/tmp/' + tmp[:-6])


def reset_tmp_failed_tar():
    shutil.rmtree(w.m)

    for tmp in os.listdir(w.tmp):
        if tmp not in os.getenv('TMP_KEY'):
            shutil.rmtree('/tmp/' + tmp)

def download():
    if not os.getcwd() == w.root:
        os.chdir(w.root)
    
    if "--e" in sys.argv: 
        os.system("python3 ./x.py run --bin setup_crates err_report")
    if "--cl" in sys.argv:
        os.system("python3 ./x.py run --bin setup_crates cratelist" )  

def run(arg):
    setup()
    download()
    
    if "--rs" in sys.argv: 
        reset_tmp_default()
    
    if "--rt" in sys.argv: 
        reset_tmp_failed_tar()

    if "--z" in sys.argv: 
        zip()
    
    os.chdir(w.root)

    if arg > 0:
        tmp = os.listdir(w.tmp)
        archive = os.listdir(w.d_a)
        e_reports = os.listdir(w.p_c)

        i = 0

        while i < arg and i < len(tmp): 
            crate = tmp[i].replace(".crate", "")
            crate_txt = tmp[i].replace(".crate", ".txt")
            e_report = tmp[i].replace(".crate", ".json")

            if (crate_txt in archive or e_report in e_reports) \
                and "--redo" not in sys.argv:
                print("Prusti already ran on crate:" + tmp[i])
                arg += 1
    
            else:
                if ".crate" in tmp[i]:
                    print("running on: " + tmp[i])
                    lock.acquire()
                    os.system("python3 ./x.py run --bin run_prusti clippy &> " + w.d_a + "/" + crate_txt + " " + crate)
                    lock.release()
                    crates.run(tmp[i].replace(".crate", ""))
                else:
                    arg += 1
            i += 1
    else:
        crate = sys.argv[1]
        lock.acquire()
        os.system("python3 ./x.py run --bin run_prusti clippy &> " + w.d_a + "/" + crate + ".txt" + " " + crate)
        lock.release()
        crates.run(crate)

        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("invalid number of args")
        raise Exception
    download()
    if sys.argv[1].isdigit():
        run(int(sys.argv[1]))



          

