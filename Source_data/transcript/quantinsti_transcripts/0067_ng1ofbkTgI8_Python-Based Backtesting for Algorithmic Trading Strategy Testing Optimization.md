---
title: "Python-Based Backtesting for Algorithmic Trading | Strategy Testing & Optimization"
video_id: "ng1ofbkTgI8"
url: "https://www.youtube.com/watch?v=ng1ofbkTgI8"
duration: "13:31"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Python-Based Backtesting for Algorithmic Trading | Strategy Testing & Optimization

[Watch on YouTube](https://www.youtube.com/watch?v=ng1ofbkTgI8)

## Transcript

[Music]
blue shift which is
uh blue shift documents page it should
tell you what it is all about right so
blue shift is another product that we
have at quen which is a platform where
you can uh both research as well as
trade investment strategies and this is
where you use Python to do uh any kind
of strategies that you want to work on
so you use it both to try stuff out and
in case your experiments turn out to be
interesting and they seem to show some
promise you can take it live into the
markets right uh so what I have done
here is I have for the sake of this
lecture I was playing around with some
stuff I want to show you guys what we've
done here right so here what we have
done is uh we are taking a Binger band
strategy from where we want to work with
the New York Stock Exchange data where
uh this is a long short strategy using
based on buer bands and SMA dual signals
so that is what this strategy
essentially does the whatever I now talk
about is less about the strategy and
more about uh all of the analytics that
we get once we run it uh and I want to
talk to you guys about how you know
platforms such as blue shift uh help you
get a much more well-rounded picture of
what your back test results look like it
gives you a slightly more realistic
picture than uh say what we do on our
own
workstations and uh it also helps you
take take stuff uh take uh things live
into the markets right based on the
Brokers those kind of things so uh let
me first give you guys a little idea of
what's Happening Here so like the way we
imported stuff you'll notice that even
here there are a bunch of imports that
first happens show you what's happening
so you import some technical indicators
like Binger bands and EMA which is
exponential moving average you import
something called commission and slippage
which we try to account for and then
there are some blue Shi specific uh API
calls like symbol order Target percent
set commission and so on now the first
thing we want to do is we want to select
a universe we want to select a universe
of uh Securities that we want to
consider when we launch our strategy
right so in this case I picked uh some
really large firms uh from the from the
US uh stock exchanges both NASDAQ as
well as NYC so we've got Adobe which is
a software firm then General Electric
Microsoft Nvidia this is meta which is
Facebook this is Tesla Tesla uh this is
Visa and this is another I forget the
name it's a I think a microchip
manufacturing firm so this becomes like
our
universe what we are doing here is we
want to work with one minute data by the
way and we've set some thresholds some
SMA period short long Binger band period
and so on right uh like I said this part
of what I'm covering with you guys is
not so much about the strategy it's more
about what emerges when we run the
strategy and uh you know run a bunch of
back tests or decide to do some pap
trading with the strategy that is what I
want to talk about right so if you go
through all of this stuff uh it it
defines certain strategy parameters it
defines certain variables to track
signals and Target
portfolio uh for for the sake of this
part we've essentially set trading cost
and slippage to be zero you can
obviously add some uh costs here based
on how things work at with your exchange
whichever part of the world you are in
and then there are certain other
functions like handle data uh run
strategy and so on now I know this this
program might look a little daunting but
the good news is that uh with regard to
Blue shift it had you know we have this
GitHub page which has got like a lot of
sample strategies and uh you can take a
sample strategy paste it in the core
editor here and makes very minor
modification to uh try stuff out right
so you don't have to start with a blank
uh you know C canvas you have like I
would say certain quite a bit of starter
code which you can use in order to
um take it as a base and then make
changes to it when you're working with
something
right so anyway so with respect to
this if I were to say that okay I want
to run it on us equities so we'll be
essentially working with us Equity is
minute level data and say since it's
minute level data I want work
with say about 3 to four months so let's
start on 1st of June
till you can say 27 September and let's
presume that I'm working with a capital
of
10,000 so I say
run so one of the things that this
particular strategy does is it's an
equal so it's trying to uh allocate the
same amount of capital to each of my uh
Securities right so I have 1 2 3 four
five six 7even eight and uh since I have
eight Securities I would not want to
invest more than 1/8 of $10,000 on any
of them right so this is like an equally
Ved approach to creating a portfolio
obviously one can choose many different
approaches we can uh size we can you
know do some position sizing based
on how our stocks are performing and
that's again you know something which is
slightly outside the scope of what we
want to talk about for for today
interestingly here what we are doing is
while we run this back testing it's
giving you it's telling you what the
results are telling right in in terms of
what would have happened if I had
followed through on these rules say from
June to September so that's like three
or four months right so it's giving you
an idea of how the Benchmark performed
and how your portfolio is
performing so let this run and while
this runs I'm going to click on uh uh go
live we'll come back to the screen in a
bit but I'm clicking on go live for now
which will show you what happens if I
want to take this live right so I run my
back test let's say I like how things
look what I then do is I click on go
live so it says uh you want to make it
compatible for a live run on Blue shift
so it gives you some things that you
that things are happening so let's just
click on accept and execute
at this stage it says uh go to settings
settings gives you some ideas on risk
management so tells you that if do you
want to set certain limits on how low
your Capital can go if it goes let's say
below 50% your Capital you want to
terminate the the the strategy the
algorithm it tells you how many maximum
number of orders that you can send it
tells you the size and so on right so
I'm just going to stick to the default
values and say save and close right now
essentially what I'm trying to do is I'm
trying to do paper trading that is I
don't want
to put actual money but I want to uh
based on how promising or how my back
test results looked I now want to paper
trade that is to say I don't deploy real
money but I uh decide to take
positions uh and see what would have
happened if those positions had been
realized right for I I could observe it
for a few days few weeks as per my wish
so I'll say continue here I'm going to
select broker so I have a paper trading
account with alpaca it's one of the US
Brokers so I'll say select
broker I'll say that I want to run it
between say today and tomorrow I could
specify a capital of say
25,000
continue it gives me an option of Auto
confirmation so I say auto execution
or it says one click where at the very
end the user needs to click on whether
you want to go live or not so I'm going
to go for
auto accept terms and conditions so I
will just go and say I
accept then says review all information
so I say
review this is my strategy I have an
account with
alpaca uh auto execution Capital risk
settings all of this looks okay just
selected default I
[Music]
confirm and this is how it begins right
uh so it gives me some details on what's
Happening it says creating necessary
resources for the algo execution so this
is like the console which gives you an
idea of what's going
on so
so
um I could take a look at
trades to see if any positions have been
taken I can go back to the dashboard I
can go to the code so any of these
things I could do at at any stage right
I can also stop my algorithm at any
stage I want right now since I have been
doing this before I I was also running
some other stuff before this lecture we
can even go and take a look at uh
um other things that I've been running
before this lecture that should give us
a little more idea so let me look at
something I started
yesterday so even this is running if I
were to go and click on trades it tells
me that on 27th of September at 11 uh
there was an buy order for Adobe but
this order didn't get filled right this
Adobe order got filled So I placed an
order for a I mean placed a uh you know
a request for a to to buy four but only
one got
filled here I want to buy four and all
four got filled so it says complete and
so on right so this is for Adobe this is
for shop so different stocks and it
gives me a picture on what happened in
the previous dat right so in general it
gives you so what I'm showing you is we
started off with back testing and then
we are now doing paper trading to
observe for how many other days we want
right
okay so let's go back to
uh what we see here so it tells me that
if I were to have run this strategy from
1st of June till 27th of September I
would have got returns of 5.43% so this
gives me like a quick description of all
the things that could have happened if I
want like a detailed description I need
to go and click on new back test and get
all those details since I've already run
it in the past I'm going to show you
guys directly what happens when you run
something like the new back test right I
mean detailed back test so previously
previous to this when IID run it IID run
it from 1st of May till 26th of
September and it tells me
uh what the performance metrics of my
strategy are so it gives me annual
returns cumulative returns and all of
this stuff right in terms of how it has
done it gives me things like sharp ratio
which is like Risk adjusted returns uh
gives me details on draw
down
uh there's also a tear sheet
where you can look at different things
like even you know a histogram of
returns the heat map of returns and what
positions we took on each of those
stocks
right uh you have some details on per
trade metrics so you have what happened
on the short trades what happened on the
long trades and so on
right you have actual transactions that
took
place so you have things like okay six
quantity of adobe was bought on say 1st
of May this is a back test right
remember this is a back test on 1 of May
at 935 we bought six stocks for at a
price of say
374 and then G we bought like 23 at a
price of 100 and so on right it gives
you all these details it gives you also
ideas of round trips so round trip is
both a buy and a sell for a given
stock so for instance here you
bought uh at 3749 and you sold at
37.17 your loss was minus 4.44 and right
so it gives you all these
details what basically blue shift does
right
[Music]
