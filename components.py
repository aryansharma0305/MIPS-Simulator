class RegisterFile:
    def __init__(self):
        self.registers = {i: "0" * 32 for i in range(32)}

    def binaryToDecimal(self, string):
        return int(string, 2)

    def writeRegsToFile(self):
        with open("MemoryFiles/Registers.txt", "w") as file:
            file.write("----------------------------------------------------\n")
            file.write("|  Reg  |  Name |             Value                |\n")
            file.write("----------------------------------------------------\n")
            register_names = ["$zero", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3",
                              "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7",
                              "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
                              "$t8", "$t9", "$k0", "$k1", "$gp", "$sp", "$fp", "$ra"]
            for i in range(32):
                value = self.registers[i]
                file.write(f"|  R{i:<2}  | {register_names[i]:<5} | {value:<32} |\n")
            file.write("----------------------------------------------------\n")

    def use(self, Read1="0", Read2="0", Write1="0", RegWrite=False, Data=None):
        read1 = self.binaryToDecimal(Read1) if Read1 else 0
        read2 = self.binaryToDecimal(Read2) if Read2 else 0
        write1 = self.binaryToDecimal(Write1) if Write1 else 0
        if RegWrite and Data is not None and write1 != 0:  # Prevent write to $zero
            self.registers[write1] = Data.zfill(32)[:32]
        self.writeRegsToFile()
        return (self.registers[read1], self.registers[read2])


#==========================================================================================================



class instrMem:
    def __init__(self):
        self.instrMem = ["0" * 8] * 4096
        self.loadFromFile("MemoryFiles/instrMem.txt")

    def loadFromFile(self, filename):
        try:
            with open(filename, "r") as f:
                for i in range(len(self.instrMem)):
                    line = f.readline().strip()
                    if line:
                        self.instrMem[i] = line.zfill(8)[:8]
                    else:
                        self.instrMem[i] = "0" * 8
        except FileNotFoundError:
            pass

    def use(self, addr="0"*32):
        addr = int(addr, 2)
        if addr % 4 != 0:
            raise ValueError(f"Instruction memory address {addr} is not word-aligned!")
        if addr + 3 >= len(self.instrMem):
            return "0" * 32
        return "".join(self.instrMem[addr:addr+4])



#==========================================================================================================


class DataMem:
    def __init__(self):
        self.data = ["0" * 8] * 4096

    def updateField(self, filename="MemoryFiles/dataMem.txt"):
        with open(filename, "w") as f:
            for i in range(len(self.data)):
                f.write(self.data[i] + "\n")

    def use(self, addr="0"*32, data="0"*32, write=False, read=False):
        addr = int(addr, 2)
        if addr % 4 != 0:
            raise ValueError("Memory address is not word-aligned!")
        if write:
            self.data[addr] = data[0:8]
            self.data[addr + 1] = data[8:16]
            self.data[addr + 2] = data[16:24]
            self.data[addr + 3] = data[24:32]
        if read:
            return self.data[addr] + self.data[addr + 1] + self.data[addr + 2] + self.data[addr + 3]
        return "0" * 32



#==========================================================================================================



class ALU:
    def use(self, alu_op, input_1, input_2):
        val1 = int(input_1, 2)
        val2 = int(input_2, 2)
        if alu_op == "10":  # ADD
            result = (val1 + val2) & 0xFFFFFFFF
        elif alu_op == "01":  # SUB (for beq)
            result = (val1 - val2) & 0xFFFFFFFF
        else:
            result = 0
        zero = "1" if result == 0 else "0"
        return bin(result)[2:].zfill(32), zero




#==========================================================================================================



class ControlUnit:
    def __init__(self):
        self.control_signals = {
            "RegDst": "0", "ALUSrc": "0", "MemToReg": "0", "RegWrite": "0",
            "MemRead": "0", "MemWrite": "0", "Branch": "0", "ALUOp1": "0",
            "ALUOp0": "0", "Jump": "0"
        }

    def use(self, opcode="000000"):
        if opcode == "000000":  # R-Type
            self.control_signals.update({"RegDst": "1", "ALUSrc": "0", "MemToReg": "0",
                                         "RegWrite": "1", "MemRead": "0", "MemWrite": "0",
                                         "Branch": "0", "ALUOp1": "1", "ALUOp0": "0", "Jump": "0"})
        elif opcode == "001000":  # ADDI
            self.control_signals.update({"RegDst": "0", "ALUSrc": "1", "MemToReg": "0",
                                         "RegWrite": "1", "MemRead": "0", "MemWrite": "0",
                                         "Branch": "0", "ALUOp1": "0", "ALUOp0": "0", "Jump": "0"})
        elif opcode == "000100":  # BEQ
            self.control_signals.update({"RegDst": "X", "ALUSrc": "0", "MemToReg": "X",
                                         "RegWrite": "0", "MemRead": "0", "MemWrite": "0",
                                         "Branch": "1", "ALUOp1": "0", "ALUOp0": "1", "Jump": "0"})
        elif opcode == "000010":  # J
            self.control_signals.update({"RegDst": "X", "ALUSrc": "X", "MemToReg": "X",
                                         "RegWrite": "0", "MemRead": "0", "MemWrite": "0",
                                         "Branch": "0", "ALUOp1": "X", "ALUOp0": "X", "Jump": "1"})
        return self.control_signals



#==========================================================================================================


class Adder:
    def use(self, input1="0"*32, input2="0"*32):
        return bin((int(input1, 2) + int(input2, 2)) & 0xFFFFFFFF)[2:].zfill(32)



#==========================================================================================================


class SignExtender:
    def use(self, input="0"*16):
        sign_bit = input[0]
        return sign_bit * (32 - 16) + input



#==========================================================================================================


class Shifter:
    def use(self, input="0"*32, shamt="0"*5):
        shift = int(shamt, 2)
        return input[shift:] + "0" * shift


#==========================================================================================================


class Mux:
    def use(self, select="0", input1="0"*32, input2="0"*32):
        return input1 if select == "0" else input2
    


#==========================================================================================================