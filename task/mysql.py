from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import Column, Boolean, Integer, String, Float,DateTime
from dnn import *
from score import *
from feature import *
from runbash import BashRun
Base = declarative_base()


def cmd_join(args,gpu=False):
    g = ''
    if gpu:
        g = '-g'
    return ' '.join(['auto-run', g]+args)



class TaskBase:
    task_id = Column(Integer)
    date = Column(String)
    elapased = Column(String)
    code = Column(Integer)
    log = Column(String)
    script = Column(String)
    def run(self):
        self.pre_run()
        log = 'log/{0}.log'.format(self.__tablename__)
        for c in self.cmd():
            self.code, self.log = BashRun(c,log)
            if self.code > 0:
                break
            
        self.post_run()
        return str(self)

    def pre_run(self):
        self.date=datetime.now()
        print '*'*50
        print 'start:{0}'.format(str(self.date))
        print self
        print '*'*50

    def post_run(self):
        self.elapased=str(datetime.now()- self.date)
        self.date=str(self.date)

        print '+'*50
        print 'end:{0}'.format(datetime.now())
        print 'elapased:{0}'.format(self.elapased)
        print ' '*20,
        print self
        print '+'*50
        self.task_id = 0

    def __repr__(self):
        return 'task_id:{0}, {1}: code={2}'.format(self.task_id, self.__tablename__, self.code)        

        
class ITask(TaskBase):
    id = Column(Integer, primary_key=True)
    
class TrainDNN(ITask, Base):
    __tablename__ = 'TrainDNN'
    
    data = Column(String)
    model = Column(String)
    ali = Column(String)
    layer = Column(Integer)
    node= Column(Integer)
    force = Column(Boolean)
    def run(self):
        super(TrainDNN,self).pre_run()
        self.code, self.log = train_dnn(self.data, self.model,
                                        self.ali, layer=6, 
                                        node=2048, force=False)
        super(TrainDNN,self).post_run()
        return str(self)

    
class DecodeDNN(ITask,Base):
    __tablename__ = 'DecodeDNN'
    data = Column(String)
    model = Column(String)
    tag = Column(String)
    graph = Column(String)
    def run(self):
        super(DecodeDNN,self).pre_run()
        self.code,self.log = decode_dnn(self.model,self.data,
                                        self.tag,self.graph)
        super(DecodeDNN,self).post_run()
        return str(self)


    

class Score(TaskBase,Base):
    __tablename__ = 'Score'
    model = Column(String)
    tag = Column(String)
    wer = Column(String)
    __table_args__=(
        PrimaryKeyConstraint('model', 'tag', 'code'),
    )
    def run(self):
        super(Score,self).pre_run()
        self.wer, self.code, self.log = score(self.model, self.tag, subset='swbd')
        super(Score,self).post_run()
        return str(self)

    def __repr__(self):
        return 'task_id:{0}, {1}: code={2}, wer={3}'.format(self.task_id, self.__tablename__, self.code, self.wer)        


class MkFmllr(ITask,Base):
    __tablename__ = 'MkFmllr'
    src_data=Column(String)
    dst_data=Column(String)
    featdir=Column(String)
    trans_dir=Column(String)
    model = Column(String)

    def run(self):
        super(MkFmllr,self).pre_run()
        self.code, self.log = make_fmllr(self.src_data, self.dst_data, self.featdir, self.trans_dir, self.model)
        super(MkFmllr,self).post_run()
        return str(self)

class MkMFCC(ITask,Base):
    __tablename__ = 'MkMFCC'
    
    src_data=Column(String)
    dst_data=Column(String)
    ext=Column(String)
    type=Column(String)

    def run(self):
        super(MkMFCC,self).pre_run()
        self.code, self.log = make_mfcc(self.src_data, self.dst_data, ext=self.ext, type=self.type)
        super(MkMFCC,self).post_run()
        return str(self)

class AlignGMM(ITask):
    
    model = Column(String)
    data = Column(String)
    ali_dir = Column(String)
    fmllr = Column(Boolean)

    def cmd(self):
        yield cmd_join([self.script,self.data, 'data/lang', self.model, self.ali_dir])

class AlignLDA(AlignGMM,Base):
    __tablename__='AlignLDA'
    

    def cmd(self):
        self.script = 'steps/align_si.sh'
        return super(AlignLDA, self).cmd()

class AlignSat(AlignGMM,Base):
    __tablename__='AlignSat'

    def cmd(self):
        self.script = 'steps/align_fmllr.sh'
        return super(AlignSat, self).cmd()
    

class TrainGMM(ITask):
        
    data=Column(String)
    pre_ali=Column(String)
    model=Column(String)
    def cmd(self):
        gmm='4300 60000'
        yield cmd_join([self.script, gmm, self.data, 
                        'data/lang',self.pre_ali, self.model])
        mk_graph = 'utils/mkgraph.sh'
        yield cmd_join([mk_graph, 'data/lang_sw1_tg',self.model,graph_dir(self.model)])

class TrainSat(TrainGMM, Base):
    __tablename__ = 'TrainSat'
    def cmd(self):
        self.script = 'steps/train_sat.sh'
        return super(TrainSat, self).cmd()

class TrainLDA(TrainGMM, Base):
    __tablename__ = 'TrainLDA'
    def cmd(self):
        self.script = 'steps/train_lda_mllt.sh'
        return super(TrainLDA, self).cmd()

class DecodeGMM(ITask,Base):
    
    __tablename__ = 'DecodeGMM'
    model = Column(String)
    data = Column(String)
    tag = Column(String)
    fmllr=Column(Boolean)

    def cmd(self):
        self.script= 'steps/decode.sh'
        if self.fmllr:
            self.script = 'steps/decode_fmllr.sh'
            
        yield cmd_join([self.script, graph_dir(self.model), 
                        self.data, decode_dir(self.model, self.tag)])

    
def table_by(name):
    try:
        return globals().get(name)
    except:
        return None

tables= ['MkMFCC',
              'TrainLDA','AlignLDA', 
              'TrainSat', 'AlignSat',
              'DecodeGMM',
              'MkFmllr',
              'TrainDNN','DecodeDNN',
              'Score']

def task_order(names=tables):
    tasks=[]
    for n in names:
        t = table_by(n)
        if t:
            tasks.append(t)
    return tasks


