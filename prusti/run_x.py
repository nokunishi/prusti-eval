import os, sys, shutil
from w import wksp

w = wksp()

def setup():
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
    if not os.path.exists(w.p_err):
        os.mkdir(w.p_err)
    if not os.path.exists(w.p_eval):
        os.mkdir(w.p_eval)
    if not os.path.exists(w.p_line):
        os.mkdir(w.p_line)
    if not os.path.exists(w.c_dir):
        os.mkdir(w.c_dir)
    if not os.path.exists(w.c_summary):
        os.mkdir(w.c_summary)

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
    
    if "--e":
        os.system("python3 ./x.py run --bin setup_crates err_report")
    if "--cl":
        os.system("python3 ./x.py run --bin setup_crates cratelist" )  
    
    os.chdir(w.p)

def main():
    if len(sys.argv) < 2:
        print("invalid number of args")
        return
    
    setup()
    download()
    
    if "--rs" in sys.argv: 
        reset_tmp_default()
    
    if "--rt" in sys.argv: 
        reset_tmp_failed_tar()

    if "--z" in sys.argv: 
        zip()
    
    if "--a" in sys.argv:
        tmp = os.listdir(w.tmp)
        archive = os.listdir(w.d_a)
        e_reports = os.listdir(w.p_err)

        i = 0
        num = int(sys.argv[1])

        while i < num and i < len(tmp): 
            crate = tmp[i].replace(".crate", ".txt")
            e_report = tmp[i].replace(".crate", ".json")

            if (crate in archive or e_report in e_reports) \
                and "--redo" not in sys.argv:
                print("Prusti already ran on crate:" + tmp[i])
                num += 1
    
            else:
                if ".crate" in tmp[i]:
                    print("running on: " + tmp[i])
                    os.system("python3 ./x.py run --bin run_prusti clippy &> " + w.d_a + "/" + crate + " " + crate)
                else:
                    num += 1
            i += 1
        else:
            crate = sys.argv[1]
            if ".txt" not in crate:
                crate += ".txt"
            os.system("python3 ./x.py run --bin run_prusti clippy &> " + w.d_a + "/" + crate + " " + crate)

    if "--log" in sys.argv:
        import err
        
if __name__ == '__main__':
    main()



          

