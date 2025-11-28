import sys
import json
import pprint
import warnings
import time

tracing = False
Trace = []
InitialCalls = []

class TraceCalls:
    def __init__(self, func_name):
        self.func_name = func_name
        self.start_time = None
        self.end_time = None
        self.nextCall = []
        self.prevCall = None

    def __enter__(self):
        global Trace, InitialCalls
        self.start_time = time.time()
        if Trace:
            self.prevCall = Trace[-1]
            self.prevCall.nextCall.append(self)

        else:
            InitialCalls.append(self)
        Trace.append(self)
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.end_time = time.time()
        Trace.pop()
    
    def duration(self):
        return (self.end_time - self.start_time) *1000

def do_set(args,envs):
    assert len(args) == 2
    assert isinstance(args[0],str)
    var_name = args[0]
    var_value = do(args[1],envs)
    env_set(var_name,var_value,envs)
    return var_value

def env_set(name,value,envs):
    assert isinstance(name,str)
    envs[-1][name] = value
    
def do_get(args,envs):
    assert len(args) == 1
    assert isinstance(args[0],str)
    var_name = args[0]
    return env_get(var_name,envs)

def env_get(name,envs):
    assert isinstance(name,str)
    for env in reversed(envs):
        if name in env:
            return env[name]
    assert False, f"Unknown variable {name}"

def do_seq(args,envs):
    for each_ops in args:
        res = do(each_ops,envs)
    return res

def do_addieren(args,envs):
    assert len(args) == 2
    left = do(args[0],envs)
    right = do(args[1],envs)
    return left + right

def do_absolutewert(args,envs):
    assert len(args) == 1
    value = do(args[0],envs)
    if value >= 0:
        return value
    return -value

def do_subtrahieren(args,envs):
    assert len(args) == 2
    left = do(args[0],envs)
    right = do(args[1],envs)
    return left - right

def do_multiplizieren(args,envs):
    assert len(args) == 2
    m1 = do(args[0],envs)
    m2 = do(args[1],envs)
    return m1*m2

def do_dividieren(args,envs):
    assert len(args) == 2
    dividend = do(args[0],envs)
    divisor = do(args[1],envs)
    assert divisor != 0, "Divisor can not be 0!"
    return dividend/divisor

def do_potenz(args,envs):
    assert len(args) == 2
    base = do(args[0],envs)
    exponent = do(args[1],envs)
    assert base > 0 or (base == 0 and exponent >= 0) or (base < 0 and (exponent >= 1 or exponent <= -1 or exponent == 0) and round(exponent) == exponent), "Stay real!"
    return base**exponent

def do_rest(args,envs):
    assert len(args) == 2
    dividend = do(args[0],envs)
    divisor = do(args[1],envs)
    assert divisor != 0, "Divisor can not be 0!"
    return dividend%divisor

def do_kleiner(args,envs):
    assert len(args) == 2
    n1 = do(args[0],envs)
    n2 = do(args[1],envs)
    return n1 < n2

def do_kleiner_gleich(args,envs):
    assert len(args) == 2
    n1 = do(args[0],envs)
    n2 = do(args[1],envs)
    return n1 <= n2

def do_groesser(args,envs):
    assert len(args) == 2
    n1 = do(args[0],envs)
    n2 = do(args[1],envs)
    return n1 > n2

def do_groesser_gleich(args,envs):
    assert len(args) == 2
    n1 = do(args[0],envs)
    n2 = do(args[1],envs)
    return n1 >= n2

def do_gleich(args,envs):
    assert len(args) == 2
    n1 = do(args[0],envs)
    n2 = do(args[1],envs)
    return n1 == n2

def do_ungleich(args,envs):
    assert len(args) == 2
    n1 = do(args[0],envs)
    n2 = do(args[1],envs)
    return n1 != n2

def do_AND(args,envs):
    assert len(args) == 2
    a1 = int(do(args[0],envs))
    a2 = int(do(args[1],envs))
    assert a1 in [0,1] and a2 in [0,1]
    if a1 and a2:
        return 1
    return 0

