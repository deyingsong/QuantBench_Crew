---
title: "Python Trading with MT5 and Interactive Brokers | Automate Your Trading Strategies"
video_id: "XQDP61YJJEU"
url: "https://www.youtube.com/watch?v=XQDP61YJJEU"
duration: "24:25"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Python Trading with MT5 and Interactive Brokers | Automate Your Trading Strategies

[Watch on YouTube](https://www.youtube.com/watch?v=XQDP61YJJEU)

## Transcript

so now let's start with an example let's
understand uh how this integration of
python happens with various platforms
and in general if there should be a
communication between broker and python
there is a straightforward way which is
through broker API you can you can use a
broker API while you're coding with
python but this is a complicated way
because you need to develop your code
from scratch and it would be a very
lengthy code and the second way is to
use a python rapper where most of the
methods are already written for you you
can just import the methods for the
general actions which we do like getting
data placing orders Etc and seamlessly
integrate with the broker API and
communicate with broker so these are the
on a high level these are the two ways
you integrate a broker and python uh
through broker API a straightforward way
but you need to build code from scratch
and through python rappers uh where the
functions are already available the
methods are already written and you just
need to use those methods or customize
those methods so let's understand uh
with an example of python rapper for mt5
so let's see a live implementation with
mt5 so I am just moving to uh another
document which is a Jupiter
notebook so we will go through all the
steps that were discussed so far but uh
with an
example uh there are few PR prerequisits
before you actually do this so the first
one is to have a desktop application
ready so you can uh download you down
you can download from this particular
link based on the platform you're using
and I've already downloaded it and I
have metat Trader ready with me and this
is how the metat trader desktop
application looks like and the second
one uh you need to install Python and
that you can this particular uh notebook
or the document will be shared with you
so that you can also explore these links
so you need to install python since we
coding with python and once you install
python you need to install metat trator
so these are the basic prerequisits you
would need in terms of
installations and once you going through
these installations you need to open a
demo account and get the login
credentials so I'm going to show how
that is
done so you
can I'm sorry so once you open your
desktop platform uh you can click on uh
accounts and you can right click and
click on open an account so this is how
you can open an account you can go to
navigator accounts and open an account
and by default meta C limited will be
selected you can proceed with that and
post this uh you can either open a demo
account or a rear account but let's go
with the demo account so that you can
you can explore this and with the demo
account you can uh you can fill these
details your first name last name email
ID uh mobile number Etc and you can also
select this option if you select this
option you would have hedging so I'm
sure most of you know what hedging is
basically you would have margin account
and you can take advantage of Leverage
so you just need to fill these basic
details and click on uh agreement and
post that your account will be uh
created
instantly so you can copy the
registration information to the
clipboard and using this we will proceed
our uh proceed our demo know so uh you
could as you could see I have pasted the
same information the login information
like that was uh just created which are
um which are these so a login account
for login and a password so this is the
demo account I created and you can also
create it instantly so let's move ahead
and let's go through all the steps we
have discussed so far and see how it is
done in life so the very first step for
any kind of automation be it mt5 be it
metat Trader I'm sorry uh be it
interactive brokers or be it am broker
or Joda or alpaka anything so the first
step you do is to establish connection
but before that uh get the documentation
handy it's a very good habit to at least
go through the documentation and
understand what kind of functions we
have and as you could see this is the
documentation of mt5 like python metat
Trader five and there are certain
functions for example there is a
function called initialize which is used
to establish a connection with metat
Trader terminal so like that there are
functions for every uh every action you
would have to take and we would use the
functions that are there from this
particular link and as we move forward
I'm going to show them also and the
practically so the very first step is to
establish a connection so for that uh
we're going to use the same login ID and
password we got by registering the
account and we would just use an
initialized method so the very method we
have seen from documentation the
initialize so using this by giving the
details as you could see the
initialization is
successful so what if if I if I give a
wrong password uh it would give me
initialized failed message and also it
it get a audible notification also but
once I give the right password right
details uh as you could see a CH and
also the message is initialization
successful so in general this is what we
do when we are manually trading when we
are manually trading we would enter into
our platform be web based or offline we
would enter our login ID and password
and we if once the authorization happens
then we would move forward and uh as a
natural step we would want to check how
much money we have in our accounts and
if we have any positions open so that's
what you can do by using the method
account info so there is this function
account info that is already built since
we are using this is python rapper which
is an official python rapper by
metatrader that's the reason the the
name is metatrader f and since we're
using that we can use the methods that
are already there by using the accoun
info method by running this code you can
get the current information see uh
currently I'm not holding any position
so profit is zero and I have
99996 188 in equity and and there is no
amount that is held for margin and
entire amount is free so I can see the
same thing here as well if I go to the
platform I can see the same thing the
current balance is this which is exactly
what we have seen here and also uh free
margin like almost all in fact entire
amount entire balance is free for
Mar so we have done the very basic steps
that we do even in automate manual
trading so the next step is to get the
data uh here is an interesting part so
when we are uh when we are doing uh
manually there are there is one minute
data which we are used to 15 minute data
daily data Etc but programmatically we
can resample into any data we want like
you can get the B the data like one
minute data and resample it to let's say
5 minute 20 minute 30 minute Etc but
interestingly with the python rappers
they give you uh many options for
example uh there uh there is a method
called copy rates from so this is the
method you use to get data but it needs
certain input right it needs certain
information to get the data so the very
first information is symbol even when
you are manually trading or if you're
searching for a chart the first thing
you input is the symbol so let's try for
uh Euro AUD Australian dollar and the
time frame what data what frequency of
data you want if it is daily data you
can use this method uh if it is early
you can use this method and there are
method for many time frames so let's use
uh daily and end time so in general end
time would be you can define an end time
so currently the end time is defined as
uh the current time and how how far into
the history you want me how many data
points you want for example if I give
the time frames as daily and if I give
end data as 20 I would get the past 20
days information let's see how it works
so I have run this code and as you could
see there is some information I got in
the form of an array and this is not
clear in fact I could see the first data
type is time but this is not clear this
is in the form of Unix and the SEC
second one is open price then the high
low close tick volume but anyway this is
not clear for me because uh this is just
in a form of an array so we have created
a function you can directly use this
function and uh and get the same data so
let me get daily data so you can use the
same function that is created and the
name of f forx data and I just used that
function and that function also uses the
method that is there in the
documentation is just that taken care of
the conversion of the time which comes
in Unix format we have changed into date
time format so that we can understand we
also Define the time zone currently us
Eastern time zone is defined so now it
is much clear so you got we go we got
the same information but it's just that
uh the data is clear now and currently
let's just check for same yes so I was
checking for Euro AUD with this
particular method and we got this
information in the form of array now we
have used this custom function created
and then got the information for the
same symbol and now it is more
structured now I can clearly see what
date and time the data is data belongs
to which is open high low close and
volume two so you can get uh you can get
data of other contracts also for example
if you go to metat Trader platform you
can see some contracts here for example
gbpusd I can also search for um
gbpusd and I get the
information but this is daily you know I
can also get one minute data as you
could see this is one minute data now
this is live data and and uh this is
data for today and this is live and in
fact interestingly I get uh I can get 10
minute data 12 minute 2 minute 20 minute
there are lots of methods that are
available this is a common feature for
all the python rappers and you can you
can get any kind of data uh you can
choose the time frames you want and
accordingly you can get the data so uh
naturally uh once you get the data the
next uh please don't mind this uh ches
so is from the trading platform since we
just connected so once you get the data
you can also get the tick data I'm not
going over tick data now you can explore
this once you get hold of this
particular document but let's go to the
important part which is defining a
trading logic and generating trading
signal so this is the reason why we
automate right so let's understand that
so you can uh see this is the place
where uh see last time when I launched a
poll 70% of the people have said they
have already explor like they don't want
to explore strategies now they don't
have a strategy ready but they want to
focus on Automation and 30% has already
had strategies so this is the place
where you make most of the difference or
most of the impact and because the
entire profitability depends on the
strategy you pick but as of now for this
demo I'm showing you an example
strategy and let's take an example
strategy that is uh quite understandable
by most of you guys which is a moving
average crossover so I've taken a pretty
orbitary numbers like five and 10 and I
would want to generate trading signals
based on uh moving average five and
moving average 10 and based on the
crossover if the uh five moving average
is greater than 10 moving average I want
to buy and in other case I would want to
sell so this is the basic strategy of
return return and as we move forward
into the webinar we will also see how to
get hold of other strategies too and as
you see I've used the same methods that
we discussed so far I've used this
particular function to get the data and
just calculated the moving averages and
generated a signal for example if I run
this um you can see I've generated a
cell signal so essentially it generates
a cell signal when five moving averag is
above 10 moving average that's what
happened here but we don't stop here
let's also Place some mods so
understanding trading logic and
generating signals is not where we stop
but we do Place orders too U you can
place orders very easily uh there are if
you go to documentation you can see
several methods that can help you to
place orders so you can see here uh how
to place orders but let's we have
created a function for you because to
place orders you need lots of
information you even when you're
manually trading you would place an
order by place by giving an information
of the symbol number of lots you want to
uh trade and whether the order type is
buy or sell and do you want at what
price you want to trade and etc etc so
this function takes care of all the
default methods that should be filled
and you just need to give the symbol and
the lot so that's how there are two
functions that were built for you for
for your practice which is play buy
order place sell order so you can
practice with this uh I would also show
you how it is done
uh for
example so let us use the method by
place order and let's give a symbol and
let's give some uh size so if I run
this now I could see a message saying
order play successfully and I've have
got an order ticket number so I'm going
to trading platform and I just want to
check whether the order been placed or
not and as you could see the order
number is this 1 15 and it ends with 748
and you can see the same order on the
trading platform and the order has been
placed and that's a buy order that's
what we did we placed a buy order for
USD CHF so let's try something let's uh
place an order for uh you guys can type
it out you guys can type it in the chat
what Forex symbol you want to uh you can
see Euro USD GBP Great Britain pound USD
USD CHF which is Swiss frank
Japan uh let's Place some order uh let
me see the chat you guys can type in the
chat and let's try to play some orders
and see if the uh platform is picking
the orders or
not
okay so people want the USD okay there
are many things like the most recent one
uh was great bitten pwn USD okay Mr
Ganesh want to see uh if you could do
this so let's see you want GBP USD right
so I guess four or five people wanted to
see if he could place order so great
Bain pound
USD yes so we have successfully placed
order so let's see we have placed a buy
order on Great Britain pound and USD for
a lot of 0.01 so so we can see it here
for the symbol gbpusd we have placed an
order just a moment ago a buy order and
with a volume of 0.01 so this is how you
place order so let's Place one more
order let's place a sell order let me go
through the chat and see what other
thing okay people want Euro USD which is
quite popular so let's do we have a Euro
USD already placed no so let's place a
sell order for EUR USD
now uh let's see so order has been place
now we place a cell order so you can see
uh it's in red which is a cell order
which is Euro USD just placed and it's a
cell order so this is how uh we can
place orders very easily using a python
rapper and this is not common this is
not only for mdy this is common for all
the trading platforms which provides
python rapper and we going to see how it
is done as we move forward but uh why
not uh why don't we use the strategy
that we have right so for we have a
basic strategy moving average crossover
which is generating a cell signal so
let's use this so um I've written some
code so I written like if this
particular function the strategy for
this symbol gives a p signal then let's
place a bod so we use the same methods
that we tried out so far let's place a
by order if the strategy gives you a
cell signal and then let's place a cell
order so I'm just okay I just ran it now
uh it is placing a cell order and the
ticket ID ends with
31 uh yes it is
here so there are orders that are uh
continuously placed if you want you can
also change the symbols and see how uh
the orders are being placed so see uh
I'm just going to this particular
desktop platform to show you that the
orders are placed on live but you don't
need to again and again open the desktop
platform right so you can also monitor
your positions by using this method
called positions undor get so I'm
running this code just to see how many
positions I have as you could see I have
four positions and even if I go to my
trading platforms I could see I have
four positions and uh let's uh go
through see uh let's run it again and
currently the profit is 0.2 and it's
about 0.2 and it's quite Dynamic and
it's quite live and uh I can actually go
through and information here the symbols
same thing we placed here so I can not
only place orders I can also do the
things that I do in general when I
manually trading this is what I do when
I'm manually trading and I'm sure others
to to go through their positions and see
I can do certain data analysis also on
this for example I can if I want to
close all these positions I can close
one position after another this is what
we do generally right if you're manually
trading you might click on close and
close one position after another there
and you can also do it you provided a
code for you to close existing positions
it's just a loop that goes through each
row of this data currently we have this
data saved um so I let me just run this
and show you so the data is shown uh
saved in the data Frame data with four
orders so we can just write a for Loop
which goes through each order and if the
order is a buy order it would place a
sell order and close it and if the order
is a sell order it would place a buy
order and close it so that what happens
here uh it is checking the positions
from the data and if the position is byy
it is placing a sell order to close the
position and if in other case it is
placing a buy order so let's run this
and I've run this code and you could see
I got four messages that these four
orders has been closed have been closed
and these are the information of the
orders that were used to close this
position so essentially we should not
have any orders now as you could see the
orders are gone now we don't hold any
position because we have closed the
existing positions so as you could see
if I if I monitor my positions now it
says no positions F so this is how uh
you can automate every step of the
manual trading you do and also could do
it much faster and efficiently according
to the way you code it uh for example uh
you don't need to write this big glp you
can also close a single order tool let's
do this simple exercise let me go to
your charts and pick up a
contract that is widely asked to place
an order okay so again Euro USD let me
place a buy order and just see how the
single order can be closed so earlier we
had no orders now I just placed a buy
order for Euro USD as you could see I
have a single order here and let's see
how to close this single order so I can
copy the uh order ticket number and you
can can check this code which is at very
end of The Notebook which is close
single position so I can just give us
order the order ID of a single position
and if I run this code uh you can see I
can run it uh run the single code and
now I could see position has been closed
successfully with this order ticket and
if I go to the platform now I'm left
with no orders so these are the general
steps you do to get the data uh let me
go to the
presentation so in general uh these are
the steps you do uh to get the data and
do analysis generate trading signals
Place orders from broker and also get
confirmation from the broker that is the
most important part if you could
remember the very first part is to get
confirmation from the broker about the
authentication right you get
authenticated by the broker and at every
step you get a confirmation or a message
from the broker that the step is done so
now we have seen an example a live one
with metat Trader and it's an example of
a rapper you can also do it similarly
with an API too and metat Trader gives
you an API which is a meta API it's a
broker API and you just need to follow
the methods that were given in that
documentation so for example if you want
to do it for interact to Brokers there
are multiple ways to do and you can use
a broker API which is twws for example
let's go to let's go to the example of
md5 we uh discussed in depth so as you
could see I in I've installed metatrader
5 because I'm dealing with metatrader
that's the reason I installed the
desktop application of metatrader python
and then install the python package
related to metat Trad what if if I have
to do with interactive brokus right then
I need to install Traders workstation I
would install Traders box station I
would install python of course and I
would install a python method that is
used by interactive brokers and the rest
of the steps would be same you need you
still need to establish a connection
even changes and it would be similar you
just need to go through the
documentation to get this particular
initialization method you just need to
change this method nothing else need to
be changed most of these would stay the
same but you just need to see what is
the name of the method for or the
function for initializing and you would
use that from interactive brokers and
once you do that you get your account
information the same way you find the
method that is used in the documentation
to get the account information and use
it here similarly you get the data and
uh Place orders all these things are
same for example uh this is a
documentation of interactive brokerss
and here I could see uh I have an order
method already this is a documentation
with all the methods and you can go
through it and this is the way I place
orders so there is an order function and
I need to provide these information and
I can place an order we had to give a
market order I need to give Market typ
as MKT if it is a limit order I need to
go order typ as LMT so the same code you
use it here this is the structure we
followed for md5 according to the
documentation of md5 and you just need
to replace this code with uh the
documentation of twws API by the
interactive brokers so that's how all
the steps are SE and the processes are
same it's just that the methods you use
would change as per the documentation of
this particular brok
