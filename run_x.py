import os
import sys
from contextlib import contextmanager

def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd

@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
       stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied


stdout_fd = sys.stdout.fileno()
with open('tr.txt', 'w') as f, stdout_redirected(f):
    import subprocess
    import io
    proc = subprocess.Popen(['python3','x.py', "run"],stdout=subprocess.PIPE)
    line = proc.stdout.readline();
    line = line.decode("utf-8")
    print(proc.stdout)
    os.write(stdout_fd, b'it is redirected now\n')
    os.system('echo this is also redirected')
print('this is goes back to stdout')



"""os.system("python3 ./x.py setup")
os.system("python3 ./x.py build")"""

""" os.system("python3 ./x.py run")"""
"""
import subprocess
proc = subprocess.Popen(['python3','x.py', "run"],stdout=subprocess.PIPE)
sys.std.flush()
while True:
  line = proc.stdout.readline()
  if not line:
    break
  #the real code does filtering here
  print ("test:", line.rstrip())"""

