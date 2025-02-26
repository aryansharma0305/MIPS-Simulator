class MIPSAssembler:
    def __init__(self):
        self.opcodes = {
            "addi": "001000",
            "beq": "000100",
            "j": "000010",
            "mult": "000000",
            "mflo": "000000",
            "move": "000000",
            "nop": "000000",
            "add": "000000" 
        }
        
        self.funct_codes = {
            "add": "100000",
            "mult": "011000",
            "mflo": "010010",
            "nop": "000000"
        }
        
        self.registers = {
            "$zero": "00000", "$at": "00001", "$v0": "00010", "$v1": "00011",
            "$a0": "00100", "$a1": "00101", "$a2": "00110", "$a3": "00111",
            "$t0": "01000", "$t1": "01001", "$t2": "01010", "$t3": "01011",
            "$t4": "01100", "$t5": "01101", "$t6": "01110", "$t7": "01111",
            "$s0": "10000", "$s1": "10001", "$s2": "10010", "$s3": "10011",
            "$s4": "10100", "$s5": "10101", "$s6": "10110", "$s7": "10111",
            "$t8": "11000", "$t9": "11001", "$k0": "11010", "$k1": "11011",
            "$gp": "11100", "$sp": "11101", "$fp": "11110", "$ra": "11111"
        }
        self.labels = {}

    def first_pass(self, input_filename):
        with open(input_filename, "r") as infile:
            instruction_address = 0
            for line in infile:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    label = line.split(":")[0].strip()
                    self.labels[label] = instruction_address
                else:
                    instruction_address += 4

    def assemble(self, instruction, current_address):
        parts = instruction.replace(",", "").split()
        if not parts:
            return None
        
        opcode = parts[0]
        
        if opcode in self.opcodes:
            op_bin = self.opcodes[opcode]

            if opcode == "move":
                if len(parts) != 3:
                    return "ERROR: move expects two registers"
                rd = self.registers.get(parts[1], "00000")
                rs = self.registers.get(parts[2], "00000")
                rt = "00000"
                shamt = "00000"
                funct = self.funct_codes["add"]
                return f"{op_bin}{rs}{rt}{rd}{shamt}{funct}"
            elif opcode == "add":  # New case for add
                if len(parts) != 4:
                    return "ERROR: add expects three registers"
                rd = self.registers.get(parts[1], "00000")
                rs = self.registers.get(parts[2], "00000")
                rt = self.registers.get(parts[3], "00000")
                shamt = "00000"
                funct = self.funct_codes["add"]
                return f"{op_bin}{rs}{rt}{rd}{shamt}{funct}"
            elif opcode == "mult":
                if len(parts) != 3:
                    return "ERROR: mult expects two registers"
                rs = self.registers.get(parts[1], "00000")
                rt = self.registers.get(parts[2], "00000")
                rd = "00000"
                shamt = "00000"
                funct = self.funct_codes["mult"]
                return f"{op_bin}{rs}{rt}{rd}{shamt}{funct}"
            elif opcode == "mflo":
                if len(parts) != 2:
                    return "ERROR: mflo expects one register"
                rd = self.registers.get(parts[1], "00000")
                rs = "00000"
                rt = "00000"
                shamt = "00000"
                funct = self.funct_codes["mflo"]
                return f"{op_bin}{rs}{rt}{rd}{shamt}{funct}"
            elif opcode == "nop":
                rs = "00000"
                rt = "00000"
                rd = "00000"
                shamt = "00000"
                funct = self.funct_codes["nop"]
                return f"{op_bin}{rs}{rt}{rd}{shamt}{funct}"
            elif opcode == "addi":
                if len(parts) != 4:
                    return "ERROR: addi expects two registers and an immediate"
                rs = self.registers.get(parts[1], "00000")
                rt = self.registers.get(parts[2], "00000")
                immediate_value = int(parts[3])
                immediate = format((immediate_value & 0xFFFF) if immediate_value >= 0 else (0x10000 + immediate_value), '016b')
                return f"{op_bin}{rs}{rt}{immediate}"
            elif opcode == "beq":
                if len(parts) != 4:
                    return "ERROR: beq expects two registers and an offset"
                rs = self.registers.get(parts[1], "00000")
                rt = self.registers.get(parts[2], "00000")
                if parts[3] in self.labels:
                    offset = (self.labels[parts[3]] - (current_address + 4)) // 4
                else:
                    offset = int(parts[3])
                immediate = format(offset & 0xFFFF, '016b')
                return f"{op_bin}{rs}{rt}{immediate}"
            elif opcode == "j":
                if len(parts) != 2:
                    return "ERROR: j expects a target"
                if parts[1] in self.labels:
                    address = format(self.labels[parts[1]] // 4, '026b')
                else:
                    address = format(int(parts[1]), '026b')
                return f"{op_bin}{address}"

        return f"ERROR: Invalid instruction '{instruction}'"

    def process_file(self, input_filename, output_filename):
        self.first_pass(input_filename)
        with open(input_filename, "r") as infile, open(output_filename, "w") as outfile:
            instruction_address = 0
            for line in infile:
                line = line.strip()
                if not line or line.startswith("#") or ":" in line:
                    continue
                machine_code = self.assemble(line, instruction_address)
                if machine_code and not machine_code.startswith("ERROR:"):
                    byte1 = machine_code[0:8]
                    byte2 = machine_code[8:16]
                    byte3 = machine_code[16:24]
                    byte4 = machine_code[24:32]
                    outfile.write(byte1 + "\n")
                    outfile.write(byte2 + "\n")
                    outfile.write(byte3 + "\n")
                    outfile.write(byte4 + "\n")
                    instruction_address += 4
                else:
                    print(f"Assembly error at address {instruction_address}: {machine_code}")



if __name__ == "__main__":
    assembler = MIPSAssembler()
    assembler.process_file("input.asm", "MemoryFiles/instrMem.txt")
    print("Assembly completed. Check 'instrMem.txt' for output.")