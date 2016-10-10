#! /usr/bin/env python

import os
import os.path
import sys

zeroes = []
ones = []

for fn in os.listdir('waves_yesno'):
    if fn.startswith('0'):
        zeroes.append(fn)   # => training set
    elif fn.startswith('1'):
        ones.append(fn)     # => test set

def text(filenames):
    results = []
    for filename in filenames:
        basename = filename.split('.')[0]
        transcript = basename.replace('1', 'YES').replace('0', 'NO').replace('_', " ")
        results.append("{} {}".format(basename.split('.')[0], transcript))

    return '\n'.join(sorted(results))

with open('data/train_yesno/text', 'w') as train_text, open('data/test_yesno/text', 'w') as test_text:
    train_text.write(text(zeroes))
    test_text.write(text(ones))

# finish this method
def wav_scp(filenames):
    results = []
    for filename in filenames:
        basename = filename.split('.')[0]
        results.append("{} {}".format(basename.split('.')[0], 'waves_yesno/'+filename))

    return '\n'.join(sorted(results))

with open('data/train_yesno/wav.scp', 'w') as train_text, open('data/test_yesno/wav.scp', 'w') as test_text:
    train_text.write(wav_scp(zeroes))
    test_text.write(wav_scp(ones))


# finish this method

def utt2spk(filenames):
    results = []
    for filename in filenames:
        basename = filename.split('.')[0]
        results.append("{} {}".format(basename.split('.')[0], 'global'))

    return '\n'.join(sorted(results))

with open('data/train_yesno/utt2spk', 'w') as train_text, open('data/test_yesno/utt2spk', 'w') as test_text:
    train_text.write(utt2spk(zeroes))
    test_text.write(utt2spk(ones))


# finish this method
# note that, spk2utt can be generate by using Kaldi util, once you have utt2spk file.
def spk2utt(filenames):
    os.system('utils/utt2spk_to_spk2utt.pl data/train_yesno/utt2spk > data/train_yesno/spk2utt')
    os.system('utils/utt2spk_to_spk2utt.pl data/test_yesno/utt2spk > data/test_yesno/spk2utt')

with open('data/train_yesno/spk2utt', 'w') as train_text, open('data/test_yesno/spk2utt', 'w') as test_text:
    spk2utt(zeroes)
    spk2utt(ones)

# run fix script to prevent complaining about sorting
os.system('utils/fix_data_dir.sh data/train_yesno/')
os.system('utils/fix_data_dir.sh data/test_yesno/')
