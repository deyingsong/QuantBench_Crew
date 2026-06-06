---
title: "Intraday Implied Volatility: What Python + Options Data Reveal"
video_id: "ISVFhvECvzc"
url: "https://www.youtube.com/watch?v=ISVFhvECvzc"
duration: "24:31"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Intraday Implied Volatility: What Python + Options Data Reveal

[Watch on YouTube](https://www.youtube.com/watch?v=ISVFhvECvzc)

## Transcript

This video is about fixing the
foundation. If you want to work as a
serious options trader or a quant or a
research analyst, you need to be
comfortable with this level of
understanding of options data. Here is
the uncomfortable truth. Most people
talk about options without understanding
them. A lot of people want to trade the
Greeks without understanding what Greeks
are. A lot of people talk about implied
volatility without understanding the
underlying mechanics and this video is
going to fix that for you.
Hello everyone and welcome to the
YouTube channel. My name is Mohawk and
in today's video we are going to talk
about options. One of the most
interesting and yet somewhat
misunderstood topics in finance. So
today if you are somebody who has been
an established trader but has not really
handled off data in Python, if you are a
research analyst, an aspiring quant or
even a seasoned quant who wants to brush
up certain concepts of data handling,
this video is for you. By the end of
this video, we will actually understand
how intraic options data is organized
and dealt with in Python. We're also
going to understand how to compute
implied volatility and what it means to
compute implied volatility. So let us
begin. So as we begin with our Python
work, let us talk about the libraries
that we importing. We got number pandas
the general ones like date time expos.
We'll use plotly for plotting. I be
using pi wall lib black scores of
impliity
for impleity. Now over here the first
thing I do is I actually load all my
data which is present in the same folder
as my IP bind file and what we're going
to do is why I see that this data is
going to have all the necessary things
that I need. It is going to have day
time it's going to have a name of the
underlying which is bank nifty in our
case. We have the expiry date of the
option. We have got the strike prices.
We've got if the option type is a put or
a call. We've got the open, high, low,
close. And we've also got the close
underscore spot which is basically the
underlying price at that minute. Okay,
this is minute level data. You see that
the same time is consistent across this
because we're seeing one after the other
different strike prices and you can
already see over here that we have got
quite a lot of rows, right? and we've
got these 12 fathers. So looking into
this, this is actually with the quarter
1 of 2022. This data starts from January
2022 and goes up to the first quarter.
Right? Now what I'm going to do is for
the easiness of handling this data and
for demonstration purpose, I'm going to
just restrict all my work to one day. So
before I get into all of that, let me
just tell you one thing that the data
needs to be organized. No matter when
you're sourcing the options data from,
if anything is not aligned properly,
things are going to break. Okay? So
whether the option is a call or put that
needs to be established, the date and
time of the trade needs to be
established. The expiry date needs to be
established. So you need all these
inputs no matter what. Otherwise things
will go downstream. So we have got the f
date time. We create the datetime object
and then what we do is we extract some
dates. We'll just extract the first five
unique dates. We get the first five
unique dates. And what I'm going to do
is I'm going to keep the date the first
unique date which is the 3rd of January
2022. And we're going to extract only
this bit and make a copy of it calling
it df. And this is df.head the 3rd of
January 2022. And you can see this is a
much smaller data set. So it becomes
slightly faster to work with this at
this point. Underly for us is bank nifty
over here. So how did bank nifty spot
behave for this? Obviously I refer to
the close spot over here. And as you can
see that this since there are a lot of
options the same date time repeating
again and again. What I need to extract
is that across time how close spot has
behaved. Okay. So here what I do is I
take only the unique values of daytime
and we drop the duplicates. Having said
that what we simply need to do is plot a
graph and here we see how the intraday
movement of that underlying behave that
day. At this point I'm showing you
everything from a baseline point of view
and a generalistic point of view. Later
I'll introduce some variations. So don't
skip any part of the video because
otherwise you will not be able to
connect. So as you can see over here I
have got my underlying price which
starts from around 35,600
goes all the way to 36,400
odd levels where we do now look into the
options data and how options tend to be
hit. But before that what is implied
volatility? Implied volatility is not an
opinion. It is not a forecast and what
it is is simply it is a number that will
help me plug that number into the model
and match the price I get from the model
with the current market prices. It's as
simple as that. So what we need in a
black scores model if you've ever used
an option calculator are the inputs that
it takes. We have the spot which is
close spot. We have the option type
which is a caller report. We have the
strike prices. We have the time to
expiry and this data time is for our
data handling. All right. So we need
these things in order to actually
compute the options impliable likely. We
will also need interest rate. But to
keep things simple in our workflow,
we're going to take interest rate equals
to zero. You see the the way we have our
data structure we have the date time
which is the point in time when we're
looking at this particular row open high
low close which is 1 minute frequency
but from this date time if you look at
the expiry there is a gap right and the
time to expiry is about that gap so we
need to compute the time to expiry we
can't just let it be like that so what
we do is we convert first we convert the
expiry to a daytime time object. I only
sort the data carefully. Having done
that, what we're going to do next is
we're going to recreate time to expiry
in years. What do I need? I. We need to
compute what is the fraction of time
compared to an year which is left for
the option to expire. So I will take all
the time the market hours the non-market
hours which is 365 days 24 hours 60 60
minutes and 60 seconds these are the
number of seconds I actually have in an
entire year and this is going to become
my denominator and expiry minus the date
time which is basically the difference
the time to expiry is going to become my
input for the numerator. Okay. Now this
ratio as we can see established over
here is t and this is the input which we
actually require. Okay. So what I'm
going to do is I'm going to compute all
of them. It's not too difficult. And we
see that happen in seconds. And if you
see the unique number of time to expiry
in this entire day you will clearly see
that in this figure the time to expiry
the unique time to expiry values start
from here and go up to here. So
consistently linearly and that's how
time works. We all know the time is
actually going down. The time to expire
is actually going down over here. What I
will do is I will just to show you I
would just do to df.head.
You can see that we have time to expiry
which is this number. It's a small
decimal number right. So we have pretty
much got what we need as far as inputs
are concerned. Now as the next step what
we want is we want to use these inputs
through a helper function through the
correct computational work in Python and
for that we need to organize our data a
little more. We need to make our columns
a bit model ready. Okay. Now if you're
slightly familiar with the black scores
model you know that these symbols are
commonly used. So S is for the
underlying price. K is for the strike
price. T is for the time to expiry. R is
the dispute rate and we flag C for calls
and P for all the ports right under the
option type. Now in order to do that we
use a helper function and this function
is going to help us to convert all of
this into the necessary column names.
All right I'm not going to go into the
detail of the code because anyway this
will be shared with you. You can check
the description box below. Okay. over
here. Now that we've established this
columns, let's have a look. So I've got
my read time, expiry strike, option,
price, STR, and the flag. Perfect. The
flag will have puts or pause. All right,
we pretty much got the columns ready to
go to the next step. Now before I go to
computing IB because things can go
downstream if the data is inconsistent.
I run a sanity check to find out if all
option prices are greater than zero. S
which is basically my spot is greater
than zero. K which is my strike price is
greater than zero. T which is tied to XY
is greater than zero. So if all that is
zero then great. So let me try and
filter this out. And before the filter I
sh see the shape of the data frame and
so will I see the shape of the data
frame after the filter. And over here I
notice that my data is quite clean
because the shape doesn't vary before
and after the sanity check. Okay. But
this step is necessary for you to do in
case you're trying this out raw options
data. There could be some gaps. All
right. Now we define a robust helper
function to actually help us compute IB.
And if you notice this actually about
just one line of code which is going to
help us compute the IV and that's it. We
use implied volatility
wall which we have imported earlier and
here we have given input as all these
various inputs which we had decided
which all come from a single row and
that's it. For every row we can
calculate the implied veity. Perfect. So
here we go. Now this function is
something I have saved. Now I need to
use dot apply to apply it across my
entire data frame all the rows. Now
should be saying that I have got my data
frame with impliable attitude. So let's
just have a look. We do df head. Voila.
There we go. Applying the function
across all rows has given me this IV
value. All right. Now that I've got I
for all the options across time across
strike prices now things get
interesting. Now I want to do something
with it. Right? We remember we have
already seen how the underlying prices
look like. And now what I'm going to do
is I'm going to choose the add the money
call and then an act the money put from
that day. Now obviously it can become
very difficult because what was at the
money and the beginning of the day may
have become in the money later right. So
here our assumption is to pick up those
likes which were very close to the money
or very close to at the money or exactly
in the money at the beginning of the day
and having done that I take out the
strike price which is relevant. So all
these are the various strike price which
are present and the strike price which
is relevant for today is something I'll
be dealing out. So the underlying price
at the beginning is 35,64.
So the closest strike from this is the
35,700
strike. So I've extracted the data for
my add the money calls and so have I
done that for the puts also. But we will
look to the put part later. Let's only
focus on calls right now. Okay. So this
is all the data for the at the money
call which was at the money in the
beginning of the day for this entire
day. All right. And similarly this is
for puts. Okay. This is how it goes.
Perfect. So this this is the same exact
same data for we add the money put at
the beginning of the day. As you can see
over here again 35,700
is the strike. Perfect. Now we need to
visualize certain things, observe
certain things visually. We have
established and organized the data. We
have established the helper function. We
have applied the helper function. We've
computed implied volatility and we have
extracted data for our obser
at the moment and then we're going to
get into the calls. All right. So here
what I'm going to show you is the plot
which represents across two different
scales. On the x-axis we know we have
time but on the yaxis on one hand we
have the underlying [clears throat]
which is this blue line as we know that
it has been in an uptrend. Also this is
the put price over here which is this
red line. Over here it is in a
downtrend. Obviously because of the
market goes up the put prices tend to
fall and or a plot over here below. I I
couldn't place an inside this because
the scale would have become weird. So
I've made a plot over here which shows
the implied volatility of the particular
put across time. So across time this put
had an implied volatility starting
around 24 and then till the middle of
the day it was hovering sideways and
then later we see that the implied
volatility has increased. Now this is
interesting. So what we notice over here
something to make mental notes about. We
have noticed the underlying being in an
uptrend. We have also noticed the puts
falling all the way down but the implied
volatility behaving slightly more
erratic than any layman could expect.
The implied volatility begins at a lower
level and ends high and then falls back
down towards the end. So why is this
happening? What are the inferences I
could gather? So well on one hand many
of you may have heard that the implied
volatility across different strikes
looks like a smile right. So as you go
more out of the money as you go more in
the money the implied volatility tends
to increase compared to at the money. So
this option became more and more out of
the money price of it which started
falling. The option price in the
beginning was around 320 and towards the
end it was just 82. So if the option has
fallen so much then it has become out of
the money as well and as it has got out
of the money we notice that the
impliable validity has increased. Now
this behavior is very common. One more
thing I notice is towards the end I see
a fall a sharp decline in impliability.
Now again this is something which is
seen commonly with puts when it comes to
relatively stable market movements. You
see high impli volatility means that
people are paying more for insurance but
lower impliableity means the market is
stable and the market perceives the
stability could continue. So we see a
fall in black. All right. Now looking
into the at the money cause let's see
the same behavior and how this behaves
without the money cost. When it comes to
the comparison between the underlying
and the call prices we see a clear
correlation. Obviously when a market
goes up we can see that at the money
strike call is also going up and
eventually this is becoming in the
money. Why? Because at the beginning if
something was at the money and the
market has gone so much up it is
obviously becoming in the money. Now
this 35,700 call by the time the market
is up and 36,400 is quite in the money
and we see over here similar behavior
first we see that the implied volatility
was relatively sideways right and then
we see it is stimuli
volatility this call has closed with
okay now it's not a direct after the at
the money stage it's not a direct
comparison between this
and that put because this is in the
money and that is out of the money but
again the inference we get over here is
something which is aligning with the
volatility smile now speaking of the
volatility smile it is important for us
to understand this concept as well
understand this phenomena and
observation as well that and I'm going
to use a particular time during the day
let's see the midday over here which is
around 12:22 p.m. in Indian markets. I'm
going to construct this. This is the
volatility mine across all the different
strikes. You can see this blue line is
slightly mildly higher. This blue line
slightly skewed. And then we have the
similar red line. So pretty much
symmetric but slightly slightly higher
on the put side. Okay, this is how the
volatility smile looks like. So across
all the strikes at 12:22 p.m. we saw
these are the volatility levels across
calls and puts. Now what I'm going to do
is I'm have a special little bonus po.
I'm going to go back and I'm going to
change the date. The date which I had
taken was the first date. Right. I'm
going to take another date which is
basically the date when the market did
not rise. On the contrary, the market
had fallen. And why we want to do this
is we want to observe something once
again with a fresh perspective on a
defeat day and see how many of these
principles carry forward or if we get to
observe something new. Okay. So this
union be which we had taken over here is
this. I have commented this part out.
I'm going to just comment this and
uncomment this. I'm going to take the
18th of January which is the date and
just to keep things fast I'm going to
run all the cells together and then you
will be able to see the observations
across 18th of January. So on the 18th
of January the price did not behave in
an uptrend it behave slightly different
it did go up almost in the first half of
the day and the second half of the day
it actually crashed and fell and closed
in the negative. Okay, so this is how
the intraday chart looks like when it
comes to the underlying. Now obviously I
do expect that the puts would have lost
money and then if the market fell they
would have gained money. So let us look
at how the puts behaved and see how the
implied volatility on those puts behaved
as well. So here we go. These are all
the liility calculations which I've
already shown to you. And then we have
something extra which is the good
behavior.
Now if you closely notice over here the
red colored line are the put prices and
the blue colored line is the underlying
and there's a sharp rise in puts towards
the second half because there was a
crash in the underlying. Okay. Now
moving on let's look at the implied
volatility. Now the implied volatility
is just going crazy. If I look at things
throughout the day and let's compare
these two things. So over here I can
easily see that the implied volatility
was stuck in a certain range because the
market had not moved sharply. In fact
implied volatility overall went a bit
down. So again this was the add the
money put option in the beginning and
the employee went down and as the market
went higher the implied volatility went
higher because the put became more and
more out of the money and then towards
the end we see that the implied
volatility has gone down again. So why
is the case over here? Because where at
the same time the market has gone down
again. Now a novice would see that if
the market has fallen they would say
that hey the implied volatility should
be at the highest of the day because the
market fell like crazy but the truth is
it's not like that. You see the
moneyiness of the option to be
considered here and if you look at this
which was at the money at the very
beginning is not very much in the money
when it comes towards the end. It is
slightly in the money. Okay. Because in
in the price established an uptrend
first and then fed. When we saw the
situation in which the market was up and
then timeline for this put was up is
because this put was becoming more and
more out of the money. But now it just
came back to add the money and then
little bit in the money. So there is no
wild move overall from the starting to
the end point of this option in reliable
rating. Now looking at the same thing
when it comes to the calls and you see
how well it is beautifully aligning with
the price movement of the underlying.
This goes to show that this is just the
part of the movement which has got to do
with the underlying. But there is this
the the hidden mechanism of impliity
over here behaves in a certain way. And
this is also quite quite correlated
because again at this point when the
market was going up this option has a
higher impact volatility as we came more
in the money and when the market went
down it went back a little out of the
money and is still having by and large
not a very very wild move compared to
the open of the impliable entity uh and
now okay so we can understand that there
are so many moving parts and This is
just the first step to actually notice
what is happening. So we earlier
discussed about the underlying price
movement during the entire day. We saw
that the downtrend come around 120 and
that's how the market fell. If we look
at the volatility smile during the
midday which is slightly before the
market fell down. We see that the put
the put implied volatilities are highly
skewed. So the put wing is actually you
know so much higher than the call side
of this volatility smile. So what
exactly is happening over here is that
the market is heavily pricing downside
risk. Now I'm not trying to imply
anything over here but this is just the
approach you need to take if you want to
observe everything when it comes to
options pricing when it comes to implied
volatility. This is the bare minimum you
need to learn how to do and you don't
need to get intimidated by options data.
It is not difficult to work with. As
long as you know where you're heading
towards, your workflow is clean and your
work is very organized. To compute what
we build over here is not a strategy but
it was a lens. So if you want to look at
the options through the quant lens and
do the bare minimum, this is something
you should know. Also now you're not
just observing option prices by the way
you're observing option prices through a
datadriven method. Thank you so much.
I'll see you in the next video.
