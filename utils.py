import instTranslator
import G_MEM, G_UTL


def readFile(filename):
    content = []
    with open(filename, 'r', encoding='UTF-8') as f:
        for l in f:
            s = l.strip()
            if s:
                content.append(s)

    return content


def printFwdAndHazard():
    print('[FORWARDING AND HAZARD UNITS] => ')
    if G_MEM.FWD['PC_WRITE'] == 1 and G_MEM.FWD['IF_ID_WRITE'] == 1 and G_MEM.FWD['FWD_A'] == 0 and G_MEM.FWD[
        'FWD_B'] == 0:
        print('We dont have any forwarding or hazard units ')
    else:
        if (G_MEM.FWD['PC_WRITE'] == 0 and G_MEM.FWD['IF_ID_WRITE'] == 0) or (
                G_MEM.ID_EX_CTRL['BRANCH'] == 1 or G_MEM.EX_MEM_CTRL['BRANCH'] == 1):
            print('Stalling (blocking write on PC and IF/ID)...')

        if G_MEM.FWD['FWD_A'] != 0:
            print(
                'FWD_A={} (MEM/WB.ALU_OUT -> A)...'.format(G_MEM.FWD['FWD_A']))

        if G_MEM.FWD['FWD_B'] != 0:
            print(
                'FWD_B={} (MEM/WB.ALU_OUT -> Mux @ aluB and EX/MEM.B)... '.format(G_MEM.FWD['FWD_B']))
    print('______________________________________________________________________________________________')


def printPC():
    print('                                   ╔════[PC]════╗')
    print('                                   ║ [{:08X}] ║'.format(G_MEM.PC))
    print('                                   ╚════════════╝')


def printInstMem():
    print('╔═════╦═════════════════════════════[PROGRAM]═══════════╦════════════════════════╗')

    for i in range(len(G_MEM.INST)):
        print('║ {:>3} ║ 0x{:08X} = 0b{:032b} ║ {:<22} ║'.format(i * 4, G_MEM.INST[i], G_MEM.INST[i],
                                                                 instTranslator.decode(G_MEM.INST[i])))

    print('╚═════╩═════════════════════════════════════════════════╩════════════════════════╝')


def printHistory(clkHistory):
    # Convert clkHistory to history board
    history = [[' ' for i in range(len(clkHistory))] for i in range(len(G_MEM.INST))]
    for i in range(len(clkHistory)):
        for exe in clkHistory[i]:
            if exe[2]:  # Idle
                history[exe[1][0]][i] = ' '
                # history[exe[1][0]][i] = '(' + exe[0] + ')' # Show idle stages
            else:
                history[exe[1][0]][i] = exe[0]

    # Print header and column titles
    print('╔═════╦════════════════════════╦' + '═' * (6 * len(clkHistory)) + '╗')
    print('║ Mem ║ ' + 'Clock #'.center(22) + ' ║', end='')
    for i in range(len(clkHistory)):
        print(str(i).center(5), end=' ')
    print('║')
    print('╠═════╬════════════════════════╬' + '═' * (6 * len(clkHistory)) + '╣')

    # Print history board
    for i in range(len(history)):
        print('║ {:>3} ║ {:>22} ║'.format(i * 4, instTranslator.decode(G_MEM.INST[i])), end='')
        for j in range(len(history[0])):
            print(history[i][j].center(5), end=' ')
        print('║')
    print('╚═════╩════════════════════════╩' + '═' * (6 * len(clkHistory)) + '╝')
