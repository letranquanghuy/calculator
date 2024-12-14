import json
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import math

# Create your views here.
def index(request):
    return render(request, "calculator\index.html")
import re
import math

def preprocess_expression(expression):
    """Preprocess a mathematical expression string for evaluation."""
    expression = apply_basic_transformations(expression)
    expression = remove_leading_zeros(expression)
    expression = process_square_root(expression)
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
        ("^", "**")  # Handles power
    ]
    for old, new in transformations:
        expression = expression.replace(old, new)
    return expression

def process_factorial(expression):
    """Replace factorial notation with math.factorial."""
    return re.sub(r"(\d+)!", r"(math.factorial(\1))", expression)

def process_square_root(expression):
    """Replace square root notation with math.sqrt."""
    return re.sub(r"√(\d+|π)", r"(math.sqrt(\1))", expression)  # Handles √ for square root and π for pi

def process_parenthesis(expression):
    """Ensure multiplication is explicitly added around parentheses where necessary."""
    patterns = [
        (r"(\d)(\()", r"\1*\2"),  # Add * between number and (
        (r"(\))(\d)", r"\1*\2"),  # Add * between ) and number
        (r"(\))(\()", r"\1*\2"),  # Add * between ) and (
    ]
    for pattern, replacement in patterns:
        expression = re.sub(pattern, replacement, expression)
    return expression

def process_pi(expression):
    """Replace pi symbol with math.pi."""
    return expression.replace("π", "(math.pi)")

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

@require_POST
def calculate_result(request):
    expression = request.POST["expression"]
    expression = preprocess_expression(expression)
    try:
        print(expression)
        result = evaluate_expression(expression)
        if result == int(result):
            result = int(result)
    except ZeroDivisionError:
        result = "INFINITY"
    except Exception as e:
        result = "ERROR"

    return JsonResponse({'result': str(result)}, status=200)