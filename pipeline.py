#! /usr/bin/env python

import os
import os.path
import sys

zeroes = []
ones = []

def text(filenames):
    results = []
    for filename in filenames:
        basename = filename.split('.')[0]
        transcript = basename.replace('1', 'YES').replace('0', 'NO').replace('_', " ")
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
    os.system('echo -e "Y\nN" > dict/phones.txt') 
    os.system('echo -e "YES Y\nNO N" > dict/lexicon.txt')

    # add phone for silence
    os.system('echo "SIL" > dict/silence_phones.txt')
    os.system('echo "SIL" > dict/optional_silence.txt')
    os.system('mv dict/phones.txt dict/nonsilence_phones.txt')

    # amend lexicon to include silence
    os.system('cp dict/lexicon.txt dict/lexicon_words.txt')
    os.system('echo "<SIL> SIL" >> dict/lexicon.txt')

if __name__ == '__main__':
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
    os.system('utils/prepare_lang.sh --position-dependent-phones false dict "SIL" dict/tmp data/lang')
    # sm to FST
    os.system('lm/prepare_lm.sh')

    # FEATURE EXTRACTION AND TRAINING
    # extract MFCC
    os.system('steps/make_mfcc.sh --nj 1 <INPUT_DIR> exp/make_mfcc/train_yesno')
