#! /usr/bin/env python

# NOTE: in addition to this file, I also had to modify lm/task.arpabo and switch NO for LO and YES for KEN


import os
import os.path
import sys
import subprocess

zeroes = []
ones = []

def text(filenames):
    results = []
    for filename in filenames:
        basename = filename.split('.')[0]
        transcript = basename.replace('1', 'KEN').replace('0', 'LO').replace('_', " ")
        results.append("{} {}".format(basename.split('.')[0], transcript))

    return '\n'.join(sorted(results))

def wav_scp(filenames):
    results = []
    for filename in filenames:
        basename = filename.split('.')[0]
        results.append("{} {}".format(basename.split('.')[0], 'waves_yesno/'+filename))

    return '\n'.join(sorted(results))

def utt2spk(filenames):
    results = []
    for filename in filenames:
        basename = filename.split('.')[0]
        results.append("{} {}".format(basename.split('.')[0], 'global'))

    return '\n'.join(sorted(results))

def spk2utt(filenames):
    os.system('utils/utt2spk_to_spk2utt.pl data/train_yesno/utt2spk > data/train_yesno/spk2utt')
    os.system('utils/utt2spk_to_spk2utt.pl data/test_yesno/utt2spk > data/test_yesno/spk2utt')

def prep_dict():
    os.system('mkdir dict')

    # initial dictionaries
    with open('dict/phones.txt', 'w') as f:
        f.write('K\nEH\nN\nL\nOW\n')
    f.close()
    with open('dict/lexicon.txt', 'w') as f:
        f.write('KEN K EH N\n')
        f.write('LO L OW\n')
    f.close()

    # add phone for silence
    with open('dict/silence_phones.txt', 'w') as f:
        f.write('SIL\n')
    f.close()
    with open('dict/optional_silence.txt', 'w') as f:
        f.write('SIL\n')
    f.close()
    os.system('mv dict/phones.txt dict/nonsilence_phones.txt')

    # amend lexicon to include silence
    os.system('cp dict/lexicon.txt dict/lexicon_words.txt')
    with open('dict/lexicon.txt', 'a') as f:
        f.write('<SIL> SIL\n')
    f.close()

if __name__ == '__main__':
    os.system('mkdir data/')
    os.system('mkdir data/train_yesno/')
    os.system('mkdir data/test_yesno/')
    
    # DATA PREP
    for fn in os.listdir('waves_yesno'):
        if fn.startswith('0'):
            zeroes.append(fn)   # => training set
        elif fn.startswith('1'):
            ones.append(fn)     # => test set

    # create files
    with open('data/train_yesno/text', 'w') as train_text, open('data/test_yesno/text', 'w') as test_text:
        train_text.write(text(zeroes))
        test_text.write(text(ones))
    with open('data/train_yesno/wav.scp', 'w') as train_text, open('data/test_yesno/wav.scp', 'w') as test_text:
        train_text.write(wav_scp(zeroes))
        test_text.write(wav_scp(ones))
    with open('data/train_yesno/utt2spk', 'w') as train_text, open('data/test_yesno/utt2spk', 'w') as test_text:
        train_text.write(utt2spk(zeroes))
        test_text.write(utt2spk(ones))
    with open('data/train_yesno/spk2utt', 'w') as train_text, open('data/test_yesno/spk2utt', 'w') as test_text:
        spk2utt(zeroes)
        spk2utt(ones)

    # run fix script to prevent complaining about sorting
    os.system('utils/fix_data_dir.sh data/train_yesno')
    os.system('utils/fix_data_dir.sh data/test_yesno')

    # PREPARING THE DICTIONARY
    prep_dict()

    # dictionary to FST
    os.system('utils/prepare_lang.sh --position-dependent-phones false dict "<SIL>" dict/tmp data/lang')
    # sm to FST
    os.system('lm/prepare_lm.sh')

    # FEATURE EXTRACTION AND TRAINING
    # extract MFCC
    os.system('steps/make_mfcc.sh --nj 1 data/train_yesno exp/make_mfcc/train_yesno')
    # normalize cepstral features
    os.system('steps/compute_cmvn_stats.sh data/train_yesno exp/make_mfcc/train_yesno')
    # train monophone models
    os.system('steps/train_mono.sh --nj 1 --cmd utils/run.pl data/train_yesno data/lang exp/mono')

    # DECODING
    # project test set into feature space
    os.system('steps/make_mfcc.sh --nj 1 data/test_yesno exp/make_mfcc/test_yesno')
    os.system('steps/compute_cmvn_stats.sh data/test_yesno exp/make_mfcc/test_yesno')
    # build fully connected FST network
    os.system('utils/mkgraph.sh --mono data/lang_test_tg exp/mono exp/mono/graph_tgpr')
    # find best path
    os.system('mkdir exp/mono/decode_test_yesno')
    os.system('steps/decode.sh --nj 1 exp/mono/graph_tgpr data/test_yesno exp/mono/decode_test_yesno')
    # get alignment
    os.system('steps/get_ctm.sh data/test_yesno data/lang exp/mono/decode_test_yesno')
