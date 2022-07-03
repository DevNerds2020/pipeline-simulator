import sys

import G_MEM
import G_UTL
import instTranslator
import stages
import utils


def main():
    filename = 'test1.txt'

    # Read
    program = utils.readFile(filename)
    programLength = len(program)

    # Encode and load .asm into memory
    for i in range(programLength):
        # Remove comments
        if not program[i] or program[i][0] == '#': continue
        encoded = instTranslator.encode(program[i].split('#')[0])
        G_MEM.INST.append(encoded)

    # Print the program as loaded
    utils.printInstMem()
    print()

    # Run simulation, will run until all pipeline stages are empty
    clkHistory = []
    clk = 0
    while clk == 0 or (
            G_UTL.ran['IF'][1] != 0 or G_UTL.ran['ID'][1] != 0 or G_UTL.ran['EX'][1] != 0 or G_UTL.ran['MEM'][1] != 0):
        print(' '.join(['─' * 20, f'CLK #{clk}', '─' * 20]))

        clkHistory.append([])

        # Run all stages 'in parallel'
        stages.EX_fwd()
        stages.WB()
        stages.MEM()
        stages.EX()
        stages.ID()
        stages.IF()
        stages.ID_hzd()

        # Keep only the 32 LSB from memory
        for i in range(len(G_MEM.REGS)):
            G_MEM.REGS[i] &= 0xFFFFFFFF
        for i in range(len(G_MEM.DATA)):
            G_MEM.DATA[i] &= 0xFFFFFFFF

        # Report if stage was run
        if G_UTL.data_hzd or G_UTL.ctrl_hzd:
            utils.printFwdAndHazard()
        for stage in ['IF', 'ID', 'EX', 'MEM', 'WB']:
            if G_UTL.ran[stage][1] != 0:
                idle = ' (idle)' if G_UTL.wasIdle[stage] else ''
                clkHistory[clk].append((stage, G_UTL.ran[stage], G_UTL.wasIdle[stage]))
                print(
                    f'> Stage {stage}: #{G_UTL.ran[stage][0] * 4} = [{instTranslator.decode(G_UTL.ran[stage][1])}]{idle}.')

        utils.printPC()
        clk += 1

        try:
            opt = input('| step: [ENTER] | end: [E|Q] | ').lower()
            skipSteps = (opt == 'e' or opt == 'q')
        except KeyboardInterrupt:
            print('\nExecution aborted.')
            exit()

    print()

    print()
    print(f'Program ran in {clk} clocks.')
    print()

    utils.printHistory(clkHistory)
    print("register file => ", G_MEM.REGS)
    print("memory file =>", G_MEM.DATA)

    return


if __name__ == '__main__':
    # To print (pipe to file) pretty borders on Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='UTF-8')

    main()
