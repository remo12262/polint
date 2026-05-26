import json
from typing import List, Dict, Optional
from datetime import datetime


class PolintDB:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: Dict[str, Dict] = {}
        self.predictions: Dict[str, Dict] = {}
        self.alerts: Dict[str, Dict] = {}
        self.hidden_networks: Dict[str, Dict] = {}

    async def init(self):
        if not self.nodes:
            self._seed_baseline()

    def _seed_baseline(self):
        now = datetime.utcnow().isoformat()
        nodes = [
            ("meloni_g",     "Giorgia Meloni",               "PolicyMaker",         "political", "IT", "Presidente del Consiglio italiano. Leader FdI. Asse con PPE EU.", 92, 20),
            ("schlein_e",    "Elly Schlein",                 "PolicyMaker",         "political", "IT", "Segretaria PD. Opposizione centrosinistra. Rete EU progressisti.", 75, 15),
            ("salvini_m",    "Matteo Salvini",               "PolicyMaker",         "political", "IT", "Vice Presidente Consiglio. Leader Lega. Asse con ID europei.", 80, 25),
            ("tajani_a",     "Antonio Tajani",               "PolicyMaker",         "political", "IT", "Ministro Esteri. Leader FI. Legami storici PPE e lobby Berlusconi.", 78, 35),
            ("fdi_it",       "Fratelli d'Italia",            "PoliticalParty",      "political", "IT", "Partito di governo. Membro ECR europeo.", 85, 20),
            ("mediaset",     "Mediaset / MFE",               "MediaOutlet",         "political", "IT", "Gruppo media Berlusconi. Influenza agenda politica italiana.", 80, 65),
            ("rai",          "RAI",                          "MediaOutlet",         "political", "IT", "Radiotelevisione pubblica italiana. Nomine politiche CdA.", 70, 55),
            ("confindustria","Confindustria",                "LobbyGroup",          "political", "IT", "Principale associazione industriale italiana. Lobbying su lavoro e fisco.", 75, 40),
            ("cdp_it",       "CDP",                          "InvestorInstitution", "political", "IT", "Cassa Depositi e Prestiti. Braccio finanziario Stato italiano.", 70, 50),
            ("vdl_u",        "Ursula von der Leyen",         "PolicyMaker",         "political", "EU", "Presidente Commissione Europea. Rete PPE e lobby farmaceutica.", 95, 30),
            ("ppe_eu",       "PPE",                          "PoliticalParty",      "political", "EU", "Partito Popolare Europeo. Principale forza al Parlamento EU.", 88, 25),
            ("accenture_eu", "Accenture EU",                 "Corporation",         "political", "EU", "Principale consulente Commissione EU. Influenza normative digitali.", 65, 70),
            ("blackrock",    "BlackRock",                    "InvestorInstitution", "political", "EU", "Maggiore asset manager mondiale. Influenza su policy finanziarie EU.", 85, 75),
            ("politico_eu",  "Politico EU",                  "MediaOutlet",         "political", "EU", "Media politico EU. Proprietà Axel Springer (Germany). Agenda-setting.", 72, 45),
            ("bruegel",      "Bruegel Think Tank",           "Foundation",          "political", "EU", "Think tank economico EU. Influenza politiche BCE e Commissione.", 68, 55),
            ("lobby_pharma", "PharmEU Lobby",                "LobbyGroup",          "political", "EU", "Coalizione lobbying farmaceutico EU. Influenza su sanità e AI medica.", 72, 68),
            ("soros_osf",    "Open Society Foundations",     "Foundation",          "political", "US", "Fondazione Soros. Finanziamento ONG e media progressisti EU.", 78, 62),
            ("wef",          "World Economic Forum",         "Foundation",          "political", "CH", "Forum di Davos. Rete informale leader globali. Agenda digitale e green.", 82, 58),
            ("nato_hq",      "NATO",                         "GovernmentAgency",    "political", "BE", "Alleanza atlantica. Influenza su budget difesa e politica estera IT.", 88, 20),
            ("xi_jinping",   "Xi Jinping / CCP",             "PolicyMaker",         "political", "CN", "Leadership cinese. Influenza via investimenti, Huawei, Via della Seta.", 90, 72),
            ("kremlin",      "Cremlino / Putin",             "PolicyMaker",         "political", "RU", "Influenza su partiti sovranisti EU tramite canali informali e media.", 85, 85),
            ("gates_f",      "Bill & Melinda Gates Foundation","Foundation",        "political", "US", "Finanziamento sanità globale. Influenza su WHO e politiche vaccinali.", 75, 48),
        ]
        edges = [
            ("e01", "mediaset",     "meloni_g",    "CITA_POSITIVO",    "Mediaset storicamente favorevole al centrodestra. Copertura positiva.", 70, 55, "2022-10"),
            ("e02", "mediaset",     "tajani_a",    "CITA_POSITIVO",    "Tajani legato all'eredità Berlusconi. Mediaset supporta FI.", 75, 60, "2023-01"),
            ("e03", "rai",          "meloni_g",    "NOMINA",           "Governo Meloni nomina vertici RAI. Influenza editoriale.", 80, 70, "2023-05"),
            ("e04", "confindustria","meloni_g",    "LOBBYING_SU",      "Confindustria principale interlocutore governo su lavoro e fisco.", 72, 45, "2023-01"),
            ("e05", "blackrock",    "vdl_u",       "FINANZIA_OCCULTO", "BlackRock consulente Commissione EU su politiche ESG e green.", 85, 80, "2021-04"),
            ("e06", "accenture_eu", "vdl_u",       "LOBBYING_SU",      "Accenture gestisce contratti digitali EU per miliardi. Accesso privilegiato.", 78, 75, "2020-01"),
            ("e07", "ppe_eu",       "vdl_u",       "ALLEATO_DI",       "Von der Leyen espressione PPE. Dipende da supporto PPE.", 90, 10, "2019-07"),
            ("e08", "kremlin",      "salvini_m",   "RETE_INFORMALE",   "Legami storici Lega-Russia. Accordo Metropol 2019 mai pienamente chiarito.", 82, 90, "2019-07"),
            ("e09", "kremlin",      "fdi_it",      "RETE_INFORMALE",   "Relazioni ECR con partiti filorussi EU. Pattern di voto allineato.", 60, 78, "2022-03"),
            ("e10", "soros_osf",    "schlein_e",   "FINANZIA",         "OSF finanzia reti progressiste EU vicine PD su migrazione e diritti.", 65, 55, "2021-01"),
            ("e11", "wef",          "vdl_u",       "RETE_INFORMALE",   "Von der Leyen partecipa Davos. Allineamento su agenda digitale WEF.", 70, 52, "2020-01"),
            ("e12", "wef",          "meloni_g",    "OPPOSTO_A",        "Meloni critica agenda WEF. Posizionamento sovranista.", 60, 20, "2023-01"),
            ("e13", "xi_jinping",   "cdp_it",      "RETE_INFORMALE",   "CDP partecipa a progetti Via della Seta. Interessi infrastrutturali cinesi.", 75, 72, "2019-03"),
            ("e14", "lobby_pharma", "vdl_u",       "LOBBYING_SU",      "Lobby farmaceutica influenza gestione contratti vaccini COVID EU.", 88, 82, "2020-12"),
            ("e15", "bruegel",      "ppe_eu",      "RETE_INFORMALE",   "Think tank Bruegel orienta posizioni PPE su politiche economiche EU.", 65, 58, "2022-01"),
            ("e16", "blackrock",    "cdp_it",      "INVESTE_IN",       "BlackRock partecipa a fondi infrastrutturali italiani via CDP.", 72, 68, "2021-06"),
            ("e17", "gates_f",      "lobby_pharma","ALLEATO_DI",       "Gates Foundation allineata con Big Pharma su accesso vaccini.", 68, 55, "2020-04"),
            ("e18", "nato_hq",      "meloni_g",    "ALLEATO_DI",       "Governo Meloni atlantista. Supporto NATO e invii Ucraina.", 82, 15, "2022-02"),
            ("e19", "politico_eu",  "vdl_u",       "CITA_POSITIVO",    "Politico EU agenda-setting favorevole a VdL su AI Act e Green Deal.", 65, 48, "2023-01"),
            ("e20", "tajani_a",     "ppe_eu",      "MEMBRO_DI",        "Tajani membro storico PPE. Vice-presidente PPE per anni.", 80, 10, "2010-01"),
        ]
        for n in nodes:
            self.nodes[n[0]] = {
                "id": n[0], "label": n[1], "type": n[2], "domain": n[3],
                "country": n[4], "description": n[5],
                "influence_score": n[6], "hidden_score": n[7],
                "created_at": now, "updated_at": now,
            }
        for e in edges:
            self.edges[e[0]] = {
                "id": e[0], "source": e[1], "target": e[2], "type": e[3],
                "fact": e[4], "influence_score": e[5], "hidden_score": e[6],
                "source_doc": "", "date": e[7], "created_at": now,
            }

    async def get_nodes(self, domain=None) -> List[Dict]:
        nodes = list(self.nodes.values())
        return sorted(nodes, key=lambda n: n.get("influence_score", 0), reverse=True)

    async def get_edges(self, domain=None) -> List[Dict]:
        edges = list(self.edges.values())
        return sorted(edges, key=lambda e: e.get("hidden_score", 0), reverse=True)

    async def get_node(self, node_id: str) -> Optional[Dict]:
        return self.nodes.get(node_id)

    async def get_node_relations(self, node_id: str) -> List[Dict]:
        results = []
        for e in self.edges.values():
            if e["source"] == node_id or e["target"] == node_id:
                src = self.nodes.get(e["source"], {})
                tgt = self.nodes.get(e["target"], {})
                results.append({
                    **e,
                    "source_label": src.get("label", ""),
                    "source_type":  src.get("type", ""),
                    "target_label": tgt.get("label", ""),
                    "target_type":  tgt.get("type", ""),
                })
        return sorted(results, key=lambda e: e.get("hidden_score", 0), reverse=True)

    async def get_influence_path(self, node_id: str) -> List[Dict]:
        neighbour_ids = set()
        for e in self.edges.values():
            if e["source"] == node_id:
                neighbour_ids.add(e["target"])
            elif e["target"] == node_id:
                neighbour_ids.add(e["source"])
        neighbours = [self.nodes[nid] for nid in neighbour_ids if nid in self.nodes]
        return sorted(neighbours, key=lambda n: n.get("influence_score", 0), reverse=True)[:10]

    async def get_predictions(self) -> List[Dict]:
        preds = sorted(
            self.predictions.values(),
            key=lambda p: (p.get("confidence", 0), p.get("created_at", "")),
            reverse=True,
        )
        return preds[:30]

    async def get_hidden_networks(self) -> List[Dict]:
        return sorted(
            self.hidden_networks.values(),
            key=lambda h: h.get("opacity_score", 0),
            reverse=True,
        )

    async def get_alerts(self, severity=None) -> List[Dict]:
        alerts = list(self.alerts.values())
        if severity:
            alerts = [a for a in alerts if a.get("severity") == severity]
        return sorted(
            alerts,
            key=lambda a: (a.get("confidence", 0), a.get("created_at", "")),
            reverse=True,
        )[:50]

    async def get_influence_ranking(self) -> List[Dict]:
        nodes = sorted(
            self.nodes.values(),
            key=lambda n: (n.get("influence_score", 0) + n.get("hidden_score", 0)) / 2,
            reverse=True,
        )[:20]
        return [
            {
                "id": n["id"], "label": n["label"], "type": n["type"],
                "country": n.get("country"),
                "influence_score": n.get("influence_score", 0),
                "hidden_score": n.get("hidden_score", 0),
                "combined_score": (n.get("influence_score", 0) + n.get("hidden_score", 0)) // 2,
            }
            for n in nodes
        ]

    async def search_nodes(self, q: str) -> List[Dict]:
        q_lower = q.lower()
        matches = [
            n for n in self.nodes.values()
            if q_lower in n.get("label", "").lower()
            or q_lower in n.get("description", "").lower()
        ]
        return sorted(matches, key=lambda n: n.get("influence_score", 0), reverse=True)[:20]

    async def get_stats(self) -> Dict:
        unread = sum(1 for a in self.alerts.values() if not a.get("is_read"))
        hi_opacity = sum(1 for n in self.nodes.values() if n.get("hidden_score", 0) > 60)
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "predictions": len(self.predictions),
            "unread_alerts": unread,
            "hidden_networks": len(self.hidden_networks),
            "high_opacity_actors": hi_opacity,
        }

    async def upsert_entities(self, entities: List[Dict]):
        now = datetime.utcnow().isoformat()
        for e in entities:
            eid = e.get("id")
            if not eid:
                continue
            if eid in self.nodes:
                self.nodes[eid]["influence_score"] = max(
                    self.nodes[eid].get("influence_score", 0), e.get("influence_score", 0)
                )
                self.nodes[eid]["hidden_score"] = max(
                    self.nodes[eid].get("hidden_score", 0), e.get("hidden_score", 0)
                )
                self.nodes[eid]["updated_at"] = now
            else:
                self.nodes[eid] = {
                    "id": eid, "label": e.get("label", ""),
                    "type": e.get("type", "Organization"), "domain": "political",
                    "country": e.get("country"), "description": e.get("description", ""),
                    "influence_score": e.get("influence_score", 0),
                    "hidden_score": e.get("hidden_score", 0),
                    "created_at": now, "updated_at": now,
                }

    async def upsert_relations(self, relations: List[Dict]):
        now = datetime.utcnow().isoformat()
        for r in relations:
            rid = f"{r.get('source')}_{r.get('target')}_{r.get('type')}"
            if rid in self.edges:
                self.edges[rid]["hidden_score"] = max(
                    self.edges[rid].get("hidden_score", 0), r.get("hidden_score", 0)
                )
            else:
                self.edges[rid] = {
                    "id": rid, "source": r.get("source"), "target": r.get("target"),
                    "type": r.get("type", "COLLEGATO_A"), "fact": r.get("fact"),
                    "influence_score": r.get("influence_score", 0),
                    "hidden_score": r.get("hidden_score", 0),
                    "source_doc": r.get("source_doc", ""), "date": r.get("date"),
                    "created_at": now,
                }

    async def upsert_predictions(self, predictions: List[Dict]):
        now = datetime.utcnow().isoformat()
        for p in predictions:
            pid = p.get("id", f"pred_{now}")
            self.predictions[pid] = {
                "id": pid, "title": p.get("title"), "prediction": p.get("prediction"),
                "actors_involved": json.dumps(p.get("actors_involved", [])),
                "hidden_network": p.get("hidden_network", ""),
                "confidence": p.get("confidence", 0), "timeframe": p.get("timeframe", ""),
                "evidence": p.get("evidence", ""), "trigger_event": p.get("trigger_event", ""),
                "impact_score": p.get("impact_score", 0),
                "category": p.get("category", "POLICY"), "severity": p.get("severity", "MEDIUM"),
                "created_at": now, "is_verified": 0,
            }

    async def upsert_hidden_networks(self, networks: List[Dict]):
        now = datetime.utcnow().isoformat()
        for hn in networks:
            hid = hn.get("id")
            if not hid:
                continue
            self.hidden_networks[hid] = {
                "id": hid, "name": hn.get("name"), "description": hn.get("description"),
                "core_actors": json.dumps(hn.get("core_actors", [])),
                "mechanism": hn.get("mechanism", ""),
                "opacity_score": hn.get("opacity_score", 0),
                "reach_score": hn.get("reach_score", 0),
                "policy_areas": json.dumps(hn.get("policy_areas", [])),
                "created_at": now,
            }

    async def upsert_alerts(self, alerts: List[Dict]):
        now = datetime.utcnow().isoformat()
        for a in alerts:
            aid = a.get("id", f"alert_{now}")
            self.alerts[aid] = {
                "id": aid, "title": a.get("title"), "description": a.get("description"),
                "severity": a.get("severity", "MEDIUM"),
                "entities_involved": a.get("entities_involved", "[]"),
                "predicted_impact": a.get("predicted_impact"),
                "timeframe": a.get("timeframe"), "recommendation": a.get("recommendation"),
                "hidden_network": a.get("hidden_network", ""),
                "confidence": a.get("confidence", 0),
                "created_at": now, "is_read": False,
            }