def do_OR(args,envs):
    assert len(args) == 2
    a1 = int(do(args[0],envs))
    a2 = int(do(args[1],envs))
    assert a1 in [0,1] and a2 in [0,1]
    if a1 or a2:
        return 1
    return 0

def do_NOT(args,envs):
    assert len(args) == 1
    a1 = int(do(args[0],envs))
    assert a1 in [0,1]
    if a1 == 1:
        return 0
    return 1

def do_loop_until(args,envs):
    assert len(args) == 2
    until = do(args[1],envs)
    assert isinstance(until,type(True))
    while not until:
        action = do(args[0],envs)
        until = do(args[1],envs)
    return action

def do_create_array(args,envs):
    assert len(args) == 1
    l = []
    size = do(args[0],envs)
    for i in range(size):
        l.append(0)
    return l

def do_get_array_value(args,envs):
    assert len(args) == 2
    array = do(args[0],envs)
    index = do(args[1],envs)
    assert isinstance(index,int)
    assert index < len(array)
    return array[index]

def do_set_array_value(args,envs):
    assert len(args) == 3
    array = do(args[0],envs)
    index = do(args[1],envs)
    value = do(args[2],envs)
    assert isinstance(array,list)
    assert isinstance(index,int) # since we now also handle floats in do
    assert index < len(array)
    assert isinstance(value,(int,float))
    array[index] = value # this works because we're modifying the array in envs
    return array

def do_get_array_size(args,envs):
    assert len(args) == 1
    array = do(args[0],envs)
    assert isinstance(array,list)
    return len(array)

def do_concatenate_array(args,envs):
    assert len(args) == 2
    a1 = do(args[0],envs)
    a2 = do(args[1],envs)
    assert isinstance(a1,list)
    assert isinstance(a2,list)
    a1.extend(a2)
    return a1

def do_create_set(args,envs): # passing args so the do function doesn't tweak out
    assert len(args) == 0
    return set()

def do_set_insert(args,envs):
    assert len(args) == 2
    s1 = do(args[0],envs)
    element = do(args[1],envs)
    assert isinstance(s1,set)
    if element in s1:
        warnings.warn("Element already in set!")
        return s1
    s1.add(element)
    return s1

def do_exist_set(args,envs):
    assert len(args) == 2
    s1 = do(args[0],envs)
    element = do(args[1],envs)
    assert isinstance(s1,set)
    if element in s1:
        return True
    return False

def do_set_size(args,envs):
    assert len(args) == 1
    s1 = do(args[0],envs)
    assert isinstance(s1,set)
    return len(s1)

def do_merge_set(args,envs):
    assert len(args) == 2
    s1 = do(args[0],envs)
    s2 = do(args[1],envs)
    assert isinstance(s1,set)
    assert isinstance(s2,set)
    for i in s2:
        if i not in s1:
            s1.add(i)
    return s1

def do_map(args, envs):
    assert len(args) == 2, "Map requires 2 arguments: array and function"
    
    array_name = args[0]
    array = env_get(array_name, envs) 
    assert isinstance(array, list), "The first argument to MAP must be an array"
    
    func_name = args[1]
    assert isinstance(func_name,str) or isinstance(func_name,list)
    func_obj = do(func_name,envs)
    assert isinstance(func_obj, list) and func_obj[0] == "func", "Second argument to MAP must be a function"

    params = func_obj[1]
    body = func_obj[2]
    assert len(params) == 1, f"Too many parameters! Should be only 1!"

    result_array = []
    for element in array:
        local_env = {params[0]: element}
        envs.append(local_env)

        mapped_value = do(body, envs)
        result_array.append(mapped_value)

        envs.pop()
    
    return result_array


