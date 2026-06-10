import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import LegalGate from './LegalGate.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <LegalGate
      appName="POLINT"
      description="POLINT mappa le reti di influenza politica e mediatica italiane a partire da fonti pubbliche: chi è connesso a chi, attraverso quali narrazioni e con quale forza. Trasforma dati dispersi in grafi leggibili — uno strumento per leggere il potere, non per accusarlo."
    >
      <App />
    </LegalGate>
  </React.StrictMode>
)
