"""Helper for Calculator Plugin."""

def word_conv(textnum, numwords={}):
    """Function that converts words to numbers"""
    if not numwords:
        units = [
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        ]

        tens = [
            "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
            "eighty", "ninety"
        ]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10**(idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            error_text = "Illegal word: "
            return error_text

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def add(left: float, right: float)-> float:
    """Add two operands.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Sum of both operands.

    """

    return left + right

def sub(left: float, right: float)-> float:
    """Subtract Second operand from the First operand.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Subtraction of the first operand from the second operand.

    """

    return left - right

def mul(left: float, right: float) -> float:
    """Multiplies first operand with the second operand.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Multiplication of the first operand with the second operand.

    """
    return left * right

def div(left: float, right: float) -> float:
    """Divides first operand with the second operand.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Division of the first operand with the second operand.

    """
    return left / right

def run(operator, left: float, right: float)-> float:
    """Execute the calculation"""
    if operator == 'add':
        res = add(left, right)
        return res
    elif operator == 'sub':
        res = sub(left, right)
        return res
    elif operator == 'multiply':
        res = mul(left, right)
        return res
    elif operator == 'division':
        res = div(left, right)
        return res


