#create the stack class
class Stack:
    #defines an array called stack (the stack is a simple array), and the max size set to 1024
    def __init__(self, max_depth=1024) -> None:
        self.stack = []
        self.max_depth = max_depth

    #defines the func push which is used to push itens into the stack
    def push(self, item: int) -> None:
        #checks if the item value is valid
        if item < 0 or item > 2**256 - 1:
            raise InvalidStackItem({"item": item})
        
        #checks if the addition of the item into the stack will cause a stack overflow
        if (len(self.stack) + 1) > self.max_depth:
            raise StackOverFlow()

        #if not it adds the item into the stack
        self.stack.append(item)

    #defines the function which is used to pop itens from the stack
    def pop(self) -> int:
        #checks if the pop will cause a stack underflow
        if len(self.stack) == 0:
            raise StackUnderFlow()

        #if not returns the stack poped
        return self.stack.pop()

#creates the memory class
class Memory:
    #initialize the memory as an array of dictionaries
    def __init__(self) -> None:
        self.memory = []

    #defines the func which is used to store values into the memory
    def store(self, offset: int, value: int) -> None:
        #check if the offset addressing is valid
        if offset < 0 or offset > MAX_UINT256:
            raise InvalidMemoryAccess({'offset': offset, 'value': value})

        #expand memory if needed
        if offset >= len(self.memory):
            self.memory.extend([0] * (offset - len(self.memory) + 1))

        #inserts the value in the relative address of the offset
        #the offset is the dictionary key and the value is the content
        self.memory[offset] = value
    
    #returns the content stored in the offset dictionary
    def load(self, offset: int) -> int:
        if offset < 0:
            raise InvalidMemoryAccess({"offset": offset})
        
        if offset >= len(self.memory):
            return 0
        
        return self.memory[offset]

#creates the class ExecutionContext
class ExecutionContext:
    #inits it with a code, stack obj, memory obj, and a pc counter 
    def __init__(self, code=bytes(), pc=0, stack=Stack(), memory=Memory()) -> None:
        self.code = code
        self.stack = stack
        self.memory = memory
        self.pc = pc
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True

    def read_code(self, num_bytes) -> int:
     
        #Returns the next num_bytes from the code buffer as an integer and advances pc by num_bytes.
        #value recives the int from bytes of the array self.code from the self.pc until self.pc + num_bytes
        value = int.from_bytes(self.code[self.pc : self.pc + num_bytes], byteorder = "big")
        self.pc += num_bytes
        return value

#defines the class instruction
class Instruction:
    #initializes it with an opcode and a name
    def __init__(self, opcode: int, name: str):
        self.opcode = opcode
        self.name = name
    
    #creates the func execute and leaves it unimplemented
    def execute(self, context: ExecutionContenxt) -> None:
        raise NotImplementedError
    
INSTRUCTIONS = []
INSTRUCTIONS_BY_OPCODE = {}

#creates the func to register the instructions passed by
def register_instruction(opcode: int, name: str, execute_func: callable):
    #creates an object of the Instruction class
    instruction = Instruction(opcode, name)

    #set it's execute method to one passed by
    instruction.execute = execute_func
        
    #appeds the object instruction to an array
    INSTRUCTIONS.append(instruction)

STOP = register_instruction(0x00, "STOP", (lambda ctx: ctx.stop()))
PUSH1 = register_instruction(
    0x60,
    "PUSH1",
    (lambda ctx: ctx.stack.push(ctx.read_code(1))),
)
ADD = register_instruction(
    0x01,
    "ADD",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() + ctx.stack.pop()) % 2**256)),
)
MUL = register_instruction(
    0x02,
    "MUL",
    (lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) % 2**256)),
)

def decode_opcode(context: ExecutionContext) -> Instruction:
    if context.pc < 0 or context.pc >= len(context.code):
        raise InvalidCodeOffset({"code": context.code, "pc": context.pc})
    
    opcode = context.read_code(1)
    instruction = INSTRUCTIONS_BY_OPCODE.get(opcode)
    if instruction is None:
        raise UnknownOpcode({"opcode": opcode})
    
    return instruction

def run(code: bytes) -> None:
    #Executes code in a fresh context

    context = ExecutionContext(code=code)

    while not context.stopped:
        pc_before = context.pc
        instruction = decode_opcode(context)
        instruction.execute(context)

        print(f"{instruction} @ pc={pc_before}")
        print(context)
        print()
