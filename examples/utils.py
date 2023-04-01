# Based on the Mark Shannon's example demonstrating the PEP 669 performance
# https://github.com/python/steering-council/issues/170
# https://gist.github.com/markshannon/da7588db3c883dc2006a727a10e00ca5

import timeit
import sys

DEBUGGER_ID = 0


def run_with_no_debug(main_func, number_of_runs):
    """Runs the `main_func()` function without a debugger."""
    print("No debug")
    print(timeit.timeit(main_func, number=number_of_runs))
    print()


def run_with_pep669(main_func,
                    func_with_break,
                    breakpoint_line,
                    hits_expected,
                    number_of_runs):
    """
    Runs a function with a trivial debugger
    based on PEP 669 implementation https://github.com/faster-cpython/cpython/tree/pep-669.

    :param main_func: The main function to be executed
    :param func_with_break: The function to put a breakpoint in
    :param breakpoint_line: The line number of the breakpoint for the `func_with_break` function
    :param hits_expected: The expected number of times the breakpoint should be hit per run
    :param number_of_runs: Number of times the `main_func` is being executed
    """

    print("PEP 669")
    if sys.version_info.minor >= 12:
        breakpoint_hits = 0
        code_with_break = func_with_break.__code__

        def pep_669_breakpoint(code, line):
            nonlocal breakpoint_hits
            if line == breakpoint_line:
                breakpoint_hits += 1
            else:
                return sys.monitoring.DISABLE

        sys.monitoring.register_callback(DEBUGGER_ID, sys.monitoring.events.LINE, pep_669_breakpoint)
        sys.monitoring.set_local_events(code_with_break, DEBUGGER_ID, sys.monitoring.events.LINE)

        print(timeit.timeit(main_func, number=number_of_runs))

        sys.monitoring.set_local_events(code_with_break, DEBUGGER_ID, 0)

        print("Breakpoint hit", breakpoint_hits, "times")
        assert breakpoint_hits == hits_expected * number_of_runs
    else:
        print("Skipped")
    print()


def run_with_settrace(main_func,
                      func_with_break,
                      breakpoint_line,
                      hits_expected,
                      number_of_runs):
    """
    Runs a function with a trivial debugger based on `sys.settrace`.
    This is about as fast as a `sys.settrace` debugger can be if written in Python.

    :param main_func: The main function to be executed
    :param func_with_break: The function to put a breakpoint in
    :param breakpoint_line: The line number of the breakpoint for the `func_with_break` function
    :param hits_expected: The expected number of times the breakpoint should be hit per run
    :param number_of_runs: Number of times the `main_func` is being executed
    """

    print("sys.settrace")

    breakpoint_hits = 0
    code_with_break = func_with_break.__code__

    def sys_settrace_breakpoint(frame, event, arg):
        nonlocal breakpoint_hits
        if frame.f_code is not code_with_break:
            return None
        if event == "line" and frame.f_lineno == breakpoint_line:
            breakpoint_hits += 1
        return sys_settrace_breakpoint

    sys.settrace(sys_settrace_breakpoint)

    print(timeit.timeit(main_func, number=number_of_runs))

    sys.settrace(None)

    print("Breakpoint hit", breakpoint_hits, "times")
    assert breakpoint_hits == hits_expected * number_of_runs
    print()
