import math

class GraphPlotter:
    """
    Class responsible for drawing the grid, axes (with tick marks), and plotting functions on a Tkinter canvas.
    """
    def __init__(self, canvas, x_range=(-10, 10), y_range=(-10, 10),
                 grid_spacing=20, grid_color="#444444", function_color="#00FF00",
                 axes_color="#FFFFFF"):
        """
        Initialize the plotter.
        
        :param canvas: Tkinter Canvas widget.
        :param x_range: Tuple (x_min, x_max) for horizontal axis.
        :param y_range: Tuple (y_min, y_max) for vertical axis.
        :param grid_spacing: Spacing (in pixels) for grid lines.
        :param grid_color: Color for grid lines.
        :param function_color: Color for the plotted function.
        :param axes_color: Color for the x and y axes (and tick marks/labels).
        """
        self.canvas = canvas
        self.x_range = x_range
        self.y_range = y_range
        self.grid_spacing = grid_spacing
        self.grid_color = grid_color
        self.function_color = function_color
        self.axes_color = axes_color

    def draw_grid(self):
        """
        Draws the grid lines, axes with tick marks and labels.
        """
        # Clear previous drawings.
        self.canvas.delete("grid")
        self.canvas.delete("axes")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Draw grid lines.
        for x in range(0, width, self.grid_spacing):
            self.canvas.create_line(x, 0, x, height, fill=self.grid_color, tags="grid")
        for y in range(0, height, self.grid_spacing):
            self.canvas.create_line(0, y, width, y, fill=self.grid_color, tags="grid")
        
        # Draw axes if 0 is within the coordinate ranges.
        if self.x_range[0] < 0 < self.x_range[1]:
            x0 = self.map_x(0)
            self.canvas.create_line(x0, 0, x0, height, fill=self.axes_color, width=2, tags="axes")
        if self.y_range[0] < 0 < self.y_range[1]:
            y0 = self.map_y(0)
            self.canvas.create_line(0, y0, width, y0, fill=self.axes_color, width=2, tags="axes")
        
        # Draw tick marks on the x-axis.
        x_min, x_max = self.x_range
        for x_val in range(math.ceil(x_min), math.floor(x_max) + 1):
            pixel_x = self.map_x(x_val)
            # Determine y position for tick marks: if x-axis exists use y=0, else use a default offset.
            if self.y_range[0] < 0 < self.y_range[1]:
                y_tick = self.map_y(0)
            else:
                y_tick = height - 10
            # Draw a small vertical tick.
            self.canvas.create_line(pixel_x, y_tick - 5, pixel_x, y_tick + 5, fill=self.axes_color, tags="axes")
            # Label the tick; label the origin as "O".
            label = "O" if x_val == 0 else str(x_val)
            self.canvas.create_text(pixel_x, y_tick + 15, text=label, fill=self.axes_color, font=("Arial", 8), tags="axes")
        
        # Draw tick marks on the y-axis.
        y_min, y_max = self.y_range
        for y_val in range(math.ceil(y_min), math.floor(y_max) + 1):
            pixel_y = self.map_y(y_val)
            # Determine x position for tick marks: if y-axis exists use x=0, else use a default offset.
            if self.x_range[0] < 0 < self.x_range[1]:
                x_tick = self.map_x(0)
            else:
                x_tick = 10
            # Draw a small horizontal tick.
            self.canvas.create_line(x_tick - 5, pixel_y, x_tick + 5, pixel_y, fill=self.axes_color, tags="axes")
            label = "O" if y_val == 0 else str(y_val)
            self.canvas.create_text(x_tick - 15, pixel_y, text=label, fill=self.axes_color, font=("Arial", 8), tags="axes")

    def map_x(self, x):
        """
        Maps a graph x-coordinate to a canvas x-coordinate.
        """
        width = self.canvas.winfo_width()
        x_min, x_max = self.x_range
        return (x - x_min) / (x_max - x_min) * width

    def map_y(self, y):
        """
        Maps a graph y-coordinate to a canvas y-coordinate.
        """
        height = self.canvas.winfo_height()
        y_min, y_max = self.y_range
        # Invert the y-coordinate because canvas y increases downward.
        return height - (y - y_min) / (y_max - y_min) * height

    def plot_function(self, func, num_points=500):
        """
        Plots a function defined by a callable over the current x_range.
        
        :param func: A callable that takes an x value and returns a y value.
        :param num_points: Number of sample points for plotting.
        """
        self.canvas.delete("function")
        width = self.canvas.winfo_width()
        if width <= 0:
            return  # Canvas is not ready.

        x_min, x_max = self.x_range
        dx = (x_max - x_min) / num_points
        points = []
        for i in range(num_points + 1):
            x_val = x_min + i * dx
            try:
                y_val = func(x_val)
            except Exception:
                y_val = None

            if y_val is None or not isinstance(y_val, (int, float)):
                continue

            canvas_x = self.map_x(x_val)
            canvas_y = self.map_y(y_val)
            points.append((canvas_x, canvas_y))

        # Draw lines connecting the points.
        if points:
            for i in range(1, len(points)):
                x1, y1 = points[i - 1]
                x2, y2 = points[i]
                if any(not math.isfinite(v) for v in (x1, y1, x2, y2)):
                    continue
                self.canvas.create_line(x1, y1, x2, y2, fill=self.function_color, tags="function")

    def set_coordinate_system(self, x_range, y_range):
        """
        Updates the coordinate system ranges.
        
        :param x_range: New (x_min, x_max) tuple.
        :param y_range: New (y_min, y_max) tuple.
        """
        self.x_range = x_range
        self.y_range = y_range