def do_reduce(args, envs):
    assert len(args) == 2, "REDUCE requires 2 arguments: array and function"
    
    array_name = args[0]
    array = env_get(array_name, envs)  
    assert isinstance(array, list), "The first argument to REDUCE must be an array"

    if len(array) == 0:
        raise Exception("REDUCE cannot be applied to an empty array")

    func_name = args[1]
    assert isinstance(func_name,str) or isinstance(func_name,list)
    func_obj = do(func_name,envs)
    assert isinstance(func_obj, list) and func_obj[0] == "func", "Second argument to REDUCE must be a function"

    params = func_obj[1]
    body = func_obj[2]
    assert len(params) == 2

    count = array[0]

    for i in range(1, len(array)):
        current_element = array[i]

        local_env = {
            params[0]: count,
            params[1]: current_element
        }

        envs.append(local_env)
        count = do(body, envs)
        envs.pop()

    return count

def do_filter(args, envs):
    assert len(args) == 2, "FILTER requires 2 arguments: array and function"
    
    array_name = args[0]
    array = env_get(array_name, envs)  
    assert isinstance(array, list), "The first argument to FILTER must be an array"
    
    func_name = args[1]
    assert isinstance(func_name,str) or isinstance(func_name,list)
    func_obj = do(func_name,envs)
    assert isinstance(func_obj, list) and func_obj[0] == "func", "Second argument to FILTER must be a function"

    params = func_obj[1]
    body = func_obj[2]
    assert len(params) == 1, f"FILTER must take only 1 parameter, got {len(params)}"

    filter_array = []

    for element in array:
        local_env = {params[0]: element}
        envs.append(local_env)
        filtered = do(body, envs)
        envs.pop()
        if filtered:
            filter_array.append(element)
        
    return filter_array

def do_print(args, envs):
    args = [do(a, envs) for a in args]
    print(*args)
    return None

def do_func(args, envs):
    assert len(args) == 2
    params = args[0]
    body = args[1]
    return ["func",params,body]

def do_call(args,envs):
    assert len(args) >= 1
    assert isinstance(args[0],str)
    name_func = args[0]
    values = [do(a,envs) for a in args[1:]]

    func = env_get(name_func,envs)
    assert isinstance(func,list) and (func[0] == "func")
    params = func[1]
    body = func[2]
    assert len(values) == len(params), f"You passed {len(values)} parameters instead of {len(params)}"

    local_env = dict() 
    for index,param_name in enumerate(params):
        local_env[param_name] = values[index]
    envs.append(local_env)

    if tracing == True: 
        with TraceCalls(name_func) as T:
            result = do(body,envs)
    else:
        result = do(body,envs)
    
    envs.pop()

    return result

OPS = {
    name.replace("do_",""): func
    for (name,func) in globals().items()
    if name.startswith("do_")
}


def do(program,envs):
    if isinstance(program,(int,float)):
        return program
    elif isinstance(program, str):
        return env_get(program, envs)
    elif isinstance(program, list):
        #print(program[0]) # have it in here for debugging purposes, remove if not needed
        assert program[0] in OPS, f"Unknown operation {program[0]}"
        func = OPS[program[0]]
        dont_trace = ["call", "set", "get", "seq", "func"]
        
        if tracing and Trace and program[0] not in dont_trace:#the "and Trace" checks if the list above already has something inside, that means it is called within another call
            with TraceCalls(program[0]) as T:
                return func(program[1:], envs)
        else:
            return func(program[1:],envs)

def TracingPrint(Calls, nested = 0):
    for Call in Calls:
        if nested == 0:
            indent = "  "*nested + "+--"
        else:
            indent = "|"+"  "*nested + "+--"
        print(f"{indent}{Call.func_name} ({Call.duration():.9f}ms)")
        TracingPrint(Call.nextCall,nested+1)

def main():
    global tracing
    if "--trace" in sys.argv:
        tracing = True
        filename = sys.argv[2]
    else: 
        filename = sys.argv[1]
    
    with open(filename,'r') as f:
        program = json.load(f)
        envs = [dict()] 
        result = do(program,envs)
    print(">>>" , result)
    pprint.pprint(envs)

    if tracing == True:
        print("main")
        TracingPrint(InitialCalls)
        print("+--print")

if __name__ == '__main__':
    main()