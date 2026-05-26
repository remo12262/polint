import asyncpg
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "")


class PolintDB:
    pool: asyncpg.Pool = None

    async def init(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS nodes (
                        id TEXT PRIMARY KEY,
                        label TEXT NOT NULL,
                        type TEXT NOT NULL,
                        domain TEXT DEFAULT 'political',
                        country TEXT,
                        description TEXT,
                        influence_score INTEGER DEFAULT 0,
                        hidden_score INTEGER DEFAULT 0,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS edges (
                        id TEXT PRIMARY KEY,
                        source TEXT NOT NULL,
                        target TEXT NOT NULL,
                        type TEXT NOT NULL,
                        fact TEXT,
                        influence_score INTEGER DEFAULT 0,
                        hidden_score INTEGER DEFAULT 0,
                        source_doc TEXT,
                        date TEXT,
                        created_at TEXT
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        prediction TEXT,
                        actors_involved TEXT,
                        hidden_network TEXT,
                        confidence INTEGER DEFAULT 0,
                        timeframe TEXT,
                        evidence TEXT,
                        trigger_event TEXT,
                        impact_score INTEGER DEFAULT 0,
                        category TEXT,
                        severity TEXT DEFAULT 'MEDIUM',
                        created_at TEXT,
                        is_verified INTEGER DEFAULT 0
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        severity TEXT DEFAULT 'MEDIUM',
                        entities_involved TEXT,
                        predicted_impact TEXT,
                        timeframe TEXT,
                        recommendation TEXT,
                        hidden_network TEXT,
                        confidence INTEGER DEFAULT 0,
                        created_at TEXT,
                        is_read INTEGER DEFAULT 0
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS hidden_networks (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        core_actors TEXT,
                        mechanism TEXT,
                        opacity_score INTEGER DEFAULT 0,
                        reach_score INTEGER DEFAULT 0,
                        policy_areas TEXT,
                        created_at TEXT
                    )
                """)
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_conf ON predictions(confidence)")

                count = await conn.fetchval("SELECT COUNT(*) FROM nodes")
                if count == 0:
                    await self._seed_baseline(conn)

    async def _seed_baseline(self, conn):
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
            ("e15", "bruegel",      "ppe_eu",       "RETE_INFORMALE",   "Think tank Bruegel orienta posizioni PPE su politiche economiche EU.", 65, 58, "2022-01"),
            ("e16", "blackrock",    "cdp_it",      "INVESTE_IN",       "BlackRock partecipa a fondi infrastrutturali italiani via CDP.", 72, 68, "2021-06"),
            ("e17", "gates_f",      "lobby_pharma","ALLEATO_DI",       "Gates Foundation allineata con Big Pharma su accesso vaccini.", 68, 55, "2020-04"),
            ("e18", "nato_hq",      "meloni_g",    "ALLEATO_DI",       "Governo Meloni atlantista. Supporto NATO e invii Ucraina.", 82, 15, "2022-02"),
            ("e19", "politico_eu",  "vdl_u",       "CITA_POSITIVO",    "Politico EU agenda-setting favorevole a VdL su AI Act e Green Deal.", 65, 48, "2023-01"),
            ("e20", "tajani_a",     "ppe_eu",       "MEMBRO_DI",        "Tajani membro storico PPE. Vice-presidente PPE per anni.", 80, 10, "2010-01"),
        ]
        await conn.executemany(
            """INSERT INTO nodes
                   (id,label,type,domain,country,description,influence_score,hidden_score,created_at,updated_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) ON CONFLICT DO NOTHING""",
            [(n[0], n[1], n[2], n[3], n[4], n[5], n[6], n[7], now, now) for n in nodes]
        )
        await conn.executemany(
            """INSERT INTO edges
                   (id,source,target,type,fact,influence_score,hidden_score,source_doc,date,created_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) ON CONFLICT DO NOTHING""",
            [(e[0], e[1], e[2], e[3], e[4], e[5], e[6], "", e[7], now) for e in edges]
        )

    async def get_nodes(self, domain=None) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM nodes ORDER BY influence_score DESC")
            return [dict(r) for r in rows]

    async def get_edges(self, domain=None) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM edges ORDER BY hidden_score DESC")
            return [dict(r) for r in rows]

    async def get_node(self, node_id: str) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM nodes WHERE id=$1", node_id)
            return dict(row) if row else None

    async def get_node_relations(self, node_id: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT e.*,
                    ns.label as source_label, ns.type as source_type,
                    nt.label as target_label, nt.type as target_type
                FROM edges e
                JOIN nodes ns ON e.source = ns.id
                JOIN nodes nt ON e.target = nt.id
                WHERE e.source=$1 OR e.target=$1
                ORDER BY e.hidden_score DESC
            """, node_id)
            return [dict(r) for r in rows]

    async def get_influence_path(self, node_id: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT DISTINCT n.id, n.label, n.type, n.influence_score, n.hidden_score
                FROM nodes n
                JOIN edges e ON (e.source = n.id OR e.target = n.id)
                WHERE (e.source=$1 OR e.target=$1) AND n.id != $1
                ORDER BY n.influence_score DESC LIMIT 10
            """, node_id)
            return [dict(r) for r in rows]

    async def get_predictions(self) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM predictions ORDER BY confidence DESC, created_at DESC LIMIT 30"
            )
            return [dict(r) for r in rows]

    async def get_hidden_networks(self) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM hidden_networks ORDER BY opacity_score DESC")
            return [dict(r) for r in rows]

    async def get_alerts(self, severity=None) -> List[Dict]:
        async with self.pool.acquire() as conn:
            if severity:
                rows = await conn.fetch(
                    "SELECT * FROM alerts WHERE severity=$1 ORDER BY confidence DESC, created_at DESC",
                    severity
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM alerts ORDER BY confidence DESC, created_at DESC LIMIT 50"
                )
            return [dict(r) for r in rows]

    async def get_influence_ranking(self) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, label, type, country, influence_score, hidden_score,
                    (influence_score + hidden_score) / 2 as combined_score
                FROM nodes ORDER BY combined_score DESC LIMIT 20
            """)
            return [dict(r) for r in rows]

    async def search_nodes(self, q: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM nodes WHERE label ILIKE $1 OR description ILIKE $1
                ORDER BY influence_score DESC LIMIT 20
            """, f"%{q}%")
            return [dict(r) for r in rows]

    async def get_stats(self) -> Dict:
        async with self.pool.acquire() as conn:
            n  = await conn.fetchval("SELECT COUNT(*) FROM nodes")
            e  = await conn.fetchval("SELECT COUNT(*) FROM edges")
            p  = await conn.fetchval("SELECT COUNT(*) FROM predictions")
            a  = await conn.fetchval("SELECT COUNT(*) FROM alerts WHERE is_read=0")
            hn = await conn.fetchval("SELECT COUNT(*) FROM hidden_networks")
            hi = await conn.fetchval("SELECT COUNT(*) FROM nodes WHERE hidden_score > 60")
            return {"nodes": n, "edges": e, "predictions": p, "unread_alerts": a,
                    "hidden_networks": hn, "high_opacity_actors": hi}

    async def upsert_entities(self, entities: List[Dict]):
        now = datetime.utcnow().isoformat()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for e in entities:
                    await conn.execute("""
                        INSERT INTO nodes
                            (id,label,type,domain,country,description,influence_score,hidden_score,created_at,updated_at)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                        ON CONFLICT(id) DO UPDATE SET
                            influence_score = GREATEST(nodes.influence_score, EXCLUDED.influence_score),
                            hidden_score    = GREATEST(nodes.hidden_score, EXCLUDED.hidden_score),
                            updated_at      = EXCLUDED.updated_at
                    """, e.get("id"), e.get("label"), e.get("type", "Organization"),
                         "political", e.get("country"), e.get("description"),
                         e.get("influence_score", 0), e.get("hidden_score", 0), now, now)

    async def upsert_relations(self, relations: List[Dict]):
        now = datetime.utcnow().isoformat()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for r in relations:
                    rid = f"{r.get('source')}_{r.get('target')}_{r.get('type')}"
                    await conn.execute("""
                        INSERT INTO edges
                            (id,source,target,type,fact,influence_score,hidden_score,source_doc,date,created_at)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                        ON CONFLICT(id) DO UPDATE SET
                            hidden_score = GREATEST(edges.hidden_score, EXCLUDED.hidden_score)
                    """, rid, r.get("source"), r.get("target"), r.get("type", "COLLEGATO_A"),
                         r.get("fact"), r.get("influence_score", 0), r.get("hidden_score", 0),
                         r.get("source_doc", ""), r.get("date"), now)

    async def upsert_predictions(self, predictions: List[Dict]):
        now = datetime.utcnow().isoformat()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for p in predictions:
                    await conn.execute("""
                        INSERT INTO predictions
                            (id,title,prediction,actors_involved,hidden_network,confidence,timeframe,
                             evidence,trigger_event,impact_score,category,severity,created_at)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                        ON CONFLICT(id) DO UPDATE SET
                            prediction = EXCLUDED.prediction,
                            confidence = EXCLUDED.confidence,
                            created_at = EXCLUDED.created_at
                    """, p.get("id", f"pred_{now}"), p.get("title"), p.get("prediction"),
                         json.dumps(p.get("actors_involved", [])), p.get("hidden_network", ""),
                         p.get("confidence", 0), p.get("timeframe", ""), p.get("evidence", ""),
                         p.get("trigger_event", ""), p.get("impact_score", 0),
                         p.get("category", "POLICY"), p.get("severity", "MEDIUM"), now)

    async def upsert_hidden_networks(self, networks: List[Dict]):
        now = datetime.utcnow().isoformat()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for hn in networks:
                    await conn.execute("""
                        INSERT INTO hidden_networks
                            (id,name,description,core_actors,mechanism,opacity_score,reach_score,policy_areas,created_at)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                        ON CONFLICT(id) DO UPDATE SET
                            opacity_score = EXCLUDED.opacity_score,
                            description   = EXCLUDED.description,
                            created_at    = EXCLUDED.created_at
                    """, hn.get("id"), hn.get("name"), hn.get("description"),
                         json.dumps(hn.get("core_actors", [])), hn.get("mechanism", ""),
                         hn.get("opacity_score", 0), hn.get("reach_score", 0),
                         json.dumps(hn.get("policy_areas", [])), now)

    async def upsert_alerts(self, alerts: List[Dict]):
        now = datetime.utcnow().isoformat()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for a in alerts:
                    await conn.execute("""
                        INSERT INTO alerts
                            (id,title,description,severity,entities_involved,predicted_impact,
                             timeframe,recommendation,hidden_network,confidence,created_at)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                        ON CONFLICT(id) DO UPDATE SET
                            description = EXCLUDED.description,
                            confidence  = EXCLUDED.confidence,
                            created_at  = EXCLUDED.created_at
                    """, a.get("id", f"alert_{now}"), a.get("title"), a.get("description"),
                         a.get("severity", "MEDIUM"), a.get("entities_involved", "[]"),
                         a.get("predicted_impact"), a.get("timeframe"), a.get("recommendation"),
                         a.get("hidden_network", ""), a.get("confidence", 0), now)
