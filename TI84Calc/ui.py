import tkinter as tk
import math
from calculator import CalculatorEngine
from graphing import GraphPlotter
from configure import BG_COLOR, DISPLAY_BG, DISPLAY_FG, BTN_BG, BTN_FG, FONT_DISPLAY, FONT_BTN, GRAPH_X_RANGE, GRAPH_Y_RANGE, GRID_SPACING, GRID_COLOR, FUNCTION_COLOR

class CalculatorUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TI-84 Graphing Calculator")
        self.root.geometry("800x600")
        self.root.configure(bg=BTN_BG)
        
        # Instantiate the calculator engine.
        self.engine = CalculatorEngine()
        
        # Set up a palette of up to 8 graph colors and a counter.
        self.graph_colors = ["#00FF00", "#FF0000", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#FFA500"]
        self.graph_index = 0
        
        # Create UI frames.
        self.create_frames()
        # Create the graph canvas.
        self.create_graph_canvas()
        # Create the expression display.
        self.create_display_label()
        # Create the keypad.
        self.create_keypad()
        
        # Initialize the GraphPlotter.
        self.plotter = GraphPlotter(self.graph_canvas, x_range=GRAPH_X_RANGE, y_range=GRAPH_Y_RANGE,
                                     grid_spacing=GRID_SPACING, grid_color=GRID_COLOR, function_color=FUNCTION_COLOR)
        self.plotter.draw_grid()
        
        # Bind keys for zooming in (I), zooming out (O), and resetting view (R).
        self.root.bind("<KeyPress-i>", lambda event: self.zoom_in())
        self.root.bind("<KeyPress-o>", lambda event: self.zoom_out())
        self.root.bind("<KeyPress-r>", lambda event: self.reset_view())
        self.root.bind("<KeyPress-R>", lambda event: self.reset_view())
        
        # Redraw graph when the canvas size changes.
        self.graph_canvas.bind("<Configure>", lambda event: self.redraw_graph())
        
        self.update_display()
        self.root.mainloop()

    def create_frames(self):
        # Top frame: Graph display.
        self.graph_frame = tk.Frame(self.root, bg=BG_COLOR, height=300)
        self.graph_frame.pack(fill="both", expand=True)
        
        # Middle frame: Expression display.
        self.display_frame = tk.Frame(self.root, bg=DISPLAY_BG, height=50)
        self.display_frame.pack(fill="x")
        
        # Bottom frame: Keypad.
        self.keypad_frame = tk.Frame(self.root, bg=BTN_BG)
        self.keypad_frame.pack(fill="both", expand=True)

    def create_graph_canvas(self):
        self.graph_canvas = tk.Canvas(self.graph_frame, bg=BG_COLOR, highlightthickness=0)
        self.graph_canvas.pack(fill="both", expand=True)

    def redraw_graph(self):
        # Redraw grid (with tick marks, axes, and labels) and the function if applicable.
        self.plotter.draw_grid()
        if self.engine.is_function():
            self.plot_function()

    def create_display_label(self):
        self.display_label = tk.Label(self.display_frame, text="", anchor="e",
                                      bg=DISPLAY_BG, fg=DISPLAY_FG, font=FONT_DISPLAY)
        self.display_label.pack(fill="both", padx=10, pady=10)

    def update_display(self):
        self.display_label.config(text=self.engine.expression)

    def create_keypad(self):
        # New keypad layout, arranged in vertical rows similar to a TI-84.
        button_layout = [
            [("Clear", self.clear), ("Del", self.delete), ("(", lambda: self.append_to_expr("(")), (")", lambda: self.append_to_expr(")")), ("Graph", self.graph_mode)],
            [("7", lambda: self.append_to_expr("7")), ("8", lambda: self.append_to_expr("8")), ("9", lambda: self.append_to_expr("9")), ("/", lambda: self.append_to_expr("/")), ("Sin", lambda: self.append_to_expr("sin("))],
            [("4", lambda: self.append_to_expr("4")), ("5", lambda: self.append_to_expr("5")), ("6", lambda: self.append_to_expr("6")), ("*", lambda: self.append_to_expr("*")), ("Cos", lambda: self.append_to_expr("cos("))],
            [("1", lambda: self.append_to_expr("1")), ("2", lambda: self.append_to_expr("2")), ("3", lambda: self.append_to_expr("3")), ("-", lambda: self.append_to_expr("-")), ("Tan", lambda: self.append_to_expr("tan("))],
            [("0", lambda: self.append_to_expr("0")), (".", lambda: self.append_to_expr(".")), ("^", lambda: self.append_to_expr("**")), ("+", lambda: self.append_to_expr("+")), ("Log", lambda: self.append_to_expr("log("))],
            [("ln", lambda: self.append_to_expr("ln(")), ("exp", lambda: self.append_to_expr("exp(")), ("x", lambda: self.append_to_expr("x")), ("√", lambda: self.append_to_expr("sqrt(")), ("x²", lambda: self.append_to_expr("**2"))],
            [("Ans", self.insert_ans), ("Y=", self.set_function_mode), ("Zoom", self.zoom), ("Window", self.window_settings), ("Trace", self.trace)],
            [("Enter", self.enter)]
        ]
        
        # Create buttons using grid layout.
        for r, row in enumerate(button_layout):
            for c, (text, command) in enumerate(row):
                btn = tk.Button(self.keypad_frame, text=text, command=command, bg=BTN_BG,
                                fg=BTN_FG, font=FONT_BTN)
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
        
        total_rows = len(button_layout)
        total_cols = max(len(row) for row in button_layout)
        for i in range(total_rows):
            self.keypad_frame.rowconfigure(i, weight=1)
        for j in range(total_cols):
            self.keypad_frame.columnconfigure(j, weight=1)

    def append_to_expr(self, value):
        self.engine.add_to_expression(value)
        self.update_display()

    def clear(self):
        # Clear both the expression and the graph.
        self.engine.clear()
        self.graph_canvas.delete("all")
        self.plotter.draw_grid()
        self.update_display()

    def delete(self):
        # Remove the last character from the expression.
        # If the expression is already empty, treat this as a command to clear the old graph.
        self.engine.expression = self.engine.expression[:-1]
        self.update_display()
        if not self.engine.expression:
            self.clear_graph()

    def clear_graph(self):
        # Delete the graph from the canvas and increment the graph index (cycling through our palette).
        self.graph_canvas.delete("function")
        self.graph_index = (self.graph_index + 1) % len(self.graph_colors)

    def enter(self):
        if self.engine.is_function():
            self.plot_function()
        else:
            self.engine.evaluate()
            self.update_display()

    def graph_mode(self):
        if self.engine.is_function():
            self.plot_function()
        else:
            self.enter()

    def set_function_mode(self):
        if "x" not in self.engine.expression:
            self.append_to_expr("x")

    def zoom(self):
        print("Use I (zoom in) and O (zoom out) keys for zooming.")

    def window_settings(self):
        print("Window settings functionality not implemented yet.")

    def trace(self):
        print("Trace functionality not implemented yet.")

    def plot_function(self):
        self.plotter.draw_grid()
        # Set the plotter's function color to the current graph color.
        self.plotter.function_color = self.graph_colors[self.graph_index]
        def func(x):
            return self.engine.evaluate_function(x)
        self.plotter.plot_function(func)
        self.update_display()

    def zoom_in(self):
        # Zoom in: reduce the viewing window by 20%.
        factor = 0.8
        x_min, x_max = self.plotter.x_range
        y_min, y_max = self.plotter.y_range
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        half_width = (x_max - x_min) * factor / 2
        half_height = (y_max - y_min) * factor / 2
        new_x_range = (x_center - half_width, x_center + half_width)
        new_y_range = (y_center - half_height, y_center + half_height)
        self.plotter.set_coordinate_system(new_x_range, new_y_range)
        self.redraw_graph()

    def zoom_out(self):
        # Zoom out: increase the viewing window by 20%.
        factor = 1.2
        x_min, x_max = self.plotter.x_range
        y_min, y_max = self.plotter.y_range
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        half_width = (x_max - x_min) * factor / 2
        half_height = (y_max - y_min) * factor / 2
        new_x_range = (x_center - half_width, x_center + half_width)
        new_y_range = (y_center - half_height, y_center + half_height)
        self.plotter.set_coordinate_system(new_x_range, new_y_range)
        self.redraw_graph()

    def reset_view(self):
        from configure import GRAPH_X_RANGE, GRAPH_Y_RANGE
        self.plotter.set_coordinate_system(GRAPH_X_RANGE, GRAPH_Y_RANGE)
        self.redraw_graph()

    def insert_ans(self):
        # Insert the last computed answer into the expression.
        self.append_to_expr(self.engine.last_answer)

if __name__ == "__main__":
    CalculatorUI()
