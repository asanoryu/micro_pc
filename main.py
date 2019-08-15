import time

from regs import Bus, Register, Rom, ALU


class PC():

    CLOCK_SPEED: float = 0.08

    def __init__(self, rom=Rom()):
        self.registers: list = []
        self.main_bus: Bus = Bus()
        self.set_registers()
        self.rom: Rom = rom
        self.alu: ALU = ALU()
        self.instruction_handlers: dict = {}
        self.setup_instruction_handlers()
        self.pc = list(self.rom.value.keys())[0]  # : Program Counter
        self.running = False  # : Are we running?

    def setup_instruction_handlers(self):
        self.instruction_handlers = {
            "mov": self.move_val,
            "mvc": self.move_c,
            "add": self.add,
            "sub": self.sub,
            "cop": self.cop,
            "jmp": self.jmp,
            "jml": self.jump_if_less,
            "jmg": self.jump_if_greater,
            "jme": self.jump_if_equal,
            "hlt": self.halt,
        }

    def move_val(self, ops):
        ops = ops.split(",")
        self.main_bus.value = (int(ops[0], 16))
        load_reg = self.get_register(ops[1])

        load_reg.load = True
        self.pc = self.rom.get_next_addr(self.pc)

    def move_c(self, ops):
        reg_c = self.get_register("C")
        target_reg = self.get_register(ops)
        target_reg.value = reg_c.value

    def add(self, ops):
        reg_c = self.get_register("C")
        reg_other = self.get_register(ops)
        reg_c.value = reg_c.value + reg_other.value
        self.pc = self.rom.get_next_addr(self.pc)

    def get_register(self, regname: str):
        # print(f"looking for register {regname}")
        for reg in self.registers:
            if reg.name.lower() == regname.lower():
                # print(f"got reg {reg}")
                return reg

    def halt(self):
        self.running = False

    def sub(self, ops):
        reg_c = self.get_register("C")
        reg_other = self.get_register(ops)
        reg_c.value = reg_c.value - reg_other.value
        self.pc = self.rom.get_next_addr(self.pc)

    def cop(self, ops):
        reg_from = self.get_register(ops)
        reg_from.enable = True
        reg_c = self.get_register("C")
        reg_c.load = True
        self.pc = self.rom.get_next_addr(self.pc)

    def jmp(self, ops):
        self.pc = ops

    def jump_if_less(self, ops):
        ops = ops.split(",")
        reg_c = self.get_register("C")
        if reg_c.value < int(ops[0], 16):
            self.pc = ops[1]
        else:
            self.pc = self.rom.get_next_addr(self.pc)

    def jump_if_greater(self, ops):
        ops = ops.split(",")
        reg_c = self.get_register("C")
        if reg_c.value > int(ops[0], 16):
            self.pc = ops[1]
        else:
            self.pc = self.rom.get_next_addr(self.pc)

    def jump_if_equal(self, ops):
        ops = ops.split(",")
        reg_c = self.get_register("C")
        if reg_c.value == int(ops[0], 16):
            self.pc = ops[1]
        else:
            self.pc = self.rom.get_next_addr(self.pc)

    def set_registers(self):
        reg_a = Register("A", self.main_bus)
        reg_b = Register("B", self.main_bus)
        reg_c = Register("C", self.main_bus)
        self.registers.append(reg_a)
        self.registers.append(reg_b)
        self.registers.append(reg_c)

    def run(self):
        self.running = True
        while True:
            print(self)
            if not self.running:
                print("PROGRAM DONE!!!HALTING!!!")
                break
            self.handle_instruction()
            for reg in self.registers:
                reg.on_clock()

            time.sleep(self.CLOCK_SPEED)

    def handle_instruction(self):
        instruction = self.rom.get_memory_value(self.pc)
        print(f"Current instruction {instruction}")
        instr_name = instruction["instruction"]
        self.instruction_handlers.get(instr_name)(instruction["ops"])
        if not self.pc:
            self.running = False

    def __repr__(self):
        rep = []
        rep.append("-"*60)
        rep.append(str(self.main_bus))
        for reg in self.registers:
            rep.append(str(reg))
        rep.append(f"Prog Counter {self.pc}")
        rep.append("-"*60)
        return "\n".join(rep)


rom = Rom()
rom.read("test_asm.txt")
# print(rom)
cpu = PC(rom=rom)
cpu.run()
