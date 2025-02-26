# MIPS32 Instruction Set Architecture (ISA)


## Explanation
1. **R-Type**: Used for arithmetic and register-based operations.
2. **I-Type**: Used for immediate operations and branching.
3. **J-Type**: Used for jump instructions.

These formats follow the **standard MIPS instruction encoding**.

## R-Type Instructions (Register-based operations)

| Instruction | Opcode (6 bits) | rs (5 bits) | rt (5 bits) | rd (5 bits) | shamt (5 bits) | funct (6 bits) | Description |
|------------|---------------|-----------|-----------|-----------|-------------|------------|-------------|
| `add`   | 000000 | rs  | rt  | rd  | 00000 | 100000 | Adds rs and rt, stores result in rd |
| `mult`  | 000000 | rs  | rt  | 00000 | 00000 | 011000 | Multiplies rs and rt, result stored in LO register |
| `mflo`  | 000000 | 00000 | 00000 | rd  | 00000 | 010010 | Moves content of LO register to rd |
| `jr`    | 000000 | rs  | 00000 | 00000 | 00000 | 001000 | Jumps to address stored in rs |

## I-Type Instructions (Immediate and branching operations)

| Instruction | Opcode (6 bits) | rs (5 bits) | rt (5 bits) | Immediate (16 bits) | Description |
|------------|---------------|-----------|-----------|-----------------|-------------|
| `addi`  | 001000 | rs  | rt  | Immediate | Adds immediate value to rs, stores result in rt |
| `beq`   | 000100 | rs  | rt  | Offset | Branches if rs equals rt |
| `bne`   | 000101 | rs  | rt  | Offset | Branches if rs is not equal to rt |

## J-Type Instructions (Jump operations)

| Instruction | Opcode (6 bits) | Target Address (26 bits) | Description |
|------------|---------------|----------------|-------------|
| `j`    | 000010 | Address | Jumps to the specified address |
| `jal`  | 000011 | Address | Jumps to the address and stores return address in $ra |


<br>
<br>
<br>

# How to use



- **Required Files:**
  - `assembler.py`: The assembler script.
  - `sim.py`: The simulator script.
  - `components.py`: Defines processor components (e.g., `RegisterFile`, `ALU`, `ControlUnit`).
  - `input.asm`: Assembly source file.
 


## Step-by-Step Usage

### 1. Write Your Assembly Program

Create a file named `input.asm` with your MIPS assembly code. Below is an example that calculates the factorial of 10 and stores the result in `$t4`:

```assembly
main:
    addi $t0, $t0, 10      # $t0 = 10 (n)
    addi $t1, $t1, 1       # $t1 = 1 (factorial accumulator)
loop:
    beq $t0, $zero, end    # If $t0 == 0, exit to end
    mult $t1, $t0          # $t1 * $t0 -> HI:LO
    mflo $t1               # Move result from LO to $t1
    addi $t0, $t0, -1      # Decrement $t0
    j loop                 # Jump back to loop
end:
    add $t4, $t1, $t2      # $t4 = $t1 + $t2 (assuming $t2 is 0)
    nop                    # End with no operation
```

### 2. Assemble the Program

Run the assembler to convert `input.asm` into machine code:

```bash
python assembler.py
```


#### Checking `instrMem.txt`

Each instruction is stored as 4 lines (big-endian format, 8 bits per line).

```text
00100001  # addi $t0, $t0, 10
00001000
00000000
00001010
00100001  # addi $t1, $t1, 1
00101001
00000000
00000001
...
```

---

### 3. Run the Simulator

Execute the simulator to run the assembled program:

```bash
python sim.py
```

#### Execution Steps
- Reads `instrMem.txt` starting at `PC = 0`.
- For each cycle:
  - Fetches the 32-bit instruction.
  - Decodes it (opcode, rs, rt, etc.).
  - Executes (updates registers, HI, LO, or PC).
  - Prints detailed state.
  - Waits for Enter key to proceed.
  - Ends on `000...000` (32 zeros) or an empty line.
- Updates `Registers.txt` with the final register states.

#### Console Output Example

```text
=== Cycle 1 ===
PC: 0, Instruction: 00100001000010000000000000001010
Control Signals: {'RegDst': '0', 'ALUSrc': '1', 'RegWrite': '1', 'Branch': '0'}
RegData1 (rs=01000): 00000000000000000000000000000000
ALUResult: 00000000000000000000000000001010
Writing 00000000000000000000000000001010 to register 01000
NextPC: 4
Press Enter to continue...
```

---

### 4. Interpret the Output

#### Registers.txt (Final Register State)

```text
----------------------------------------------------
|  Reg  |  Name |             Value                |
----------------------------------------------------
|  R8   | $t0   | 00000000000000000000000000000000 |
|  R9   | $t1   | 00000000000000000000110111100000 | # 3628800 (10!)
|  R12  | $t4   | 00000000000000000000110111100000 |
...
----------------------------------------------------
```
