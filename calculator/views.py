import json
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import math
from math import sqrt, factorial, pi

# Create your views here.
def index(request):
    return render(request, r"calculator\index.html")


def preprocess_expression(expression):
    """Preprocess a mathematical expression string for evaluation."""
    open_count = expression.count('(')
    close_count = expression.count(')')

    # If '(' are greater than ')', append ')' to balance
    if open_count > close_count:
        expression += ')' * (open_count - close_count)
    elif open_count < close_count:
        return "ERROR"
    
    expression = apply_basic_transformations(expression)
    expression = remove_leading_zeros(expression)
    expression = process_factorial(expression)
    expression = process_pi(expression)
    expression = process_parenthesis(expression)

    return expression

def apply_basic_transformations(expression):
    """Apply basic symbol transformations for mathematical expressions."""
    transformations = [
        ("x", "*"),
        ("÷", "/"),
        ("%", "/100"),
        ("√", "sqrt"),
        ("^", "**")  # Handles power
    ]
    for old, new in transformations:
        expression = expression.replace(old, new)
    return expression

def process_factorial(expression):
    """Replace factorial notation with factorial."""
    return re.sub(r"(\d+)!", r"(factorial(\1))", expression)

def process_parenthesis(expression):
    """Ensure multiplication is explicitly added around parentheses where necessary."""
    patterns = [
        (r"(\d)(\()", r"\1*\2"),  # Add * between number and (
        (r"(\))(\d)", r"\1*\2"),  # Add * between ) and number
        (r"(\))(\()", r"\1*\2"),  # Add * between ) and (
        (r"(\d)(sqrt)", r"\1*\2"),  # Add * between number and sqrt
        (r"(\))(sqrt)", r"\1*\2"),  # Add * between ) and sqrt
    ]
    for pattern, replacement in patterns:
        expression = re.sub(pattern, replacement, expression)
    return expression

def process_pi(expression):
    """Replace pi symbol with pi."""
    return expression.replace("π", "(pi)")

def remove_leading_zeros(expression):
    """Remove unnecessary leading zeros from numbers."""
    return re.sub(r"\b0+(\d)", r"\1", expression)

def evaluate_expression(expression):
    result = eval(expression)
    if isinstance(result, float):
        result = round(result, 10)
    if result == int(result):
        result = int(result)
    return result

def cal_eval(expression):
    result = eval(expression)
    if result.is_integer():
        result = int(result)
    return str(result)

def calculate(expression, start=0):
    sub_expression = ""
    i = start
    while i < len(expression):
        if expression[i] == ")":
            return cal_eval(sub_expression), i
        if expression[i] == "(":
            is_sqrt = expression[i-4: i] == "sqrt"
            result, i = calculate(expression, start=i+1)
            if i < (len(expression)-1) and expression[i+1] == "!":
                if is_sqrt:
                    sub_expression = sub_expression[:-4] + "factorial"
                    result = cal_eval(f"sqrt({result})")
                else:
                    sub_expression += "factorial"
                sub_expression += "("
                sub_expression += result
                sub_expression += ")"

                i += 2
                continue
            sub_expression += "("
            sub_expression += result
        sub_expression += expression[i]
        i += 1
    
    return cal_eval(sub_expression)
@require_POST
def calculate_result(request):
    expression = request.POST["expression"]
    expression = preprocess_expression(expression)
    try:
        print("expression", expression)
        result = calculate(expression)
    except ZeroDivisionError:
        result = "INFINITY"

    return JsonResponse({'result': str(result)}, status=200)