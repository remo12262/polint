import anthropic
import json
import os
from typing import Dict, List
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Sei un sistema di intelligence politica avanzato specializzato in:
1. Identificazione di reti di influenza NASCOSTE (non dichiarate)
2. Analisi predittiva di decisioni politiche future
3. Tracciamento flussi di finanziamento e lobbying

Tipi di entità:
- PolicyMaker: ministri, parlamentari, commissari EU, capi di governo
- PoliticalParty: partiti, movimenti, coalizioni
- LobbyGroup: gruppi lobbying, associazioni di categoria, think tank
- MediaOutlet: giornali, TV, piattaforme, influencer politici
- Corporation: aziende con interessi politici (energia, difesa, pharma, tech, finanza)
- Foundation: fondazioni, ONG, centri di ricerca con agenda politica
- GovernmentAgency: agenzie, ministeri, istituzioni EU
- Person: individui chiave (CEO, donatori, consulenti)
- InvestorInstitution: fondi, banche, investitori con influenza politica

Tipi di relazione (focus su INFLUENZA NASCOSTA):
- FINANZIA_OCCULTO: finanziamento non trasparente o indiretto
- CONTROLLA_MEDIA: controllo editoriale di media
- LOBBYING_SU: attività lobbying verso decisore
- REVOLVING_DOOR: ex politico ora in azienda o viceversa
- RETE_INFORMALE: connessione informale non documentata
- FINANZIA: finanziamento diretto dichiarato
- MEMBRO_DI: membership in organizzazioni
- ALLEATO_DI: alleanza politica
- OPPOSTO_A: opposizione politica
- NOMINA: ha nominato / è stato nominato da
- CITA_POSITIVO: media cita positivamente
- CITA_NEGATIVO: media cita negativamente

Per ogni relazione calcola:
- influence_score (0-100): quanto questa relazione impatta sulle decisioni politiche
- hidden_score (0-100): quanto questa relazione è nascosta/non trasparente
- ALTA hidden_score se: finanziamento indiretto, revolving door, media control, connessioni non dichiarate"""

EXTRACT_PROMPT = """Analizza questo testo politico ed estrai entità e relazioni di influenza.
Focalizzati su connessioni NON OVVIE e reti di influenza nascoste.

Testo:
{text}

Rispondi SOLO con JSON:
{{
  "entities": [
    {{
      "id": "slug_univoco",
      "label": "Nome",
      "type": "TipoEntità",
      "country": "IT/EU/US/etc",
      "description": "ruolo e contesto",
      "influence_score": 0-100,
      "hidden_score": 0-100
    }}
  ],
  "relations": [
    {{
      "source": "id1",
      "target": "id2",
      "type": "TIPO_RELAZIONE",
      "fact": "descrizione concisa",
      "influence_score": 0-100,
      "hidden_score": 0-100,
      "date": "YYYY-MM o null"
    }}
  ]
}}"""

PREDICT_PROMPT = """Sei un analista politico di intelligence di alto livello.
Analizza questo knowledge graph di influenze politiche e genera previsioni concrete.

Graph data:
{graph_data}

Genera 4-6 previsioni predittive strutturate così:
[
  {{
    "id": "pred_slug",
    "title": "Titolo previsione concreta",
    "prediction": "Descrizione dettagliata di cosa accadrà",
    "actors_involved": ["id1", "id2"],
    "hidden_network": "Descrizione della rete nascosta che guida questo evento",
    "confidence": 0-100,
    "timeframe": "es. 2-4 mesi",
    "evidence": "Evidenze nel grafo che supportano questa previsione",
    "trigger_event": "Evento scatenante atteso",
    "impact_score": 0-100,
    "category": "POLICY|ELECTION|APPOINTMENT|REGULATION|ALLIANCE|FINANCIAL",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW"
  }}
]

Focus su:
- Nomine imminenti guidate da reti informali
- Cambi di posizione su normative EU (AI Act, energia, difesa)
- Alleanze e rotture di coalizioni
- Movimenti di finanziamento che anticipano decisioni politiche
- Pattern di media coverage che preannunciano mosse politiche

Rispondi SOLO con JSON valido."""

HIDDEN_NETWORKS_PROMPT = """Analizza questo grafo di influenze e identifica cluster di influenza nascosta.

Entità: {entities}
Relazioni: {relations}

Identifica 3-5 reti di influenza nascoste:
[
  {{
    "id": "network_slug",
    "name": "Nome rete",
    "description": "Come opera questa rete di influenza",
    "core_actors": ["id1", "id2"],
    "mechanism": "Come esercita influenza (es. media control, finanziamenti, revolving door)",
    "opacity_score": 0-100,
    "reach_score": 0-100,
    "policy_areas": ["es. energia", "difesa", "AI regulation"]
  }}
]

