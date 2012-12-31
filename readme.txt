Author : Salniger
Date   : 01/14/2013
Version: 1.0.0


This is Chatterbot(人工無脳) on Raspberry Pi.
If you connect Character LCD (compatible HD44780), you can get output on LCD
(If you use LCD, please read lcd.py too).


Dependence:
Please install these modules.
  RPI.GPIO (If you use LCD)
  simplejson
  MeCab


How to use:
1. If you run on your PC (not Raspberry Pi),please rewrite line 371 like this.
     ai = MunouChan(display = True) => ai = MunouChan(display = False)
   And please comment out line 15.
     import lcd => # import lcd
   If run on Raspberry Pi with LCD, skip this.

2. Run this command.
[Without LCD]
$ python munou_chan.py

[On Raspberry Pi with LCD]
$ sudo python munou_chan.py


Options:
If you rewrite line 375, you can set sleep time what you want to rewrite
(Default: 30 sec.).

Now default dataset is our lab members tweets.
If you want to use other dataset, set some .tsv file under ./tweet dir.
There is a sample.tsv file in ./tweet dir. Please remove before run this.
Next, remove or rename ./probability.pkl.
After that, please run according to [How to use].
