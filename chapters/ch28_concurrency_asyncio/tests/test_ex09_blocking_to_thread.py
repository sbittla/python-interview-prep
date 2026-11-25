import asyncio
import subprocess
import sys


def test_examples(load):
    m = load("ex09_blocking_to_thread")
    assert asyncio.run(m.call_blocking()) == (False, 0)
    assert asyncio.run(m.call_to_thread()) == (True, 3)


def test_run_in_executor(load):
    m = load("ex09_blocking_to_thread")
    assert asyncio.run(m.call_run_in_executor()) == (True, 3)


def test_repeatable(load):
    m = load("ex09_blocking_to_thread")
    assert all(asyncio.run(m.call_to_thread()) == (True, 3) for _ in range(5))


def test_cpu_in_process_runs_as_script(load):
    # ProcessPoolExecutor children import the worker by module name: run the file as __main__.
    m = load("ex09_blocking_to_thread")
    proc = subprocess.run([sys.executable, m.__file__], capture_output=True, text=True,
                          timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert "CPU work in a process pool: True" in proc.stdout
