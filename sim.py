from components import RegisterFile, instrMem, DataMem, ALU, ControlUnit, Adder, SignExtender, Shifter, Mux

pc = "0" * 32
HI = "0" * 32
LO = "0" * 32


reg_file = RegisterFile()
instr_mem = instrMem()
data_mem = DataMem()
alu = ALU()
control_unit = ControlUnit()
adder_pc = Adder()
adder_branch = Adder()
sign_extender = SignExtender()
shifter = Shifter()
mux_alu_src = Mux()
mux_reg_dst = Mux()
mux_pc_src = Mux()

cycle = 0

while True:
    input("Press Enter to continue...")
    cycle += 1
    print(f"\n=============== Cycle {cycle} ===================")
    
    instruction = instr_mem.use(pc)
    if instruction == "0" * 32 or instruction == "":
        print("Simulation terminated: Instruction is all zeros.")
        break
    if not all(c in '01' for c in instruction) or len(instruction) != 32:
        print(f"Invalid instruction at PC {pc}: {instruction}")
        break
    print(f"PC: {pc}, Instruction: {instruction}")

    opcode = instruction[0:6]
    rs = instruction[6:11]
    rt = instruction[11:16]
    rd = instruction[16:21]
    shamt = instruction[21:26]
    funct = instruction[26:32]
    imm = instruction[16:32]
    target_addr = instruction[6:32]

    control_signals = control_unit.use(opcode)
    print(f"Control Signals: {control_signals}")

    reg_data1, reg_data2 = reg_file.use(Read1=rs, Read2=rt)
    sign_extended_imm = sign_extender.use(imm)
    print(f"RegData1 (rs={rs}): {reg_data1}, RegData2 (rt={rt}): {reg_data2}")
    print(f"SignExtendedImm: {sign_extended_imm}")

    alu_input2 = mux_alu_src.use(control_signals["ALUSrc"], reg_data2, sign_extended_imm)
    print(f"ALUInput2: {alu_input2}")

    if control_signals["ALUOp1"] == "1" and control_signals["ALUOp0"] == "0":  
        if funct == "100000": 
            alu_result, zero = alu.use("10", reg_data1, alu_input2)
        elif funct == "011000": 
            val1 = int(reg_data1, 2)
            if val1 & 0x80000000: 
                val1 -= 0x100000000
            val2 = int(reg_data2, 2)
            if val2 & 0x80000000:
                val2 -= 0x100000000
            product = val1 * val2
            product_bin = format(product & 0xFFFFFFFFFFFFFFFF, '064b')
            LO = product_bin[32:]
            HI = product_bin[:32]
            alu_result = "0" * 32 
            zero = "0"
        elif funct == "010010": 
            alu_result = LO
            zero = "0"
        else:
            alu_result, zero = "0" * 32, "0"
            print(f"Unsupported R-type funct: {funct}")
    elif control_signals["ALUOp1"] == "0" and control_signals["ALUOp0"] == "1":  # beq
        alu_result, zero = alu.use("01", reg_data1, reg_data2)
    else: 
        alu_result, zero = alu.use("10", reg_data1, alu_input2)
    print(f"ALUResult: {alu_result}, Zero: {zero}")

   
    write_reg = mux_reg_dst.use(control_signals["RegDst"], rt, rd)
    if control_signals["RegWrite"] == "1":
        reg_file.use(Write1=write_reg, RegWrite=True, Data=alu_result)
        print(f"Writing {alu_result} to register {write_reg}")
    else:
        print("No register write back.")

    
    next_pc_normal = adder_pc.use(pc, bin(4)[2:].zfill(32))
    shifted_imm = shifter.use(sign_extended_imm, "00010")
    branch_target = adder_branch.use(next_pc_normal, shifted_imm)
    jump_target = pc[:4] + target_addr + "00"
    print(f"NextPCNormal: {next_pc_normal}")
    print(f"BranchTarget: {branch_target}")
    print(f"JumpTarget: {jump_target}")

    if control_signals["Jump"] == "1":
        pc = jump_target
        print(f"Jump taken, PC set to {pc}")
    elif control_signals["Branch"] == "1" and zero == "1":
        pc = branch_target
        print(f"Branch taken, PC set to {pc}")
    else:
        pc = next_pc_normal
        print(f"PC incremented, PC set to {pc}")

reg_file.writeRegsToFile()
print("Simulation completed. Register state written to 'MemoryFiles/Registers.txt'.")