Rispondi SOLO con JSON valido."""


class InfluenceExtractor:

    def _slug(self, text: str) -> str:
        import re
        return re.sub(r'[^a-z0-9_]', '', text.lower().replace(' ', '_'))[:32]

    async def extract(self, text: str, source_id: str = "") -> Dict:
        if not text or len(text.strip()) < 50:
            return {"entities": [], "relations": []}
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": EXTRACT_PROMPT.format(text=text[:3000])}]
            )
            raw = next((b.text for b in msg.content if hasattr(b, "text")), "").strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
            result = json.loads(raw)
            for e in result.get("entities", []):
                if not e.get("id"):
                    e["id"] = self._slug(e.get("label", "unknown"))
            for r in result.get("relations", []):
                r["source_doc"] = source_id
            return result
        except Exception as e:
            print(f"[extractor] extract error: {e}")
            return {"entities": [], "relations": []}

    async def extract_batch(self, items: List[Dict], text_field: str = "summary") -> Dict:
        import asyncio
        all_entities: Dict[str, Dict] = {}
        all_relations: List[Dict] = []
        tasks = [
            self.extract(
                item.get(text_field, "") + " " + item.get("title", ""),
                source_id=item.get("id", "")
            )
            for item in items[:12]
        ]
        results = await asyncio.gather(*tasks)
        for result in results:
            for entity in result.get("entities", []):
                eid = entity["id"]
                if eid not in all_entities:
                    all_entities[eid] = entity
                else:
                    existing = all_entities[eid]
                    existing["influence_score"] = max(
                        existing.get("influence_score", 0),
                        entity.get("influence_score", 0)
                    )
                    existing["hidden_score"] = max(
                        existing.get("hidden_score", 0),
                        entity.get("hidden_score", 0)
                    )
            all_relations.extend(result.get("relations", []))
        return {"entities": list(all_entities.values()), "relations": all_relations}

    async def generate_predictions(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Generate political predictions from the influence graph."""
        if not nodes:
            return []
        # Focus on high-influence and high-hidden-score nodes
        key_nodes = sorted(nodes, key=lambda n: n.get("influence_score", 0) + n.get("hidden_score", 0), reverse=True)[:15]
        key_edges = sorted(edges, key=lambda e: e.get("hidden_score", 0), reverse=True)[:20]
        graph_data = json.dumps({
            "key_actors": key_nodes,
            "hidden_relations": key_edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }, indent=2, ensure_ascii=False)
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2500,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": PREDICT_PROMPT.format(graph_data=graph_data)}]
            )
            raw = next((b.text for b in msg.content if hasattr(b, "text")), "").strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
            return json.loads(raw)
        except Exception as e:
            print(f"[extractor] prediction error: {e}")
            return []

    async def detect_hidden_networks(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Detect hidden influence clusters in the graph."""
        if not nodes:
            return []
        # Only high hidden_score items
        hidden_nodes = [n for n in nodes if n.get("hidden_score", 0) > 40][:20]
        hidden_edges = [e for e in edges if e.get("hidden_score", 0) > 40][:25]
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": HIDDEN_NETWORKS_PROMPT.format(
                    entities=json.dumps(hidden_nodes, ensure_ascii=False),
                    relations=json.dumps(hidden_edges, ensure_ascii=False)
                )}]
            )
            raw = next((b.text for b in msg.content if hasattr(b, "text")), "").strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
            return json.loads(raw)
        except Exception as e:
            print(f"[extractor] hidden networks error: {e}")
            return []

    async def generate_alerts(self, predictions: List[Dict]) -> List[Dict]:
        """Convert high-confidence predictions into alerts."""
        alerts = []
        for p in predictions:
            if p.get("confidence", 0) >= 60:
                alerts.append({
                    "id": f"alert_{p.get('id', '')}",
                    "title": p.get("title", ""),
                    "description": p.get("prediction", ""),
                    "severity": p.get("severity", "MEDIUM"),
                    "entities_involved": json.dumps(p.get("actors_involved", [])),
                    "predicted_impact": p.get("evidence", ""),
                    "timeframe": p.get("timeframe", ""),
                    "recommendation": f"Categoria: {p.get('category','')} · Confidence: {p.get('confidence',0)}%",
                    "hidden_network": p.get("hidden_network", ""),
                    "confidence": p.get("confidence", 0),
                })
        return alerts
