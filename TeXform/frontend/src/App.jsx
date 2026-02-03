import { useState, useCallback } from 'react'
import './App.css'

const API_BASE = '/api'
const ALLOWED_TYPES = ['.pdf', '.png', '.jpg', '.jpeg']
const MAX_SIZE_MB = 50
const REQUEST_TIMEOUT_MS = 180000 // 3 min for OCR

export default function App() {
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const reset = useCallback(() => {
    setFile(null)
    setError(null)
    setResult(null)
  }, [])

  const handleFile = useCallback((f) => {
    if (!f) return
    const ext = '.' + (f.name.split('.').pop() || '').toLowerCase()
    if (!ALLOWED_TYPES.includes(ext)) {
      setError(`Unsupported type. Allowed: ${ALLOWED_TYPES.join(', ')}`)
      return
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File too large. Maximum: ${MAX_SIZE_MB} MB`)
      return
    }
    setError(null)
    setResult(null)
    setFile(f)
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer?.files?.[0]
    handleFile(f)
  }, [handleFile])

  const onDragOver = useCallback((e) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const onDragLeave = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const onInputChange = useCallback((e) => {
    const f = e.target?.files?.[0]
    handleFile(f)
  }, [handleFile])

  const process = useCallback(async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    const formData = new FormData()
    formData.append('file', file)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
    try {
      const res = await fetch(`${API_BASE}/process`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(data.detail || res.statusText || 'Processing failed')
        return
      }
      setResult({ latex: data.latex || '', pdfBase64: data.pdf_base64 ?? null })
    } catch (err) {
      clearTimeout(timeoutId)
      if (err.name === 'AbortError') {
        setError('Request timed out. Try a smaller file or fewer pages.')
      } else {
        setError(err.message || 'Network or server error')
      }
    } finally {
      setLoading(false)
    }
  }, [file])

  const downloadTex = useCallback(() => {
    if (!result?.latex) return
    const blob = new Blob([result.latex], { type: 'text/x-tex' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'texform_notes.tex'
    a.click()
    URL.revokeObjectURL(url)
  }, [result])

  const downloadPdf = useCallback(() => {
    if (!result?.pdfBase64) return
    const bin = atob(result.pdfBase64)
    const arr = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i)
    const blob = new Blob([arr], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'texform_notes.pdf'
    a.click()
    URL.revokeObjectURL(url)
  }, [result])

  return (
    <div className="app">
      <header className="header">
        <h1>TeXForm</h1>
        <p className="tagline">Handwritten notes → LaTeX</p>
      </header>

      <main className="main">
        <section className="intro">
          <p>
            Upload a <strong>PDF</strong> or <strong>image</strong> (PNG, JPG) of handwritten notes.
            TeXForm runs handwriting OCR (TrOCR), detects math (MathPix or Pix2Text), and assembles a LaTeX document.
          </p>
        </section>

        {!result ? (
          <>
            <div
              className={`upload-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
            >
              <input
                type="file"
                id="file-input"
                accept={ALLOWED_TYPES.join(',')}
                onChange={onInputChange}
                className="file-input"
              />
              <label htmlFor="file-input" className="upload-label">
                {file ? (
                  <span className="file-name">{file.name}</span>
                ) : (
                  <>
                    <span className="upload-icon">📂</span>
                    <span>Drop a file here or click to choose</span>
                  </>
                )}
              </label>
            </div>

            {error && (
              <div className="message error" role="alert">
                {error}
              </div>
            )}

            <div className="actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={process}
                disabled={!file || loading}
              >
                {loading ? 'Processing…' : 'Convert to LaTeX'}
              </button>
              {file && !loading && (
                <button type="button" className="btn btn-secondary" onClick={reset}>
                  Clear
                </button>
              )}
            </div>

            {loading && (
              <p className="loading-note">
                This can take 30–120 seconds for multi-page PDFs. Please wait.
              </p>
            )}
          </>
        ) : (
          <section className="result">
            <h2>Generated LaTeX</h2>
            <div className="latex-preview">
              <pre><code>{result.latex}</code></pre>
            </div>
            <div className="downloads">
              <button type="button" className="btn btn-primary" onClick={downloadTex}>
                Download .tex
              </button>
              {result.pdfBase64 ? (
                <button type="button" className="btn btn-primary" onClick={downloadPdf}>
                  Download PDF
                </button>
              ) : (
                <span className="no-pdf">PDF not available (LaTeX not installed on server)</span>
              )}
              <button type="button" className="btn btn-secondary" onClick={reset}>
                Convert another
              </button>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>TeXForm — Handwriting OCR (TrOCR) + math recognition (MathPix / Pix2Text)</p>
      </footer>
    </div>
  )
}
