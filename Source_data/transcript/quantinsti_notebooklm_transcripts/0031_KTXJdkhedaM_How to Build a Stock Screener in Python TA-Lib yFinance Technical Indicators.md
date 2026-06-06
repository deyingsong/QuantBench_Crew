---
title: "How to Build a Stock Screener in Python | TA-Lib, yFinance & Technical Indicators"
video_id: "KTXJdkhedaM"
url: "https://www.youtube.com/watch?v=KTXJdkhedaM"
duration: "25:29"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# How to Build a Stock Screener in Python | TA-Lib, yFinance & Technical Indicators

[Watch on YouTube](https://www.youtube.com/watch?v=KTXJdkhedaM)

## Transcript

that this is the holy grail. I'm not
saying that at all. I'm just saying this
is a framework for you to take guidance
for. However, approach we have taken in
this framework is something worth
spending your time. Import my libraries.
Okay, I like pandas and numpy for sure.
I'm going to use javo for data ta
library which is talib library imported
as ta for my technical Hello everyone,
welcome to another tutorial. Today we
are going to understand what market
scanners are and how we can create our
own market scanner using py. So what are
market scanners? For a very long period
of time, traders especially those who
have a very wide universe of stocks.
Let's say you are a trader and you trade
anything from a pool of 200 stocks. In
these 200 stocks, you're looking for hot
opportunities. So, you don't want to go
to the market and try and look at 200
charts, intraday chart. You want to zero
in. You want to do some homework. And
also during the live market hours, you
want something to tell you that hey,
don't give your attention to each and
every stock. Put your attention in this
stock. This is hot today. This is
buzzing today, etc. So a lot of the
traders who even follow news sometimes
they follow news so that they know what
is buzzing in the market and a lot of
the traders who are using maybe not
fully algorithmic fully automated
trading systems. They are using
semi-automated trading systems. They are
using systems where the signal is
generated in a automated way as in data
is streaming and automatically your
program is generating the signals. But
once it comes to the point where you
want to take the trade, you introduce a
human element some judgment in terms of
either position sizing or for example if
it's a event day so you want to trade
more or you don't want to trade at all
or you want to trade less etc. So these
are some small judgments you can take or
if you have already got enough exposure
if you're getting a signal
simultaneously on multiple stocks then
you don't want to trade right. So you
need to make those judgments if you're
using a semi-automated algorithmic
trading system. So even in that case,
even in cases where you want to see what
is hot, what is buzzing, right? All of
those things which you want to do in
terms of improving your edge in the
market, you want to make sure you do a
lot of homework behind. And while you're
doing your homework behind it, you can
one either rely on other external
resources which show you some market
scanners, some websites, some platforms
etc. But one thing which you can do is
you can create your own market scanner.
And this is exactly what we are going to
do today. So today is about
understanding what a market scanner
looks like in the background and then
see how it presents to you something in
the front and are we going to do it
randomly with some stocks and you know
just putting in some rules no we are
going to take something very systematic
something thoughtfully put and I'm not
saying that this is the holy grail I'm
not saying that at all I'm just saying
this is a framework for you to take
guidance from. However, the approach we
have taken in this framework is
something worth spending your time. The
first step I do is I import my
libraries. Okay, I like pandas and numpy
for sure. I'm going to use javo for data
ta library which is talib library
imported as ta for my technical analysis
indicators. N lump plot.pipplot pie plot
and seed bond for visualization. I'm
also going to be using date packag next
what I'm going to do is I'm going to
take all the Dow Jones Industrial
Average tickers. Okay, so these are the
30 stocks all the tickers are here with
me in my list and I'm going to use my
YF.d download to download these
stickers. Okay, what I'm going to do is
while I download these stickers, I'm
making threads equals to true and auto
adjust which is anyway equals to true,
but I'm letting it know that this is
true. So, it's going to auto adjust the
close and I'm going to group by the
data. I'm going to use the dot group by
because I want the data for every ticker
separately. So, there will be data frame
which looks something like this. I'm
just going to show you. Okay. So we are
going to download it. It's been
downloaded. Here we go. It's done. Let's
just have a look at the data flow. So
here if I look at data.head. This is how
it looks like. Okay. So I have got CR in
this ticker. Open high low close volume
for KO for Coca-Cola. I have open high
low close volume and so on and so forth
for all my tickers. Okay. So we see this
white data frame. I'm going to use a lot
of these. I'm not going to use close
because in some other videos you may
have seen we use only the close prices.
We want the close to close returns. But
here I want something a little more.
Okay. I need the volumes as well. Let's
take a look at indicators. Our goal is
to use technical analysis indicators but
not in their raw form. You see technical
analysis indicators have two conflicting
point of views. One of the point of
views is that yes they are quantitative
in nature because they are quantified or
they are calculated from prices. They
are like a first order derivative of
price. Right? That is one way of looking
at it and the other way of looking at it
is that technical analysis indicators
are subjective in nature because
ultimately you have to read them
visually. Okay. So technical analysts
who are you know used to reading
something visually and not testing it
using Python their approach is a very
subjective and a qualitative approach
whereas what we want from it is the
quantitative approach. So we are not
going to use technical analysis
indicator in a raw home we're going to
make some modifications.
So let us understand some modifications
that are being made over here. Okay. So
the first indicator I'm going to use is
the MA50 which is the moving average 50
moving average simple moving average.
I'm going to be using this function
which I'm creating a function for this.
Okay. So what happens is that I'm going
to use my individual functions for every
indicator and then put them together so
I can create my market scan every time.
Okay. So let's begin. So M50
score. Okay. uh you can read the log
string later you can pause the video you
can code along with it we going to give
the code in the description but I want
you to go through the entire video so
you can understand this code better okay
so first we create a MA series okay so
50 moving average series obviously we're
using the TA library so TAL the
technical analysis library so TAS SMA
does the job time period is 50 and then
I have a 200 series also I'm just about
to tell you why I'm going to use moving
average 200. Okay. Then as a next set
what I'm doing is I'm using ML of T is
last. Okay. I'm going to extract the
last value of MA of T which is going to
be the end of my column. So let's say I
pulling the data. I'll apply this
function. I apply these calculations. So
the last values are the latest values of
50. Right? So moving average 50 I have
and then I have moving average 5 days
ago. Okay. So min -1 2 3 4 5. Okay. So
from today the last day another 4 days
pushed back. Okay. So 5 days ago this
was the then I have MA 200 which is my
latest MA 200 moving average 200. And
then I have my closing price is my
latest closing. Okay. So dot I lock
minus one. Now from this moving average
there are many ways I could actually
approach some quantification.
But what I have to do is I'm going to
come to a certain score. Yes, a score
which is going to show me something
between minus1 and a + one minus one
would tilt towards bearishness + one as
it if the score goes towards + one it
would show us extreme bullishness. Okay.
So I want to get a score which is bound
between minus1 and + one and I'm going
to be doing this for every indicator by
the way. Okay. So here I use a simple
logic that I'm not going to use one
logic. Okay. There could be a way I
could use any one of these logic but I
would not get a more refined answer I'm
already getting. Okay. So let's look at
so distance from MA50. So what I do is I
take a difference between the close and
the latest moving average. So the close
may be much higher than the moving
average. Right. So this will be a
positive number. So close be higher than
the 50 moving average which obviously
gives us the undertone understanding
that something is bullish. Something is
broadly speaking bullish. Right? I
divide it by 50. Right? So I hit some
sort of a ratio. So the difference
between the close and the moving average
and then dividing it by M50, right?
Again all of this is illustrative but I
have put some decent level of heart and
have transferred some decent level of
understanding within this code which
could be something close to the line of
thinking an analyst needs to have. Okay,
exactly like the analyst needs to have.
Now again all this thing which you see
I'm doing is obviously quantitative in
nature what a quantitative researcher
does but there could be more behind
this. There would be a lot of more
testing, a lot more creation of
distributions, signals etc. But
ultimately quantitative researcher would
come up with certain unique ideas like
this. So I want you not to just take
this directly and use it. If you want
you can but you know you need to test it
properly but I want you to take the
framework the approach and the depth
behind this. Okay. So now I take this
ratio right I have a ratio which is
called dist and I create a discore score
okay now if the disc underscore score is
basically a large number okay if the
close is way higher than the 50 moving
average then it will restrict itself to
the minimum of one on that large number
okay now this is something I have just
put over here but if you look at it
closely in most cases you will see right
if the there's a difference between the
close and moving average it will not go
beyond this it should not go all the way
to one okay so but this is something I
used as standard just to make sure
everything is cap between one and minus
one so now I have got the minimum of
this to one so highest it can go to is
one and now the maximum of minus one or
this so in case the number is really
really small right that means the closer
is way below the moving average then
this could be a negative number and the
minimum of it would be actually that
negative right and that negative number
should not go beyond minus one per se
but yes in that case it will take minus1
the maximum right so this is how it will
be bound right and then now as the next
step I'm going to take the slope this
slope between the moving average and the
50 moving average 5 days ago divided by
the 50 moving average. So this will give
me an angle if if the angle is actually
very steep that it will tend towards you
know a higher number whereas if the
angle is small it will tend towards a
lower number. Okay. So I'm going to take
this slope and I'm going to scale it for
the range because the slope is basically
going to give me a small ratio. I'm
going to multiply it by five. Right? And
then I'm going to use a slope score. I
again use the same approach over here as
I did earlier to keep it bound between
minus1 and + one. Right? And then I
check the long-term regime. Okay? Now
the long-term regime is going to give me
a minus1 or + one as in if the 50 moving
average is greater than the 200 moving
average. Okay. So I store it in
somewhere something called regime a
variable called regime. Right? The score
which I finally create is going to use
0.5 weights of the disc score 3 weights
of the slope score and 2 weights of the
regime. Okay, all of it is going to be
returned ultimately to B and again it is
bound between minus1 and one. So what
have we learned? We have learned that we
get to something beyond a raw indicator.
Okay, so we can use multiple ideas and
approaches to understand the scent of
the trend. For example, the distance
from the close would show us how the
overall trend is. Whereas the slope
would give me an understanding of the
immediate movement, the immediate
momentum and then the regime would give
me again an understanding of the
long-term momentum. Okay. So all of this
put together I come to a score, right?
And this is going to lead me somewhere
to a stock which is either very bullish
or very bearish or at least giving a
score or and if the score is very high
and this kind of stock is quite bullish
from this course's perspective. Okay. So
this is what we do with moving average
then we have something called RSI score.
Now RSI momentum sounds a little
counterintuitive because a lot of people
use RSI to see the overbought and
oversold zones. And what happens is that
no RSI not just limited to overbought
and oversold. They can be used for
momentum as well. While a lot of things
again are subjective in nature, what we
need to understand is that RSI chain can
be looked into. Okay. So I created a
series of RSI D which is the difference
of RSI from its previous RSI and my goal
is similar to get to a score which is
either minus one or plus one. Okay. Then
I take the change of the RSI the last
change which is the last dependence from
this RSI change variable right from the
series I take the last figure along I'm
going to look at the standard deviation
of RSI change. So how much actually
changes on daily basis and then come to
a standard deviation I'm going to look
at the standard deviation of RSI changes
and how much RSI changes on regular
basis. I have my standard deviation of
the regular changes in RSI and then I
have the large change in RSI. I can
compare the two. So what I will do is I
will use change divided by two into the
standard deviation. Right? So change
could be positive or negative divided by
two into the standard deviation. So if
the change is positive and it's a high
number it will go close to one other it
will go close to minus one. This is how
I get my RSI score. So I use my second
indicator got my RSI code as well. Okay.
Now I have saved this particular
function. Lastly I get a volume score.
Okay. Now the trick with volumes is now
when it comes to volumes you have got a
saw which is going up and there is
higher volume the spike in volume or a
sudden volume which you have not seen in
many days. That shows that the market
participants are quite quite interested
in the stock and the stock has gone
strongly up. That means a lot of market
participates have participated in. Okay.
And that's a very bullish sign that's
supporting the bullishness so to speak.
But if you look at the downside, if the
market is going down, it's really
falling. It's crashing and there are
high volumes. Again, it is a bearish
thing because what happens is a lot of
lot of the market participants are
actually participating in the downfall
and are selling aggressively. Obviously
if somebody is selling, somebody is
buying as well. But there means there's
a lot of activity. High volumes means
high activity which is supportive of a
large market movement be it upside or
the downside. So the trick over here is
that if I get a high volume and
everything else is bearish, my volume
score needs to go negative. And if I get
a high volume and everything is bullish,
my volume score needs to go positive.
Okay. So here I'm going to modify the
volume in such a way that I come to a
score and I get something in the range
of minus one and one. In this way what
happens is I get a holistic idea of
volume without the fact that it is you
know mostly unilateral or the good thing
behind volume or the strength behind
volume is something which goes on the
positive side. Okay. So I use something
for that. I use calculations for that. I
use ideas for that. Right? So I've got
average volume right. So first I take
the average volume with a certain look
back period and the look back window
which I have taken over here for volume
is 20. Okay. So this is look back. This
is by default 20. You can change it
later. That's okay. And there's nothing
else look back trend which I will be
using in a bit. Okay. So I've got my
average volume. I take the last value.
So this is my average last average of 20
days volumes. Then I have the current
volume. Okay. So lefer volume is do I
look minus one. So what does this mean?
This means that when I have my last
volume, I'm going to use this as the
current volume. Okay? I create a ratio
of this, right? And the ratio of this
would be current volume divided by the
average volume. Okay? So it is going to
lead me to a number and this number can
obviously be greater than one. Okay. So
if that volume is spiking like crazy,
it's like 50 times of what it has done
average. So number will obviously be
greater than one. That time I need to
cap at one. You must be noticing that
I'm not using a minus one capping over
here. Right? Because volumes can cannot
go negative. Volumes can only go
positive. Right? So we're going to take
care of that part. Now I used introduce
something called a trend sign. A trend
sign. Okay? So this trend sign is going
to be either plus one or minus one. this
there are many approaches I could use. I
could compare the high with the previous
X days high. I could compare the low
with the previous X day low etc. But to
keep things simple I've used the close.
So the current close is actually higher
than the previous close. My trend sign
is one. That means things are bullish.
So on the other hand my trend sign
becomes minus one if the current close
is less than the previous close. Okay.
So what ultimately happens is I multiply
my ratio with the trend side and I get a
score for the volume. Okay, I get the
score, right? So finally I get my score
volume which is my ratio multiplied by
the trend side. So if the trend sign is
negative my higher volumes point towards
a minus one. If the trend sign is
positive my higher volumes point towards
a min a plus one. So again that is
something good. Now let us compute
scores for all the tickers. So what
happens is that I use my empty list for
results. Right? In this empty list I'm
going to append something. I'm going to
pass you know a for loop. I'm going to
append something right. I'm going to use
a for loop right and for ticker and
tickers that means through every ticker
in my data frame I'm going to look and
extract that part once. I'm going to be
using clone add volumes as I told
earlier. Drop any drop the nan values of
any right because that needs to be done.
Then I create something called result a
dictionary which will have my ticker
which will have my M of T score which my
RSI score and my volume score. As I
create these basically this dictionary
as I create each and every column
because this dictionary is going to
become a data frame later. I'm going to
use my function n lf50
scorecore
momentum volume score. Right? So I'm
going to be using all of that and you
can see that in the end I'm going to
have something called result which is
going to make total result which will
also be appended in result. Right? So
I've got my results.append append find I
get result and I'm going to create this
into a data frame which I'll call
scanner_df
okay so now that I have run all of this
not this yeah now let me run all of this
now okay it says m not defined I forgot
to run this let me run this yeah now let
me run this for loop and here we go I
have got my scores so I have got applegn
ba all these stickers
along with uh I've got the various
scores, right? So I've got MA50 score,
SI score, volume score, final score,
fire score is obviously going to be the
average of these scores, right? So I can
see on the top how the scores look like.
I'm going to see it in details. So let's
see it in details like all the tickers,
right? So we have 30 tickers. I should
be getting three rows and we can see
that the final score row which is
basically this row can have some big
numbers closer to one or closer to minus
one. Okay, this looks interesting. Now
obviously it depends on the market day.
I'm looking at the latest market day. So
from that point of view it's fine. I'm
going to just take it how it is right
and then maybe in your own time what you
can do is I can go you can go back to a
previous market day which was very
bullish or very bearish and you can see
how this behaved. Right? Now I visualize
these scores in a bar plot. Okay. So
this plot will give me numbers close to
+ one and minus one. You can see all
these stickers. You can visualize this.
So if I see something way beyond 6 78
that means a lot of bullishness is
there. Extreme ones are extremely
bearish. Okay. Now now let's use this to
come to a heat map. Okay. Now this is
very interesting. Again the heat map
over here is scaled to the maximum the
lowest and the highest code in this
particular data frame which we have. So
we can see the worst performing stock
and the best performing stock. I'll see
the current momentum. see what is hot
basically. So this is the purpose right.
So let's say AMGN is something I want to
check out. AMGN and I've taken the
latest day of the market. So basically
this is AMGN. If I look closely then on
the RSI front must be some action and
and you know I'm not going to go to the
math behind it because I have to really
go back into the function but what I can
see is a strong t uptick in volume as
well. So overall if this has shown me
green and this shows that there's
current momentum in the strong in the
end of the day then this scal is
actually giving me a proper signal. Okay
I wouldn't call it a signal to trade but
a a signal of momentum. Okay on the
other hand let's see the worst
performing stock maybe we can look at
MSFT Microsoft or IBM. So this gives me
understand that something should be
trending over here. So yes the stocks
this stock has fallen IBM and then let's
look at Microsoft and this shows kind of
looks bearish as well in terms of how it
has fallen and I'm not sure about the
volume but at least within this minus1
and plus one it has some score right so
if I look at Microsoft what is the score
of Microsoft roughly it's it's like the
worst right slightly more than minus.6
It's it's not not as bad as it could be
but it is bad at least for today it's
the worst performing stock like from my
momentum signal point of view okay so
what is this there are a lot of
inferences that can come from here which
are subjective here I've just done not
tail to check the last state okay anyway
so there are a lot of inferences that
can come here and a lot of them can be
subjective so I leave that to your
interpretation and your testing you can
go back to various different market
phrases and you can check out how this
channel is responding to market data.
Okay. And this is something which you
can use as a framework to come up with
more ideas of your own. And just like I
have come up with a final score, you
could also come up with a scalar where
you are coming with a momentum score or
some other kind of score. So stay with
the logic and experiment. Bye-bye. Take
care.
[Music]
[Applause]
