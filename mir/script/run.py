import os, sys
import threading

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(1, os.getenv('ROOT'))
from workspace import Wksp as w

cwd = os.getcwd()
root = os.path.abspath(os.path.join(cwd, os.pardir))
mir_rust = os.path.join(root, "mir-rust")

lock = threading.Lock()

def run():
    os.chdir(mir_rust);
    lock.acquire()
    os.system("cargo build")
    lock.release()

    os.system("cargo run ")

if __name__ == "__main__":
    run()