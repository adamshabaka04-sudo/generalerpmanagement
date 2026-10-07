"""Local demonstration pilot. Run: python app.py."""
import json
import os
import sqlite3
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent
DB = Path(os.environ.get('FITOUT_DB', ROOT / 'fitout.sqlite3'))

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def initialize():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY, kind TEXT NOT NULL, company TEXT NOT NULL,
            name TEXT NOT NULL, detail TEXT NOT NULL, amount REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS stock (
            company TEXT PRIMARY KEY, litres REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY, company TEXT NOT NULL, home INTEGER NOT NULL,
            quantity REAL NOT NULL, note TEXT NOT NULL, submission TEXT UNIQUE NOT NULL);
        ''')
        if not db.execute('SELECT 1 FROM stock').fetchone():
            for company in ['Company A', 'Company B', 'Company C']:
                db.execute('INSERT INTO stock VALUES (?, ?)', (company, 200))
            seeds = [
                ('clients','Company A','Palm Residence Development','Dubai · 20-home fit-out',0,'Active'),
                ('projects','Company A','Palm Residence · 20 homes','Interior painting and fit-out',200000,'Planning'),
                ('purchasing','Company A','Interior paint · 100 litres','Confirmed incoming supply',2500,'Ordered'),
                ('clients','Company B','Al Noor Trading','Sharjah · supply-only customer',0,'Active'),
                ('projects','Company C','Marina Apartment Renovation','Abu Dhabi · interior finishing',85000,'Active')]
            db.executemany('INSERT INTO records(kind,company,name,detail,amount,status) VALUES (?,?,?,?,?,?)', seeds)

def number(value, label, minimum=0):
    import math
    value = float(value)
    if not math.isfinite(value) or value < minimum:
        raise ValueError(f'{label} must be a finite number of at least {minimum}.')
    return value

def mutate(data):
    company = data.get('company')
    if company not in ['Company A','Company B','Company C']:
        raise ValueError('Choose a valid company.')
    action = data.get('action')
    with connect() as db:
        if action == 'record':
            kind = data.get('kind')
            if kind not in ['clients','projects','purchasing','estimates']:
                raise ValueError('Unknown record type.')
            name = str(data.get('name','')).strip()
            if not name: raise ValueError('A name is required.')
            amount = number(data.get('amount',0), 'Amount')
            status = {'clients':'Active','projects':'Planning','purchasing':'Requested','estimates':'Draft'}[kind]
            db.execute('INSERT INTO records(kind,company,name,detail,amount,status) VALUES (?,?,?,?,?,?)',
                       (kind,company,name,str(data.get('detail','')),amount,status))
        elif action == 'stock':
            quantity = number(data.get('quantity'), 'Quantity', 0.01)
            direction = data.get('direction')
            if direction not in ['receive','consume']: raise ValueError('Invalid stock action.')
            delta = quantity if direction == 'receive' else -quantity
            result = db.execute('UPDATE stock SET litres=litres+? WHERE company=? AND litres+? >= 0', (delta,company,delta))
            if result.rowcount != 1: raise ValueError('Insufficient stock for this consumption.')
            db.execute('INSERT INTO records(kind,company,name,detail,amount,status) VALUES (?,?,?,?,?,?)',
                       ('movements',company,direction,str(data.get('detail','')),quantity,'Recorded'))
        elif action == 'report':
            home = number(data.get('home'), 'Home', 1)
            if home != int(home) or home > 20: raise ValueError('Home must be between 1 and 20.')
            quantity = number(data.get('quantity'), 'Completed area')
            submission = str(data.get('submission','')).strip()
            if not submission: raise ValueError('Submission ID required.')
            db.execute('INSERT OR IGNORE INTO reports(company,home,quantity,note,submission) VALUES (?,?,?,?,?)',
                       (company,int(home),quantity,str(data.get('note','')),submission))
        else: raise ValueError('Unknown action.')

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body=json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            self.send_json({'status':'ok'})
            return
        if self.path == '/api/state':
            with connect() as db:
                self.send_json({table:[dict(row) for row in db.execute('SELECT * FROM '+table)]
                                for table in ['records','stock','reports']})
            return
        paths={'/':'index.html','/style.css':'style.css','/app.js':'app.js'}
        if self.path not in paths: self.send_error(404); return
        path=ROOT/'static'/paths[self.path]
        body=path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',{'html':'text/html; charset=utf-8','css':'text/css','js':'text/javascript'}[path.suffix[1:]])
        self.send_header('Content-Length',str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        if self.path != '/api/action': self.send_error(404); return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length > 100000: raise ValueError('Request too large.')
            mutate(json.loads(self.rfile.read(length)))
            self.send_json({'ok':True},201)
        except (ValueError, TypeError, KeyError) as error:
            self.send_json({'error':str(error)},400)

if __name__ == '__main__':
    initialize()
    port=int(os.environ.get('PORT','8000'))
    print(f'Fit-Out Manager listening on port {port}',flush=True)
    ThreadingHTTPServer((os.environ.get('HOST','127.0.0.1'),port),Handler).serve_forever()
