---
title: "How to Backtest a Machine Learning Trading Strategy using Python"
video_id: "SPyAu0crMt0"
url: "https://www.youtube.com/watch?v=SPyAu0crMt0"
duration: "8:48"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# How to Backtest a Machine Learning Trading Strategy using Python

[Watch on YouTube](https://www.youtube.com/watch?v=SPyAu0crMt0)

## Transcript

As I said, I coded a lot of code for the
the final aim to have a little to be um
messed up with when it comes to the
[Music]
user. The when it comes to the steps, it
really takes, you know, some time to
understand what you have to achieve and
how you are going to achieve it. because
uh we're talking here about probably
3600 lines of code. Uh surely you can do
something that's you know shorter,
simpler. I opted for a you know a more
enclosed and more designed program. Uh
and we will see why then. Uh but the
steps that I really followed was
defining the problem which is going from
the data to uh so price data to the the
final predictions. Uh designing a
program structure. How do you want to
design and implement the program? How do
you want the program to look and to be
used? Um and then yeah using functional
and object- oriented particles which are
very common within the software
development industry. Um and then after
having uh you know uh the the first
version of the program and the project
um I've tried to bring uh improvements
and new features. Um before finishing I
had to you know test usability because
the the program is very interactive and
then of course you want also to be sure
that the figures you come you come with
at the end are um reliable and so all
the the the calculations results and all
the figures that you have make sense. So
these were the main steps. Um let's
start with the overview. As I said, I
coded a lot of code for the the final
aim to have a little to be um messed up
with when it comes to the user. And so
basically we have nine steps that allow
you to use um my program. And the first
one is providing some uh details within
this dictionary. Um and yeah, you pass
in the the stock you want to analyze the
dates um of the time frame and then
because here we run uh a scraping from
Twitter, you can pass some uh parameters
that are related to Twitter accounts and
uh
key keywords for for you know for
hashtags and searching those posts and
um yeah that's it. That's these are the
parameters you pass in to let's say
define your analysis on the stock the
time frame and the the Twitter content
and then we go ahead and we have few
methods um that will basically uh
exploit the whole program. Uh the first
thing you do is to uh initialize a
pipeline uh which is um um a direct
click graph in this case where all the
functions get pushed in and each
function output will feed the next
function input. Um so you initialize a
pipeline you call the run method of the
instance of the pipeline in which is our
first step and then you basically end up
with the data and the data will be the
one the the the data set where the the
the program will um compute the back
testing calculation. So once you have
the data you retrieve those data and you
initialize in our fifth step uh the back
test strategy. Now this back test
strategy uh class has few methods which
we will see in the next
slide. Uh like in point 6 we uh can
pre-process data which means take care
of missing values uh outliers um any
anything that has to do with cleaning
the data manipulating the data so that
we can feed correctly the machine
learning algorithm and then you you can
start training the model with the
seventh method uh and uh test the model.
All these uh steps are let's say
recursive and interactive. So that
basically once you call one of these
method you will be prompted with a menu
u driven program and you will just input
data as you are interacting with any
other application um within you know
your environment of development and yeah
you can write files you can save files
you can delete files from this program
which are related to the machine
learning model and the program will do
everything for you. uh at the end
there's the last method which is
strategy performance and you basically
call that to end up with your plots and
uh tables that will show the result of
the strategy which we will see in the
next slide. So this is one of the table
that get as a output. Um so as as we see
we have the the return of the buy and
hold strategy as as well as the
annualized return and then we have the
returns of the the trading strategy. Um
and then we have few more parameters
like sharp ratio um the total number of
trades that the the back testing um
carried out, the heat ratio which is you
know how many trades were successful and
then you have um how what was the
average profit for each trade? What was
the average loss for each trade? the
maximum draw down. Uh so how much went
your uh account down um it its maximum
figure and how many days it took to
recover from that um draw down. And this
is this is one of the the outputs that
the program will give you to analyze
your strategy whether it is uh you know
worth to be uh further developed or
implemented. And then you have some
graphs. This is for the draw down. So
you'll see you have you know uh what we
have seen as 1.42 42 we have here on the
graph and it happens around um probably
that was March 2020 so when the pandemic
started um and yeah you so you you you
find you know visualization of those
figures on on your plots and you can
have a sense check and then you have the
the returns plotted and this just
compare the buy and hold strategy which
means just buying the stock and and
holding the stock on the same time
frame. as opposed to um if we were
trading according to the strategy. And
so we we have here in orange we have the
trading strategy. We see it's it's a
very uh steady curve up um which was
catching towards the end also you know
returns that the the just the the stock
couldn't do it was just falling. So this
let's say um can give us how the the
strategy performed along the the time
frame. Uh and again we can see in March
2020 uh when the stock went down because
of the wider market going down the
strategy kept you know making money uh
which is I mean it's it's good to see
however um you guys still have to uh
take in account all the simplifications
that a program like this uh brings uh
when when compared to uh actually live
trading the strategy. Um, one of the I
think the one of the last improvements I
did was to include transaction fees into
the the
um back testing strategy and also uh the
the
um the option to uh give to pass in how
much of your account you are trading at
each trade because those are you know uh
circumstances that you you have in real
trading. And so um yeah, this was one of
the the latest um improvement I did. And
once you tweak these parameters, you can
see how the strategy changes in terms of
total returns as opposed to the the buy
and hold strategy. Um yeah, this is
pretty much basically how you use the
program. Um at the end of this webinar,
you will have uh links to the the GitHub
um repository. So if you want to um you
know uh get your hands dirty with the
program you are feel free to do it clone
the repository uh recycle this program
use this program for your own research
or just to understand or experiment. Um
but yeah you will see that the program
is very very easy to use and everything
is documented on my uh GitHub repository
page.
[Music]
