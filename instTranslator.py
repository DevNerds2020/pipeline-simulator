import G_UTL


# getting the instruction for encoding
def encode(inst):
    inst = inst.replace(',', '')  # Ignore commas

    # Replace register names with its index
    for i in range(len(G_UTL.regNames)):
        inst = inst.replace(G_UTL.regNames[i], str(i))
    inst = inst.replace('$', '')  # for deleting the $ sign

    inst = inst.split()

    if inst[0] in G_UTL.rTypeWords:  # R-Type
        out = 0b000000 << 5

        if inst[0] == 'sll' or inst[0] == 'srl':
            rd, rt, shamt = [int(i, 0) for i in inst[1:]]  # Accepts any base (e.g. 0b, 0o, 0x)

            # Check for under/overflow
            nrd, nrt, nshamt = rd & 0x1F, rt & 0x1F, shamt & 0x1F
            rd, rt, shamt = nrd, nrt, nshamt

            # Encode
            out |= rt
            out <<= 5
            out |= rd
            out <<= 5
            out |= shamt
            out <<= 6
            out |= G_UTL.rTypeWords[inst[0]]

        else:  # R-Types other than sll/srl
            rd, rs, rt = [int(i, 0) for i in inst[1:]]  # Accepts any base (e.g. 0b, 0o, 0x)

            # Check for under/overflow
            nrd, nrs, nrt = rd & 0x1F, rs & 0x1F, rt & 0x1F
            rd, rs, rt = nrd, nrs, nrt

            # Encode
            out |= rs
            out <<= 5
            out |= rt
            out <<= 5
            out |= rd
            out <<= 11
            out |= G_UTL.rTypeWords[inst[0]]

    elif inst[0] == 'lw' or inst[0] == 'sw':
        opcode = {'lw': 0b100011, 'sw': 0b101011}
        out = opcode[inst[0]] << 5

        inst[2] = inst[2].split('(')
        inst[2:] = inst[2][0], inst[2][1][:-1]

        rt, offset, rs = [int(i, 0) for i in inst[1:]]  # Accepts any base (e.g. 0b, 0o, 0x)

        # Check for under/overflow
        nrt, nrs, noffset = rt & 0x1F, rs & 0x1F, offset & 0xFFFF
        rt, rs, offset = nrt, nrs, noffset

        # Encode
        out |= rs
        out <<= 5
        out |= rt
        out <<= 16
        out |= offset

    elif inst[0] == 'beq':
        out = 0b000100 << 5

        rs, rt, offset = [int(i, 0) for i in inst[1:]]  # Accepts any base (e.g. 0b, 0o, 0x)

        # Check for under/overflow
        nrs, nrt, noffset = rs & 0x1F, rt & 0x1F, offset & 0xFFFF

        rs, rt, offset = nrs, nrt, noffset

        # Encode
        out |= rs
        out <<= 5
        out |= rt
        out <<= 16
        out |= offset

    elif inst[0] == 'addi':
        out = 0b001000 << 5

        rt, rs, imm = [int(i, 0) for i in inst[1:]]  # Accepts any base (e.g. 0b, 0o, 0x)

        # Check for under/overflow
        nrt, nrs, nimm = rt & 0x1F, rs & 0x1F, imm & 0xFFFF

        rt, rs, imm = nrt, nrs, nimm

        # Encode
        out |= rs
        out <<= 5
        out |= rt
        out <<= 16
        out |= imm

    return out


# Convert from int to string
def decode(inst):
    inst = f'{inst:032b}'

    out = ''
    opcode = int(inst[0:6], 2)
    rs, rt = int(inst[6:11], 2), int(inst[11:16], 2)
    last16 = inst[16:32]

    if opcode == 0b000000:  # R-Type
        rd, aluOp = int(last16[0:5], 2), int(last16[10:16], 2)

        if aluOp == G_UTL.rTypeWords['sll'] or aluOp == G_UTL.rTypeWords['srl']:
            shamt = int(last16[5:10], 2)
            out = f'{G_UTL.rTypeBins[aluOp]} {G_UTL.regNames[rd]}, {G_UTL.regNames[rt]}, {shamt}'
        else:
            out = f'{G_UTL.rTypeBins[aluOp]} {G_UTL.regNames[rd]}, {G_UTL.regNames[rs]}, {G_UTL.regNames[rt]}'
    elif opcode == 0b100011 or opcode == 0b101011:  # lw/sw
        if opcode == 0b100011:
            out = 'lw'
        elif opcode == 0b101011:
            out = 'sw'

        out += f' {G_UTL.regNames[rt]}, {int(last16, 2)}({G_UTL.regNames[rs]})'
    elif opcode == 0b000100:  # beq
        out = f'beq {G_UTL.regNames[rs]}, {G_UTL.regNames[rt]}, {int(last16, 2)}'
    elif opcode == 0b001000:  # addi
        out = f'addi {G_UTL.regNames[rt]}, {G_UTL.regNames[rs]}, {int(last16, 2)}'

    return out
