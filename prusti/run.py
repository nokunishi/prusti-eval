import time
import run_x as x

if __name__ == "__main__":
    i = 0
    """
    while i < len(os.listdir("/tmp")):
        x.run(5)
        i += 5
        time.sleep(30 * 60)
    """
    while i < 5:
        x.run(2)
        i += 2
        time.sleep(30)


        