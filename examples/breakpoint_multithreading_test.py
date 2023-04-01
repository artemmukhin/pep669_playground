import threading
from time import sleep

from utils import run_with_no_debug, run_with_pep669, run_with_settrace


def worker():
    for _ in range(3):
        sleep(0.1)  # break


def main_func():
    t1 = threading.Thread(target=worker)
    t1.start()

    t2 = threading.Thread(target=worker)
    t2.start()

    t1.join()
    t2.join()


if __name__ == '__main__':
    breakpoint_line = 9
    hits_expected = 2 * 3  # two threads with three iterations each
    number_of_runs = 1

    run_with_no_debug(main_func, number_of_runs)
    run_with_pep669(main_func, worker, breakpoint_line, hits_expected, number_of_runs)

    # `sys.settrace` is thread-specific, so the breakpoint will not hit
    run_with_settrace(main_func, worker, breakpoint_line, 0, number_of_runs)
