import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import LegalGate from './LegalGate.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <LegalGate appName="POLINT">
      <App />
    </LegalGate>
  </React.StrictMode>
)
