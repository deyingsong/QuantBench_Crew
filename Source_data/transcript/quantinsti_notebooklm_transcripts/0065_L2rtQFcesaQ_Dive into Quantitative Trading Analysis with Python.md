---
title: "Dive into Quantitative Trading Analysis with Python"
video_id: "L2rtQFcesaQ"
url: "https://www.youtube.com/watch?v=L2rtQFcesaQ"
duration: "28:22"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Dive into Quantitative Trading Analysis with Python

[Watch on YouTube](https://www.youtube.com/watch?v=L2rtQFcesaQ)

## Transcript

all right so let's start with uh what we
would typically do in the case of
uh when we start working with financial
Market data right so the first thing we
typically do is we UT a set of libraries
so I had referred to a certain set of
libraries a little while back so you
would do things like this import n NP uh
import pandas a speedy so uh now as I
mentioned earlier these libraries are
used for processing the data so numai is
used for comp computation pandas is used
for handling Financial Market data so it
kind of uh structures your data in the
form of tables which look like
spreadsheets but are a lot more powerful
and you have things like uh matplot lip
which uh
is used for charting why Finance as I
mentioned earlier is used for uh
downloading
of data via Yahoo finance so this is
like when you look at a Python program
this is like pretty standard stuff so
for instance now if I want to download
let's say the data for NVIDIA
Corporation so Nvidia manufactures these
um you can say uh chips graphic Graphics
processing units gpus which have become
very popular these days uh and it's
quite an exciting company it's a largely
a hardware company networking and I
think chips that's what they're they
they they typically work with so if you
want to download it so we could use say
yf.
download
uh you want to do that you can specify
the ticker that we want so in case of
Nvidia it's
nvda uh we want to specify say the start
date for when we want this data so let's
say we wanted from 1st Jan
2018 up to
say 27th of
September if you were to run
this voila it's done right so at this
stage we've got our data and if you want
to see how this data
looks you'll see that uh we've got about
1450 rows starting from 2 of Jan where
the price was uh around the close price
was around 49.8 the adjusted close also
was around
49.3 and eventually on 26th of September
it was about 419 or so right notice the
information that we have here we have
the Open high low close adjusted close
and volume right so this is very typical
of financial Market data where we have
this each day for the last five OD years
five six years right from eight start of
2018 until
yesterday now U this is the way you know
we kind of fetch the data so it saves us
the time of going and downloading a file
and opening it and all of that right now
let's say you want some basic statistics
of this there's a Nifty little function
called DF uh so firstly DF is uh the
name we've given to this what we call a
data frame which is the uh like I said
it's it's kind of like EX on steroids uh
the data frame itself
sorry and uh it's it's used for
basically handling this data and and uh
adding columns and and in general
manipulating the data because we are
dealing with like many rows of this
right all right so let's start with
something like a DF do
describe you want to run this it gives
you some details right it gives you the
count the mean the standard deviation
the minimum value Val and these give you
uh the the percentile value so what is
there at the 25th percentile the 50th
percentile which is nothing but the
median 75th percentile and the max value
right so for instance if you were to
look at uh let's just look at the
adjusted close column right for uh for
the sake of this session so we have
essentially
1443 number of values for adjusted close
the mean over this entire period was 143
stand standard deviation was 105 the
minimum was about 31 and these are the
percentile values and the max being
about 493 right so this gives you some
details if you want to do like a a
sanity check on your data you can do
like a DF doino so this incidentally
also tells you by the way that this is a
panda's data frame notice that it says
data frame here which is what it's
called this particular data type it's
also got some details on
uh the The Columns that you
have the data type that it have it has
and uh the number of non-null values
that it contains so when I say non-null
it means your data is not corrupted so
it so a null value would mean that for
that specific day for that specific row
uh some data was lost right so here you
can see that all of them are non-
null float essentially tells you that
these these can have fractional numbers
so you could have values like and we
know this right with stock prices you
can have fractional Parts you could have
prices like
48375 and so on however volume is stored
as an INT which is nothing but an
integer so these are numbers that don't
take fractional
values it gives you some kind of idea on
uh how these prices go uh now that
you've downloaded this data you may also
want to
uh save it if you'd like to right so if
I want to save it all I need to do is
could say DF uh dot toore say CSV so I
want to save it as a CSV file for those
of us who don't know CSV file is nothing
but I'd say it's like one of the flat
data files that you have it's comma
separated values so all it it kind of
looks like a spreadsheet but it's a lot
less richer so you don't have like uh
columns with borders and you don't have
like certain values which are bold and
so on but nevertheless it's a beautiful
way to store the data because it can be
shared across languages and across
various systems so CSV files are like a
I'd say a standard way to store data
files so I could you know create
say
uh a CSV file called Nvidia and if I say
df2 CSV and if I go to my um working
directory I here I have a file called
Nvidia right so if I double click on
this sorry
you can see that I have this entire
data okay so this is like basically one
way for us to uh download data as a CSV
file for one specific stock right what
if you want to work with multiple stock
data you want to work with multiple
stocks you can specify more uh stocks
so let me do one thing instead of typing
this stuff I was I was planning to type
this stuff and walk you guys through it
but you know because of the poity of
time I think I'm going to go to my after
file so I had an after before and an
after file thinking we could walk
through this stuff but there's so much
that I want to talk to you guys about
that I think I should
probably directly work with this
so I can I'd rather talk about what we
are doing than start typing it all right
okay so now if you want to work with
multiple stock
data you can specify say start you can
create variables like start date and end
date so we've created that here and when
we do the download we specify all of the
stocks that we want Within These square
brackets so for instance here I want
Nvidia I want the firm Visa which who
sticker symbol is V and there's
caterpillar which is uh a construction
Machinery firm and pep is Pepsi Pepsi
Cola so if I want to download all of
this stuff I can do
that okay I need to Define it let's do
this so we'll import all the
libraries
and we
will download it
here
great beautiful so now you have the data
for what like eight or nine years of
four firms and all their details right
you have adjusted close
close high low open all of the stuff for
all of these forms right so if you do
like a do head you get those details and
if you do the first few rows and if you
do a DOT tail you get the last few rows
right now suppose I just want to pull
out the adjusted close prices because I
want to work with that I can create
another data frame called adjusted close
where I pull out the adjusted close
prices so now all the prices I have are
for cat Nvidia Pepsi and Visa right so I
have all these details notice that I
have about 2200 rows of data so because
it's over8 nine years again I can do
something like a describe which we saw
earlier now suppose I want to plot this
stuff right this is I would say like you
know uh whenever we start with Quant and
is we we like to view I would say
graphically look at our data because it
starts telling us certain things and it
starts giving us certain insights which
is hard to see when you just look at
tables of numbers right so let's do that
let's
um plot
it so here we've now plotted all four
firms and their prices notice what we've
done here when we say do plot we specify
that we want a grid we specify the width
of the line and we specify the size of
the figure that we want right so you
have all four of them
here and uh it's kind of hard to compare
because all of them have different
starting points right because obviously
the prices of these four uh
stocks if you look at even like the data
here cat started around $71 uh Nvidia
started around
$5 uh Pepsi started around 73 and Visa
started around 62 and eventually they
are at you know these levels 272 425 and
so on so since the starting points and
ending points are so uh you know vastly
different it's a little harder to see
what's actually going
on when you want to compare the four of
them right so if you want to compare the
four of them one thing to do is why not
make the starting point kind of common
right
so uh what what we can then do is we
can uh equalize the first number to be
one for all of them and every other
number is proportionately changing with
respect to that particular stock right
so we take all of these prices basically
what we do is let's look at this we take
all each of these so let's talk about
cat so every number in this column is
being divided by
7186 so the first number then becomes
one this would then be 68 divided by 71
this would be 67 divided 71 and so on
similarly for NVIDIA each number is
going to be divided by the very first
one so 4.83 divided 4.83 4.75 divided by
4.83 and so on same thing for Pepsi same
thing for Visa so that way the first
number for all of them would be one and
everything else would proportionately
change
right so we do that
here and so this looks quite nice your
starting points are the same so it's
kind of like you know a race and we want
to see what happens at the end of the
race right in terms of how they did over
these eight nine years so now that we
know this works Let's uh create a data
frame called common start data frame and
instead of keeping it as one let's say
that all of them were at the price $100
on at the start of 2015 and we want to
know that if or rephrase that let's say
I had invested $100 on each of these
firms on 2nd of Jan
2015 where would I be on 27th of
September 2023 if I want the answer to
that question this should give me this
should get me closer to that answer
right so a $100 investment in cat would
have gotten me to say $379 a $100 on
Nvidia would have made me a Millionaire
right I would have been nearly at
$9,000 for Pepsi it would have been at
230 and for Visa it would have been at
about
370 we can do a plot of
this when you look at a plot like this
uh you get a better picture of what's
happening now clearly Nvidia is like the
breakout Star right it's it's done
phenomenally well compared to the other
three but since uh that makes it harder
for us to compare these three guys we
can only plot these three guys to at
least get a sense of what's going on
there right so notice what we are doing
here we are now specifying that okay I
want to just look at cat pep and B so I
run that notice again when I say do plot
I have a grid I have line width I have
big size I run
it and gives me an idea of what's
happening with these three guys right so
it appears like visa and
Cat if I had invested $100 would have
gotten me somewhere near 375 or so right
and comparatively Pepsi hasn't done all
that well right over those 8 nine
years so this is again some interesting
analysis of say analyzing a group of
stocks right we may want to drill down a
little deeper on one specific stock so
let's say I want to do it with Nvidia
let's just work with the adjusted close
column oh I forgot to run the first few
sets let me run
that DF
okay DF is defined let's go back down
because the error set DF wasn't defined
where are we okay so now we should be
good all right so now we have
uh another data frame called nvda nvan
and with just the adjusted close
prices so I want to create a column with
the returns that you get uh if
you um so a column called returns where
essentially what I'm doing is I want to
know uh what the daily Returns on say
Nvidia would have so when I say daily
returns I mean I buy at 49 and I sell at
52 right so that would mean the return
on say third of Jan 20180 similarly I
buy at 52.5 and sell at 52.8 right now
this can be easily done with a function
called percentage change which I run
here I run that and I check so now I
have a new column right called returns
that gives me the daily returns for the
entire uh column of nearly or rather uh
we have like nearly 1500 rows of data it
calculates all of that I have one na or
not a number here so I drop that
specific row to make uh things a little
easier and now I want to check and see
the distribution of how my returns look
over this period right so if you want to
check for things like distribution a
histogram is a good place to start so we
essentially plot a histogram where we
specify the number of bins we want so we
can even specify something like 10 but
10 is uh a little too Co so if you want
a you know a higher resolution image you
should probably do like a 100 gives you
a nicer shape gives you an idea that
returns in general seem to be around 0%
right daily returns with uh most returns
being just a little low zero right so we
can make that 100 even a th
okay th000 is too fine so I think 100's
100's
better so this gives you an idea of the
histogram you can also get a density
plot right so a probability density plot
where you do like something like a Dot
Plot and you specify that you want a
density plot this time so it gives you a
different uh I'd say view of the same
data right so it gives you so this is
essentially like plotting a
curve around this right so what our eyes
were doing implicitly is being done
explicitly here when you get a density
plot going right okay so so we've spent
some time now on looking at single stock
multi stock and doing some preliminary
data analysis data analysis right so now
what I want to do is I want to go and
jump into a strategy in terms of what
you can do using python to run a
strategy right so we are going to use a
very simple strategy it's called a
moving average crossover so here what
we'll do is uh we are going to compute
these moving averages so you compute the
average
price uh of a stock over say the last
few days right in our case we going to
look at run uh Computing the price over
say 45 days or over say 90 days and
every time the short moving
average uh crosses the the longer moving
average we are going to
buy the polarity is exactly the opposite
we are going to go short that is we are
going to sell right uh now this is a
pretty I'd say standard strategy that is
used in the markets it's referred to as
the hello world of Quant strategies
because um this is one of the first
things that people start experimenting
with when they uh want to start working
with systematic trading or Quant trading
right so we are going to do that here so
we create two variables it's called s
shorter look back period and longer look
back period referring to 45 days and 90
days and we compute the uh rolling means
or the moving averages so Computing
moving averages is done via the rolling
mean uh function in p uh in Python and
pandas so that's what we've run here we
Computing them and then we want to plot
them all to see how they look right so
what you see on your screen here is the
price of Nvidia over these last five six
years and these orange and green lines
which show you the shorter look back and
the longer look back right so what we
want to do is every time these lines
cross we want to take a position right
we want to go either long or we want to
go short so really speaking the times
when we do it is going to be say here
it's going to happen around here
is going to happen around here and so on
right wherever you see these crosses is
where we are going to start taking
positions and like I mentioned earlier
the position we take is either we go
long or we go
short right so when I say go long it
means we are buying the asset and when I
say go short it means we sell the asset
right this is not the same as selling
something we own it is
selling uh selling before we buy right
it's a it's a it's a specific concept
that happens in the markets you can look
it up you know online and see what the
meaning of Short Selling is where you
are essentially reversing the order in
which a buy and a sell happens so rather
than buying first and selling later you
sell first and then you buy back what
you sold
right okay so uh what we do here is we
create a column called position where we
denote one for going long that is buying
and we denote uh going short or selling
as minus one right so if the shorter
look back is greater than longer look
back you're going to encode that as one
else we going to encode it as minus one
that's what we do here we drop the nas
to make our life a little
easier and when we now take a look at
dat the data frame you'll see all these
new columns that we've created right the
shorter look back the longer look back
as well as the positions Vector that
we've created
now at this stage it would be
interesting to
plot uh all of these together to see
what's going on right so what we are
doing here is we are plotting the
adjusted clo the shorter look back and
the longer look back which had anyways
done earlier which is here but
additionally we also want to plot the
position uh column and since the
position column only takes plus one and
minus one uh we will have a a different
AIS for it so you'll have a y axis on
the right side which is going to track
what's happening to the position right
so let's do this
plot so when you when you look at this
plot notice that the left side the left
Y axis is for the prizes right for
adjusted close shorter look back longer
look back and the the y- axis on the
right is for monitoring what is
happening with the plus ones and minus
ones right so you can see that uh it was
was minus one for a little while in
2018 then it was plus one for like what
appears to be about a year then it was
minus one
again plus one again minus one again and
so on right that's what is
happening so in terms of uh the
positions we took over the years right
now uh at this stage if you want to
compute the returns of what your
strategy would have given you as opposed
to a passive investment strategy where
you just bought the Nvidia stock say in
2018 and you were sitting pretty right
so this is what we call a passive
investment approach where we just buy a
stock and we hold on to it we call it
Buy and Hold right so we create u a
column called Buy and Hold returns vnh
hore returns and we compute the log
returns so it's taken by Computing the
the log price of today's so today's
price divided by yesterday yesterday's
price we take the log of that right to
compute the returns and for the strategy
returns we need to essentially uh take
these Buy and Hold and multiply it by
the position Vector right so the
position position takes care of the fact
that we uh it it tells us when we are it
will multiply the right number based on
whether it's plus one or minus one
because we may be either long or short
right so this entire these two new
columns are giving you the returns of
the Buy and Hold as well as the strategy
right
so over the years what is happening is
as time Rolls by what you can see here
is that uh the Blue Line gives you buy
and hold so you started off here and
then you make a little bit you make a
little bit of returns and there were
there was a period when you you know
notionally were below 50% of what you
had invested right the returns were
really low because the The Firm did go
through some really rough times if you
invested around here and then around
2020 it picked up and then since then
it's it's kind of had a really good run
right until say about 22 and it went
down again and then it's again been
going up right that's what a Buy and
Hold is essentially done whereas your
strategy in some sense has managed
to uh go over this period quite well
right so you manag to uh take the right
kind of positions when the firm went
through some really rough rough times
because uh those moving averages seem to
have worked worked out
well around here the strategy has
actually cost you a little bit right so
the firm seem to be doing well but the
strategy has uh gotten you take
positions where you you made lesser
returns than you otherwise would have
but nevertheless you've still been uh on
the positive side more than the negative
side I mean overall you you've still you
know made money and again this period
strategy seems to have done right so
overall it looks like the strategy has
uh done better than a Buy and Hold right
so when we do take positions in a
strategy that is the least we expect
right because we are investing our time
our effort to craft a strategy and at
the very least we hope that it does
better than a passive investment
strategy right I'm not saying this is
the only way to uh
measure the performance of a strategy
but this is I'd say like one of
the first steps we do in order to
evaluate whether the strategy is doing
well or not comparing it to our Buy and
Hold okay so again we can just do a DF
to take a look at all the new columns
we've created we created all of this
stuff uh if you want to check what the
actual returns were over this
period uh this tells you that the Buy
and Hold would have fetched you returns
and by the way these are log returns
right they are not the typical numbers
that we used to
the the kind of returns that we read in
our investment books and investment
return uh you know portfolios that our
money managers may be giving us so if
you want to get a hold of that number
you need to uh kind of exponentiate
these numbers to get that value right so
which is what we've done here
so if you want to know how much would an
initial capital of $100 from day one AC
cre to at the end of this time period if
you want to compare say a Buy and Hold
with a strategy Returns what you should
do is you you kind of exponentiate this
number and we multiplied by 100 because
we want to compare it to $100 we want to
take a round figure so if you were to
run this what it essentially tells you
is a $100 investment in Nvidia back then
would mean you're sitting on a pretty
some of $6 $60 today and if you had
followed through with your strategy you
would have made like more than a, bucks
right so your strategy has clearly
outperformed the Buy and
Hold so this entire uh thing that we
went through now is to give you like a
glimpse of what uh back testing looks
like when we start working with
historical data and we want
to kind of see what would have happened
if I had taken those
positions based on certain rules that I
created right so as the name suggest
back testing means we want to go back in
time to see what would have happened
right so I would say this is like one of
the initial steps when we work with
strategies and start doing our analysis
