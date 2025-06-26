#!/usr/bin/env python3
"""
Sistema Biblioteca - Setup Automatizzato
Database: MongoDB
Linguaggio: Python 3.8+
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import subprocess
from pathlib import Path

# Dipendenze
try:
    from pymongo import MongoClient
    from bson import ObjectId
    import click
    from faker import Faker
    import requests
except ImportError as e:
    print(f"Errore: {e}")
    print("Installa le dipendenze con: pip install -r requirements.txt")
    sys.exit(1)

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('biblioteca.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BibliotecaSetup:
    """Classe principale per setup e gestione della biblioteca"""
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/", db_name: str = "biblioteca"):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.faker = Faker('it_IT')
        
    def connect_database(self):
        """Connessione al database MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Test connessione
            self.client.admin.command('ping')
            logger.info(f"✅ Connesso a MongoDB: {self.db_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Errore connessione MongoDB: {e}")
            return False
    
    def create_collections_and_indexes(self):
        """Crea le collezioni e gli indici necessari"""
        try:
            # Collezioni
            collections = ['autori', 'categorie', 'libri', 'utenti', 'prestiti', 'prenotazioni']
            
            for collection in collections:
                if collection not in self.db.list_collection_names():
                    self.db.create_collection(collection)
                    logger.info(f"✅ Collezione '{collection}' creata")
            
            # Indici per performance
            indexes = [
                ('autori', [('cognome', 1), ('nome', 1)]),
                ('libri', [('titolo', 'text'), ('isbn', 1)]),
                ('libri', [('categoria_id', 1), ('disponibile', 1)]),
                ('utenti', [('email', 1)]),
                ('prestiti', [('utente_id', 1), ('stato', 1)]),
                ('prestiti', [('data_scadenza', 1)]),
                ('prenotazioni', [('utente_id', 1), ('stato', 1)])
            ]
            
            for collection, index in indexes:
                self.db[collection].create_index(index)
                logger.info(f"✅ Indice creato su {collection}: {index}")
            
            # Indice univoco per email utenti
            self.db.utenti.create_index('email', unique=True)
            self.db.libri.create_index('isbn', unique=True, sparse=True)
            
            logger.info("✅ Collezioni e indici creati con successo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore creazione collezioni: {e}")
            return False
    
    def load_sample_data(self):
        """Carica dati di esempio"""
        try:
            # Categorie
            categorie = [
                {"nome": "Narrativa Italiana", "descrizione": "Opere di narrativa di autori italiani"},
                {"nome": "Fantascienza", "descrizione": "Romanzi e racconti di fantascienza"},
                {"nome": "Saggistica", "descrizione": "Saggi su vari argomenti"},
                {"nome": "Poesia", "descrizione": "Raccolte poetiche"},
                {"nome": "Storia", "descrizione": "Libri di storia e biografie"},
                {"nome": "Filosofia", "descrizione": "Testi filosofici e di pensiero"},
                {"nome": "Gialli", "descrizione": "Romanzi gialli e thriller"},
                {"nome": "Classici", "descrizione": "I grandi classici della letteratura"}
            ]
            
            categorie_ids = []
            for cat in categorie:
                cat['created_at'] = datetime.now()
                result = self.db.categorie.insert_one(cat)
                categorie_ids.append(result.inserted_id)
            
            logger.info(f"✅ Inserite {len(categorie)} categorie")
            
            # Autori famosi
            autori = [
                {"nome": "Alessandro", "cognome": "Manzoni", "data_nascita": "1785-03-07", "nazionalita": "Italiana"},
                {"nome": "Italo", "cognome": "Calvino", "data_nascita": "1923-10-15", "nazionalita": "Italiana"},
                {"nome": "Umberto", "cognome": "Eco", "data_nascita": "1932-01-05", "nazionalita": "Italiana"},
                {"nome": "Elena", "cognome": "Ferrante", "nazionalita": "Italiana"},
                {"nome": "Roberto", "cognome": "Saviano", "data_nascita": "1979-09-22", "nazionalita": "Italiana"},
                {"nome": "Primo", "cognome": "Levi", "data_nascita": "1919-07-31", "nazionalita": "Italiana"},
                {"nome": "Gabriel", "cognome": "García Márquez", "data_nascita": "1927-03-06", "nazionalita": "Colombiana"},
                {"nome": "George", "cognome": "Orwell", "data_nascita": "1903-06-25", "nazionalita": "Britannica"},
                {"nome": "Agatha", "cognome": "Christie", "data_nascita": "1890-09-15", "nazionalita": "Britannica"},
                {"nome": "Isaac", "cognome": "Asimov", "data_nascita": "1920-01-02", "nazionalita": "Americana"}
            ]
            
            autori_ids = []
            for autore in autori:
                autore['created_at'] = datetime.now()
                if 'data_nascita' in autore:
                    autore['data_nascita'] = datetime.strptime(autore['data_nascita'], '%Y-%m-%d')
                result = self.db.autori.insert_one(autore)
                autori_ids.append(result.inserted_id)
            
            logger.info(f"✅ Inseriti {len(autori)} autori")
            
            # Libri famosi
            libri = [
                {
                    "titolo": "I Promessi Sposi",
                    "isbn": "9788804123456",
                    "anno_pubblicazione": 1827,
                    "numero_pagine": 672,
                    "lingua": "Italiano",
                    "editore": "Mondadori",
                    "categoria_id": categorie_ids[0],  # Narrativa Italiana
                    "autore_ids": [autori_ids[0]],    # Manzoni
                    "numero_copie": 3,
                    "disponibile": True
                },
                {
                    "titolo": "Le Città Invisibili",
                    "isbn": "9788806234567",
                    "anno_pubblicazione": 1972,
                    "numero_pagine": 164,
                    "lingua": "Italiano",
                    "editore": "Einaudi",
                    "categoria_id": categorie_ids[0],  # Narrativa Italiana
                    "autore_ids": [autori_ids[1]],    # Calvino
                    "numero_copie": 2,
                    "disponibile": True
                },
                {
                    "titolo": "Il Nome della Rosa",
                    "isbn": "9788845292344",
                    "anno_pubblicazione": 1980,
                    "numero_pagine": 503,
                    "lingua": "Italiano",
                    "editore": "Bompiani",
                    "categoria_id": categorie_ids[6],  # Gialli
                    "autore_ids": [autori_ids[2]],    # Eco
                    "numero_copie": 4,
                    "disponibile": True
                },
                {
                    "titolo": "L'Amica Geniale",
                    "isbn": "9788866345678",
                    "anno_pubblicazione": 2011,
                    "numero_pagine": 331,
                    "lingua": "Italiano",
                    "editore": "E/O",
                    "categoria_id": categorie_ids[0],  # Narrativa Italiana
                    "autore_ids": [autori_ids[3]],    # Ferrante
                    "numero_copie": 1,
                    "disponibile": False
                },
                {
                    "titolo": "1984",
                    "isbn": "9780451524935",
                    "anno_pubblicazione": 1949,
                    "numero_pagine": 328,
                    "lingua": "Inglese",
                    "editore": "Secker & Warburg",
                    "categoria_id": categorie_ids[1],  # Fantascienza
                    "autore_ids": [autori_ids[7]],    # Orwell
                    "numero_copie": 3,
                    "disponibile": True
                }
            ]
            
            libri_ids = []
            for libro in libri:
                libro['created_at'] = datetime.now()
                result = self.db.libri.insert_one(libro)
                libri_ids.append(result.inserted_id)
            
            logger.info(f"✅ Inseriti {len(libri)} libri")
            
            # Utenti di esempio
            utenti = []
            for i in range(20):
                utente = {
                    "nome": self.faker.first_name(),
                    "cognome": self.faker.last_name(),
                    "email": self.faker.email(),
                    "telefono": self.faker.phone_number(),
                    "indirizzo": f"{self.faker.street_address()}, {self.faker.city()}",
                    "data_registrazione": self.faker.date_time_between(start_date='-2y', end_date='now'),
                    "attivo": True,
                    "created_at": datetime.now()
                }
                utenti.append(utente)
            
            utenti_result = self.db.utenti.insert_many(utenti)
            logger.info(f"✅ Inseriti {len(utenti)} utenti")
            
            # Prestiti di esempio
            prestiti = []
            for i in range(10):
                data_prestito = self.faker.date_time_between(start_date='-30d', end_date='now')
                prestito = {
                    "utente_id": self.faker.random_element(utenti_result.inserted_ids),
                    "libro_id": self.faker.random_element(libri_ids),
                    "data_prestito": data_prestito,
                    "data_scadenza": data_prestito + timedelta(days=30),
                    "stato": self.faker.random_element(['attivo', 'restituito']),
                    "created_at": datetime.now()
                }
                
                if prestito['stato'] == 'restituito':
                    prestito['data_restituzione'] = data_prestito + timedelta(days=self.faker.random_int(1, 28))
                
                prestiti.append(prestito)
            
            self.db.prestiti.insert_many(prestiti)
            logger.info(f"✅ Inseriti {len(prestiti)} prestiti")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore caricamento dati: {e}")
            return False
    
    def generate_api_data(self):
        """Genera file JSON con dati di esempio per API"""
        try:
            # Recupera alcuni dati dal database
            sample_data = {
                "autori": list(self.db.autori.find().limit(5)),
                "categorie": list(self.db.categorie.find().limit(5)),
                "libri": list(self.db.libri.find().limit(5)),
                "utenti": list(self.db.utenti.find().limit(3)),
                "prestiti": list(self.db.prestiti.find().limit(3))
            }
            
            # Converte ObjectId in string per JSON
            def convert_objectid(obj):
                if isinstance(obj, ObjectId):
                    return str(obj)
                elif isinstance(obj, dict):
                    return {k: convert_objectid(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_objectid(item) for item in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            sample_data = convert_objectid(sample_data)
            
            # Salva in file
            with open('sample_data.json', 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info("✅ File sample_data.json generato")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore generazione API data: {e}")
            return False


class BibliotecaAPI:
    """API per gestione biblioteca"""
    
    def __init__(self, db):
        self.db = db
    
    def cerca_libri(self, query: str = None, categoria: str = None, 
                   autore: str = None, disponibile: bool = None) -> List[Dict]:
        """Cerca libri con filtri multipli"""
        try:
            match_conditions = {}
            
            if query:
                match_conditions['$text'] = {'$search': query}
            
            if categoria:
                # Trova categoria per nome
                cat = self.db.categorie.find_one({'nome': categoria})
                if cat:
                    match_conditions['categoria_id'] = cat['_id']
            
            if disponibile is not None:
                match_conditions['disponibile'] = disponibile
            
            pipeline = [
                {'$match': match_conditions},
                {
                    '$lookup': {
                        'from': 'autori',
                        'localField': 'autore_ids',
                        'foreignField': '_id',
                        'as': 'autori_info'
                    }
                },
                {
                    '$lookup': {
                        'from': 'categorie',
                        'localField': 'categoria_id',
                        'foreignField': '_id',
                        'as': 'categoria_info'
                    }
                },
                {
                    '$project': {
                        'titolo': 1,
                        'isbn': 1,
                        'anno_pubblicazione': 1,
                        'disponibile': 1,
                        'numero_copie': 1,
                        'autori': '$autori_info.cognome',
                        'categoria': {'$arrayElemAt': ['$categoria_info.nome', 0]}
                    }
                }
            ]
            
            return list(self.db.libri.aggregate(pipeline))
            
        except Exception as e:
            logger.error(f"Errore ricerca libri: {e}")
            return []
    
    def crea_prestito(self, utente_id: str, libro_id: str, giorni: int = 30) -> Dict:
        """Crea un nuovo prestito"""
        try:
            # Verifica disponibilità libro
            libro = self.db.libri.find_one({'_id': ObjectId(libro_id)})
            if not libro or not libro.get('disponibile') or libro.get('numero_copie', 0) <= 0:
                return {'success': False, 'error': 'Libro non disponibile'}
            
            # Verifica utente
            utente = self.db.utenti.find_one({'_id': ObjectId(utente_id)})
            if not utente or not utente.get('attivo'):
                return {'success': False, 'error': 'Utente non valido'}
            
            # Crea prestito
            prestito = {
                'utente_id': ObjectId(utente_id),
                'libro_id': ObjectId(libro_id),
                'data_prestito': datetime.now(),
                'data_scadenza': datetime.now() + timedelta(days=giorni),
                'stato': 'attivo',
                'created_at': datetime.now()
            }
            
            result = self.db.prestiti.insert_one(prestito)
            
            # Aggiorna disponibilità libro
            self.db.libri.update_one(
                {'_id': ObjectId(libro_id)},
                {
                    '$inc': {'numero_copie': -1},
                    '$set': {'disponibile': libro['numero_copie'] > 1}
                }
            )
            
            return {
                'success': True,
                'prestito_id': str(result.inserted_id),
                'data_scadenza': prestito['data_scadenza'].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Errore creazione prestito: {e}")
            return {'success': False, 'error': str(e)}
    
    def statistiche(self) -> Dict:
        """Genera statistiche della biblioteca"""
        try:
            stats = {
                'totale_libri': self.db.libri.count_documents({}),
                'libri_disponibili': self.db.libri.count_documents({'disponibile': True}),
                'prestiti_attivi': self.db.prestiti.count_documents({'stato': 'attivo'}),
                'utenti_registrati': self.db.utenti.count_documents({'attivo': True}),
                'prestiti_scaduti': self.db.prestiti.count_documents({
                    'stato': 'attivo',
                    'data_scadenza': {'$lt': datetime.now()}
                })
            }
            
            # Libri più prestati
            pipeline = [
                {'$group': {'_id': '$libro_id', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 5},
                {
                    '$lookup': {
                        'from': 'libri',
                        'localField': '_id',
                        'foreignField': '_id',
                        'as': 'libro'
                    }
                }
            ]
            
            stats['libri_piu_prestati'] = list(self.db.prestiti.aggregate(pipeline))
            
            return stats
            
        except Exception as e:
            logger.error(f"Errore statistiche: {e}")
            return {}


# CLI Commands
@click.group()
def cli():
    """Sistema di gestione biblioteca con MongoDB"""
    pass

@cli.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/', help='URI MongoDB')
@click.option('--db-name', default='biblioteca', help='Nome database')
def setup(mongo_uri, db_name):
    """Setup iniziale del database"""
    setup_obj = BibliotecaSetup(mongo_uri, db_name)
    
    if not setup_obj.connect_database():
        return
    
    logger.info("🚀 Avvio setup biblioteca...")
    
    if setup_obj.create_collections_and_indexes():
        logger.info("✅ Collezioni create")
    
    if setup_obj.load_sample_data():
        logger.info("✅ Dati di esempio caricati")
    
    if setup_obj.generate_api_data():
        logger.info("✅ File API generati")
    
    logger.info("🎉 Setup completato con successo!")

@cli.command()
@click.option('--query', help='Cerca per titolo')
@click.option('--categoria', help='Filtra per categoria')
@click.option('--disponibile', is_flag=True, help='Solo libri disponibili')
def cerca(query, categoria, disponibile):
    """Cerca libri nel database"""
    setup_obj = BibliotecaSetup()
    if not setup_obj.connect_database():
        return
    
    api = BibliotecaAPI(setup_obj.db)
    risultati = api.cerca_libri(query, categoria, disponibile=disponibile)
    
    if risultati:
        for libro in risultati:
            print(f"📚 {libro['titolo']} - {', '.join(libro.get('autori', []))}")
            print(f"   Categoria: {libro.get('categoria', 'N/A')}")
            print(f"   Disponibile: {'✅' if libro.get('disponibile') else '❌'}")
            print()
    else:
        print("Nessun libro trovato")

@cli.command()
def stats():
    """Mostra statistiche biblioteca"""
    setup_obj = BibliotecaSetup()
    if not setup_obj.connect_database():
        return
    
    api = BibliotecaAPI(setup_obj.db)
    statistiche = api.statistiche()
    
    print("📊 STATISTICHE BIBLIOTECA")
    print("=" * 30)
    print(f"Totale libri: {statistiche.get('totale_libri', 0)}")
    print(f"Libri disponibili: {statistiche.get('libri_disponibili', 0)}")
    print(f"Prestiti attivi: {statistiche.get('prestiti_attivi', 0)}")
    print(f"Utenti registrati: {statistiche.get('utenti_registrati', 0)}")
    print(f"Prestiti scaduti: {statistiche.get('prestiti_scaduti', 0)}")

if __name__ == '__main__':
    cli()
