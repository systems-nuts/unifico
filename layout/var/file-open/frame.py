import gdb
import platform


BORDER_LIMIT = 76
STACK_BORDER = BORDER_LIMIT * "+"
FRAME_BORDER = BORDER_LIMIT * "="


class PrintFrame(gdb.Command):
    """
    Display the stack memory layout for all frames up to this point.
    """

    def __init__(self):
        super(PrintFrame, self).__init__("frame_info", gdb.COMMAND_STACK)

    def invoke(self, arg, from_tty):
        try:
            print(STACK_BORDER)

            frame = gdb.newest_frame()
            while frame is not None:
                if platform.machine() == "x86_64":
                    stack_pointer_name = "rsp"
                    base_pointer_name = "rbp"
                elif platform.machine() == "aarch64":
                    stack_pointer_name = "sp"
                    base_pointer_name = "x29"
                else:
                    print("Unsupported architecture.")
                    exit()

                stack_pointer = frame.read_register(stack_pointer_name)
                base_pointer = frame.read_register(base_pointer_name)

                gdb.execute("up-silently 1")
                old_stack_pointer = gdb.parse_and_eval(
                    "${}".format(stack_pointer_name)
                )
                gdb.execute("down-silently 1")

                # print(stack_pointer)
                # print(old_stack_pointer)

                if (
                    base_pointer == stack_pointer and frame.older() is not None
                ):  # and old_stack_pointer > stack_pointer + 16:
                    addr_diff = int(old_stack_pointer) - int(stack_pointer)
                else:
                    addr_diff = int(base_pointer) - int(stack_pointer) + 16

                words = addr_diff / 4
                x_cmd = "x/{}x {}".format(int(words), stack_pointer)
                gdb.execute(x_cmd)

                frame = frame.older()
                gdb.execute("up-silently 1")
                print(FRAME_BORDER)

        except gdb.error:
            print("gdb got an error. Maybe we are not currently running?")


PrintFrame()
