#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Author : Salniger
# Date   : 01/14/2013
# Version: 1.0.0

import os
import codecs
import simplejson as json
import MeCab
import cPickle as pickle
import random
import pdb
import lcd
import time

class TweetsParser(object):
    """
    Parsing tweet data from .tsv files in target directories for munou-chan.
    """
    root_path = u'./tweets/'
    dump_path = u'./'

    def get_tweet_file_list(self):
        """
        Get file path strings.

        These file format must be .tsv file
          and 1st row must be raw tweet string
            (Please look sample files).  

        [Return]
        (list(unicode)) file paths
        """
        paths = []
        for root, dirs, files in os.walk(self.root_path):
            for f in files:
                if os.path.splitext(os.path.basename(f))[1] == u'.tsv':
                    paths.append(os.path.join(root,f))
        return paths

    def get_tweets(self,remove_at = True):
        """
        Get tweets in root_path files.

        [Args]
        (bool) remove_at: True -> Remove reply tweet. False -> Not remove.

        [Return]
        (dictionary((unicode):(unicode)))
          dictionary{
            user_name1: tweet list1
            user_name2: tweet list2
            ...
            }
        """
        paths = self.get_tweet_file_list()
        tweets = {}
        for p in paths:
            name = os.path.splitext(os.path.basename(p))[0]
            print '[Parse tweet file (start): ' + name + ']'
            tweets[name] = []
            counter = 0
            for line in codecs.open(p,'r','utf-8',errors = 'ignore'):
                try:
                    l = line.split('\t')[0]
                    if remove_at == True and l[0] == u'@':
                        pass
                    else:
                        tweets[name].append(self.split_to_words(l))
                        counter += 1
                        if counter % 100 == 0:
                            print 'Count:', counter
                except:
                    # print l
                    pass
            print '[Parse tweet file (end): ' + name + ']'
        return tweets

    def get_yomi_bigram_wordcounts_dict(self):
        """
        Get word yomis count (bigram).

        [Return]
        (dictionary(dictionary((unicode):(int))))
          first_word_dictionary(
            first_word1:{
              second_word1:count1
              second_word2:count2
              ...
            }
            first_word2:{
              second_word1:count1
              second_word2:count2
            }
            ...
          )
        """
        tweets = self.load_splitted_text()
        pairs = []
        dict = {}
        for user in tweets.keys():
            for tweet in tweets[user]:
                # Use yomi pairs
                pairs.append((u"[start]",tweet[1][3]))
                pairs.extend(
                    [(tweet[i][3],tweet[i+1][3]) for i in range(1,len(tweet)-2)]
                    )
                pairs.append((tweet[-2][3],u"[end]"))
        for pair in pairs:
            if not dict.has_key(pair[0]):
                dict[pair[0]] = {pair[1]:1}
            else:
                if not dict[pair[0]].has_key(pair[1]):
                    dict[pair[0]][pair[1]] = 1
                else:
                    dict[pair[0]][pair[1]] += 1
        return dict

    def get_yomi_bigram_word_probability(self):
        """
        Get word yomis probability (bigram).

        [Return]
        (dictionary(dictionary((unicode):(float))))
          first_word_dictionary(
            first_word1:{
              second_word1:probability1
              second_word2:probability2
              ...
              # sum(probability1 ... n) nearly equal 1
            }
            first_word2:{
              second_word1:count1
              second_word2:count2
            }
            ...
          )
        """
        dict = self.get_yomi_bigram_wordcounts_dict()
        for first_word in dict.keys():
            sum_value = sum(dict[first_word].values())
            for second_word in dict[first_word].keys():
                dict[first_word][second_word]\
                    = 1.0 * dict[first_word][second_word] / sum_value
        # self.pp(dict)
        return dict

    def split_to_words(self,string):
        """
        Split target string by MeCab.

        Arg string must be unicode.

        [Args]
        (unicode) string: Japanese string.

        [Return]
        (list((unicode),(unicode),(unicode),(unicode)))
        words = [
          (word1 surface, word1 pos-tag, normalized word1, yomi of word1),
          (word2 surface, word2 pos-tag, normalized word2, yomi of word2),
          ...
        ]
        """
        string = string.encode("utf-8")
        m = MeCab.Tagger("-Ochasen")
        # If reprace                                                                           
        #   string
        # to
        #   StringEncoder.to_unicode(string).encode("utf-8"),
        # node.surface return crazy values. 
        # This reason is by Garbage collection
        node = m.parseToNode(string)
        result = []
        while node:
            surface = node.surface.decode('utf-8')
            features = node.feature.decode('utf-8').split(u",")
            pos = features[0]
            normalized = features[6]
            yomi = features[7]
            if normalized == u"*":
                normalized = node.surface.decode('utf-8')
            result.append(
                (
                    surface,
                    pos,
                    normalized,
                    yomi
                    )
                )
            node = node.next
        return result
    
    def dump_splitted_text(self):
        """
        Dump splitted text data by cPickle.
        """
        data = self.get_tweets()
        f = open(self.dump_path + 'tweet.pkl','wb')
        pickle.dump(data,f)
        return

    def load_splitted_text(self):
        """
        Load splitted text data by cPickle.

        [Return]
        (list((unicode),(unicode),(unicode),(unicode)))
        words = [
          (word1 surface, word1 pos-tag, normalized word1, yomi of word1),
          (word2 surface, word2 pos-tag, normalized word2, yomi of word2),
          ...
        ]        
        """
        if os.path.exists(self.dump_path+'tweet.pkl'):
            return pickle.load(open(self.dump_path + 'tweet.pkl','rb'))
        else:
            self.dump_splitted_text()
            return pickle.load(open(self.dump_path + 'tweet.pkl','rb'))        

    def dump_yomi_bigram_word_probability(self):
        """
        Dump word yomis probability (bigram) data by cPickle.
        """
        data = self.get_yomi_bigram_word_probability()
        f = open(self.dump_path + 'probability.pkl','wb')
        pickle.dump(data,f)
        return

    def load_yomi_bigram_word_probability(self):
        """
        Load word yomis probability (bigram) data by cPickle.

        (dictionary(dictionary((unicode):(float))))
          first_word_dictionary(
            first_word1:{
              second_word1:probability1
              second_word2:probability2
              ...
              # sum(probability1 ... n) nearly equal 1
            }
            first_word2:{
              second_word1:count1
              second_word2:count2
            }
            ...
          )
        """
        if os.path.exists(self.dump_path+'probability.pkl'):
            return pickle.load(open(self.dump_path + 'probability.pkl','rb'))
        else:
            self.dump_yomi_bigram_word_probability()
            return pickle.load(open(self.dump_path + 'probability.pkl','rb'))

    # For debug...
    def pp(self,obj):
        """
        print obj with formating...

        [Args]
        (str,unicode,list,dict or etc...) obj: you want to print object. 
        """
        if isinstance(obj, list) or isinstance(obj, dict):
            orig = json.dumps(obj, indent=4)
            print eval("u'''%s'''" % orig).encode('utf-8')
        else:
            print obj

