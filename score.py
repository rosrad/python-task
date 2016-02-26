from runbash import BashPipe
from taskbase import *


def score(model, tag, subset='swbd'):

    dir = decode_dir(model,tag)
    cmd = '''
    ./local/fmllr/wer.sh \
    --subset {0} {1}'''.format(subset,
                               dir)
    out,err = BashPipe(cmd)
    
    keys=['wer', 'msg']
    
    if out:
        return (out.split()[0],0,'')
    else:
        return ('', -1, err)

    
# model = 'exp/30k/60k/60k/60k/dnn5b_pretrain-dbn_dnn'
# tag = 'eval2000'

# wer,_ = score(model, tag)
# print wer


