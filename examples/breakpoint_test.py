from utils import run_with_no_debug, run_with_pep669, run_with_settrace


def main_func():
    for i in range(100_000):
        if i == 50_000:
            pass  # break


if __name__ == '__main__':
    breakpoint_line = 7
    hits_expected = 1
    number_of_runs = 100

    run_with_no_debug(main_func, number_of_runs)
    run_with_pep669(main_func, main_func, breakpoint_line, hits_expected, number_of_runs)
    run_with_settrace(main_func, main_func, breakpoint_line, hits_expected, number_of_runs)
