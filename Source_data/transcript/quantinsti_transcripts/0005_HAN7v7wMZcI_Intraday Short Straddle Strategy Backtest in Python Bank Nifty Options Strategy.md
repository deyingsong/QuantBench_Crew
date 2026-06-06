---
title: "Intraday Short Straddle Strategy Backtest in Python | Bank Nifty Options Strategy"
video_id: "HAN7v7wMZcI"
url: "https://www.youtube.com/watch?v=HAN7v7wMZcI"
duration: "24:10"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Intraday Short Straddle Strategy Backtest in Python | Bank Nifty Options Strategy

[Watch on YouTube](https://www.youtube.com/watch?v=HAN7v7wMZcI)

## Transcript

I say that spot data on this drawdown
day looks something like this.
This is a plot of the return
distribution. We see that in most cases
the profit is not very high, but
somewhere around zero or slightly above.
But then when there are losses, then
there are quite extreme losses. So we
calculate the total P&L, we calculate
the average daily P&L, the win rate, the
average win, average losses. The
drawdown as we just saw around 1,040
points.
Hello everyone.
Welcome to the YouTube channel.
My name is Mohak.
And today's session we are going to test
and analyze
how an intraday
short straddle strategy works
on Bank Nifty.
And we are going to do all this using
Python.
We have 1-minute options data.
We're going to see about the
at-the-money options.
And then we are going to understand how
this strategy works across
a number of days.
Now,
before we get into the coding,
let us understand the instrument first.
So you imagine a trading day when the
market opens and it moves in a small
range. Overall it is range bound. There
is no directional conviction and then
the market closes around that area. Now
what happens over here in such an
environment is that the option premium
tend to decay a lot and option sellers
want to capture this decay and profit
from it.
So,
that is where the short straddle
strategy clearly fits in. It gives us
the clear
opportunity or the gives us the clear
strategy to actually make money from the
opportunity of such a premium decay.
A short straddle strategy involves
selling at-the-money call option and
at-the-money put option. They should be
of the same strike, they should be of
the same expiry.
And that's it. This is a short straddle.
Now, when the market is expressing
itself in a way that the volatility
remains contained,
one tends to profit from the strategy.
However, when there is an expansion on
one direction,
then the strategy is going to lead to
losses.
Now let us understand why at the money.
Okay, even in this notebook is in this
Jupiter notebook where we test
everything, we're going to actually see
what the at-the-money options are. Why
at the money?
You see, at-the-money options contain
the highest premium.
They are typically the most liquid
options.
And they is a great sensitivity to price
movements. Okay?
So, when you enter the at-the-money
straddle, approximately both sides delta
is equal. So if the delta is 0.5 plus
for a call, it is approximately
-0.5 for a put. So when you sell both
these, what happens is that you are
delta neutral.
That means immediately there is no
directional bias. So you're not going to
lose money if there is a small
directional movement here and there.
However, this position is short gamma,
it is short Vega, and it is
long theta.
So what happens is when there is theta
decay, because of the theta decay, we
make money.
And if the volatility is low, then again
we make money.
If we had taken out-of-the-money options
instead, there would be lesser gamma
risk. They would be less the delta would
be less sensitive to changes.
But
it would also have much lesser premium.
And had we taken in-the-money option,
it would be very sensitive to any one
direction.
The at-the-money straddle therefore
provides a clean setting.
A clean setting for a pure short
volatility strategy.
What is the relationship
to volatility?
The profitability of a short straddle
strategy depends on the relationship
between the implied volatility at the
entry
and the realized volatility during the
session.
Now if the realized volatility, which is
the volatility ultimately realized by
the market movement, remains lower than
the volatility which was implied at the
beginning,
then the sellers would benefit from the
strategy.
If the realized volatility exceeds
expectations,
then losses can accumulate quickly due
to the convexity of exposure. The
interaction between volatility
and gamma
produces a very characteristic return
profile, which is frequent small gains,
occasional large losses,
and a negative skew.
So this was the conceptual foundation.
Now we move into the data
and begin constructing the strategy.
Now let's go to our Jupiter notebook and
first we set up the environment. Well,
first we need to import the important
libraries.
We have pandas, we have numpy, we put
OS.
We also import datetime
and timedelta.
We use plotly for plotting.
And then we import warnings to suppress
any warnings. So here we go. And then as
a next step, we load the 1-minute
options data set.
So I have the first quarter of 2022
options data set.
This is the path and since it is already
saved in the same folder as this Jupiter
notebook, giving out this path is going
to be enough and we'll download this
data over here. Now,
shortly as we see, uh it's going to take
a little while because there is a lot of
data. Here we go.
Now we see that there are so many so
many rows and 12 columns.
And over here,
we see we have datetime, we have date,
we have time.
And this is 1-minute data as I told you.
So,
you see, for every minute you have every
options data,
whichever option was available at that
time.
Over here,
you have the expiry column.
You have This name over here is for the
name of the underlying, which is Bank
Nifty, consistent across everywhere.
Then we have the different strike
prices. We have the option type, is it a
PE or CE? Is it a put or a call?
Then we have the open, high, low, close
of that 1-minute data. And then we have
the close at the end of every minute for
the spot data. Okay, for the underlying,
which is Bank Nifty.
So we have all these columns. Because we
do have all these columns, we also want
to make sure that we are consistent with
how we're going to work with it. So I
need a lot of datetime because I see
over here the different columns
representing date and time are object
type. They are not datetime columns.
They're not date type dtypes. So what
I'm going to do is I'm going to clean
this data a little bit and standardize
this data a little bit such that I
ultimately change the various required
columns to the datetime data type.
Once done, I'm going to see that
how my data looks like.
Observe the dtypes. I'm going to see it
here.
Perfect.
Now after converting, I see that the
required columns are now datetime
objects. Okay.
Now moving on, the data frame still
looks the same.
And now I'm going to get into the
strategy design.
We've already discussed the core idea
behind the strategy. Now let us get into
the rules.
The first rule is that, you know, the
entry of this strategy is going to be at
9:20 a.m.
We know that the market opens at 9:15.
But there's a little bit of price
discovery, there is some ad hoc
volatility, and maybe liquidity
collecting across where the market is
right now.
So we assume that the market settles
decently in the first 5 minutes.
And at 9:20, we check out what the
various at-the-money options are, as in
what is the at-the-money strike.
And once we do that, we take the
at-the-money call and we take the
at-the-money put.
And then we sell them.
So this is our entry at 9:20.
Then we talk about the exit.
Now in reality, and as I said this
before, we're going to look at the
strategy at a structural level. In
reality, there could be stop losses,
there could be some discretionary exits,
there could be some event-based exit,
maybe on a very very volatile day nobody
wants to trade also.
All that is possible. But what we are
here to test is that
if I were to use this strategy to trade
on everyday basis,
regardless of any discretionary or any
qualitative idea behind it,
and do it plainly in a way where I'm
selling options at 9:20
and exiting my short straddle at
3:15,
how would the results be? So now my exit
rule is also like that that regardless
of anything else, whatever my straddle I
charted at the beginning of the day,
at 3:15, I'm going to exit that
strategy. Okay?
There is no overnight exposure,
everything is intraday, there is no stop
loss, and no discretionary exit.
Okay.
Now at the entry, obviously I'm delta
neutral, but I'm short gamma, I'm short
Vega, and I'm positive theta. Okay?
Now let's see what exactly happens in
the coding part of things.
So here I have defined my entry time,
which is entry_time, and my exit time,
which is exit_time.
This is of the Indian change later.
And since we are not using functions
etc.
What we are simply doing is we are
putting in step-by-step.
Although testing any strategy is
generally not a linear process, it's
modular in nature.
Right now at a simplified level, we're
breaking it down into a step-by-step
process.
So if you want to run this notebook
again after changing the time just to
check things out, we'll actually have to
manually come and do it over here.
Now, here I have something on the strike
step.
Now at the beginning of the day, the
market may not be standing exactly at a
certain exact strike.
So the strike
which is the at-the-money strike may be
a few points here or there. Now, what we
want to do with Bank Nifty is that we're
going to take a nearest round figure of
100
and then choose the at-the-money strike
to be what it is. Okay?
So a simple calculation would involve
that now we have the strike step as 100,
which is my variable as defined.
What I'm going to do is first I'm going
to
change I'm going to create a data frame
called entry underscore DF.
Basically, what I'm doing is I'm taking
wherever the entry time
matches with the date and row.
So my entry time was defined as 9:20 and
now all the 9:20 data daytime column
wherever there is 9:20, all that is
being extracted over here.
Okay?
This is what all the data, all the
options. Okay, but wait.
Now,
as the next step what I'm going to do is
I'm going to check out which is the ATM
strike. So I'm going to filter this data
a little more.
Now the at-the-money strike as I earlier
discussed would be calculated using the
strike step.
We have the strike step over here.
Right?
Perfect. And we take the round figure
and then we take the nearest option
around the strike price. It gives us the
exact at-the-money strike.
So now what we are doing is we are
taking entry DF
and we are filtering out only the ATM
strike.
And this data is right over here, only
the at-the-money strikes
where we have at 9:20. Okay?
Now, as the next step we want to
construct the short straddle.
So what do we do at the entry?
We sell an at-the-money call, we sell an
at-the-money put.
This forms the short straddle, right?
Now, over here how do we do it in terms
of coding is we first create a trade
sheet, right?
Here I I have got everything which is
the data of 60 days because I'm using 60
days data.
Right?
I am using the at-the-money strike.
I'm using
the expiry of the exact same date.
And if we further construct the short
straddle, we want to pull out the
earliest expiry
and we create a data frame where this
trade sheet also has the earliest
expiry, all the options and this is data
for 60 days.
So over here if I simply just check out
the length of trade sheet,
you will see there should be exactly 60.
Okay, so I have these 60 rows where for
specifically every day because I have 60
days of data, 60 trading days of data,
every day's short straddle can be easily
seen.
Now let's go to the exit logic. We know
exit logic is that 3:15 we are going to
exactly exit the trade we took at 9:20.
Now over here if you see that what is
what is to be done is not to exactly
rush into the exit right now,
but first we do is we manipulate the
data
to create the entry straddle data frame.
Okay, when you create the entry straddle
data frame, what you are essentially
doing is you know that how much premium
you're going to collect. Right?
So you take the
call at the entry price, you take the
put at the entry price
and you sum it up
and you ultimately get the entry of the
short straddle. Okay? So over here the
CE at entry, PE at entry and the total
premium at entry is available to you in
the data frame.
Again, this has got 60 rows. So for
every single day I have got the entry
premium with me. As the next step, I
prepare my full M2M data set.
So I'm going to take my entire data. I'm
going to take every minute data and how
the option actually is performing, what
is the expiry, what is the open high low
close, what is the at-the-money strike
at that point. I'm going to take all of
that data. Now as the next step, I
filter out the data.
All the data which is beyond the entry
time and before the exit time. So from
9:15 to 9:20 where I don't have anything
to do with that data and 3:15 to 3:30
all the data I remove. I only take the
area where my strat short straddle
strategy was live. Okay?
So this helps me further filter into
lesser rows data set.
So my agenda with this data is now to
construct the correct straddle time
series.
Okay, if I am able to do that, I'm going
to take only the trade list strike and
the expiry which is necessary.
And then I'm going to see how this M2M
going to look like. So over here this
data represents my trade date, my strike
price, my at-the-money strike, the
expiry, the expiry
X and the expiry Y.
Now in the process of constructing the
straddle time series, I take a number of
steps and the code will be shared with
you so you can go through this
step-by-step. Right?
As I take the full DF M2M, I take a lot
of data which is corresponding to the
correct trade date and expiry.
And then I further build on the straddle
time series. Herein I see that the
entire straddle price needs to be
something which I need to know minute by
minute how the price change. So here I
have got 9:20, I've got 9:21,
what 9:22. So for every minute I can see
the change that is happening.
Right?
Now we add premium to each of these
trades. So we need to understand how the
premium is fluctuating.
Here I have the straddle price. As the
straddle price is changing,
I need to make sure that I have this
premium
which is the straddle price and the
premium at the entry. So this straddle
price is changing where at the entry the
price and it's consistent across the day
and once we see the difference between
the two is simply going to be the
premium at entry minus the premium
or sorry, we minus the straddle price
currently. I'm going to get the P&L.
Once I have this P&L, most of my job is
done.
So from here I take the intra intraday
P&L and I compare it with the original
entry to the final exit.
Now I have got my P&L for every single
day.
So the
entry to the final exit, what is the
difference? This is my P&L exit and
therefore I have got 60 days of data.
And as I said we're doing things as
simplified way so I'm not going minute
by minute in that case. What I'm doing
is I'm taking the P&L for every single
day.
Once I have the P&L of every single day,
I can actually see my whole equity
curve. As I said we'll be using Plotly
to plot it.
First let's find out how the daily P&L
and the drawdown looks like. We have the
daily P&L column and we have got the
drawdown column.
Now we plot the equity curve. The equity
curve which is going to show us how the
strategy has performed across time.
And one disclaimer over here is that
we've not used transaction cost.
It's going to show us the overall equity
curve as in what is the profitability at
a plain vanilla level.
So I'm waiting for the plot to come up.
Here we go. So everything over here is
not in percentage terms, we're using
absolute terms and we're using 3 months
of data so there has not been a major
move in Bank Nifty in 3 months that it
would make a lot of difference to only
use percentages. We're using the
absolute amount. The first day there was
a loss, that is why we don't start from
zero and by the end I see that I've got
some 869.4
points in profit in a matter of one
quarter. Okay? And there have been ups
and downs and some major drawdown as you
can see over here has been there. Now
important thing over here for us to see
is the drawdown curve where actually the
risk lives. So if I construct the
drawdown curve, it is going to be
something like this.
That I'm going to start with almost
zero. There was a first drawdown on the
day one.
And overall under the water, this is the
major drawdown we can see over here
which is about 1040 points. And since we
already have seen these things visually
now, it is important for us to now check
out what the performance metrics look
like in actual numbers.
So we calculate the total P&L, we
calculate the average daily P&L, the win
rate, the average win, average losses,
the drawdown as we just saw around 1040
points, right? And the Sharpe ratio.
So things noteworthy over here. The
average daily P&L is 14.49 points. Okay?
The win rate is slightly less than one,
uh 0.67, quite less than one.
The average win is 112. The average loss
is big. The average loss is 181.
So it tends to win. Overall it is
winning. It is making money. So it tends
to win more often, but when there are
losses, the losses are actually bigger
than the average wins also. Okay? That
is what this data is telling me. The
profit factor is 1.23
and the maximum drawdown as we discussed
1040 points. Now,
looking at the reason why these large
drawdowns occur is because if I take up
only one day, the day where one of the
highest drawdowns happened, okay? So,
this is the drawdown dot idx mean. Here
I can see that on the worst day, which
is actually the first 31st January 2022
on this day there was a large drawdown.
And this is how the intraday P&L was
behaving. So, at the beginning
I had my straddle P&L
starting from zero. Obviously, this is
the P&L. This is not the total straddle
value. So, it went and it went down
completely all the way till here and it
closed around
108 points. So, this was the worst
single day drawdown. So, now we're going
to check over here that which was the
worst single day drawdown, okay? So,
this is the intraday P&L on the worst
drawdown day. And this goes to show that
from the very beginning when the market
was quite volatile or quite one-sided,
the straddle actually lost a lot of
money in the first half itself, okay?
Now, on a trending day, okay? So, if I
take the spot data,
I see that spot data on this drawdown
day looks something like this. If you
look at these two figures, they look
pretty much very similar. But in
reality, the truth is that because the
market went down significantly,
there was a significant loss over here
also because the puts we have expanded
in value, right? Now, on a extreme day,
what happens is that there's high
volatility, there's gamma risk, etc.
Now, let's have a look at another
interesting thing. There's now all the
morning gamma risk, okay? Now, the short
straddles are extremely vulnerable at
the entry times, like the earlier time
of the session, okay? So, why is this
so? It's because the gamma is very high.
The volatility tends to be unstable and
the price discovery is quite active. So,
if there's a very, very strongly
trending day, quite often you would see
that the day is a trending day since the
very morning itself, okay?
Now, what I'm going to do is I'm going
to create a plot of the average P&L
profile. So, in most cases, we are
seeing that from the very beginning in
the morning, we see that on an average
the P&L tends to be very stable. Now,
obviously, this is the average intraday
P&L profile. It doesn't mean that there
would not have been any losses in the
morning. We just saw an example where
the losses were there in the morning,
right? But on an average across the 60
days of data, this is how the P&L has
behaved. So, we notice that the overall
behavior till the half of the day
roughly is actually quite stable on an
average. And we see that there are
major, major drawdowns that happen in
the second half. And there is quite a
chance that all the profits which have
been accumulated, either they wiped out
or they turn into losses.
So, if we interpret that, we have to
understand that the drawdowns are a
function of direction and persistence,
okay?
And the losses totally depend on the
market regime. If it is a volatile
regime, is it not a volatile regime? If
it is a strongly directional regime,
then we are going to see such state
losses, right?
Also, the time of the day has some
implication on how the strategy is going
to behave.
Even the time of the day matters, we see
that there's asymmetry in outcomes. This
is a plot of the return distribution. We
see that in most cases the profit is not
very high, but somewhere around zero or
slightly above. But then when there are
losses, then there are quite extreme
losses, okay? And we see that this
negative skew is quite visible over
here. So, overall, we can understand
that the tendency for the large
drawdowns and the asymmetrical outcome
exists why it exists, right?
Now, it is not a linear income strategy.
It is short gamma. It is short
convexity. It is regime sensitive and it
is time dependent.
This is what we learn from this.
So, thank you so much. I'll see you in
the next video.
