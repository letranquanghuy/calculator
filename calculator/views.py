import json
import re
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import math

# Create your views here.
def index(request):
    return render(request, "calculator\index.html")

def preprocess_expression(expression):
    expression = remove_leading_zeros(expression)
    expression = process_square_root(expression)
    expression = process_factorial(expression)
    expression = process_pi(expression)
    expression = process_power(expression)
    expression = process_parenthesis(expression)
    return expression

def process_factorial(expression):
    return re.sub(r"(\d+)!", r"(math.factorial(\1))", expression)

def process_square_root(expression):
    expression = re.sub(r"√(\d+)", r"(math.sqrt(\1))", expression)
    expression = re.sub(r"√(π)", r"(math.sqrt(\1))", expression)
    return expression

def process_power(expression):
    return expression.replace("^","**")

def process_parenthesis(expression):
    # Thêm dấu '*' giữa số và dấu '('
    expression = re.sub(r"(\d)(\()", r"\1*\2", expression)
    # Thêm dấu '*' giữa ')' và số
    expression = re.sub(r"(\))(\d)", r"\1*\2", expression)
    # Thêm dấu '*' giữa ')' và '('
    expression = re.sub(r"(\))(\()", r"\1*\2", expression)
    return expression

def process_pi(expression):
    return expression.replace("π","(math.pi)")

def remove_leading_zeros(expression):
    return re.sub(r'\b0+(\d)', r'\1', expression)

def evaluate_expression(expression):
    try:
        result = eval(expression)
        if isinstance(result, float):
            result = round(result, 10)
        if result == int(result):
            result = int(result)
    except Exception as e:
        result = str(e)
    return result

@require_POST
def calculate_result(request):
    expression = request.POST["expression"]
    expression = expression.replace("x", "*").replace("÷", "/").replace("%", "/100")
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