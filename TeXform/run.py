"""
Launcher for the TeXForm API. Sets TRANSFORMERS_NO_TF=1 before any other
imports so transformers uses only PyTorch and never loads TensorFlow,
avoiding the "Unable to convert function return value to a Python type!
The signature was () -> handle" error from TensorFlow/ml_dtypes.
"""
import os

os.environ["TRANSFORMERS_NO_TF"] = "1"

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
