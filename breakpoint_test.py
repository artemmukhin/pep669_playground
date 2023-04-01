# Based on the Mark Shannon's example demonstrating the PEP 669 performance
# https://github.com/python/steering-council/issues/170
# https://gist.github.com/markshannon/da7588db3c883dc2006a727a10e00ca5

import timeit
import sys


def foo():
    for i in range(100_000):
        if i == 50_000:
            pass  # Put breakpoint here


DEBUGGER_ID = 0
BREAKPOINT_LINE = 12
NUMBER_OF_RUNS = 100


def run_with_no_debug():
    """Runs the `foo()` function without a debugger."""
    print("No debug")
    print(timeit.timeit(foo, number=NUMBER_OF_RUNS))
    print()


# Use https://github.com/faster-cpython/cpython/tree/pep-669 implementation
def run_with_pep669():
    """Runs the `foo()` function with a trivial debugger based on PEP 669."""
    print("PEP 669")
    if sys.version_info.minor >= 12:
        break_count = 0

        def pep_669_breakpoint(code, line):
            nonlocal break_count
            if line == BREAKPOINT_LINE:
                break_count += 1
            else:
                return sys.monitoring.DISABLE

        sys.monitoring.register_callback(DEBUGGER_ID, sys.monitoring.events.LINE, pep_669_breakpoint)
        sys.monitoring.set_local_events(foo.__code__, DEBUGGER_ID, sys.monitoring.events.LINE)

        print(timeit.timeit(foo, number=NUMBER_OF_RUNS))

        sys.monitoring.set_local_events(foo.__code__, DEBUGGER_ID, 0)

        assert break_count == NUMBER_OF_RUNS
        print("Breakpoint hit", break_count, "times")
    else:
        print("Skipped")
    print()


def run_with_settrace():
    """
    Runs the `foo()` function with a trivial debugger based on `sys.settrace`.
    This is about as fast as a `sys.settrace` debugger can be if written in Python
    """
    print("sys.settrace")

    break_count = 0
    foo_code = foo.__code__

    def sys_settrace_breakpoint(frame, event, arg):
        nonlocal break_count
        if frame.f_code is not foo_code:
            return None
        if event == "line" and frame.f_lineno == BREAKPOINT_LINE:
            break_count += 1
        return sys_settrace_breakpoint

    sys.settrace(sys_settrace_breakpoint)

    print(timeit.timeit(foo, number=NUMBER_OF_RUNS))

    sys.settrace(None)

    assert break_count == NUMBER_OF_RUNS
    print("Breakpoint hit", break_count, "times")
    print()


if __name__ == '__main__':
    run_with_no_debug()
    run_with_pep669()
    run_with_settrace()
