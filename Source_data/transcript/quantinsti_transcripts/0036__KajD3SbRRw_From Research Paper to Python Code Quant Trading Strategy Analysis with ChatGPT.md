---
title: "From Research Paper to Python Code | Quant Trading Strategy Analysis with ChatGPT"
video_id: "_KajD3SbRRw"
url: "https://www.youtube.com/watch?v=_KajD3SbRRw"
duration: "28:31"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# From Research Paper to Python Code | Quant Trading Strategy Analysis with ChatGPT

[Watch on YouTube](https://www.youtube.com/watch?v=_KajD3SbRRw)

## Transcript

[Music]
somewhat understand was night only and
day only and we're going to then compute
the night returns. So I'm going to say
hey please give me some simple bullet
points.
So day return is actually a little
negative. We can see that. So let's go
for it.
Hello everyone. My name is Mo and
today's video is about chad GPT and its
use in quantitative finance research. In
today's video, we are going to take
charge GPT and do something very
interesting with it. In the last
approximately 3 years, the world of
quantitative finance has changed. Yes, a
lot of packages, a lot of new
technology, a lot of research has been
published. But the LMS like CH GPT and
the likes of it they have changed the
world. What could not have earlier been
done in a matter of days can be also
done in a matter of a couple of hours or
a few minutes also. This is because
these elements are helping us and I'm
going to show you that if you are a
beginner quant and you find certain
things intimidating you don't know where
to start you don't know how to take up a
project what is the idea behind it and
how to actually go from the idea to the
Python implementation
this video is for you I'm going to show
you how you can do all of that we are
going to take a research paper we are
then going to ask GPT team to help
summarize this research paper. As the
next step, I will ask Yajib Bri to give
me a flow diagram. How could I actually
go through the entire process? And this
flow diagram would also help me to not
just go through the process of Python
implementation, but it is going to give
me the specific code in every step of
the process. In the end, once we have
everything in front of us, we're going
to derive some inferences from this
research. So, let's get to it. I'll tell
you what I did. I went to the SSRN
website where obviously you find a lot
of research papers and I actually typed
anomalies in US equity. So, anomalies
would be obviously a large number of
research papers. As you can see in front
of you, it is about to appear.
one to 100 of 10,000 papers the 10,000
papers if not more written only on the
anomalies in the US equity markets so I
scrolled down I found I searched and
finally I had come to this particular
paper the difference the return
differences between the trading and the
non-trading hours like night and day so
in a nutshell is the night returns
versus the day returns okay so over Here
you could open this PDF in the browser
or you could also choose to download the
paper whatever you want to do. You
ultimately take a look at the paper and
what I did was I found it to be a 48page
paper. Now as a beginner quant if you
look at a 48page paper the first thing
you're going to do is no I'm not going
to read that. You actually have to go
step by step and read every bit of it in
real world. But with the power of chat
GPT what we can do is we can make our
work far more efficient. So I took up
this research paper and if I were to do
it very rigorously and take number of
hours or some days to actually go
through each and everything and actually
encode it I would have to go to a long
drawn process and for a beginner quan if
you're doing this then it can be crazily
intimidating. It can be daunting to
actually see so many formulas, so much
math, so much text, so much financial
literature which is actually so many
years old that even the English may be
of a different style and then you come
across many tables, many graphs and
perhaps a lot more formulas and even in
some cases some programming codes. So
what you do is ultimately after
scrolling all this I came across only
one particular graph which I could
somewhat understand was night only and
day only it says the growth of $1
investment in night returns and day
returns. So this is showing me the night
returns versus the day returns in one
graph. So by and large this particular
paper is very very intimidating and I
want to make my work shorter. So what I
simply do is I go to charge GP first. I
have already downloaded the paper. So I
would recommend you first download
upload the paper in your machine and
then you upload the paper. So that's
what I'm going to do. I'm going to
upload the paper.
Here we go. I'm going to talk to Chad
GPT. Have a look at my interaction and
let's see where it goes.
Hi. Can you
summarize
this paper for me?
As I said the first step is that we ask
to summarize this entire paper. So it
gives me the name of the authors. This
paper was ultimately published I think
in 2008. Uh the entire study spans
across 1993 to 2006.
It decomposes US stock returns into day
open to close and night close to open
returns. H So let's just pause and
think. day open to close that means
today if I see the market open at a
certain price and then close by the time
market is closing by the end of the day
so the difference between open and close
is the return I'm getting in the daytime
in the trading hours and then says night
close to open returns so close to open
would here refer to the previous day's
close and today's
Guys, very often we see that there is
some sort of a gap up or a gap down.
Markets are never sleeping. There's a
lot of economic news. There's a lot of
things which go around in the world. And
sometimes
if not many times the markets actually
give us some returns or positive or
negative just by opening higher or
lower. So the night returns would be
close, previous close to today's open.
Okay. using transaction level data from
1993 to 2006. So this seems like there's
a lot of work which has gone over there.
The key findings are being presented
over here by charging team. Nearly the
entire US equity premium comes from
overnight close to open returns.
Interesting. It says that the daytime
that is open to close as the trading
hour returns are on an average zero or
even negative.
Okay. The pattern holds consistently
across these various index futures, ETFs
and such uh exchanges and the various
instruments. It holds consistently
across the days of the week, the months
and the years as well. So this is I
think the major crux because these are
the key findings and then discusses
certain notable patterns. a strong
negative return in the first hour after
the market open and gives me some more
uh long drawn conclusions. Okay, I'm
going to ask it to just give me some
simple bullet points. So, I'm going to
say, "Hey, please give me some simple
bullet points
to understand this.
It says absolutely
here is a set of simple clean bullet
points. Okay. The paper studies US stock
returns during the trading hours and the
non-trading hours. This is something we
understood. It finds that almost all
stock market returns the past weekends
happened overnight. All of that positive
returns occurred every day of the week.
Uh so if you calculate it from day to
day and then you calculate it from month
to month and there's a lot about risk
and volatility differences. I want have
something about liquidity or transaction
cost also and the earnings announcement
timing the classic weekend effect. So
again it is not making it too simple. I
think I think I should ask you to
simplify it a little more because if
you're going to implement this on Python
transaction level data is not something
which I have immediately right now.
Simplify it a bit more
as as if I am a beginner
quot
okay. So as if I'm a beginner, I'm
asking to simplify. So simple bullet
points are here. Now I think by and
large you have already understood what
the major crux of this particular paper
is. It focuses upon night versus day
returns. So uh the conclusion we want to
actually get to is the conclusion in the
paper as we could see in that particular
graph itself. So this is the graph. Yes,
this is the conclusion which we want to
see. We actually want to see uh that
after whatever Python implementation I'm
going to do I should ultimately see that
for a particular instrument or a series
of set of instruments perhaps uh the
returns on the night non-trading hours
night returns were far greater than the
day returns. So let us begin. So as the
next step, I'm going to ask Chief to
create a flow diagram and help me
implement this in Python.
Please create a flow diagram helping me
implement this research in Python. Just
the flow diagram. Okay, let's see what
it comes up with.
This is the flow we start. We first
download the price data
with the open and close prices. Of
course, we calculate the previous day's
close. So, we're calculating what the
previous day's close was. And we're
going to then compute the night returns
obviously because from previous day to
today's open is the night returns. Then
we compute the day return which is from
today's open to today's close. Perfect.
And then we combine these returns into a
data frame. All right. We plot the
cumulative night returns and the day
returns separately. Night returns and
the day returns separately. And we
compare the total returns. Okay. Both
day and night total returns. And then we
check the percentage of returns for day
and night. And then it decomposes the
returns to full the first hour, midday,
last hour, etc. So this is something
which says that open to 10:30 then
midday 10:30 to 3 p.m. then last are 3
p.m. to close. Interesting. So this is
something I have to decompose the day
returns into three different periods.
But I'm not sure if I'll get that level
of data or that frequency of data when I
could go so deep. Nonetheless visualize
the results whatever the line plots bar
charts are. Interpret findings and
compare uh the paper insights. Perfect.
Uh it says would I like to go and
translate this into code step by step. I
would say yes. Help me code this. Step
one, please. Now to implement this, I'm
sure all of you who are watching this
could do this yourself. But I'm going to
show you how you could go to the Google
Collab
and using Google Collab, you could
actually open a new notebook. Okay.
new notebook and drive. So this is
something which is going to be saved to
my Google drive
and once this is open I will begin with
a clean slate copy and pasting
everything that trads me to do. Okay. So
the step one is to download the price
data. It has given me a particular block
of code and I copy this and straight
away I want to paste this over here and
let's run this. Let's see what we got.
Okay, so we have tickers spy gold start
date 2020 end date 2024 December
and then we have this code and we
finally got all that stored in data and
it says inspect the columns to confirm
the structure data dot columns. Okay,
let's see what's got next. It says
after we got data column should look
like this. Is it looking like this? Let
me just double check. Yeah, it is. It's
perfect. Once you run this, just drop go
and we move to step two. Perfect. Let's
try go. See where it goes.
Right. Now, calculate the night and the
day returns. The night return, as we've
discussed a couple of times, open and
close difference divided by the previous
open and previous close night returns.
Uh day returns would be today's close
minus the open. So all of that is there.
Let me just copy and paste this. And it
says this will cleanly add previous,
close, n return, and year return. So
here we go.
Pasting it over here.
Perfect.
Says print tickers zero dot head. So
tickers has one and two items, two
elements in this list called tickers.
because index zero would be spy. So this
is I guess only for spy and it says that
I should go s for spy first. So we have
got a returns. We can clearly see that
night returns and previous close is not
available. Night returns the first row
will not be available. But let's see
what trade does to that. Okay. And then
we go to step three.
All right.
Plot the cumulative returns. So compute
cumulative returns for both night and
day returns. Plot them to visualize the
time growth over time. It is also
importing mattplot li over here. Looks
like it is going to plot using mattplot
plot plot. Ctrl V and voila. Let's see
what happens.
So it says initialize your plot and when
is within this uh initialization
it is running this for loop and then it
says
for ticker integers
and then it calculates something and
let's see the end result. The end result
is a plot. Now let's go back and see
what it calculates. It calculates
oneplus data night return
compro. Okay. So in our previous steps
we got an ID return and day return on
percentage basis is doing one plus and
then dot compro which is cumulative
product all that put together in two
different ways for two different tickles
and ultimately plotting four different
lines on the plot. These four different
lines also have legend. So this
particular red line is the GLD. This is
for gold. GLD day return. So day return
is actually a little negative. We can
see that. And GLD night return is this
green line which seems to be giving me
the highest returns in this time period.
SPY day return is this orange line which
I can clearly see go from 1 to somewhere
between 1.2 and 1.4.
This is not that bad.
and then spy night return which is again
beating the spy day return. Okay. So we
see that gold has got a significant
difference although spy also has got
some difference by and large but overall
for both instruments the night return
actually wins. Perfect. Maybe charge is
also wanting to show us what the exact
numbers are. Right now it's just shown
the plot. Let's go to the next step.
Let's type go.
Okay. And I must tell you that the time
period that we took was from 2020 to
2024.
So we going to go and experiment with a
certain different period of time as
well. Okay. Now it says summary
statistics. Perfect. This was the
workflow. Now that that we've got our
various vectors of the night and day
returns, let's summarize them with the
metrics.
We have got everything over here. Let's
copy this. And this should give you a
clean summary table with the mean,
returns, SD, and so on. So let's go for
it. Ctrl V. It's creating this really
nice looking data frame. Here we go. So
we've got ticker spy. This is the mean
returns night mean returns 10 mean
returns the standard deviation for the
night and day and then the caggr the
compounded annual growth rate. Okay. So
we can clearly see that the night
returns significantly beat the day
returns in both the cases. Perfect. Now
let's go to the next step. Bar plots for
summary statistics. We create side by
side bar plots for mean returns and
caggr.
Let me just copy this
and see what ultimately I'm getting over
here. Paste this. Perfect.
Now it is importing COD as SNS as well.
So I'm going to be using the C bond over
here as well. One second. So we've got a
bar plot
shows the mean returns
of the day and the night mean returns.
So for SPY I've got the day and night
mean returns. As I told you the
difference wasn't much but still the
night returns are high. For gold the the
night return is doing most of the work.
The day returns actually negative. And
then we have the night versus the CGR.
So the CGR is going to be the compounded
annual growth rate. Obviously it is
going to be very similar to the
cumulative return because of the overall
time period we're looking at is kind of
just 4 five years. So yes, so this is
interesting. We we see that the knight
mean returns the knight C here I kind of
everything this wins this wins knight
returns win. That's it. I mean we got
this. Now this wraps up the clean
implementation of the core analysis.
Chang itself says that would you like to
add cumulative return line plots with
shaded volatility bands year- wise
breakdown a final report summary for uh
C CSV or Excel. So I think I'm going to
stop here. But one thing which I can do
is I can at least ask for this bit. This
is
something I want. Yeah, I can ask it for
at least the cumulative return plots
with the volatility maps. All right,
perfect. So, let's see what code it
tends to generate. The cumulative return
line plots with shaded volatility map.
All right,
here we go.
Just paste this over here.
So this is kind of
of analysis going on up here says
incomplete input. I hope I have copied
this successfully.
So here I see that the
rolling volatility
is being calculated volatility band. So
we have got a rolling volatility rolling
std
and the window is a 20-day trading
window. So 20-day trading window
volatility calculated for the night
returns
and the cumulative night returns both
put together in a certain plot. Okay.
Then we have the cumulative day returns.
The day will actually be in the 20
period because window is 20
and
this again plotted.
So here we go.
This is the spy night return and the spy
day return. So this is cumulative
returns with rolling period. So this
seems to me that this is the night
return and the day return only for spy.
Let's move on. See this is the night
return and day return only for the price
of gold
right perfect so cumulative returns with
rolling 20 volatility bands I don't see
any bands I I kind of get confused
because the band should be visible so
let me just look into it more closely
maybe there are bands inside so in that
case I would have to actually shorten
the data itself
So
I can't see the bands. Let me ask it how
I can see the bands, right? I mean I
know how I can see the band. I want Chad
to do this. Okay. I cannot see the
bands. What's the solution? What's going
on? Why you're not seeing the bands?
Nightwoodity is like 0.5 per day. So the
problem is that these bands are actually
small because this standard deviation is
small. The night is typically tiny like
0.005 per day. Multiplying it directly
by cumulative returns barely moves the
line at all. So your shaded band
overlaps exactly which is making it
invisible for your eyes which is
understandable. It's not a problem.
Okay. Then it's given me corrected code
for visible volatility bands and how it
has fixed the problem. Apply volatility
band as a percentage band relative to
the cumulative return. Let's see if
something happens over here. Let me just
paste this as it is.
Okay. Seems like I still don't see these
bands but I see slightly better. I can
see this haziness around this over here.
These are the volatility bands. So this
haziness little bit more visible but it
is true in saying that because the
number of data points are so much that
fitting them into a plot in a way that
we can see very a small difference
between the cumulative return and the
band is going to be difficult. So
understanding the fact that the
volatility is low and this is happening
quite understandable. So let's come to
conclusions. So let's say thanks
I got the desired results
and the research paper
also
aligns with my inferences.
How can I
use this inference?
What are the possible
applications
of this? So while this is thinking and
giving me the answer, allow me to just
take you back over here and suggest to
you that when you're doing such
research, maybe you can ask JBT to make
the code a little funible. That means
maybe it can make functions out of it
and it could take ticker list or list of
tickers as a input in the function. And
then you could try it out with different
assets, different instruments, maybe
some popular stocks, maybe your favorite
stocks and maybe you could go to
different time periods and check out all
of this how this happens. Right? So
since it's calling tickers with a fresh
variable definition of tickers again and
again that is why I'm not going back and
doing it because it's very likely that
my code will not run. You see over here
it has defined tickers and then again
over here it has defined tickers and
then maybe in other places it has
defined certain things again. So this
experimentation could best be done with
functions where the parameters once
given uh would actually permit into the
other functions as well. The encoding
needs to be modular that way. So given
that uh you should experiment. I highly
recommend. So coming back to what I
asked IP this is what it gives me. It
says that intraday strategies are a
place where I could use my inferences.
Portfolio construction and risk
management. I'm not reading everything
in detail right now. Volatility and
trail risk assessment,
algorithmic execution and market timing,
cross asset and multi market analysis,
uh signal engineering. And I'm sure if
you just take one of these points and
dive deep into how you could use this
night versus day return inference in any
of these particular
fragment of the answer long answer which
it gave any of these particular subtopic
then you would definitely get some more
interesting answers. So in summary your
Python implementation becomes a robust
quant research tool to test refine and
deploy strategies exploiting intraay
return dynamics. You can automate the
pipeline for different markets, time
frames and instruments. A powerful edge
in quantitative trading. If you want, I
can help you. And it is ready to help me
with some very interesting things as
well. But this is it for today. We're
going to call it today. It was a very
very interesting session where I was
able to actually ask RGBT everything and
let's say within a matter of about half
an hour we could actually go through
what this research paper was telling us
about and actually implement it on
Python. I would recommend you to go by
yourself do some Google search or search
on the SSRM website. Find out about more
such papers. Try and upload them into
charged and ask for inferences. Whenever
you get stuck, copy paste the error to
JPT. Ask it for the corrective steps.
Take a recourse once or twice if
required at all. Ask it to simplify and
summarize. And I'm more than sure that
you will get to learn a lot and leverage
the power of AI, leverage the power of
these LLS in your field. Thank you so
much. I'll see you in another video.
[Music]
