---
title: "Learn to use IbridgePy | Expert's insights"
video_id: "VSsMqDTkmsw"
url: "https://www.youtube.com/watch?v=VSsMqDTkmsw"
duration: "27:56"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Learn to use IbridgePy | Expert's insights

[Watch on YouTube](https://www.youtube.com/watch?v=VSsMqDTkmsw)

## Transcript

there's tutorial you can click one of
them or all of them that is if you open
ry. py you will find multiple lines of
file
name then next part let's talk about
interactive brokers inter interactive
brokers is LLC
we call it IB and it's a us-based
brokerage form it operates the largest
electronic trading platform in the
United States by number of daily average
revenue
trades um this is a Interactive Broker
so
website you can go
there take a look quickly yeah this is a
interactive brokers
sorry I'm just checking the questions
okay this is Interactive Broker main
website uh if you are interested in it
you can just click y
IBK then you can read through about this
page based on my personal
experience the advantages of
IB the most important to myself is is
Advanced AP API
technology API stands
for actually is uh automated program
interface which
enables traders to do
trading using
uh API actually it's a just a uh
interface between two computer so that
you can communicate
information and ab ib's Advanced API
technology enable traders to use
program to
trade that's the most important thing I
think for IB the next part is IB
provides very competitive pricing so by
trading with IB you can uh save some
cost and make more profit the next part
is IP offers Global Market access
if you go through the website you will
find I be access 125 markets in 31
countries and use 22
currencies so it's a
very uh convenience to do trading with
IB then the next part is how to do outo
trading with
IB just as I explained you can use p
some programs in
ibdp and then get connected to IB and
then trade this is the brief
introduction about Interactive
Broker the next part let's talk about
iage P IBD pad is a python
software helping traders to set up outgo
trading
platform at their own
computers or at the virtual computers in
Cloud
uh this is ibrid
Pi's website
www
ip.com
go there to take look together yeah this
is
I web web page you can take a look so is
is is the python platform to back test
and live trade with inter back through
Brokers but
actually in the most recent release is
you can use ibrid P to trade with Robin
Hood Robin Hood is a US based brokerage
form again and it offers zero commission
trading so if you are interested you can
take a
look the advantages of iage piie I will
talk about the first is iage pie can
protect Traders intellectual properties
because IBD P help Traders set up
everything at their own
computer so that Traders does not need
to disclose anything orst any
information on
internet think about other competitors
online most of them ask
trailers to code their
strategies on their
website so think about if you code your
python on a website
so actually ion in Python you cannot
hide anything and then you upload your
strategy to other website there
definitely some
risks of your intellectual properties
but think about it if you do everything
on your local computer computer then
that's you can control everything yeah
that's the safest way to protect your
strategies the next part of aage p is
you can back test and live
trade
together one place I will demonstrate
that the next part is you can use any
python packages including
uh Ai and then machine learnings and
other packages you can trade with
different Brokers manage multiple
accounts and run quantopian algorithms
if you are familiar with uh uh
quantopian
preparation there are a few preparations
to set up uh i brid p trading platform
but it's a pretty straight
for the first thing is to go to ip.com
slown we download iage pie
there go through it very quickly if you
go to download download average
p and if you are a user then you can log
in and then we can L there okay it's
there download the most Reon
version is there and if you are
interested what has been released you
can go to the release note and take
look right
there and
then so check out your operating system
it support
Windows Mac and ubo
Linux also you need to think
about what can now python you are using
if you are a Windows user you must
install an account of python but you can
choose to use you either
2.7
3.6 or
3.7 for others you can just uh uh follow
the instruction here what you need to do
is go
to HD P python 2 60p 4 bit if you are
using Windows
Anda
2.7 so what you need to do is just click
and download the Z file and save it to
your
local and then unve it yeah I won't
explain it too much because it's pretty
straightforward and
then what you need to do is to apply
Live account either a paper account or
Live account with interactive brokers so
you go to interactive brokers you can
either open a real account or click free
trial both of them works on iage P then
the next part is download and
install IB official terminals on your
local
computer one of of them called IB
Gateway the other way called Trader
workstation you just click the download
link yeah just click
download and install the software as
required it's pretty straightforward and
then config IB Gateway and
twws install a python because we are
going to write python code and execute
python code
so you need a python if you have any
questions you can go to IBD P tutorials
to read
it uh read the
instruction details tutorials
there there's tutorial you can click one
of them or all of
them other thing you may be interested
is I brid by
documentation so that you can see what
function
are provided in ibrid p and what are
their
performance if you have any other
questions maybe they are listed at a QA
section there you can go through
questions and find out the
answers another thing I would like to
introduce is the
community because the users are very
active on this
forum and you can see a lot of questions
and answers there just
quickly experience about that then the
next part is give you a demo
about how to config twws and IB
Gateway after you log
in to IBT
WS it will
looks like this you provide your ID and
a
password a few things you need to do is
config click
file Global
configuration left side on
API
settings on the right hand side what you
need to do is enable active X and socket
CLI make make sure the socket Port is
7496 and then click
okay that's all you need to do to config
twws is documented in the I Bridge P
tutorial if you miss it you can go back
to
there and
then let me talk about the I quick demo
here so first step is to open a python
environment right now I'm using
Windows so that I install
Ana Anda has its
own python ID
environment called
spider so I open spider
already you can see I'm using python 3.6
not the latest
python that is also supported
already typically I like
to organize my
windows so left side is
code right hand side is iyon
console what I like to is restart a
kernel at the beginning
and then first thing you need to do is
open the file in iage P folder called
run me.
py this is the main
entrance of aage
pack what you need to do
is first find out your account code in
IB Gateway All
twws In PWS you can see on the upper
right corner you will see your account
code d230 626 that's my paper account
code write it
down and then look for the r me.
py you can see
the account code is
here you just check change it to your
own account
code this is one thing you need to
do okay either real account or paper
account but I'm using paper account
right now then the next what you need to
do is to choose an IBD by ex example
code by commenting out all other file
names I mean
by that is if you open Ry
py you will find the multiple lines of
file
name with example code
there you
just comment in one
line indicating the python code you want
to run and comment out all
others that's what you need to do run uh
uh python code and then the last step is
just run run me. pii in Python what I
mean by that is just click
this green
triangle and run
it the demo I want to give you
is the first demo
is example show positions.
py so this code will download your AR
account information and display on
screen we run it and take a look pretty
fast let's quick look take quick look so
ibrid P verion
5.64 file name is showing up there the
next part is starting initialized
Trader and initialized Trader completed
when you see that which means your iage
P run while on your
computer and then the next part it will
print out your account balance three
numbers cash value portolio value and
positions
value then if you have any
positions for example I have
apple
Forex Euro to USD dollar and I have
spy which is the uh
ETF tracking SP 500
Index so this
is my
positions and you can trade the stocks
options Futures
Forex any contracts supported in IB
using aage pad then if you you have any
pending
orders it will list it up there you can
see I have one order order ID is
134 status is
submitted other information
there you can see this is a
limit to buy
limit of buy Forex USD uh Euro to USD
dollars limited price is 1 cent that's
why is still app pending
order and if you place
orders which cannot
be manipulated by the program it will
listed by perm
ID there so that your code cannot touch
it there
Amazon and uh in your Brokers stock
there then e and
D that's the end of the information
there okay this is the demo of how to
run i brid p if you want to switch to
other program what you need to do is
just a comment out this
line in Python you use
hash has
son then the next part is to comment out
this one this one example is to show
real time
price right
now oh Market is open
already let's still run this real time
price right now I'm
showing real time prices of Euro to USD
dollars you can see it prints out price
every second
yeah stop
there and I like to clean the kernel
every
time make screen oh this is the
code okay this code is a very
simple what I want to show you is right
now the market is open
I want to get the real time price of
spy and let's print spy as simple as
that and then go to run me. py and run
it you can see spy price coming in right
now because right now US market is
open see it's going on all right now
let's startop
it for example I just want to obtain
historical data what I will do is to
comment out the other code
and comment in this line so it will get
historical
data for example I just run it to I want
to give you a feeling about how it
runs so it print out the historical data
of
spy in my code I ask for the price of
Apple and Google you can see the
historical data comes in yeah this is
the quick demo of how aage P runs if you
are interested in what the code
in the
sample in the sample code what you need
to do is open
file this is the iage P folder and you
go to
strategies and look for for example this
is the code I use to get historical data
example get historical data. py you
don't open it up you can take look is
very
straightforward we Define symbol and
request historical data and then
print as simple as
P okay let's go back to the
presentation see anything else okay the
code
structure so we start to talking about
the python code I will talk about a few
functions uh at the beginning it may not
be as straightforward but please follow
me you will understand it's a pretty
simple actually in aage P there are
three basic functions the first one is
called
initialize this function is used to
declare average P Global variables I
will show you
example this function runs once at the
beginning of your
execution so which means just one time
if you want to run something one time at
the beginning of your code put it there
in this
function the other function is called
handle
data this is the function where you put
your trading
decisions it runs every second as
default but it's configurable you can
change
it and as I mentioned trading decisions
are made there if you want to make
decisions have a fixed schedule for
example every second every minute every
hour or even every day or every 10
minutes something like that you can
configure
it however you may not want to do
something
regularly as often as one minute you
just say I want to do something at the
beginning of the market 930 eastern
Time or you want to do something just
one second before the market
close so that you will use a function
called schedule function you can
schedule events there you can call
function there yeah this is the three
basic functions you need to
run you need to R your
code okay give you uh let's talk about
the code a little bit so initialized
function looks like
this in the example of show realtime
prices so this sample code will print
ask price of SP every second just what I
demoed for you so in
initialize I Define a global variable
called
security the way I Define it is I put
context do security so in this this way
context. security becomes a global
variable in average P so that you can
use in use it in other functions for
example handle
data Contex Out Security here and I use
a i function called symbol to define the
contract so I put spy which means I want
to trade spy
ETF and trade the
IB
then because I want to print ask price
ofp every
second so I put my trading decision even
if it's not trading decision but just
print action so I put the function show
real time
price in handle data so that this part
of code will be executed every second as
def4 and then I
put the global variable here and tell it
I want
to have ask PR there and then I put a
variable local variable called ask price
and then I just print as I showed you in
the example it just keep running every
second as we showed you the show real
time price and it just keep going it
just show real time price think about
you have the real time price you can do
the calculation for example when the
price is greater than $300 I just place
order so what you need to do is continue
this handle data and place order there
iage P will execute
that the next example is to fetch
historical dat
this sample code will fetch
his data of
spy daily bar from today go back to five
days same thing I put Global variable in
initialized to tell the code I
want to handle contract of
spy and then I put things in handle data
say first print and then use I function
called request
histor historical
data and then I say I want
spy I want the daily bar I want to go
back five
days then H is a pandas data
frame it has the return information of
historical data of py and then print
because I just want to do it
once once so I use end to end my
code and then it will print
out looks like this just as I showed you
in the the demo
