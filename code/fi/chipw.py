import sys
import time
import chipwhisperer as cw


SCOPETYPE = 'OPENADC'
PLATFORM = 'CW303'


def init():
    try:
        if not scope.connectStatus:
            scope.con()
    except NameError:
        scope = cw.scope()

    target = cw.target(scope)

    time.sleep(0.05)
    scope.default_setup()

    return scope, target


if "STM" in PLATFORM or PLATFORM == "CWLITEARM" or PLATFORM == "CWNANO":
    prog = cw.programmers.STM32FProgrammer
elif PLATFORM == "CW303" or PLATFORM == "CWLITEXMEGA":
    prog = cw.programmers.XMEGAProgrammer
else:
    prog = None


def reset_target(scope):
    if PLATFORM == "CW303" or PLATFORM == "CWLITEXMEGA":
        scope.io.pdic = 'low'
        time.sleep(0.05)
        scope.io.pdic = 'high_z'  # XMEGA doesn't like pdic driven high
        time.sleep(0.05)
    else:
        scope.io.nrst = 'low'
        time.sleep(0.05)
        scope.io.nrst = 'high'
        time.sleep(0.05)


def usage(progname):
    print(f'usage: {progname} <firmware path>')
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage(sys.argv[0])

    fw_path = sys.argv[1]

    scope, target = init()

    cw.program_target(scope, prog, fw_path)

    target.flush()

    reset_target(scope)

    response = target.read()

    print(f'{response!r}')
