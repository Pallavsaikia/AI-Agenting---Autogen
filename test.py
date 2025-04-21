import inspect

async def sum_of_number(number1: int, number2: int) -> float:
    print(number1, number2)
    return number1 + number2

# Get function source code as string
function_code = inspect.getsource(sum_of_number)

print(function_code)
