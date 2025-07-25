import math

class CalculatorEngine:
    def __init__(self):
        # Store the current expression as a string.
        self.expression = ""
        # Last computed answer; used for the Ans key.
        self.last_answer = "0"
        # Angle mode: "RAD" (default) or "DEG".
        self.angle_mode = "RAD"
        # Predefined constants, stored with high precision.
        self.variables = {
            "pi": float(f"{math.pi:.30f}"),
            "e": float(f"{math.e:.30f}")
        }

    def add_to_expression(self, value):
        """Appends a character or substring to the current expression."""
        self.expression += str(value)
    
    def set_expression(self, expr):
        """Directly sets the current expression (useful for function definitions)."""
        self.expression = str(expr)
    
    def clear(self):
        """Clears the current expression."""
        self.expression = ""
    
    def set_angle_mode(self, mode):
        """Sets the angle mode to 'RAD' or 'DEG' (case-insensitive)."""
        mode = mode.upper()
        if mode in ("RAD", "DEG"):
            self.angle_mode = mode
        else:
            raise ValueError("Angle mode must be 'RAD' or 'DEG'.")

    def is_function(self):
        """Returns True if the current expression contains the variable 'x'."""
        return 'x' in self.expression

    # --- Internal helper functions for safe evaluation ---
    def _sin(self, x):
        if self.angle_mode == "DEG":
            return math.sin(math.radians(x))
        return math.sin(x)

    def _cos(self, x):
        if self.angle_mode == "DEG":
            return math.cos(math.radians(x))
        return math.cos(x)

    def _tan(self, x):
        if self.angle_mode == "DEG":
            return math.tan(math.radians(x))
        return math.tan(x)
    
    def _get_allowed_names(self):
        """
        Returns a dictionary of allowed functions and variables for safe evaluation.
        """
        allowed = {
            "sin": self._sin,
            "cos": self._cos,
            "tan": self._tan,
            "log": math.log10,  # Base-10 logarithm
            "ln": math.log,     # Natural logarithm
            "sqrt": math.sqrt,
            "abs": abs,
            "exp": math.exp     # Exponential function
        }
        # Include our constants.
        allowed.update(self.variables)
        return allowed

    # --- Evaluation methods ---
    def evaluate(self):
        """
        Evaluates the current expression (for constant expressions).
        Returns the result as a string and updates the expression and last_answer.
        """
        try:
            allowed = self._get_allowed_names()
            result = eval(self.expression, {"__builtins__": {}}, allowed)
            self.last_answer = str(result)
            self.expression = str(result)
            return self.expression
        except Exception:
            self.expression = "Error"
            return self.expression

    def evaluate_function(self, x_value):
        """
        Evaluates the current expression as a function of x.
        Substitutes the provided x_value into the expression and returns the computed result.
        """
        try:
            allowed = self._get_allowed_names()
            allowed['x'] = x_value
            result = eval(self.expression, {"__builtins__": {}}, allowed)
            return result
        except Exception:
            return None

    # --- Convenience methods ---
    def square(self):
        """Squares the current expression."""
        try:
            allowed = self._get_allowed_names()
            result = eval(f"({self.expression})**2", {"__builtins__": {}}, allowed)
            self.last_answer = str(result)
            self.expression = str(result)
            return self.expression
        except Exception:
            self.expression = "Error"
            return self.expression

    def square_root(self):
        """Takes the square root of the current expression."""
        try:
            allowed = self._get_allowed_names()
            result = eval(f"sqrt({self.expression})", {"__builtins__": {}}, allowed)
            self.last_answer = str(result)
            self.expression = str(result)
            return self.expression
        except Exception:
            self.expression = "Error"
            return self.expression

# Example testing block (can be removed for production)
if __name__ == "__main__":
    engine = CalculatorEngine()
    engine.set_expression("2+3*4")
    print("Evaluate 2+3*4 =", engine.evaluate())  # Expected: 14

    engine.set_expression("x**2 + 2*x + 1")
    print("f(5) =", engine.evaluate_function(5))   # Expected: 36

    engine.set_expression("sin(30)")
    engine.set_angle_mode("DEG")
    print("sin(30 DEG) =", engine.evaluate())  # Expected: 0.5
