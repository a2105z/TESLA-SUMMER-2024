"""
Flask backend for the Pathfinding Visualizer.
Defines the `/api/solve` endpoint, dispatches to the selected algorithm,
and returns the exploration order and final path for animation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import all algorithms
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from algorithms.bidirectional import bidirectional_search
from algorithms.greedy_best_first import greedy_best_first
from algorithms.jump_point_search import jump_point_search
from algorithms.recursive_best_first import recursive_best_first


# Initialize Flask app and enable CORS for local development
app = Flask(__name__)
CORS(app)

# Mapping of algorithm keys to functions
ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "dijkstra": dijkstra,
    "astar": astar,
    "bidirectional": bidirectional_search,
    "gbfs": greedy_best_first,
    "jps": jump_point_search,
    "rbfs": recursive_best_first,
}

@app.route("/api/solve", methods=["POST"])
def solve():
    """
    Expects a JSON payload:
    {
        "grid": List[List[int]],  # 0 = empty, 1 = wall
        "start": [row, col],
        "end": [row, col],
        "algorithm": str        # one of: bfs, dfs, dijkstra, astar, bidirectional
    }

    Returns:
    {
        "visited": [[r, c], ...],  # order of node visits
        "path": [[r, c], ...]      # final reconstructed path
    }
    """
    try:
        data = request.get_json(force=True)
        grid = data["grid"]
        start = tuple(data["start"])
        end = tuple(data["end"])
        algo_name = data.get("algorithm", "astar").lower()

        algo_fn = ALGORITHMS.get(algo_name)
        if algo_fn is None:
            return jsonify({"error": f"Unknown algorithm '{algo_name}'"}), 400

        # Run the algorithm
        visited_order, shortest_path = algo_fn(grid, start, end)

        return jsonify({
            "visited": visited_order,
            "path": shortest_path
        })

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400
    except Exception as e:
        app.logger.exception("Error during pathfinding")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Development server (hot reload, debug mode)
    app.run(host="127.0.0.1", port=5000, debug=True)
