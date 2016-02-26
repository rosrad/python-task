from runbash import BashRun, Exists
from os.path import join


def featdir(data,prefix='mfcc'):
    return join(prefix, data)

def compute_cmvn(data,featdir):
    assert Exists(data)
    cmd = '''
    auto-run steps/compute_cmvn_stats.sh \
    {0} {1}/log {1}'''.format(data, featdir)
    return BashRun(cmd, 'log/compute_cmvn.log')


def transform_fmllr(src_data, dst_data, featdir,
                    trans_dir, model_dir ):
    assert( Exists(src_data) and 
            Exists(trans_dir) and
            Exists(model_dir))
    
    cmd = ''' 
    auto-run  steps/nnet/make_fmllr_feats.sh \
        --nj 20 --transform-dir {0} \
        {1} {2} {3} {4}/log {4}'''.format(trans_dir,
                                          dst_data,
                                          src_data,
                                          model_dir,
                                          featdir)
    return BashRun(cmd,'log/transform_fmllr.log')

def make_fmllr(src_data, dst_data, featdir,
               trans_dir, model_dir ):
    err_code = transform_fmllr(src_data,
                               dst_data,
                               featdir,
                               trans_dir,
                               model_dir)
    return (err_code and compute_cmvn(dst_data,featdir)) 


def make_mfcc(src_data, dst_data, ext, type):
    cmd = '''
        auto-run -g \
        local/fmllr/compute_mfcc.sh \
        --type {0} --feat {1} {2} {3}'''.format(type,
                                                ext,
                                                src_data,
                                                dst_data)
    return BashRun(cmd, 'log/compute_mfcc.log')




#
#src_data= 'data/segwav/mcode/eval2000'
#dst_data = join('data-fmllr',src_data)
#dst_data += '_mcode_mfcc_kaldi_fmllr'
#featdir = featdir(dst_data,'fmllr')
#trans_dir = 'exp/30k/60k/60k/tri4b/decode_eval2000_sw1_tg'
#model_dir = 'exp/30k/60k/60k/tri4b'
#
#make_fmllr(src_data,
#           dst_data,
#           featdir,
#           trans_dir,
#           model_dir)
#
