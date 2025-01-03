import json
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import math
from math import sqrt, factorial, pi
import sys
from sympy import sympify, oo, zoo, I
from decimal import Decimal

from calculator.models import CalculationHistory


sys.set_int_max_str_digits(0)


# Create your views here.
def index(request):
    history = CalculationHistory.objects.all()
    formatted_history = [
        {
            "expression": format_display_expression(record.expression),
            "result": format_display_number(record.result),
            "created_at": record.created_at,
        }
        for record in history
    ]
    return render(request, r"calculator\index.html", {"history": formatted_history})


def format_display_expression(value):
    value = value.replace("+-", "-")
    return re.sub(
        r"\d+(\.\d+)?", lambda match: format_display_number(match.group()), value
    )


def format_display_number(number_str):
    print("raw number_str", number_str)
    number = Decimal(number_str)
    number_str = f"{number:.10f}".rstrip("0").rstrip(".")
    print("number_str", number_str)
    if "." in number_str:
        integer_part, fractional_part = number_str.split(".")
        formatted_integer = f"{int(integer_part):,}"
        print("fractional_part", fractional_part)
        return f"{formatted_integer}.{fractional_part}"
    else:
        return f"{int(number_str):,}"


def preprocess_expression(expression):
    """Preprocess a mathematical expression string for evaluation."""
    print("expression in preprocess", expression)
    open_count = expression.count("(")
    close_count = expression.count(")")

    # If '(' are greater than ')', append ')' to balance
    if open_count > close_count:
        expression += ")" * (open_count - close_count)
    elif open_count < close_count:
        return "ERROR"

    expression = apply_basic_transformations(expression)
    expression = normalize_number(expression)
    expression = process_pi(expression)
    expression = process_parenthesis(expression)
    if not validate_balance_parenthese(expression):
        return "ERROR"
    return expression


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
    transformations = [("x", "*"), ("÷", "/"), ("√", "sqrt"), ("^", "**")]
    for old, new in transformations:
        expression = expression.replace(old, new)
    return expression


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
        if "." not in match.group():
            return str(int(match.group()))
        return f"{float(match.group()):.10f}".rstrip("0").rstrip(".")

    normalized_expression = re.sub(
        r"(?<!\w)(0+)?\d+(\.\d+)?(?!\w)", normalize_match, expression
    )
    return normalized_expression


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def evaluate_expression(expression):
    result = sympify(expression).evalf()
    if result is zoo or result is oo:
        raise ZeroDivisionError

    if result.has(I):
        raise ValueError(f"Complex number detected in expression: {expression}")

    if result.is_real:
        # Làm tròn đến 10 chữ số thập phân
        result = round(float(result), 10)
        if result.is_integer():
            result = int(result)
    return str(result)


def replace_match_with_evaluation(match):
    expression = match.group(0)
    return f"({evaluate_expression(expression)})"


def replace_factorial(match):
    if match.group(1):
        num_str = match.group(1)
    else:
        num_str = match.group(0)[1:-2]
    num = float(num_str)
    if not num.is_integer() or num < 0:
        raise ValueError(
            f"Factorial is not defined for non-integer values in expression: {num_str}"
        )
    return f"factorial({int(num)})"


def calculate(expression):
    i = 0
    old_expression = None
    while not is_number(expression):
        print("expression in calculate", expression)
        if old_expression == expression:
            expression = evaluate_expression(expression)
            break
        old_expression = expression
        # calculate the expression inside parentheses
        expression = re.sub(
            r"(\(([-+]?\d*\.?\d+|\(-?\d+\.?\d*\))([+\-*/^]+[-+\-*/\d.]+)+\))",
            replace_match_with_evaluation,
            expression,
        )
        print("expression in calculate", expression)
        # calculate the function
        expression = re.sub(
            r"\b[a-zA-Z_]+\(([-+*/\d.\s]+)\)", replace_match_with_evaluation, expression
        )
        print("expression in calculate", expression)
        # process factorial
        expression = re.sub(
            r"(\d+(\.\d+)?)!|(\((-?\d*\.?\d+)\))!", replace_factorial, expression
        )
        print("expression after process factorial", expression)
        if "sqrt" not in expression and "!" not in expression:
            expression = evaluate_expression(expression)
        print("expression in calculate", expression)
    else:
        expression = evaluate_expression(expression)
    print("expression after calculate", expression)
    return expression


@require_POST
def calculate_result(request):
    record = False
    expression = request.POST["expression"]
    if not expression:
        return JsonResponse({"result": ""}, status=200)

    original_expression = expression
    expression = preprocess_expression(expression)
    try:
        print("expression", expression)
        result = calculate(expression)
        display_result = format_display_number(result)
        # Get the last entry from the database
        last_entry = CalculationHistory.objects.all().last()
        if not last_entry or (
            last_entry.expression != original_expression or last_entry.result != result
        ):
            history_entry = CalculationHistory(
                expression=original_expression, result=result
            )
            history_entry.save()
            record = True
    except ZeroDivisionError or OverflowError:
        display_result = "INFINITY"
    except ValueError as e:
        if "Exceeds the limit" in str(e):
            display_result = "INFINITY"
        else:
            display_result = "ERROR"
    except Exception:
        display_result = "ERROR"

    return JsonResponse({"result": display_result, "record": record}, status=200)


@require_POST
def handle_percentage(request):
    expression = request.POST["expression"]
    sub_expression = ""
    last_index = 0
    first_open = None
    stack = []
    if not expression:
        return JsonResponse({"result": ""}, status=200)
    if expression[-1] != ")":
        print("its num", expression)
        if expression[-1] == "π":
            result = expression[:-1] + str(pi/100)
        else:
            result = re.sub(
                r"([0-9.]+)%",
                lambda match: f"{float(calculate(preprocess_expression(match.group(1) + "/100"))):.10f}".rstrip(
                    "0"
                ).rstrip(
                    "."
                ),
                expression + "%",
            )
            print("result after %", result)
            if "%" in result:
                result = expression

    else:
        for i in range(len(expression) - 1, -1, -1):
            last_index = i
            if expression[i] == ")":
                stack.append(expression[i])
            elif expression[i] == "(":
                stack.pop()
                if first_open is None and not (i != 0 and expression[i - 1] == "√"):
                    first_open = i
            sub_expression = expression[i] + sub_expression
            if not stack:
                if expression[i - 1] == "√":
                    sub_expression = "√" + sub_expression
                    last_index = i - 1
                break
        if stack:
            result = expression[:first_open] + "ERROR"
        else:
            print(sub_expression)
            result = expression[:last_index] + calculate(
                preprocess_expression(sub_expression) + "/100"
            )

    display_result = format_display_expression(str(result))
    print("display_result", display_result)
    return JsonResponse({"result": display_result}, status=200)


@require_POST
def clear_history(request):
    try:
        # Assuming the history is stored in a model called History
        CalculationHistory.objects.all().delete()  # Delete all history records
        return JsonResponse({"status": "success"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
