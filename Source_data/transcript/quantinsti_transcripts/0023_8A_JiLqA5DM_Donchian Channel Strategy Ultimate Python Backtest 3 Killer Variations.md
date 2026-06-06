---
title: "Donchian Channel Strategy: Ultimate Python Backtest & 3 Killer Variations"
video_id: "8A_JiLqA5DM"
url: "https://www.youtube.com/watch?v=8A_JiLqA5DM"
duration: "38:50"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Donchian Channel Strategy: Ultimate Python Backtest & 3 Killer Variations

[Watch on YouTube](https://www.youtube.com/watch?v=8A_JiLqA5DM)

## Transcript

This is for you to train your mind to
think in different ways, experiment in
different ways, innovate in different
ways. So wherever there's a difference
between the positions when there's
ongoing position of things being closed
or if there's no position and a fresh
position is being taken in those cases,
the difference between these position
columns would be one. Now uh using this
position calling and using my close to
close returns and aligning positioning
with the connect close to close returns.
I can see that I get this strategy gross
returns. Perfect. Now comes the
important part transaction cost which is
our notorious something that can break
or make a strategy. All right. So here
we have got the turnover method which
we're going to use to compute the
transaction cost. For that first we need
to compute wherever there is a change in
the position. So as I said we go flat
first we go from 0 to one uh then we go
from 1 to 0 or 1 to minus1.
Hello everyone welcome to the channel I
am walk and today we are going to talk
about the donen channel trading
strategy. So this trading strategy is
very interesting because it's find its
roots or it's find its fame rather in
the total trading strategy and these
turtle traders maybe you've heard about
them maybe you've not heard about them
but I'm pretty sure if you are in the
world of trading and algorithmic trading
you must have heard about the turtle
traders now the turtle trading strategy
from which the turtle traders made
millions of dollars had at its heart and
soul called the Donin channel strategy.
Now this Donian channel was developed by
somebody called Richard Donian and he
was famously known for trend following.
Okay. So this is a trend following
strategy. In front of your screen as you
can see this looks like three channels
very similar to Ballinger bands but
trust me it is not at all similar to
Ballinger band. It's something totally
different. Okay. So we're going to
understand this particular indicator.
Then we're not going to just code one,
not even two, but three different back
tests. And these are going to be just
three variations of uh strategy which
we're going to try out and then we are
going to compare it across different
asset classes. All right. So stay with
me. Before we get into the code, let us
understand what this is about. So
friends, the donian channel indicator is
about having these three upper, middle
and lower channel. Okay. Now these
different channels what are they trying
to show us and how do we calculate them.
So by default there is a look back
window. Okay. And in general it is if
you see generator chatting platforms by
default have 20 as the look at look back
window and this look back window is
nothing but the last 20 periods. All
right. So in the last 20 periods first
let's focus on the upper channel okay
the last 20 periods whatever the high
was this becomes the upper channel right
and over here if you notice that since
price is continuously making new highs
the upper channel kind of gets pushed
kind of gets pushed right but overall in
a downtrending market when the market
actually does not make new highs rather
it makes new lows the upper channel
remains static like over here. Okay.
Similarly, the downward channel is
associated within last X days or last N
days lows. Okay. So, the last N days
would be the default uh 20 period on
this chart. But we can play around with
this parameter. So, the look back window
being 20. In the last 20 periods, this
was the lowest low. So, that don lower
channel sets itself over here. And as
you can see, it says that no new lows
made. You can see this is pretty much
static over here. And in a downward
phase of the market, a downtrending
market, you can see it is pushing down,
down, and down. All right. Now, let's
come to the middle channel. The middle
channel is nothing but the average of
these two channels. Okay. So, this is
basically trying to show us something.
Every indicator comes with a message,
right? Now, there are volatility
indicators like Ballinger bands.
uh there are trend following indicators
like moving averages and there are even
momentum indicators like RSI. Well, this
comes under the category of a trend
following indicator. Why? Even though it
looks like Ballinger Bank is actually a
trend following indicator because it
clearly follows the trend and it is
built upon the very essence of a trend.
The very essence of a trend is in an
uptrend there are higher highs and in
the downtrend there are the lower lows.
Also one of the reasons why I took this
strategy is because this follows the
very basics of trend following. Okay.
Now moving ahead step by step with how
we would enter and exit. Now that you've
understood how this is placed, the more
intuitive or the most logical thing
seems like let's say let's enter when
the upper channel is broken, let's enter
into a long position or when the lower
channel is broken, let's enter into the
short position. Okay, that is the
general intuition. But when we want to
code the strategy, we want to be highly
accurate. We want to understand the
various aspects which our eyes cannot
easily see. Okay. So I'm just going to
lay out some rules while we go come back
to this chart later. Let's do everything
on the code for now. All right. So let
us get to the Jupyter notebook.
Now before going into the back test, let
us understand how we can visualize this
on Python using this Jupyter notebook.
So I have this code script with me which
is already written. I'm going to explain
some of the important bits and this is
going to be something you can actually
get access to. Just go and check the
description box below. So first thing
first, we're going to import our
libraries. I'm going to be using our
finance to download the data. I'm going
to be using plot league to plot the data
and visualize it. Okay. So this is done.
I created this one little function in
order to actually download the data
which is pretty much simple over here.
All right. Now as we go ahead uh let me
just download the data and show it to
you. Now this is the data we are
downloading for the last approximately
10 years of the S&P 500. Okay. So spyat
of data is here and we have our data
head where we can see clearly we've got
the open high low close and volume data.
Perfect. Now moving on in order to
create this don visualization I'll be
using plot l. I'm not going to the every
detail of every code line over here.
What I'm going to understand is that in
order to create these channels in this
data frame, I use this data frame and I
created some more columns in this data
frame. One of the important things to
know over here is that when we saw the
chart on the charting platform, you
would have not seen that any particular
line is crossing the torch channel from
the upward downward direction. uh when
it comes to the upper channel or the
lower channel. But when I run this the
visualization from this particular
Python code script uh you will now see
how the don channel actually looks like
and this is about to yeah over here. So
the down channel over here looks
somewhat similar but there's a slight
difference that there are places where
the close actually goes above the upper
channel or in some cases where there's a
market uh which is a downtrending
market. You would see the close go below
the lower channel. Okay. Now this is not
something which is saw in the chart
previous to this. But the reason why I
have plotted it like that and how I
plotted it like that is something you
need to know. So if I'm trading today
okay generally what I would do is I
would look at the data which I already
have and I would not account for the
data which I'm going to have by the end
of the day. Okay. So in general
when you're looking at any indicator it
is highly advisable to not have any kind
of look ahead bias. So over here where
I'm looking at this particular indicator
what I'm going to look at is the last 20
days high or the last 20 days low. Now
for the upper channel for example I want
to use the dot rolling and this channel
window is 20 assigned 20 to it dot max.
So this is the highest in the last 20
days the column high column. Okay so the
highest time in the last 20 days but I
have shift one over here. This shift fun
is actually to move the column one day
back and actually associate it with the
previous days last 20 days high. Okay.
So we don't have any local buys. Okay.
This would be highly applicable in
certain style of strategies. Maybe
exactly not with the ones which are
going to try today but this is in
general very much applicable in strategy
band testing. All right. So now that we
have un understood this code uh and then
we understood that the middle band being
an average of the two what we can check
out is how the data looks like. All
right. So this is how the launcher
channels look like. Not going to spend
too much time over here. This is
something which we have already seen. So
let dive into the back test code. Let's
understand the rules etc.
So what we're going to do is we're going
to start with one baseline strategy and
in the next step we are going to move to
two variations or two variants of the
same strategy and why the same strategy
because all of them are going to use the
nonchain channel indicator. All right.
So uh before I go into the rules, let me
run you through some of the functions
which I created which are going to be
used again and again by me. Okay. So
first I import my various libraries.
This is something we already did. Then I
have one function which I created
download the data. All right. Now to
download the data I will use sticker as
the variable for the ticker symbol. I'll
be using our finance and then I have
this start date, end date etc. Moving
on, inside this function I calculate two
other things so I don't have to
calculate it later. One is the 200
period moving average and second is the
close to close return. All right. So
return CC or RD CC is basically DF close
dot percentage change. All right. So
this is sorted. Now moving on.
So this is one function which helps me
plot the strategy cumulative returns.
All right. Now over here as you can see
I have commented out a certain part
which is the buy and hold returns part.
So we're going to uncomment it and check
out how this looks like as well. But by
and large this function is something
which we're going to use at the end of
every strategy to see how our equity
curve looks like. Perfect. Now we have
the metrics table. Again this is going
to be reused again and again again after
every strategy which is going to lay out
the various metrics like the annualized
return the annualized one the sharp
ratio the maximum draw down of the
strategy. So this is something which we
need to uh be aware of. This is our
strategy evaluation and it is going to
be used again and again therefore a
function right. So these are just basic
calculation of analyze return analyze
volatility etc. I wish you can just go
and see it for yourself by accessing the
code. All right moving on. So run these.
No I have not done this. So let me just
run these. Therefore these functions get
saved in publish here. Perfect. Now
let's go to the back test. All right.
Now the baseline strategy the longshot
strategy. All right. Now here as I said
before this is not exactly the turtle
trading strategy. All right. It is not
using those position sizing rules exact
entry exact rules but it is a sort of
adaptation or some something which we
have borrowed uh the den channel the
entries and exit part. Okay. So in this
case at the very baseline level we have
four different points. the long entry
point, the short entry point, the exit
long and the exit short point. So why
are these four different? You must be
thinking that up till now you saw like
the upper channel, the middle channel
and lower channel. So let me tell you
this that in this case one of the things
which we're going to experiment with is
that we take a different look back
window for entry and we take a different
look back window for an exit. Okay. So
when you take a look back window for an
entry which is of a higher time frame.
So for example we're going to take the
example of 40 being our entry window.
What happens is when the last 40 days
high is crossed then uh the strategy
goes low right then we could law
according to the strategy rules and if
uh it keeps going up well and good but
then if you look at the last 40 days
lower channel is going to be quite a
wide difference and maybe we don't want
that maybe we want to keep our equity
curve smooth by keeping our stop losses
a bit limited So what we will do in
those cases is we will take a smaller
period for the exit value. Now this is
something you can always experiment with
because in the back test this is
something which is funible. This is
something which you can try out and
optimize but at this point the logic is
something which you need to understand.
Okay. So the entry window can be
different. The exit window can be
different. Secondly, in this particular
strategy, one important part is that
once you go long,
then you first exit the trade. It is not
the kind of a strategy which is
perpetually long or short. This is
something which many of you may not be
familiar with. Okay. So depending on the
path of the price if first position
which is initiated is a short position
and then regardless of where the market
goes regardless of the profit or loss
the moment our exit short comes in when
that signal comes in we simply flatten
the position. So from the position being
minus one it first goes to zero before
it goes to + one if at all. And
similarly if the position is a long
position the first thing which you do is
if you have position one which is the
long position when you exit the long it
flattens and becomes zero and then you
go and take a short position later if
you get a signal. So at any given point
in time we are not flipping the trade
entirely. We are going to first flatten
the position. So that is an important
note uh which we have made over here and
then trades which are executed at the
close of the day. Now secondly the what
we're going to do is we're going to take
a trade at the close of the day. Okay
here in your long entry long exit we can
see that a long position is opened when
the closing price moves above the top
bar. So we are not looking for higher
highs but we looking for a close above
the highest high. Similarly for the
downside we're not looking for lower
lows only we are looking for the close
which is below torch. Okay. So
everything is happening at the close
over here and even the exit is happening
on the close. All right. So we're
keeping this part a bit simple right.
Obviously you can go and check out some
variations uh put your brains and I
would highly encourage you to do that.
But these are the rules for us today.
Well, as far as that based on I
encourage you to do that but for now
these are the rules for us uh the
baseline long short channel strategy.
Okay. Now let's get into the back test
code. For this I have created a function
and in that function the first thing I
have defined is all these various
channels. Okay. We're doing nothing with
the middle channel over here. So here I
have not really coded anything for the
middle channel but we do have two
different windows. One is the look back
window for entry and one is look back
window for exit. And for that reason
what I'm doing doing over here is that I
have a upper entry okay which is
associated with the entry window and
then the upper exit is associated with
the exit window and vice versa for the
short position where we have the lower
entry for that with the entry window and
the lower exit with the exit window.
Okay. Now this is something which we
will experiment with when we call this
function and you will see and get more
clarity. Okay. Now obviously we need our
signals the long entry the short entry
the long exit and short exit and then we
create a panda series called positions.
Okay. Now this position I'll come back
to this band later. This position gets
its value through this for loop which
we're going to write. And in this for
loop we're going to check according to
the path of the brakes as to where is
there a signal. So if there is a signal
at all then we take a trade. So if there
is no position currently and there is a
fresh signal that comes in that is where
we take a trade. So this is from where
it is going to check that if the
previous position is zero then we take
the long entry and we make position
equals 1.
Otherwise if there's a short entry then
remain to position minus one otherwise
we let it remain zero. Okay. Now this is
the entry condition. Now the exit
condition in this case where the
previous position equals 1. If the long
exit occurs the position becomes zero
otherwise it continues being one. In
case there's a position with minus one
so there's a short position. If there's
a short exit then it goes back to zero
otherwise it continues being minus one.
All right. Now this previous position is
something which I told you I'll come
back to. So this previous position is
basically I -1. So depending on when
we're looking at we look back one period
in one row back in the data frame and we
see I minus one. uh if that position is
zero then previous position becomes zero
and if it is one it becomes one if it is
minus one it becomes minus y now in this
very first little block what I'm doing
is I'm checking if this is the first row
so if it is the first row then I
actually break out of this loop and
continue with the next iteration now
that I've assigned various different
positions at various places according to
my strategy rules what I'm going to do
is I'm going to create a condom called
positions which is going to actually
mean these positions itself. So now my
data frame has kind of expanded from
where I began. So we begin with uh just
the open high low close and uh returns
and now we also have the various dungeon
channels and then we also have this
position calling. All right. Now uh
using this position calling I'm using my
close to close returns and aligning
positioning with the correct close to
close returns. I can see that I get the
strategy gross returns. Perfect. Now
comes the important part transaction
cost which is our notorious something
that can break or make a strategy. All
right. So here we have got the turnover
method which we're going to use to
compute the transaction cost. For that
first we need to compute wherever there
is a change in the position. So as I
said we go flat first we go from 0 to
one uh then we go from one to zero or
one to minus one is something we non
jumped right. So wherever there's a
difference between the positions when
there's ongoing position which is being
closed or if there's no position and a
fresh position is being taken in those
cases the difference between these
position columns would be one. So what I
can do is in order to actually calculate
the to turn over would I would simply
see the absolute difference. So from
minus1 to 0 or 0 to minus1 or vice versa
all of those would be one and the rest
of the other rest of the non columns
will be zeros. So I have got my turnover
column. Perfect. I simply multiply this
turnover column with my transaction cost
which is my TC over here. So the
transaction cost is something which I
input in the function and here I've got
my transaction cost multiplying by the
turnover. Now this will be subtracted
from my gross returns I'm going to get
my net returns.
So the next thing is to find the
cumulative returns which I do 1 + net
returns dot compro
and these are cumulative binds and then
the function returns the entire data
frame. All right. So now let's go step
by step and actually apply this
function. Let's call this function. And
for that we're going to use this code
set. So as you can see over here what is
being done over here is that I have got
my download process state. Okay. So now
this is something which I would like to
run all together. But for your better
understanding, let me just put this over
here. All right. Now this is going to
first download the data. So now my DF
looks like this.
All right. So this is something which
happened because it downloaded the now
what I'm going to I'm going to take this
second line of code and uh here
just to show you what happens when we
run them together. So this is again
getting input as DF in a data frame and
is going to get back DF for us. Now DF
has assigned the entire back test
function so to speak the back test
function is being called and DF has been
one of the parameters. All right. The
transaction cost over here we take is 10
basis points and the entry window over
here is 40. Exit window is 20. This is
experimental. You can try something else
as well. All right. Perfect. Now you
look at df.head. Now so many different
columns appear because this back
function actually expanded our data
frame. So we've got open, high, low,
close, the return column, uh, and so on
and so forth. So many other things
including our net returns and gross
returns and turnover and cumulative net
returns and so on. All right. So we have
got all these quantum. So the back test
has been done inherently. And now moving
on to plotting DF. So again I can do it
in a separate set but I just choose to
do it over here to keep it neat. Uh if
we plot the cumulative returns this is
how they appear. All right and I told
you I'm going to uncomment and show you
a comparison between the buy and hold
and the cumulative but we'll do it in a
bit. All right now moving on we tweak
the metric table to calculate and
compare between the buy and hold returns
and the strategy returns. And this is
how the metrics table looks like. All
right. So we have got uh annualized. So
this is the cumulative return in the
last 10 years which is 10% which is
barely okay. The net strategy return is
1.06%.
The annualized volatility is 16.81%.
And so on you can see the sharp ratio is
very very low and the maximum draw down
is quite not impressive. It's pretty
much I would have been better with the
buy and hold signal. Okay. Now it is not
every time important that the strategy
should actually beat the market but if
the strategy can beat the market not in
terms of return but a better sharp ratio
better risk adjusted return even that is
okay but that's not something we see
over here so let me go back and check
how the buy and hold return if I were to
uncomment that part of the function over
here as extend how would it look like
and the reason why I commented
uh commented that was because
uh the buy returns are so magnificent in
front of our strategy returns. There's
this curve looks kind of subdued. So you
can't clearly see how choppy it is. All
right. So this is buy and hold returns
versus strategy returns. So the baseline
strategy clearly is not that crazily
impressive but but we're going to try
some more periods as I had promised you.
So hey, let's go back and let's just
comment that part out for now. So later
we don't have to go back and do that. So
wait, here we go.
See, let me just run this again.
And now we go to our next particular
strategy. Sorry. So our next strategy
and I'm running this again without the
buy involved. So this is how the
strategy cumulative. SL later we're
going to try all of these out with
different instruments as well. So now
moving on one interesting idea that
comes to my mind is why not try the loss
only version of the strategy. So you see
when it comes to equity markets uh they
tend to have a long-term upward drift
mostly because equities are backed by
companies which create a long-term value
and therefore these long-term upward
drift is seen in the trend. So in such
cases many quads like to actually apply
no long strategies to certain asset
classes. Okay. So if we were to see how
the null only strategy can work on this
same scenario, we can check out by
putting it in a different way by
plugging in certain different rules. So
first we've got a long entry and we have
got a long exit after that and that's
it. There is no short entry, there is no
short exit. Everything else pretty much
remains the same. We have things based
on the closing prices. It's not above
higher high but about the highest close
above the higher high. Okay. And then we
have exit which is going to be the
close. Now this depends on the exit
window. Here again we will experiment
with 40 and 20. 40 being the entry
window and 20 being the exit window. So
you can get a fair idea that I'm going
to take only long trades. And looking
back, one thing which I can perceive is
because of this long-term upward drift
and this very strongly trending overall
uptrend in the long run, I might get
much better returns and this strategy
might prove to be slightly better. Okay.
Uh so let's see how this works and also
I will have lesser transaction costs
because I have lesser transactions now
possibly. So let's check out. Okay. So
now we have got our long only strategy.
So I'm not going into every detail of
this code but similar to what we did
last time but not having the short
position we're going to create the long
entry long exit signals and we're going
to put our position through this entire
for loop and later create a position
column and then finally create the net
returns and then finally get our gross
returns. deducting the transactional
cost, we get our net results and then
finally the cumulative strike returns.
Okay, so all of this is being done in
the bank test and here again and now
this time I'm learning all the functions
together. I've got the same data set,
the same transaction cost of 10 basis
points and I have got
our exit window and entry window to be
the exact same as well. Now the only
difference is that this strategy is long
old whereas the previous one was long
short. Perfect. Now let's see the
cumulative return is 7.81%.
Which is actually much much much better
and much smoother than this 10.03%.
So over a 10 year 10 year period we got
72.8%
return and the annualized return becomes
6.25. Okay. Now looking at these metrics
again it's not just about the red and it
is also about the sharp ratio. The sharp
ratio seemingly doesn't improve a lot
but one thing which has drastically gone
down is the maximum draw down. So the
maximum draw down had you hand on the
trade using the buy and hold returns
would be 33.72%.
But if you applied this strategy you
would have a lesser maximum order of
about 27.29%.
So by and large I see that there is some
needle movement. There's something
better I got out of this
experimentation.
I therefore I want to try something else
now. So now time for the next variant.
In the next variant what I'm going to do
is I'm going to take a long
strategy and add a 200 moving average
filter. Moving averages are another
trend indicator. But when it comes to
the 200 period moving average, it is a
trend indicator but it is something
which you associate with a very
long-term price movement. So in this
case what I do is I keep everything else
the same as the previous variant. That
means everything is long only. But I
have one additional condition over here
is that before taking entry with the
entry signal, we got to check that if
the price has closed above the 200
moving average as well or not. Okay, in
order to do that I keep everything same.
And this side one extend thing which I
do is first I obviously pull into 200
moving average for my data frame and
also I use this condition called MAC
okay. So if this condition is okay we
will actually take this signal. So our
long entry signal has this extra amper
and and then the ma okay which means if
these two of the conditions meet then
this is one then the signal is true.
Okay. And therefore this MA_OP is a
symbol close above the 200 period moving
average. Perfect. So this is our back
test as usual and not getting too deep
into it. But let's run this all these
options together. And this time we have
the 200 back test partial. So while
running this together and get some other
first just run this
here I get 61.29. 29% cumulative returns
I get annualized return of 5.44% I get a
maximum draw down 31.2% 2% IO so I see
nothing improving not the maximum draw
out I don't see the sharp ratio
improving either uh I don't see I mean
the sharp ratio over here was about 67
so it's actually gone down and therefore
it seems like uh the only thing which
slightly improved is the annualized
modality which was earlier 9.31%
and now is 9.15%.
So by and large this is actually not
giving me any extra results. In fact, it
is shaving off 10% of the cumulative
gwise getting. So I would not actually
really look so happily or
enthusiastically into the results of
this strategy. But but what if I tried
different instrument from different
asset classes perhaps. So let's try
something else. So now that we have
completed all our back tests, I created
this function over here to compare the
different strategies. Okay,
this function simply takes a dictionary
of the various alerts and gives me back
a particular table which neatly plots on
the various strategy metrics. Okay, now
which neatly plots on the return
metrics.
So now what I'm going to do is I'm going
to try it with different stocks. All
right. So here I have made all these
various inputs consistent and you could
try with different entry like windows
and whatnot. That's completely up to
you. But let's try with the stock Apple.
Okay. Many of you have your favorite
stocks Apple, Tesla and whatn not like
some people like bitcoins also etc. So
depending on the one of the asset
depending on the nature of the movement
of price or the long run you probably
can see different results compared to
what we saw with S&P. Okay. So what I'm
going to show over here is that we're
going to keep these parameters and then
we're going to keep this as our last 10
years of data. So art ticker is happen.
So let me just run this now. Run this.
And now we have all these three
different back tests which are over
here. And from here we get all the
various metrics. Okay. So let's run
this. And finally our comparison table
is ready which gives me a clear
comparison of the three different
variants for Apple stock. Okay. So for
the stock Apple if I look at the low
short strategy I get a mere 2.68%. 68%
arrowized return and I get a heavy
maximum cuto off. But if I shift to the
long only strategy, I see a 21.75% draw
down which is much much much lesser and
I see a sharp ratio which is above one
which is a bit impressive at this stage.
Okay. And if I look at the annualized
volatility, it has gone down
significantly. If I look the analyzed
return, it has gone up significantly. So
all this is pretty good. And if I put
the 200 moving average trader, I see
that I get obviously a significant
lesser draw down than the long shot
strategy. And I see a pretty decent
sharp ratio, but I don't see a higher
return, higher annualized return. That's
for sure. And that's okay. Let's try
some other stock and we can try Tesla.
For that's we can see that uh for the
various different variants we have the
ionized return for long shot is pathetic
with 4%. But if you go for the 20 200 MA
filter you see your highest annualized
return at 30.84%.
Okay. And these are very close to each
other. Okay. But one important thing is
that a long shot strategy would have
almost 80% draw down. Whereas in both
the other two casings you have about 57
and 53% not okay. Uh the sharp ratio has
improved significantly by going long and
having the 200 MA filter. Okay. And
obviously I could experiment a little
more. So I just taking one very volatile
asset class which is basically BTC USD.
And then if I test over here, I see that
the returns are actually significantly
improving. Uh and first the sharp ratio
above one again. So now let's try
Microsoft as well. So one thing which I
see uh with Microsoft is again a very
improved sharp ratio with the last
strategy and a better annualized turn
compared to the longshot strategy. Much
lesser maximum draw down. So I see some
needle movement by adding these
different layers above our baseline
strategy. Also if I look back I think
the more volatile the assets are and the
more long-term upward trend they're
showing then they tend to show a much
better returns obviously because we're
looking at a law only strategy. So the
purpose of this approach in this
tutorial is clearly to make you
understand how you can think in
different perspectives as a quantitative
strategist as a systematic trader. All
right. This is not at all any kind of a
recommendation. Not at all. This is for
you to train your mind to think in
different ways, experiment in different
ways, innovate in different ways. So if
you have some other idea, you try out
that idea with a baseline level strategy
and then add some layers, add some
filters, add some variants and
experiment across different asset
classes and different instruments as to
what the results and the metrics look
like. So this was it. I'll see you in
another video. Thank you. Bye-bye.
