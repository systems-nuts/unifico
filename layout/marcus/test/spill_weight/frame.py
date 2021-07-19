import gdb
import platform

FILE = None #["vec.c"]
FUNC = ["func", "saved"]
OUT = "./test_frame"
LOG = 0 # 0 for all, 1 for changes only
fout = open(OUT, 'w')

def fprint(s):
    fout.write(s)

def print_frame():
    try:
        frame = gdb.newest_frame()
        fdict = {}
        while frame is not None:

            if platform.machine() == 'x86_64':
                stack_pointer_name = 'rsp'
                base_pointer_name = 'rbp'
            elif platform.machine() == 'aarch64':
                stack_pointer_name = 'sp'
                base_pointer_name = 'x29'
            else:
                print('Unsupported architecture.')
                exit()

            stack_pointer = frame.read_register(stack_pointer_name)
            base_pointer = frame.read_register(base_pointer_name)

            gdb.execute('up-silently 1')
            old_stack_pointer = gdb.parse_and_eval('${}'.format(stack_pointer_name))
            gdb.execute('down-silently 1')

            if base_pointer == stack_pointer and frame.older() is not None:# and old_stack_pointer > stack_pointer + 16: 
                addr_diff = int(old_stack_pointer) - int(stack_pointer) 
            else:
                addr_diff = int(base_pointer) - int(stack_pointer) + 16

            words =  addr_diff / 4 - 4
            x_cmd = 'x/{}x {}'.format(int(words), stack_pointer) 
            fdict[frame.name()] = gdb.execute(x_cmd, to_string=True)

            frame = frame.older()
            gdb.execute('up-silently 1')

        return fdict
    except gdb.error:
        print("gdb got an error. Maybe we are not currently running?")


class TestAllFrame(gdb.Command):
    """
    find all function sites and add break point on it
    """
    def __init__ (self):
        super(TestAllFrame, self).__init__ ("all_frame", gdb.COMMAND_STACK)

    def invoke(self, arg, from_tty):
        try:
            if FILE is not None:
                for cfile in FILE:
                    gdb.execute('rbreak ' + cfile + ':.')
            if FUNC is not None:
                for f in FUNC:
                    gdb.execute('break ' + f)
            gdb.execute('r')
            fsave = {}
            cnt = 0
            while True:
                fdict = print_frame()
                fprint("FRAME" + str(cnt) + '\n')
                # output entire frames
                if LOG == 0:
                    for fname in fdict:
                        fprint(fname + ":\n" + fdict[fname])
                    fprint('\n')
                # only output changes
                elif LOG == 1:
                    fcurr = gdb.newest_frame().name()
                    fprint(fcurr + ":")
                    if len(fdict[fcurr]) != 0:
                        fprint('\n' + fdict[fcurr])
                    else:
                        fprint("Empty Frame\n")
                    
                    # changed slot update
                    for fname in fsave:
                        if fname in fdict:
                            # if stack positions for same function are not mapping 
                            # we have arrived another function stack
                            if fsave[fname][0:11] != fdict[fname][0:11]:
                                fprint("Stack " + fname + " position changed:\n")
                                fprint("FROM " + old_value[0:11] + " TO " + new_value[0:11] + '\n')
                                continue

                            # find changed slots for stack
                            old_value = fsave[fname].split('\n')
                            new_value = fdict[fname].split('\n')
                            change = []
                            for i in range(len(old_value)):
                                if old_value[i] != new_value[i]:
                                    change.append(i)
                            if len(change) != 0:
                                fprint("CHANGE\n" + fname + ":\n")
                                for i in change:
                                    fprint(old_value[i] + " >\n" + new_value[i] + "\n")
                    # save curr frames
                    for fname in fdict:
                        fsave[fname] = fdict[fname]
                    fprint('\n')

                gdb.execute('c')
                cnt += 1
                if len(gdb.selected_inferior().threads()) == 0:
                    print("INFERIOR EXIT")
                    break
            
            fout.close()
        except gdb.error:
            print("gdb got an error. Maybe we are not currently running?")


TestAllFrame()
