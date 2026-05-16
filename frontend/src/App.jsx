import React, {useState} from 'react'

export default function App(){
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  async function onSubmit(e){
    e.preventDefault()
    setError(null)
    setResult(null)
    if(!file){
      setError('Please choose a JSON report to upload.')
      return
    }
    setLoading(true)
    try{
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch('http://127.0.0.1:8000/analyze/upload', { method: 'POST', body: fd })
      if(!res.ok){
        const body = await res.json().catch(()=>({detail: 'Invalid response'}))
        throw new Error(body.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
    }catch(err){
      setError(err.message)
    }finally{
      setLoading(false)
    }
  }

  function severityCount(sev){
    if(!result || !result.summary_by_severity) return 0
    return result.summary_by_severity[sev] || 0
  }

  return (
    <div className="container">
      <header>
        <h1>AI Cloud Security Remediation Copilot</h1>
        <p className="subtitle">Upload a Checkov JSON report to get a quick remediation summary.</p>
      </header>

      <main>
        <form onSubmit={onSubmit} className="upload-form">
          <input type="file" accept="application/json" onChange={e=>setFile(e.target.files[0])} />
          <div className="actions">
            <button type="submit" disabled={loading}>Analyze</button>
          </div>
        </form>

        {loading && <div className="status">Loading…</div>}
        {error && <div className="error">Error: {error}</div>}

        {result && (
          <section className="results">
            <h2>Summary</h2>
            <div className="summary">
              <div className="tile critical">CRITICAL: {severityCount('CRITICAL')}</div>
              <div className="tile high">HIGH: {severityCount('HIGH')}</div>
              <div className="tile medium">MEDIUM: {severityCount('MEDIUM')}</div>
              <div className="tile low">LOW: {severityCount('LOW')}</div>
            </div>

            <h3>Findings ({result.total_findings})</h3>
            <ul className="findings">
              {result.findings.map((f, idx)=> (
                <li key={idx} className={`finding ${f.severity.toLowerCase()}`}>
                  <div className="left">
                    <div className="name">{f.check_name} <span className="id">{f.check_id}</span></div>
                    <div className="meta">{f.file_path} — {f.severity}</div>
                    <div className="message">{f.message}</div>
                  </div>
                  <div className="right">
                    <strong>Remediation</strong>
                    <p>{f.remediation}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>

      <footer>
        <small>Simple MVP — great for a DevSecOps portfolio.</small>
      </footer>
    </div>
  )
}
