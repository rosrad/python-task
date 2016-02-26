from runbash import BashRun, Exists
from os.path import join
from taskbase import * 

class dnn:
    def __init__(self, data, exp=None, layer=6, node=2048, force=False):
        "dnn initilaize"
        self.data=data
        if exp :
            self.exp=exp
        else:
            self.exp=join('exp',data)
        self.layer = layer
        self.node = node
        self.force = force
            
    def dbn_net(self):
        return '{0}/{1}.dbn'.format(self.dbn_dir(), self.layer)
    
    def dbn_dir(self):
        return join(self.exp, 'dbn')

    def dnn_net(self):
        return join(self.dnn_dir(), 'final.nnet')

    def dnn_dir(self):
        return join(self.exp, 'dnn')

    def train_dbn(self):
        if Exists(self.dbn_net()) and not self.force :
            return
        cmd = '''
        auto-run -g \
        steps/nnet/pretrain_dbn.sh \
        --rbm-iter 1 {0} {1}'''.format(self.data, self.dbn_dir())
        log = join(self.dbn_dir(), 'train_dbn.log')
        return BashRun(cmd, log)

    def train_dnn(self, ali):
        ali_egs=join(ali,'ali.1.gz')
        if not Exists(ali_egs) :
            return "ali missing:{}".format(ali_egs)
        if Exists(self.dnn_net()) and not self.force :
            return
        if not Exists(self.dbn_net()):
            self.train_dbn()
        self.splice_data()
        cmd = '''
        auto-run -g \
        steps/nnet/train.sh \
        --feature-transform {0}/final.feature_transform \
        --dbn {1} \
        --hid-layers 0 --learn-rate 0.008 \
        {2}_tr90 {2}_cv10 data/lang \
        {3} {3} {4}'''.format(self.dbn_dir(),
                              self.dbn_net(),
                              self.data,
                              ali,
                              self.dnn_dir())
        log = join(self.dnn_dir(), 'train_dnn.log')
        return BashRun(cmd, log)

    def splice_data(self):
        cmd = '''
        utils/subset_data_dir_tr_cv.sh \
        {0} {0}_tr90 {0}_cv10'''.format(self.data)
        return BashRun(cmd)


    def decode(self, data, tag, graph):
        decode_dnn(self.dnn_dir, data, tag, graph)


def train_dnn(data, exp, ali, layer=6, node=2048, force=False):
    return dnn(data.strip(),exp=exp.strip(),
               layer=layer,node=node,
               force=force).train_dnn(ali.strip())

def decode_dnn(dnn_dir, data, tag, graph):
    nnet ='{}/final.nnet'.format(dnn_dir)
    assert Exists(nnet)

    dir = decode_dir(dnn_dir, tag)

    cmd = '''
    auto-run -g \
    steps/nnet/decode.sh --nj {0} \
    --config conf/decode_dnn.config --acwt 0.08333 \
    {1}/graph_sw1_tg {2} {3}'''.format(10,
                                       graph,
                                       data,
                                       dir)
    log = '{}/decode.log'.format(dir)
    return BashRun(cmd,log)
    
