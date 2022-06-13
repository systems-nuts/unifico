#!/usr/bin/env python3

import gdb


class GenerateCoreBreakpoint(gdb.Breakpoint):
    def stop(self):
        gdb.execute(f"generate-core-file dump.bp.{self.number}.core")
        return False


class _BreakCore(gdb.Command):
    def __init__(self) -> None:
        gdb.Command.__init__(
            self, "break-core", gdb.COMMAND_BREAKPOINTS, gdb.COMPLETE_FILENAME
        )

    def invoke(self, arg, from_tty) -> None:
        gdb.execute("echo doing break-core\\n")


_BreakCore()
