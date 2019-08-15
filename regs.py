
class InvalidAddressException(Exception):
    pass


class ALU():
    pass


class Bus():
    def __init__(self):
        self.value = 0b00000000

    def __repr__(self):
        return f"<Bus {self.value:08b} : 0x{self.value:02X}>"


class Register():
    def __init__(self, name: str, bus: Bus):
        self.value = 0b00000000
        self.name = name
        self.bus = bus
        self.enable: bool = False
        self.load: bool = False

    def on_clock(self):
        # print(f"Register{self.name} clocking")
        if self.load:
            self.read_bus()
            self.load = False
        if self.enable:
            self.write_to_bus()
            self.enable = False

    def read_bus(self):
        self.value = self.bus.value

    def write_to_bus(self):
        self.bus.value = self.value

    def __repr__(self):
        return f"<Register{self.name}:{self.value:08b} : 0x{self.value:02x}>"


class Rom():
    def __init__(self):
        self.value: dict = {}

    def read(self, fname):
        with open(fname) as src:
            cont = src.readlines()
            for line in cont:
                if len(line) == 0:
                    continue
                sp = line.split()
                if len(sp) == 0:
                    continue
                if sp[0] == "REM":
                    continue
                memloc = {sp[0]:
                          {"instruction": sp[1], "ops": sp[2]}
                          }
                self.value.update(memloc)

    def get_memory_value(self, addr):
        addr_val = self.value.get(addr, None)
        if not addr_val:
            raise InvalidAddressException(f"Nothing in memory address {addr}")
        return addr_val

    def get_next_addr(self, addr):
        addr_list = list(self.value.keys())
        try:
            next_addr = addr_list[addr_list.index(addr) + 1]
        except IndexError:
            return False
        return next_addr

    def __repr__(self):
        lines = []
        lines.append("ADDR\tINST\tOPS")
        lines.append("-"*60)
        for addr, instr in self.value.items():
            lines.append(f'{addr}\t{instr["instruction"]}\t{instr["ops"]}')
        return "\n".join(lines)
