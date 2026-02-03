# TeXForm: Handwritten Notes → LaTeX
# Multi-stage: build React frontend, then run FastAPI backend
FROM node:20-slim AS frontend-builder

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --legacy-peer-deps || npm install

COPY frontend/ .
RUN npm run build

# Python + LaTeX runtime
FROM python:3.11-slim

# System deps: LaTeX (pdflatex) for PDF download
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY backend/ backend/
COPY config/ config/
COPY --from=frontend-builder /build/dist frontend/dist

EXPOSE 8000

# Prevent transformers from loading TensorFlow (avoids ml_dtypes "handle" error)
ENV TRANSFORMERS_NO_TF=1

# Run FastAPI with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
