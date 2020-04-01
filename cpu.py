import sys

class CPU:

    def __init__(self):
        self.registers = [0] * 8
        self.running = False
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 7
        self.flag = 0b00000000

    def increment_pc(self, op_code):
        add_to_pc = (op_code >> 6) + 1
        self.pc += add_to_pc

    def load(self, filename):
        address = 0

        with open(filename) as f:
            for line in f:
                comment_split = line.split('#')
                number = comment_split[0].strip()

                if number == "":
                    continue

                val = int(number, 2)
                self.write(val, address)

                address += 1

    def alu(self, op, reg_a, reg_b):

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        elif op == "MUL":
            self.registers[reg_a] = self.registers[reg_a] * \
                self.registers[reg_b]
        elif op == "CMP":
            if self.registers[reg_a] == self.registers[reg_b]:
                self.flag = 0b00000001
            elif self.registers[reg_a] > self.registers[reg_b]:
                self.flag = 0b00000010
            else:
                self.flag = 0b00000100

    def run(self):
        self.running = True

        while self.running:
            op_code = self.read(self.pc)

            if op_code == 0b00000001:  # HLT
                self.running = False
                sys.exit(1)

            elif op_code == 0b10000010:  # LDI
                address = self.read(self.pc + 1)
                data = self.read(self.pc + 2)
                self.registers[address] = data
                self.increment_pc(op_code)

            elif op_code == 0b01000111:  # PRN
                address_a = self.read(self.pc + 1)
                print(self.registers[address_a])
                self.increment_pc(op_code)
                pass

            elif op_code == 0b10100111:  # CMP
                address_a = self.read(self.pc + 1)
                address_b = self.read(self.pc + 2)
                self.alu('CMP', address_a, address_b)
                self.increment_pc(op_code)

            elif op_code == 0b10100000:  # ADD
                address_a = self.read(self.pc + 1)
                address_b = self.read(self.pc + 2)
                self.alu('ADD', address_a, address_b)
                self.increment_pc(op_code)

            elif op_code == 0b10100010:  # MUL
                address_a = self.read(self.pc + 1)
                address_b = self.read(self.pc + 2)
                self.alu('MUL', address_a, address_b)
                self.increment_pc(op_code)

            elif op_code == 0b01010100:  # jump
                register_address = self.read(self.pc + 1)
                self.pc = self.registers[register_address]

            elif op_code == 0b01010101:  # jump if equal
                register_address = self.read(self.pc + 1)
                if self.flag == 0b00000001:
                    self.pc = self.registers[register_address]
                else:
                    self.increment_pc(op_code)

            elif op_code == 0b01010110:  # jump if not equal
                register_address = self.read(self.pc + 1)
                if self.flag != 0b00000001:
                    self.pc = self.registers[register_address]
                else:
                    self.increment_pc(op_code)

            elif op_code == 0b01000101:  # PUSH
                register_address = self.read(self.pc + 1)
                val = self.registers[register_address]
                self.registers[self.sp] -= 1 
                self.ram[self.registers[self.sp]] = val
                self.increment_pc(op_code)

            elif op_code == 0b01000110:  # POP
                register_address = self.read(self.pc + 1)
                val = self.ram[self.registers[self.sp]]
                self.registers[register_address] = val
                self.registers[self.sp] += 1
                self.increment_pc(op_code)
    
    def read(self, MAR):
        return self.ram[MAR]

    def write(self, MDR, MAR):
        self.ram[MAR] = MDR