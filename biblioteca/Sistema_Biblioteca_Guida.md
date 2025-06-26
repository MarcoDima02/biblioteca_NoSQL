
# 🏛️ Sistema Biblioteca - Guida Completa

## 📋 Indice
1. [Panoramica del Sistema](#panoramica)
2. [Installazione e Setup](#installazione)
3. [Configurazione MongoDB](#mongodb)
4. [Utilizzo del Sistema](#utilizzo)
5. [API e Interfacce](#api)
6. [Manutenzione e Backup](#manutenzione)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Panoramica del Sistema {#panoramica}

### Caratteristiche Principali
- **Database**: MongoDB (NoSQL)
- **Linguaggio**: Python 3.8+
- **Framework**: Flask/FastAPI
- **Gestione**: CLI automatizzata
- **Containerizzazione**: Docker + Docker Compose

### Funzionalità
- ✅ Gestione libri, autori, categorie
- ✅ Sistema prestiti e prenotazioni
- ✅ Ricerca avanzata full-text
- ✅ Statistiche e report
- ✅ API RESTful
- ✅ Backup automatico
- ✅ Interface web di amministrazione

---

## 🚀 Installazione e Setup {#installazione}

### Prerequisiti
```bash
# Python 3.8+
python --version

# Docker e Docker Compose
docker --version
docker-compose --version

# Git (per clonare il progetto)
git --version
```

### Setup Rapido (Metodo Consigliato)

#### 1. Preparazione Ambiente
```bash
mkdir sistema-biblioteca
cd sistema-biblioteca
python -m venv venv

# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Copia i file del sistema (biblioteca_setup.py, requirements.txt, etc.)
```

#### 2. Installazione Automatica
```bash
pip install -r requirements.txt
make setup
# O manualmente:
docker-compose up -d
sleep 10
python biblioteca_setup.py setup
```

#### 3. Verifica Installazione
```bash
make status
python biblioteca_setup.py stats
python biblioteca_setup.py cerca --query "manzoni"
```

---

## 🗄️ Configurazione MongoDB {#mongodb}

### Installazione MongoDB

#### Opzione 1: Docker (Consigliata)
```bash
docker-compose up -d
docker ps
# Dovresti vedere: biblioteca_mongo e biblioteca_mongo_express
```

#### Opzione 2: Installazione Nativa

**Ubuntu/Debian:**
```bash
# Importa chiave GPG
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
# Aggiungi repository e installa MongoDB
```

---

## 🛠️ Manutenzione e Backup {#manutenzione}

### Backup del Database
```bash
make backup
```

### Ripristino da Backup
```bash
make restore BACKUP_PATH=./backup_20240601_153000
```

### Pulizia Completa del Sistema
```bash
make clean
```

---

## ❓ Troubleshooting {#troubleshooting}

### Errore: `Connection refused` su MongoDB
- Verifica container:
  ```bash
  docker ps
  ```
- Log:
  ```bash
  make logs
  ```

### Errore: `pymongo.errors.ServerSelectionTimeoutError`
- MongoDB non attivo sulla porta 27017.

### Errore: `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

### Ambiente Virtuale
```bash
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

---

## 📡 API e Interfacce {#api}

### Avvio API con Uvicorn
```bash
uvicorn api_main:app --host 0.0.0.0 --port 5000
```

### Endpoint Esempio
- `GET /libri?query=manzoni`
- `POST /prestiti`
- `GET /statistiche`

---

## ✅ Comandi Rapidi

| Comando | Descrizione |
|--------|-------------|
| `make setup` | Setup completo sistema |
| `make status` | Stato servizi |
| `make backup` | Backup database |
| `make restore BACKUP_PATH=...` | Ripristino da backup |
| `python biblioteca_setup.py stats` | Statistiche biblioteca |
| `python biblioteca_setup.py cerca --query "titolo"` | Ricerca libri |

---

## 📚 Fine Guida

Sistema Biblioteca è pronto per la gestione completa di una libreria moderna, scalabile e con API pronte all’uso.

🔗 **Consigliato**: MongoDB >= 7.0 e Python >= 3.8
