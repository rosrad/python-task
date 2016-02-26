import pyexcel as pe
import pandas as pd
import pyexcel.ext.xlsx
import itertools
from pyexcel.sheets.nominablesheet import names_to_indices
from sqlalchemy import create_engine, asc, func
from sqlalchemy.orm import sessionmaker
from  mysql import *
import mysql
from runbash  import deep_run, gmap

def disp(x):
    print x
    
def to_str(t):
    return str(t)

def run(t):
    return t.run()


class sql_task(object):
    def __init__(self, excel=None, db='working.db'):

        self.excel = excel
        self.db = db
        self.engine = create_engine('sqlite:///{0}'.format(self.db)) 
            
        Base.metadata.create_all(self.engine) 
        Session=sessionmaker(bind=self.engine)
        self.session = Session()
        self.data={}
        self.Q = {}
        
        if self.excel:
            self.from_excel(self.excel)
            
           
    def to_excel(self,excel=None, original=True):
        if not excel:              
            return 
        writer = pd.ExcelWriter(excel, engine='xlsxwriter')
        for k, v in self.data.iteritems():
            v.to_excel(writer, sheet_name=k,index=False)
        
        writer.close()
            
    def from_excel(self,file):
        r = pd.ExcelFile(file)
        tables = filter(lambda x: x in r.sheet_names,  mysql.tables)
        for s in tables:
            t = r.parse(s).sort_values('task_id')
            self.data[s]=t
            for k,v in t.groupby(['task_id']).groups.iteritems():
                if k <= 0:
                    continue
                c = [(s,k,i,t.loc[i].to_dict()) for i in v]
                if k in self.Q:
                    self.Q[k]+=[c]
                else:
                    self.Q[k]=[c]
                    

    def Queue(self):
        print ''
        if not self.Q:
            print 'No task will be in queue'
            return
        v = self.Q.values()
        map(lambda l : map(lambda sl:
                           map(disp,sl), 
                           l), v)

    def run(self, flush=True):


        def run_record(r):
            c = table_by(r[0])
            s = c(** r[3])
            s.run()
            self.session.merge(s)
            res = { k:s.__dict__[k] for k,v in r[3].iteritems() }
            self.data[r[0]].loc[r[2]] = pd.Series(res)

        v = self.Q.values()
        self.result=gmap(lambda l : 
                         map(lambda sl:
                             gmap(run_record,sl, job=2), 
                             l), 
                         v, job=5)
        self.session.commit()

        if flush:
            self.flush_back()
        return self

    def flush_back(self):
        if self.excel:
            self.to_excel(self.excel)

    def show_result(self):
        print ''
        if self.result:
            deep_run(disp, self.result)



# file = '/home/14/ren/shared/task-excel/gmm_test.xlsx'
# db = '/home/14/ren/shared/task-excel/working.db'
# mgr = sql_task(excel=file,db=db)

# for k, v in mgr.Q.iteritems():
#     print k
#     for i in v:
#         print len(i)

# mgr.Queue()
# mgr.run()
# # #mgr.from_excel(file)
# # #mgr.fetch_queue()
# mgr.Queue()
# mgr.run().show_result()
# mgr.to_excel(file)
#print mgr.result
#deep_run(disp, msg)

# print mgr.session.query(Score).first().__dict__

# mgr.to_excel(file)

