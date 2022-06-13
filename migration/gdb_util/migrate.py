#!/usr/bin/env python3

import gdb
import json


class CoredumpBreakpoint(gdb.Breakpoint):
    def stop(self):
        gdb.execute(f"generate-core-file dump-{self.location}.core")
        return False


class _Migrate(gdb.Command):
    def __init__(self) -> None:
        gdb.Command.__init__(
            self, "migrate", gdb.COMMAND_BREAKPOINTS, gdb.COMPLETE_FILENAME
        )

    def invoke(self, arg, from_tty) -> None:
        with open(arg) as jsonfile:
            cfg = json.load(jsonfile)
            self.info = cfg["point"]["info"]
            self.filename = cfg["point"]["filename"]
            self.line = cfg["point"]["line"]

        CoredumpBreakpoint(f"{self.filename}:{self.line}", gdb.BP_BREAKPOINT)


_Migrate()
