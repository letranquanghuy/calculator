# Calculator

This is a simple calculator application built with Django.

## Install the required packages:

    pip install -r requirements.txt

## Running the Application

1. Apply the migration:

    ```sh
    python manage.py migrate
    ```

2. Start the development server:

    ```sh
    python manage.py runserver
    ```

3. Open your web browser and go to:

    ```
    http://127.0.0.1:8000/
    ```

## Usage

- Use the calculator interface to perform basic arithmetic operations.
- The application supports addition, subtraction, multiplication, division, square root, and factorial operations.
- The logic is defined in calculator\views.py.
- The UI is implemented in templates\calculator\index.html.

## Keyboard Shortcuts

This application supports the following keyboard shortcuts for faster interaction:

| Key             | Action                          |
|-----------------|---------------------------------|
| `0`-`9`         | Click the corresponding number button |
| `+`             | Click the add button           |
| `-`             | Click the subtract button      |
| `*`             | Click the multiply button      |
| `/`             | Click the divide button        |
| `Enter`         | Click the equals button        |
| `Backspace`     | Click the backspace button     |
| `Delete`        | Click the clear button         |
| `(`             | Click the open parenthesis button |
| `)`             | Click the close parenthesis button |
| `.`             | Click the decimal point button |
| `%`             | Click the percentage button    |
| `^`             | Click the power button         |
| `!`             | Click the factorial button     |
| `p`             | Click the pi button            |
| `s`             | Click the square root button   |
