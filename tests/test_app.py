import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        app.DB=Path(self.tmp.name)/'test.sqlite3'
        app.initialize()
    def tearDown(self): self.tmp.cleanup()
    def test_persistence_and_company_ownership(self):
        app.mutate(dict(action='record',kind='projects',company='Company B',name='New project',detail='Scope',amount=200000))
        app.initialize()
        with app.connect() as db:
            row=db.execute("SELECT * FROM records WHERE name='New project'").fetchone()
            self.assertEqual(row['company'],'Company B')
            self.assertEqual(row['amount'],200000)
    def test_negative_stock_rejected(self):
        with self.assertRaises(ValueError):
            app.mutate(dict(action='stock',company='Company A',direction='consume',quantity=201))
        app.mutate(dict(action='stock',company='Company A',direction='consume',quantity=22))
        with app.connect() as db:
            self.assertEqual(db.execute("SELECT litres FROM stock WHERE company='Company A'").fetchone()[0],178)
            self.assertEqual(db.execute("SELECT litres FROM stock WHERE company='Company B'").fetchone()[0],200)
    def test_report_retry_creates_one_record(self):
        data=dict(action='report',company='Company A',home=20,quantity=30,note='Painting',submission='unique-test')
        app.mutate(data);app.mutate(data)
        with app.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM reports').fetchone()[0],1)
    def test_invalid_values(self):
        for value in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):app.number(value,'Quantity')

if __name__=='__main__':unittest.main()
