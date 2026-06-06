---
title: "Monte Carlo Simulation for Trading | Why Backtest Isn’t Enough?"
video_id: "y-d5FtnAFnY"
url: "https://www.youtube.com/watch?v=y-d5FtnAFnY"
duration: "35:02"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Monte Carlo Simulation for Trading | Why Backtest Isn’t Enough?

[Watch on YouTube](https://www.youtube.com/watch?v=y-d5FtnAFnY)

## Transcript

I go long on the days the price is above
both these moving averages. So for
example, let's go to this day. On this
particular day, the price is actually
above both of the moving averages. So
there's very very positively skewed in a
way say right. So this is the
distribution of my 5,000 simulation. Now
as I warn you don't just look at returns
and for this we're going to use Monte
Carlo simulation. So let us begin.
Hello everyone. If you have been around
quantitative finance you must have seen
this explosion of lines on your screen
you must have seen this at many places
in articles and reports and LinkedIn
posts etc.
What are these lines? Of course, as many
people already know it, these are
simulations popularly known as Monte
Carlo simulations. And they have some
significance, in fact, great
significance in quantitative finance.
But what are these things? How are they
applied? Where do we apply them? And why
so many lines?
They look kind of beautiful and
colorful, but we're going to understand
what Monte Carlo simulations are. and
we're going to apply it in building
testing a trading strategy.
Quantitative finance the word itself
means to quantify finance in most cases
financial assets. So what we mean over
here is that as quants we want to
quantify a lot of things but we also
believe that there's a strong element of
randomness in the future. The future is
uncertain very difficult to predict. So
we take a lot of data and we try to
model things thoughtfully and if we can
model the future and the uncertaintities
thoughtfully then we believe that we are
at a better safer and a more sher place
of doing what we want to do. Not all
quads do the same thing. So wherever
possible wherever the models allow
there's a strong use case of multicolor
simulation. For example, models where
you want to find out value at risk. As a
respond, you might want to find out a
lot of extreme case scenarios that are
out there. A lot of f future
uncertaintity which can step in and you
want to use Monte Carlo simulation to
simulate future scenarios. That is one
use case of Monte Carlo simulation.
Another use case could be to price
options. So you want to find out what
the future cash flows of this asset is.
Another distinct use case could be to
find out the various permutation
combinations of the different returns
and the different weights and portfolio
optimization asset allocation.
Now that is again another use case of
Monte Carlo simulation. So if I try and
go into each and every use case, I won't
be able to go very deep. So what I'm
going to do is I'm going to take one use
case which is testing the strategy
robustness. Yes, in algorithmic trading,
in quantitative trading, you can check,
you can test, you can test your strategy
in a way to find out how robust your
strategies. And there is an application
of Monte Carlo simulation right there.
To give you a simple example, let's say
I have this bottle with me, okay? And I
want to see how robust it is. Now, if
this were made out of glass, if this
were brittle, I would just throw it and
it would break. So if my strategy is
brittle, only a very little bit of
testing and optimization can make me
believe that this strategy is of no use.
But if this bottle is actually very
sturdy, let's say it is made of steel,
it can even withstand heat and cold very
easily. Whereas because it is made of
plastic, what will happen is that it
will melt away. So in a nutshell, we try
to do a lot of things with the strategy
to find out how robust our strategy is.
And that is exactly what we're going to
do today. And for this, we're going to
use multiolor simulation. So let us
begin. As you can see in front of your
screen, we have the chart of S&P 500. It
is the daily chart and it has got two
moving averages plotted upon it. The 10
moving average and the 30 moving
average. So let me take you to this very
interesting strategy which I discovered
and when I tested it, it gave me
fabulous results. So I'm giving it to
you right in front of you. So pay
attention. Right? So I have the 10
moving average and 30 moving average. My
logic is very simple. It is a long only
strategy. I go long on the days the
price is above both these moving
averages. So for example, let's go to
this day. On this particular day, the
price is actually above both of the
moving averages. I simply would go long
here and I would exit my position
wherever this condition is not met. So
this condition is not met over here. So
I'll simply exit my position. Then I'll
go long again when the price closes
above the 10 moving average which is
over here. So it's technically above
both the moving averages and I will keep
and I will stay long and I will exit
when it goes below any one of them also.
So basically this is a very simple
strategy and I saw it working pretty
well especially in strong market phases
like for example over here if there's a
strength in the market I would be able
to go long and probably stay long for a
pretty decent time and then go long
again and stay long for a pretty decent
time go long again stay long for a
pretty decent time. So this way it would
make me money. Now this is something I
saw visually. I saw in a more
qualitative way and I needed to quantify
it. So what we're going to do is we're
going to take this strategy. We're going
to take a lot of data. Okay. So I was
talking about testing a strategy is
robustness. One of the major things
which quants do is they understand that
one thing I should not do with my
strategy is to test it over a small
period of time. Because if I take a
small time frame, a small window of time
and I want to test that strategy only in
this particular window of time, I might
be actually very biased. I may take a
strategy only during the time when the
market is bullish and I say, "Wow, my
long strategy is going to perform so
well, so I should trade forever. I'll
become a billionaire doing that." No, it
doesn't work like that. So professional
quants know this that one of the first
steps is to have enough data enough data
points which cover different market
regimes different market phases
different types of trends and volatility
and even sideways market that itself as
a first step gives us an understanding
of how a strategy is going to work. So
let us begin. So the first thing I'm
going to do is I'm going to import the
libraries and download the historical
data. As you can see over here, I have
all the important libraries I need
today. Now you may be wondering, hey Mo,
what happened? Where is the library you
want to use for Monte Carlo simulation?
Now you see there are a lot of libraries
which have Monte Carlo simulation
inbuilt in some of their functions. But
what we're going to focus on today and
what is mostly the entire industry is
relying on is using numpy for Monte
Carlo simlion because there is the
random module with numpy and using
np.trandom
you can do a lot of things and you can
create simulations. So multicolor
simulation particularly does not 100%
require to you to use a particular
library but you can simulate a lot of
things using just numpy.
Then I download my data. Ticker is spy.
My start date is 2015 January. I go all
the way up to the end of May 2025.
And then I download all the data and
then I have DF which is my data frame. I
just have a look at DF. But I need to
run this. Yes, here we go. Perfect. So
now that I have the data with me, I have
basically got date and close. We're
going to be using date and close. We
don't need open, high, low, close for
this strategy. And you still see the
strategy works well. Then I have the
strategy back test. As I back test the
strategy, you can very clearly see I'm
creating two indicators, the MA 10 and
M_30.
And I create a signal. And the signal is
wherever the close is greater than both
of these, I simply go long, stay long.
Now that I have my signal, I adjust my
signal around my returns in a way that I
get my strategy returns. And now that
I've got my clear strategy returns, I
simply drop the N values which may be
there in the beginning. And I have now
got my DF. So now my DF dot head would
actually look like this. Perfect. So
here is my signal. Here are my returns.
Here are my strategy returns. So this is
how we're going to see how a strategy
returns are going to build over time. So
let's visualize the performance of this
strategy if it was a cumulative
strategy. And here I'm assuming that my
initial capital is $1,000. It could be
100,000. I'm just taking a random figure
which is actually a whole number so that
we can see things more clearly. Now I'm
going to visualize the strategy how the
strategy has performed over a period of
time. Obviously this code calculates the
cumulative return. And here I have a
subplot also to show you the draw downs.
So let me just show that to you. Here we
go. Here are my strategy returns and
here are the associated draw downs. So
as I can see the draw down plot because
it is important for want to understand
how bad it's like a 40% draw down.
Obviously you want to avoid that
strategy. But here I see a draw down
between 10 to 12%. And I'll show you the
numbers in a bit. Over here I see the
cumulative return path and this strategy
looks amazing. You see this is something
I came up with and trust me the first
time I saw this I just felt like nothing
in the world can stop me from becoming a
billionaire in the next few months
because I've decoded the market. I have
been able to hack the market. I've been
able to understand how this works. And
if I can create such great returns, such
smoothlooking returns, then wow, I'm in
the right job. So that was at the time
when I was a beginner. So $1,000 in the
beginning would actually turn out to
become somewhere around $2,000 in a
matter of roughly 10 years. Okay. So
obviously when you are trading, you can
add leverage and you can do more with
this. Make this return path a little
more smooth. So now let us check out my
return metrics. My return metrics over
here is basically like this. My total
returns are 96.57%.
My annualized return 6.95%
which seems modest. But if I look at the
annualized volatility that is also at
8.66%. Which is not great. So basically
I have a pretty smooth curve and I can
do a lot with the strategy. I can
possibly take leverage and get more
returns etc. Let's see. But let's look
at the sharp ratio as well. Now the
sharp ratio is8 which I would not say is
extremely bad but it's not the best
sharp ratio either. However, if I look
at the equity curve, my equity curve
looks pretty attractive and the maximum
draw down as I saw is numerically minus
11.69%. So that is the maximum draw down
I have seen 11.69%.
But then I did some robustness testing
and for that I used Monte Carlo
simulation and let's see what happened.
So now that I have got my baseline
strategy what I want to do is I want to
see its path dependency. Yes. So path
dependency is what Monte Carlo
simulations are going to help me
understand how path dependent my
strategy is. For example, as I given an
earlier example that if I want to test a
long strategy in a bull market, it would
obviously appear well. But despite the
fact that I'm taking 10 years of data or
slightly more than 10 years of data, I
am already taking a lot of market
regimes over here. It still may be
possible that the particular path price
takes as in if I look at my DF and I
look at my close if I take SNP which is
my DF and I say let's say I take close
right and I just simply plot this I see
there is a certain path price tends to
take which is simply this. Now had price
taken some other path, some other
specific path, I may have not got the
same returns which I got. My equity
curve may not look like this. Nice and
attractive. But it still looks way
better than buy and hold because buy and
hold although it is going up, it just
has these big dips in between and these
big draw downs in between. So it doesn't
have a sharp ratio as good. Okay. So
moving on what I do is I take this back
test and I turn this back test into a
function. So next time with only one
line of code I can actually change my
parameters or change my path etc and do
experimentation.
So now I have my function called
run_back test which I have created over
here. I can call this function run_back
test as I will in the coming four code
cells. Now that I have a function, my
next step is to check what Monte Carlo
can do for me. My function is here. My
strategy is here. Now Monte Carlo
simulation come into the picture. I'm
going to be creating simulations. Now
going back to the different applications
of Monte Carlo. These simulations are
possible to compute and even plot even
work around with in multiple different
ways.
There is no one specific way to compute
Monte Carlo simulations.
It is all about what your use case is.
So in some use case you may be taking
the mean of your past data and the
standard deviation of your past data and
using these two statistical properties
try and simulate a path for n number of
data points which follow the same
statistical property. And this path
would be a random path. You could use
multiple approaches for this simulation.
But one of the approach which we will be
using is the historical bootstrapping
method where what I simply do is I first
see that on this 10 years of data every
day from t0 to t1 and then from t1 to t2
I have got different returns. Now what I
do is I rearrange these returns.
Basically I'm reampling this return
column which I will create and I'm going
to create new parts on that basis. Now
there could be a debatable point that
Mohawk is this actually the correct way
to use Monte Carlo simulation for
strategy back testing. The answer is not
100%. There are more complex ways
quantraders use and they may be more
robust ways. For example, with
historical bootstrapping, you lose the
feature of autocorrelation.
So in another case scenario, a trader
may actually use Monte Carlo simulation
in a way that they are doing historical
bootstrapping, but instead of resampling
each day's return, they're taking a
block of days return. or they could be
using marco models or could be doing any
number of complex things but to suit a
illustrative example this is a very good
approach that we are taking so we do
this resampling and let me show you how
I'm doing this resampling the first
thing I do is I compute log returns the
log returns of my existing data I simply
use nb.log log to do so. And for Monte
Carlo simulations, more often than not,
we use log returns because they're
additive, easier to work with, and they
assume normality. So, we will not see
negative prices. So, once I have run
this code cell, I'm going to do the
simulation part. What I want to do is I
want to create 5,000 different parts.
These 5,000 different parts are going to
be of the exact same size of my data
frame. So the data frame I use to test,
I want to use the same size of data, the
same number of days of data to do my
Monte Carlo simulation. So at any given
point in time one array that I create
that npar that one array which I create
is going to be an array with so many
data points as is the length of my data
frame. Okay. So I've got num path 5,000
paths I'm going to create and every path
is going to have the same length as my
original data frame which is 10 years of
data. I have the start price. I could
take anything else as well. So I could
take I look minus I could take I look
zero. It doesn't matter because I'm
going to anyway be using a percentage
change to compute the cumulative returns
right. So I'm going to use possibly I
love zero. Then I have simulated paths
which is a empty list which I have
instantiated. Now using a simple for
loop a for loop that actually iterates
5,000 times because my nomore path is
5,000. So for underscore in range num
paths. Now I'll create the sample
returns. Now these sample returns are
going to be as I told you earlier using
the historical bootstrapping method. In
order to do that I take n.trandom
because nb.trandom is going to generate
random numbers and nb.trandom non choice
is going to help me achieve my
historical bootstrap. to this function.
I feed the log returns which is
basically my array of all the returns of
my historical data. I tell it what is
the size of the data frame or the size
of the array I want to create and then I
replace one with the other in case and
then what happens is I create a path. So
one path is created in every iteration
and such 5,000 paths are created. Okay.
Now simulated paths.append append path
means that I'm going to store all of
this in simulated paths. So if I look at
simulated paths first let me just run
this block of code and then it'll take a
few seconds. It has already done it.
Here is simulated paths. So you can see
the thousands of arrays over here. If I
check the length of this, this should be
around 5,000.
The len of simulated paths is 5,000. and
the simulated underscore path. If I want
to just pick up a few of these. Let me
just pick up the 100. Then this is how
it looks like. Let me pick up something
from between because 5,000 is a big
number. So let me pick up 1,203rd.
Here we go. Right. So we've got a number
of arrays all random. All came out of
historical bootstrapping. And now that I
have this particular list called
simulated paths, I can do a lot with
this. Basically, this is the array of
returns. Now the next step I want to
create that explosion of lines. I've got
my simulated paths. So I create a plot
over here. And to just show you how this
behaves is let's start with 10
simulations to go with. So over here
I've got 0 to 10. And I can see these
are the 10 simulation 10 random
simulations. Okay. Now let me take up
let's say 0 to 50 50 random simulations.
Let's see how they look like. 50 random
simulations. As you see as I increase
this number let's make it 200. This
picture is going to get denser. It is
going to have more random simulation. it
will have a lot of the lines in between
and then it's going to have some lines
in the extremes. So this is going to
become denser and denser. So I can put
up to 5,000 different simulations over
here. I can visualize that. Right? But
what makes sense for me to understand is
that the understanding that these are
the different ways S&P 500 could move.
Right? This is my basic understanding.
The best case scenarios would actually
take it as high as this. the worst case
scenarios could actually take it as low
as this. So by and large these are going
to the possible alternative random
uncertain case scenarios which I can see
which hold up some statistical
properties of my original historical
data. Now going forward I'm not going to
use this exactly over here. This is not
the end of what I want to do. What I
want to do is I want to take each one of
these possible parts of price and I want
to apply the strategy 5,000 times. 5,000
times I apply the strategy and then see
how the strategy tends to work. That is
what my job is. So what do I have with
me? I have my strategy return list which
is a new list which I'm instantiating.
So my previous list which had all the
paths simulated paths that is going to
go through the function the function I
created for my back test which is
run_back test and all of this is going
to happen with a for loop. So the for
loop is going to iterate 5,000
simulations 5,000 times with the
different parts and it will create
something called BT which is a back test
basically and I'm going to finally
append this BT to my portfolio values
right all these are the final values
which I have so basically going to run
this and this is happening 5,000 times
okay so ultimately as I told you my
function which is my strategy back test.
It takes percentage change, right?
That's how we do back testing. So it
doesn't matter what my starting point
is. I could start with historically the
price being 100, the price being what it
was at the onset of the data or what it
was at the end of the data. Doesn't
matter. So now let's visualize these
outcomes. To not give my engine a lot of
pressure, I'm just going to to take a
look at the last 200 simulation. The
first 200 simulation, they are random.
So, first or last doesn't matter. All of
this is scaled to one. So, you can see
how across different paths my strategy
would perform. And the very interesting
thing is that this particular black line
which is my original back test is
something which I've added to the plot
and you can clearly see that my original
back test if if let's say we started
from one goes all the way up to 1.97
almost at two but there could be case
scenarios where I could get much higher
returns and even many case scenarios
which I could get negative returns or
much lower returns.
So these are just 200 simulations.
Imagine what happens if I make this 200
to let's say 400. Okay. Obviously I see
a denser plot. I see more simulations
and I will see how this seems like. Now
I may not show you all the 5,000
simulation in the plot but that is fine.
But what I can show you is that now that
we have stored everything in our
variables, right? And this these are the
400 plots 400 simulated paths and not
just the paths basically how much
strategy performance would be across
these 400 parts. So we have stored all
of this we maybe not visualizing 5,000
or 1,000 but yeah we have stored all of
this. Right now now that we have stored
all of this how do I see if my strategy
is actually robust or not? You can come
up to me and say, "Hey, you've just
generated random bugs and you're showing
that there's a possibility of negative
returns, but my strategy looks so good.
I have put so much thought into it, put
so much observation into it, put so much
testing into it, put so much
optimization into it. But then what
happens is that you need to put these
things into numbers, right? So you have
seen the worst case scenario, you have
seen the best case scenario graphically.
Now let's put it into numbers. Let's see
how this can make sense to me. So the
first thing I want to do and I'm going
to use very simple metric so that
everybody can understand it very
clearly. I'm going to use a distribution
of my final portfolio values. Right? And
by using the distribution of my final
portfolio values I basically get an idea
of how my returns look like and I'm
going to create the different
percentiles. The 5 percentile 25
percentile 50 percentile 75% and 95.
Right now I'm going to plot these
different vert percentiles vertically
and these distributions have been
divided into obviously divided into
certain bins how my histogram works and
you can change this. By the way all this
code will be given to you. You can check
the description but listen to the video
so that you can understand all that
there is in the code. Right? So you go
to the description for the code. I'm
going to share this with you. You can
use it for your practice, for your
studies and make the most out of your
learning. Now, as the next step, I have
now plotted the distribution of the
various returns in a histogram plot and
we can see that I have I have these
vertical lines over here. Now, these
vertical lines are going to be
percentiles. Let me just zoom into this
particular area and we can see this is
the fifth percentile. Okay, so the fifth
percent what is the interpretation of
it? Among all the various things which
are happening over here among all the
various simulations this fifth
percentile is showing me basically the
area on the left hand side of this
percentile percentile is the worst case
scenario are the worst returns which I
created right and with 95% confidence I
can say that my strategy is not going to
perform any worse than this
fifth percentile. So what is my fifth
percentile coming to 11.82%.
Right? Similarly when it comes to the
extreme happy case scenario when I'm
getting extremely good returns outline
returns I look at 95% right and
everything beyond this so this is 249%
almost 250% by itself. Now all that is
beyond this is just 5% of my case
scenarios. So there's a very rare very
rare chance that I could go in that
extreme end and have that random luck to
actually create more than uh this 249.60
percentile. So I have given you a
certain interpretation of how these
percentiles can be interpreted. So you
can do that in your own time. Let's move
forward with the code. So by using this
right my first inference about my
strategy is what is that my extreme
worst case scenario is just - 11.82%.
That means in 95% of the cases I should
not be losing anything more than 11.82%.
Which is actually good. This goes to
actually show me that my strategy is
kind of reliable to some extent. Now
obviously depending on the firm,
depending on the setting, depending on
risk appetite, you may have a different
liability for different kinds of
distribution. And you may always want to
see that okay fine my original back test
gave me around 100% returns. Where do
the other possibilities lie? And you may
be very happy to see that this has a fat
right tail. That means although we don't
have a lot of extreme case downside
scenarios I mean the worst is what let's
see the worst comes to what worst come
to somewhere around 65% 65% negative
65%. But if you look at the best case
scenario the best case scenario is full
of these outlier returns and these
outlier returns go to even six almost
600%. So when you look at this, you feel
amazing like, "Oh my god, this strategy
can actually give me these outlier
returns." So I can potentially give this
a thumbs up right here and say, "Wow, it
may not be going and give me only
positive returns, but there's a
significant significant chunk of returns
that are positive because on the right
hand side of the zero, I see a lot of
numbers. So that's very very positively
skewed in a way you can say right. So
this is the distribution of my 5,000
simulation. Now as you want you don't
just look at returns obviously you look
at other metrics as well. Quads may not
just look at returns. They may want to
also look at other metrics such as the
maximum draw down or the sharp ratio. We
all know what these are but just to give
you an understanding the maximum draw
down is the maximum fall from a
particular peak to a particular drop in
the overall equity curve and the sharp
ratio is a ratio which shows us what are
risk adjusted returns. So now I have
created a function for both of these and
then what I do is I create two lists
maximum draw down and max and the sharp
ratio similar to what I did earlier I
run the for loop with 5,000 iterations
so run this block of code and then
finally now that I've got all the
iterations see this is still running
because 5,000 iterations and two
functions to go through perfectly done
now I create props Now we look at the
5,000 maximum draw downs coming from
these 5,000 simulations had my strategy
been running on these different paths
and I see something very interesting
over here. Something which actually
saddens me a little. I see that my
original back test maximum draw down was
just 11.69% as we just saw. But I see in
most cases my maximum draw down is
greater than that greater than that and
in some cases far greater than that up
to even 65% which is obviously not
likable. So I remember having given a
thumbs up to the strategy but now
looking at this I am going to step a
little back and say how is it possible
maybe my strategy was actually very path
dependent. Maybe if I take this strategy
and run it over the next 10 years, I
will see I'm very highly likely to see
this sort of extreme case scenarios,
right? And I don't want a 30 40 50% draw
down on my equity curve. And if you see
that there's a lot of draw downs which
are clustered around this 20 to 30 zone,
right? So this is also quite high. But
then I now take my strategy with a pen.
So let us explore a little more about
how the sharp ratios are distributed.
Now as the next step, let's see how the
sharp ratio is distributed across these
5,000 simulations. So I have my back
test sharp which is ready. And just like
the previous case, I have got this black
dotted line over here which shows the
sharp ratio according to my original
back test. And these are the 5,000
simulations sharp ratio. So I see this
is very interesting. This from a far
away you know distance it looks like a
normal curve which it is not. You see
the zero is over here right. Anyway this
is not not a zcore but yeah this is zero
which is sharp should should not be
zero. It should definitely be greater
than zero. In fact should be as high as
possible right. But my back test sharp
which was pretty impressive which is
around 76 uh sorry 79.8 date I see that
a lot of the sharp ratios are actually
below it that is on the left hand side
again I need to step back I had given
this strategy a thumbs up earlier but
now I have to give it the second thumbs
down I'm not very impressed with the
sharp ratio now where would I be more
convinced that my strategy is less part
dependent had the sharp ratios be all
clustered around my original back test
sharp then I would see my strategy as
being robust across different types of
market environments or different paths
the market could possibly take but this
doesn't seem convincing.
So ultimately with all the testing that
I've done I see that my original
strategy which is over here which I was
very impressed with which I thought
would lead me to become a billionaire
very soon doesn't seem actually so so so
impressive. So what have we learned from
this? We have learned that Monte Carlo
simulations
can help us test if a strategy is path
dependent or not. It is a type of
robustness stress testing and this is
something which you can now apply to
your own trading strategy. I'll see you
in another video. Thank you so much.
[Music]
