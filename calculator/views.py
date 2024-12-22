import json
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import math
from math import sqrt, factorial, pi
import sys

from calculator.models import CalculationHistory
# sys.set_int_max_str_digits(0)
# Create your views here.
def index(request):
    history = CalculationHistory.objects.all()
    return render(request, r"calculator\index.html", {'history': history})


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
    expression = normalize_number(expression)
    expression = replace_scientific_notation(expression)
    expression = process_factorial(expression)
    expression = process_pi(expression)
    expression = process_parenthesis(expression)
    if not validate_balance_parenthese(expression):
        return "ERROR"
    return expression


def replace_scientific_notation(expression):
    # Match scientific notation in the form of e-n where n is a number
    return re.sub(r'e-(\d+)', r'*10**(-\1)', expression)

def validate_balance_parenthese(expression):
    stack = []
    for char in expression:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack:
                return False
            stack.pop()
    return not stack

def apply_basic_transformations(expression):
    """Apply basic symbol transformations for mathematical expressions."""
    transformations = [
        ("x", "*"),
        ("÷", "/"),
        ("√", "sqrt"),
        ("^", "**")
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
    return expression.replace("π", f"({pi})")

def normalize_number(expression):
    def normalize_match(match):
        if '.' not in match.group():
            return str(int(match.group()))
        return str(float(match.group()))

    normalized_expression = re.sub(r'(\d+(\.\d+)?e[+-]?\d+)', lambda match: f"({match.group()})", expression)
    normalized_expression = re.sub(r'(?<!\w)(0+)?\d+(\.\d+)?(?!\w)', normalize_match, normalized_expression)
    return normalized_expression


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def evaluate_expression(expression):
    result = eval(expression)
    if isinstance(result, float):
        result = round(result, 10)
    if result.is_integer():
        result = int(result)
    return str(result)

def replace_match_with_evaluation(match):
    expression = match.group(0)
    return evaluate_expression(expression)

def replace_factorial(match):
    if match.group(1):
        num = match.group(1)
        return f"factorial({num})"

    if match.group(3):
        expression = match.group(3)
        return f"factorial({expression})"

def calculate(expression):
    i = 0
    old_expression = None
    while not is_number(expression):
        if old_expression == expression:
            expression = "ERROR"
            break
        old_expression = expression
        # calculate the expression inside parentheses
        expression = re.sub(r"(?<!\w)(\(([-+*/\d.\s]+)\))", replace_match_with_evaluation, expression)
        # calculate the function
        expression = re.sub(r"\b[a-zA-Z_]+\(([-+*/\d.\s]+)\)", replace_match_with_evaluation, expression)
        # process factorial
        expression = re.sub(r"(\d+(\.\d+)?)!|(\(([-+*/\d.\s]+)\))!", replace_factorial, expression)
        print(f"after factorial: {expression}")
        if "(" not in expression and ")" not in expression:
            expression = evaluate_expression(expression)
    else:
        expression = evaluate_expression(expression)
    return expression

@require_POST
def calculate_result(request):
    expression = request.POST["expression"]
    original_expression = expression
    print("pre_expression", expression)
    expression = preprocess_expression(expression)
    try:
        print("expression", expression)
        result = calculate(expression)
        history_entry = CalculationHistory(expression=original_expression, result=str(result))
        history_entry.save()
    except ZeroDivisionError and OverflowError:
        result = "INFINITY"
    except ValueError as e:
        if "Exceeds the limit" in str(e):
            result = "INFINITY"
        else:
            result = "ERROR"
    except Exception:
        result = "ERROR"

    return JsonResponse({'result': str(result)}, status=200)

@require_POST
def handle_percentage(request):
    expression = request.POST["expression"]
    sub_expression = ""
    last_index = 0
    first_open = None
    stack = []

    if expression[-1] != ")":
        result = re.sub(
            r'(\d+(\.\d+)?(e[+-]?\d+)?)%', 
            lambda match: calculate(preprocess_expression(match.group(1)+"/100")), 
            expression + "%"
        )
        if "%" in result:
            result = expression
        if result == "π":
            result = pi/100
    else:
        for i in range(len(expression) - 1, -1, -1):
            last_index = i
            if expression[i] == ")":
                stack.append(expression[i])
            elif expression[i] == "(":
                stack.pop()
                if first_open is None:
                    first_open = i
            sub_expression = expression[i] + sub_expression
            if not stack:
                if expression[i-1] == "√":
                    sub_expression = "√" + sub_expression
                    last_index = i - 1
                break
        if stack:
            result = expression[:first_open] + "ERROR"
        else:
            print(sub_expression)
            result =expression[:last_index] + calculate(preprocess_expression(sub_expression)+'/100')

    return JsonResponse({'result': str(result)}, status=200)

@require_POST
def clear_history(request):
    try:
        # Assuming the history is stored in a model called History
        CalculationHistory.objects.all().delete()  # Delete all history records
        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)