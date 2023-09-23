import json
import linecache
import os
import tracemalloc
from .observer import Event, ProcessEvent
from .application import Application


def _trace_top_malloc(snapshot, key_type="lineno", limit=5):
    snapshot = snapshot.filter_traces(
        (
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        )
    )
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print("    %s" % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))

    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


def tracemalloc_start():
    tracemalloc.start()


def tracemalloc_stop():
    snapshot = tracemalloc.take_snapshot()
    _trace_top_malloc(snapshot)


def get_config_from_file(fname: str) -> dict:
    retval = None
    try:
        with open(fname) as f:
            retval = json.load(f)
    except Exception as e:
        print(f"_get_config_from_file exception: '{e}'")
    return retval