class MunouChan(object):
    """
    Munou-Chan is chaos from our lab's.
    
    She always talks by Katakana (but sometimes uses odd symbol).
    She is based on markov Model.
    """
    def __init__(self,display = True):
        """
        For initialize. Load yomi bigram data.

        [Args]
        (bool) display: Use character LCD or not
          If you use Raspberry pi having Character LCD(HD44780),
            You should set True (But must be run root user by sudo).
        """
        tp = TweetsParser()
        self.dict = tp.load_yomi_bigram_word_probability()
        self.display = display
        if display == True:
            self.lcd = lcd.HD44780()
            self.jp_char = lcd.JapaneseCharacter()
        return

    def create_string(self,max_lenght = 32):
        """
        Create string (If it over limit, return False).
        
        [Args]
        (int) max_length: If over this length, return False.
        
        [Return]
        (unicode or bool) string (under max_length) or False.
        """
        word = u'[start]'
        words_list = []
        while True:
            word = self.choose_word(word)
            if word == u'[end]':
                break
            else:
                words_list.append(word)
        string = u' '.join(words_list)
        if len(string) > max_lenght:
            return False
        else:
            return string

    def choose_word(self,word):
        """
        Choose word based on markov Model in dictionary.

        [Args]
        (unicode) word: target word.
       
        [Return]
        (unicode) next word.
        """
        # Define 0~1 probability values
        second_words_dict = self.dict[word]
        s = 0
        l = []
        for key in second_words_dict:
            buf = second_words_dict[key]
            l.append((key,second_words_dict[key]+s))
            s += second_words_dict[key]
        # Choice word
        v = random.random()
        i = 0
        while True:
            if not i == len(l) - 1:
                if l[i][1] < v and v <= l[i+1][1]:
                    word = l[i][0]
                    break
                i += 1
            else:
                word = l[-1][0]
                break
        return word

    def output(self):
        """
        Output string.
        """
        while True:
            string = self.create_string()
            if string != False:
                if self.display == True:
                    result = self.jp_char.check_length(string)
                    if (not result == False) and (result <= 32):
                        self.lcd.string(string[:16],1)
                        self.lcd.string(string[16:],2)
                        print string
                        return
                else:
                    print string
                    return

def main():
    # How to use
    ai = MunouChan(display = True) # If use character LCD 
                                   #   else only output to stdout.
    while True:
        ai.output()
        time.sleep(30)
    return

if __name__ == '__main__':
    main()
