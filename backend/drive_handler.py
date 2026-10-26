# drive_handler.py  (filename kept so main.py needs NO changes)
# Storage layer. NO Google Drive anymore.
#   - If MONGODB_URI is set  -> data stored in MongoDB Atlas (use this when live)
#   - Otherwise              -> data stored in local ./data folder (local testing only)

import os
import io
import json
import gzip
import base64
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', '').strip()
DATA_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

_db = None
def _mongo():
    global _db
    if _db is None:
        from pymongo import MongoClient
        _db = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=8000)['ecoledger']
    return _db


def _local_path(city, name):
    d = os.path.join(DATA_DIR, city.upper())
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)


def get_or_create_city_folder(city_name: str) -> str:
    return city_name.upper()


def upload_csv_to_city_folder(city_name: str, file_bytes: bytes, filename: str) -> str:
    """Keep a copy of the raw CSV (skipped silently if too big for Mongo)."""
    city = city_name.upper()
    if MONGODB_URI:
        packed = gzip.compress(file_bytes)
        if len(packed) < 10_000_000:
            _mongo()['raw_csv'].replace_one(
                {'_id': city},
                {'_id': city, 'filename': filename,
                 'data': base64.b64encode(packed).decode()},
                upsert=True)
    else:
        with open(_local_path(city, filename), 'wb') as f:
            f.write(file_bytes)
    return filename


def save_results_to_city_folder(city_name: str, results: dict) -> str:
    city = city_name.upper()
    payload = json.dumps(results)
    if MONGODB_URI:
        _mongo()['results'].replace_one(
            {'_id': city}, {'_id': city, 'json': payload}, upsert=True)
    else:
        with open(_local_path(city, f'{city}_edd_results.json'), 'w') as f:
            f.write(payload)
    return city


def load_city_results(city_name: str) -> dict | None:
    city = city_name.upper()
    if MONGODB_URI:
        doc = _mongo()['results'].find_one({'_id': city})
        return json.loads(doc['json']) if doc else None
    p = os.path.join(DATA_DIR, city, f'{city}_edd_results.json')
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def list_all_cities() -> list[str]:
    if MONGODB_URI:
        return sorted(d['_id'] for d in _mongo()['results'].find({}, {'_id': 1}))
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(
        c for c in os.listdir(DATA_DIR)
        if os.path.exists(os.path.join(DATA_DIR, c, f'{c}_edd_results.json')))
