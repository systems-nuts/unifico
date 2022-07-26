#!/usr/bin/env python3

import gdb
import json
import time

tstamp = None


class CoredumpBreakpoint(gdb.Breakpoint):
    def stop(self):
        gdb.execute("generate-core-file dump-{}.core".format(self.location))
        return True


class _Migrate(gdb.Command):
    def __init__(self):
        gdb.Command.__init__(
            self, "migrate", gdb.COMMAND_BREAKPOINTS, gdb.COMPLETE_FILENAME
        )

    def invoke(self, arg, from_tty):
        with open(arg) as jsonfile:
            cfg = json.load(jsonfile)
            self.info = cfg["point"]["info"]
            self.filename = cfg["point"]["filename"]
            self.line = cfg["point"]["line"]

        CoredumpBreakpoint(
            "{}:{}".format(self.filename, self.line), gdb.BP_BREAKPOINT
        )


class _TimedRun(gdb.Command):
    def __init__(self):
        gdb.Command.__init__(
            self, "timed-run", gdb.COMMAND_RUNNING, gdb.COMPLETE_FILENAME
        )

    def invoke(self, arg, from_tty):
        global tstamp
        tstamp = time.time()

        gdb.execute("run")


def cbpHandler(bpEvent):
    if isinstance(bpEvent, gdb.BreakpointEvent):
        bps = bpEvent.breakpoints
        if len(bps) == 1 and isinstance(bps[0], CoredumpBreakpoint):
            global tstamp
            t = time.time()
            elapsed = t - tstamp
            tstamp = t
            print(elapsed)

            gdb.execute("cont")

    return


def exitedHandler(exitEvent):
    global tstamp
    elapsed = time.time() - tstamp
    print(elapsed)

    return


gdb.events.stop.connect(cbpHandler)
gdb.events.exited.connect(exitedHandler)

_Migrate()
_TimedRun()
