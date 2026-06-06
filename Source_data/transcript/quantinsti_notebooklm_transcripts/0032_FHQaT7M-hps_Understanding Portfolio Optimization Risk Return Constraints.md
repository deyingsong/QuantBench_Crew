---
title: "Understanding Portfolio Optimization: Risk, Return & Constraints"
video_id: "FHQaT7M-hps"
url: "https://www.youtube.com/watch?v=FHQaT7M-hps"
duration: "37:06"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Understanding Portfolio Optimization: Risk, Return & Constraints

[Watch on YouTube](https://www.youtube.com/watch?v=FHQaT7M-hps)

## Transcript

And I can see this I can very clearly
see this max sharp portfolio. What I
want to see is what are the weight
proportions of every ETF in size. I have
a 1% weight in of the asset and call it
optimal. This is quite impractical. I
would actually want something else. And
from those portfolios we plugged out the
most optimal. So now allow me to
introduce you the CVXP by right which is
basically our solver.
Hello everyone and welcome to the
channel. Today we are going to talk
about portfolio optimization.
Well, portfolio optimization
lies at the heart of quantitative
portfolio management. It is a very very
very pertinent important topic for all
asset managers for qualitative portfolio
managers for budding qus even for data
scientists. So what we going to do today
is going to help a lot of you watching
over here and the way you're going to go
ahead with portfolio optimization is
going to be very very unique. So stay
tuned.
Now many of you may have heard of
portfolio optimization. For those who
don't know, let me just put things in
perspective. There are three major steps
to portfolio management. Number one is
to select the asset which is the asset
selections.
Number two is the asset allocation step.
And number three is to monitor the
portfolio and rebalance the portfolio.
So number three about portfolio
rebalancing we have one video which was
recently uploaded but today our focus is
going to be the asset allocation which
is the second step. Now what do I mean
by asset allocation? As the word
suggests we allocate our exposure we
allocate our capital to these different
assets in a portfolio. It's as simple as
that. But the s game and all hard work
that goes behind it and the complexity
behind it can be much can be a handful.
But why do people take up that city?
Because historically it has been seen
that even more than how you select
assets, asset allocation has played a
major role in creating alpha for a lot
of portfolio managers. So if your asset
allocation is right,
your portfolio with the same assets of
another form manager could actually be
performing better. Now a lot of you may
be familiar with the efficient frontier.
So I'm not going to go into a lot of
math. I'm not going to bore you with a
lot of statistics or formulas.
But what I'm going to do today is to
give you a visual a visual understanding
of how we can bridge the gap between
model portfolio theory while the
makovit's efficient frontier sales all
the way to how you can actually apply it
in real life and we're going to do this
in python I want you to focus with me
once you focus step by step I have
broken everything down into steps you
will have a better understanding of how
to do things by yourself and experiment
by yourself. Okay, so let's get to it.
So as the very first step, I'm going to
import all the necessary libraries. I
have these libraries installed. In case
you do not have some of these installed,
you can install them if you want to code
with me. Okay, so I will import Y
finances app to pull the data. I'm going
to be using pandas and numpy to to do
all the computational work. CVXPY
is an important library for today. I'll
get into details with it when we come to
the next portions of this particular
tutorial. Then I have got import plotly
plucky and map plotlet and seabboard.
All of this is for visualization. Okay.
So once I import this then I come to
this point and what I'm going to do over
here is I have taken these stickers. So
SPY stands for equity, SP S&P 500, TLD
stands for bonds, GLE stands for gold,
QQQ for NASDAQ and EN
for the emerging markets. So all these
are basically are ETFs. Okay. And the
data for this ETFs is being downloaded
from Yahoo Finance. The data I'm going
to take is 2018 to 20 end of 2024. Okay.
So once I have a price data, this is how
it looks like. And here I have all the
price data from 2018 onwards over here.
Okay. Now as a step two which I'm not
going to spend a lot of time on because
I believe a lot of you know these basic
things. First I take the log returns the
log returns of all this data. I find the
mean returns as well as the covariance.
Okay. So once I have all this we can
check how mean returns look like so that
you know we are all on the same page. So
mean returns look like this with
different tickers. this out. Okay. And
the covariant matrix, the covariance
matrix is going to be slightly bigger in
nature because you've got what? You've
got about five tickers. So this is how
it looks like because each one of them
has some cool with each other. Okay,
moving on. I simulate portfolios. Now
that I have my mean returns, I have my
coariance matrix. I'm going to use the
mean to find out how much each portfolio
is going to create as returns or is
expected to create as returns and
covariance matrix I'm going to be using
to compute the expected analyze
volatility. Okay. So this is how we do
the very basic step which is to come to
a point where I have the efficient
frontier. Now this simulation is
basically a random simulation. What is
happening over here? Please note, I'm
going to simulate 10,000 portfolios.
Okay. And the length of the tickers
which is five stocks or five ETFs here
is my N_asset.
Okay. Here I have put random C2 just in
case I want to regenerate it and compare
something and I'm creating a particular
dictionary called results which later I
will turn into a data.
Now what I'm doing is I'm creating
weights using np.trandom.trand.
Now np.trandom.rand
for all the nump by module called
np.trandom
does something very interesting. It
picks some numbers from the overall
normal distribution from minus1 to one.
Okay. The standard normal distribution.
So if it takes standard normal extreme
variables which can all go all the way
to minus one or go all the way to + one
then we have the different combination
of waves it is assigning and very very
random positive or negative numbers
obviously less than one and greater than
minus one
here I'm going to normalize this so I'm
going to use the absolute weights and
normalize this over here Okay, so the
normalizing of the sum to one is going
to happen.
Now I have my portfolio returns which
will use np. the individual weights for
every iteration because I've got input
folio there'll be 10,000 iterations for
every iteration I'll be having a
different combination of pairs and then
the majors
and from there I will find out also my
portfolio volatility by simply plugging
in the volatility formula I use the
coariance matrix I earlier computed for
this
and then finally and finally sharp
dation okay so the sharp ratio of every
portfolio is something which I compute
over here. Okay. In the end,
I'll store all the these results into my
dictionary results
later. This will become my portfolio_df.
So, let me run this. Now that this is
done, let me run this and let me just
quickly visualize how portfolio_df
looks like. Okay. So this is how it
looks like as well weights which are
very long numbers because of decimal
numbers. Remember everything is between
minus1 and + one. So you have very small
numbers a lot of long decimal numbers.
Anyway, let me just delete this for the
brevity and then we go to step four.
Step four what I do is I plot all these
portfolios which I have my portfolios_df
and you can check this out. This is a
scatter plot which leads us to a very
nice looking efficient frontier. Now
many of you may be surprised over here.
This efficient frontier does not really
look like what you see in some textbook
sometimes whereas it does look at many
times what you see on the textbook as
well as the internet. So you may have
seen of the raw official plant here
multiple types of shapes. Okay. Now this
over here compared to the forthcoming
shapes which I'm going to share with you
has a mild difference here. It looks
almost symmetrical. So all these 10,000
portfolios have been given the entire
freedom to even have negative weights.
Okay. So a portfolio over here due to
np.random. random dot on n could also
have negatives right now here all total
it should have a total sum of weights to
be one if I take the absolute weights so
if I'm going long on something I'm going
short on something all that put together
if I take the absolute weight should be
equal to one okay so this is how I have
created a raw efficient frontier when
allowed to go short on stocks and this
is how it looks like what do I want next
say I know all the various sharp ratios.
I can also see from the visual over here
in front of me and as I as I go and my
cursor moves around let's say I zoom in
over here I take even one tiny portfolio
from here I can see all the metrics are
present so isn't this really really nice
to look at now what I want is I want the
most optimal portfolio and for me the
most optimal portfolio is a portfolio
with the best sharp ratio for simplicity
is the sake for the sake of illustration
And as it is given in many times in the
theoretical form we have not taken any
risk free return we will take sharp
ratio as a ratio between the annualized
return divide by the analyze volatility.
So moving so here I have my next figure
to show and this figure highlights the
sharp ratio. So this is the max sharp
portfolio. I'm going to zoom this in a
bit and you can see exactly at this
point I get the maximum sharp ratio. Now
what I would actually like to see is
when I have this sharp ratio and I can
see this I can very clearly see this max
sharp portfolio. What I want to see is
what are the weight proportions of every
ETF in size. Okay let's get into that.
So here is my weight proportions. So
this is also pretty clearly done for
visual and I can see that SY has a minus
27% weightage whereas
TL has a plus 24% weightage. Gold has a
plus 30% weightage. U has a minus 5%
weightage and then EM has a minus3%
weightage. Now what I want you to
understand is that refining the raw
efficient frontier allow the portfolios
to have negative weights. While it may
still be possible for some firms or some
fund managers to do this but in many
cases in most cases or at least in
individual cases of people want who want
to allocate their portfolios and decide
all of this individually
shorting maybe not an option. Okay, most
cases like that people would not prefer
going short. So we need to do something
about we need to do something more. We
need to kind of optimize it. Now up till
now we optimizing it by choosing from
this efficient frontier. So what if I
create another efficient frontier in
which I'm not really allowed to go
short. I can only go long and have
positive weight allocations on any of
the stocks or any of the asset. So let's
move on. What I'm going to do now is I'm
going to simulate a long only
appreciation front and for this I will
be again taking 10,000 different
simulations. Okay. So here I my n
portfolios and n portfolios which was
previously defined and I got random seed
just to ensure that I can save this
random generated scenes. So anyway I
have got my 10,000 portfolio simulated
because of this for loop and in this for
loop this time I don't go for
np.trandom.trandom
I go for np.trandom dot random. So
np.trandom random random does what is
that it creates all positive portfolios.
Ah what happens what happens is that all
these positive weights also should sum
up to one. So we normalize this over
here and this means that the total will
anyway come to one. Okay. So I'm going
to just press shift enter. We'll do the
same process and this is how I will get
my portfolios long_d.
And using this portfolios long_df I must
visualize my now efficient trunk which
looks something like this I has got my
maximum sh portfolio as well. So what do
I notice over here? I notice that the
shape of this efficient portfolio looks
quite different from the one over here.
Okay. So this goes to show that there is
a lot of possibility of negative returns
as to the current data. uh if I have
negative weights so if I do random ws
like this and go short probably I'll get
a lot of I'll get almost an equal number
of portfolios probably negative but in
this case and given the data that we
have with long only I see that most of
the portfolios are giving me greater
than zero there is positive returns in
fact all the portfolios are greater than
zero I've got my maximum sharp so let's
just put a cursor over Here uh it will
show us the different things about our
portfolio. So this will have all the
component of weights. What I'm going to
do is I'm going to use some brains and
I'm going to extract the component of
weights and just to make it shorter.
I've already done that for you. We're
not going to do do it actively. But yes,
you can look into this code. I'm going
to be sharing this in the description
below. But before looking at this entire
video, don't look into the code because
otherwise you'll not understand
anything. So here we go. Here I can see
the different bits. So this is my best
sharp portfolio and for this best sharp
portfolio for long only efficient
frontier I can see the various weight
allocation and I can see that XPY has
got nearly 1%
1% weight allocation. DND has got 45%
weight allocation. Gold has got 37%
weight allocation. And then you have
QQQ5% in M again 1%.
So as a portfolio manager or maybe as an
individual maintaining my individual
portfolio, would I actually like to go
by this route? Would I actually like to
create an efficient frontier and do this
and get this? No. Not at all. This is
quite impractical.
I don't want to create a five asset
portfolio. I have a 1% weight in of the
asset and call it optimal. This is quite
impractical. I would actually want
something else. I would want some sort
of a decimation of weights which would
look would have some decent parity
either. It could be a logic like equal
weighted or it could be a logic like
weighted according to the inverse of
rares like we do in respon
there are many other ways of optimizing.
But if I take the mean variance if I
take the sharp ratio or the optimal
portfolio or if I swear by the efficient
PI and get the optimal portfolio and I'm
going to get this. I want you to think
and understand is this exactly what I
want. Is this exactly practical in real
life? No. So, and what we're going to do
is we're going to take a next step. I'm
going to now change the paradigm here.
Change the paradigm of our approach.
Up till now what we did was we simulated
a lot of and from those portfolios we
plugged out the most optimal. So now
allow me to introduce you the CVXP by
library which is basically our solver.
You may have seen other solvers or you
may have seen other libraries like
sideby.optimize
uh etc. But what we're going to do today
is we're going to use this solver to not
take something out of a simulation but
to practically let the math speak for
itself. let the solver solve the and do
the math in the background while we give
it some inputs. We give it some
constraints also and then we see what is
the most optimal weight of the best
portfolio. Okay, so the most optimal
portfolio weight is something to give
back to us. Okay, so I have got the
inputs over here. I'm going to first
convert my data into number array. Some
of these because this is important for
CXPY
and I suggest everyone that the code
which you're going to see right now will
not be something you do regularly in
Python. So I would like you to
understand the framework over here and
then in your own time or you can pause
this video and understand the flow code
better. Okay. So in a naction what we're
trying to do is we're going to find out
W and this W is the variable which will
have the most optimal portfolio. Okay,
this will be variable with the five
assets. So basically it's going to give
me the five allocations
and what are the inputs that I'm going
to define is the mu and the rate weight
which is basically telling us that this
is going to be my mean of the portfolio
and this is going to be my portfolio
volatility.
Now that I have that I need to put in
some constraints. These constraints can
be tricky. Now you might be thinking why
constraints more because you just said
that I'm going to optimize and I will
talk about any other thing I'm going to
just use the solver and mathematically
see what comes so some constraints are
required over here one is because we
want the sum of weights to be one right
because this is just a practical
constraint otherwise it would not be
even legitimate to go ahead with
something mathematical so I'm giving it
all the freedom to find the best the
most optimal portfolio and give you the
mathematically accurate answer and not
just be limited to the efficient
frontier which is only 10,000 portfolios
but this constraint is equally
necessary. Similarly, portfolio
volatility is less than one. We're not
talking percentages. So less than equal
to one means less than equal to 100%.
Why does the volatility need to be less
than 100%. because I obviously don't
want the portfolio to go minus through
300 and plus 500 and you know go
everywhere and finally see that the
volatility is so high and that the
formula and the math is going berserk in
the background. So this constraint is
important. You can imagine the video
game Mario, right? So when the character
Mario cat's name, let's say it's stage
one, it drops from the middle of the app
and then it can't go back. It can only
go forward in the game and once it has
actually completed that stage it cannot
go forward per that stage ends there it
can't go forward right can't go forward
in the scene so these kind of
constraints constraints are extremely
practical and necessary even for a video
game so must must be something important
for the portfolio as well now moving on
what happens is I solve this problem it
creates a problem to solve I give the
input
And it solves my problem. And it says
I'm keeping the language very simple so
that you understand this better as to
what the inputs are, what the outputs
are. I there is no math that you need to
do. No lag range equations, no nothing.
All you need to do is give the right
inputs with the right constraint and
know what you're doing. Any end what you
get is all over here in W. In W I have
the optimal portfolio weight stored. So
W dot value will give me everything I
need. And here we go. I see something
interesting over here. The weights are
represented which are greater than one
minus five weightage plus four weightage
etc. So I need to see this visually and
I want to see where the most optimal
portfolio lies. So let's check out the
efficient frontier and plot this and see
where on the efficient frontier this
lies. So in step line this is what we're
going to do. Voila.
Oh my god. What just happened here is my
efficient frontier. The optimal
portfolio is nowhere close. It is far
beyond over here.
So this is my optimal portfolio which is
so far away from the efficient frontier.
Now why do you think this is happening?
This is happening because my weights are
so high. I mathematically not
constrained something else. But whatever
I constraint according to that
mathematically this is the most accurate
portfolio. Okay. Now let's check out how
the weights look like. Okay. The weights
look like this.
Voila. So this is 4.49 9 which means the
portfolio weight itself is 400
something%.
And here we can see minus 500 on the
scale. So this spy is minus 553%.
So is it again legitimate to have such
high weightage both on positive and
negative side especially on negative
side again not so practical. So what I
will do is I will not allow the shorting
anymore. Up till now I allowed the
shorting. I said the total of the weight
should be one. I never constrained how
much each weight should be at the peak
or the floor level. Okay. So what I will
do now is first I will add another layer
of constraint to what I already had. So
this target could also be other things.
For now what we are doing is we're just
doing this as an experimentation as an
illustration and as I go ahead and if
you see some modification
in any step I would encourage you to go
back and experiment a little bit in
different blocks of code of the code.
Okay. So I should be getting greater
than the mean returns and I should be
getting each weight to be greater than
zero. So I cannot have negative weights.
And finally my law only weights if I
print over here look like this. Okay,
this looks very interesting. And if I
did not have this decimal, this would be
a very small number because I'm rounding
up till the fourth decimal. I can see
that this is zero. Okay, let's visualize
this on a plot. Let's create a bar plot
out of it. Let's create the efficient
frontier. So first let's take out the
appreciation complete. So here you know
while I was doing creating this code
while I was doing all this experiment uh
what I wanted to do was keep this small
like I've done. So if I kept the size
something like 10 which I have done for
some of the other previous plots this
was getting very small and hidden sort
of hidden right so I increase the size a
little bit I'm making this 25
and by doing this I can see slightly
bigger stuff so you see this is now
looking slightly more
nice it is near the frontier it's on
almost on the efficient frontier here
you know with cluster somewhere between
uh some of the simulation that we have
created so this looks practical now
let's have a look at the bar plot our
bar plot of weights look like this now
again as I told you earlier since I had
rounded this up it seems very close to
zero but this is slightly
slightly in the positive okay because if
you notice my earlier constraint which
which I had applied over here is that
every weight is going to be greater than
equal to zero. And we're not allowed to
have extreme constraints. So I have to
use that equal to sign. Which is why I
finally as we just saw I do get that
portfolio on the efficient frontier. But
I get something else.
I get
these weightages. So the weightage for
this looks 42%, this 33%, this 25%. And
this suddenly comes to a point where I
get 0% weightages. So again, what just
happened is that I created a law only
constraint, right? But I did not do
anything about the minimum weightage I
should have for every asset. So I did
get a portfolio but despite using the
math I did not get something which is
practical. So let's take an other step
ahead. What if I want to optimize the
portfolio using these boundaries
on the upper and the lower capping of
fates?
Okay. So let's do that. And I'm going to
give this optimizer a little more
freedom
by
creating a return flow. That is now I'm
not going to say create greater than the
mean returns. I'm going to say create
positive returns. That's it. Okay. So
what I'm going to do is I'm going to use
5% and 40%. Now please remember if you
are exterminating with a longer list of
tickers and this 5% and 40% becomes
impractical. Say you have 30 tickers and
you say the minimum weight needs to be
5%. Then your code will throw an error.
Okay? Because I have these five tickers.
I'm making sure that that matches with
my constraint logic. Okay? So it lo in
practical in case you're experimenting
with this. So I take the same very steps
and one thing which I give to the solver
is an additional constraint over here.
Then w is greater than equal to 005 and
w is less than equal to 4. Also my
target return over here is the minimum
expected return. It is not greater than
the mean return. Okay. So here it is.
I'm running this and let's patiently
look at the different weight is it is
throwing to me. Now this looks nice. It
says spy is minus.0 I'm sorry not minus
04.05
and GD is also 05 whereas the rest like
2.37.32
let's visualize this on our plot. So
let's plot this on the efficient
frontier. This is the long only one. And
this is also something I needed to
really increase the size. You can just
I'll just show you. When I had this at
10, I could not literally see where my
portfolio is. It was so small. This
little star. Okay. And now I know
because it was right here, right? So
what I did was I increase the size. So
if you ever face this problem, you know,
just go for it. Just increase the size
and you'll be able to detect your
optimal portfolio better. So this is
where my optimal portfolio is. I can see
it on the efficient frontier. And if I
look at the bar plot of the different
weights. Now this looks much much more
practical. This goes to show that I have
a 37% weight here, 33 here, like 20%
here and then 5% over in these two. So
now that I have the optimal weight
according to my solver,
what I see is that this is something as
a fund manager or as an individual
managing his own portfolio, I can apply
this. This seems practical.
But it was quite a journey to come from
something which was very raw the
efficient frontier used at the very very
beginning and then come to a point where
we created all these modifications and
user solver and experimenting came to a
point where we realized that we need to
do multiple things.
We realized that when we started from
something very raw, we needed to put
constraints layer by layer. When we
started from something very raw, it
seemed as if it is not very practical.
But as we use the solver, we come to a
point where we creating solutions more
mathematically.
Now up in a point, the solver is
extremely mathematical.
But after a certain point the math needs
to be fed by the correct constraints.
Now if the constraints become more that
sharp ratio the best optimal portfolio
the highest sharp portfolio is an
approximation. It is not the exact but
the log only the initial example it was
the exact market. So if it is an
approximation it's a very close
approximation and definitely used in the
industry. However to put into
perspective what are the different
layers that we saw? We saw that you need
to constain the first layer was a
minimum return that we require a minimum
return of greater than zero. The minimum
weight of every allocation again greater
than zero.
Then there was the maximum standard
deviation we could go for in case number
one which is less than 100 that is less
than one less than 100%.
Okay. Then we saw the capping in the
floor of every weight possible. So the
minimum was to have 5% and the maximum
was to have 40%. So if you can see that
has been accommodated over here and we
can clearly study this mode. The Jupyter
notebook will be shared with you. It's
in the description you can check all of
these constraints
according to the different situations is
something which you could experiment.
Okay. So I really really encourage you
to check this out and experiment. Now as
the last step I have put together all
the portfolios. So the first portfolio
where we use a solver for the max and
sharp portfolio obviously but we had
long and short allowed. And then the
second portfolio where we had long only.
I have the third portfolio which was
long only but instead of maximizing the
sharp ratio what we're trying to do is
we trying to minimize the risk okay and
automatically we reach an approximation
as in spoken
the last but all of this is summary df
and you show summary_df
just round it to four decimal places so
I can see the weights more neatly now
for my first portfolio where shorting
was allowed. I could see my weightes go
all the way here and there but it gave a
very attractive sharp ratio. So here
using a solver just like when you're
using the portfolio efficient frontier
for the optimal portfolio. So when
you're using the solver just like when
you're using the efficient frontier what
tends to happen is then you may land up
with a very impractical result which is
not very easily implementable or not at
all implementable but then what you do
is you you understand that okay fine
let's say I can go long only I cannot
take shorts so here I come to a
portfolio which will not have a sharp as
attractive as 1.31 but it will be
fairly the best shot. Okay, so that's
fair enough to have the breast sha as
long as you only stick by the rules. Now
the last part where we have the capping
in the floor, I can see my sharp ratio
has drastically come down to 0.54.
But I can definitely say that this is
the most practical allocation that could
be which accommodates my interest in all
these different assets even though minus
5% bridge at the same time it creates a
foundation of the upper capping of 40%.
Okay. So all this put together even
though my sharp ratio is declining but
the practical implementation or the
practical logic being retained is
highest in the portfolio over here in
the last row.
So I once again encourage you to go to
the description below the final Jupyter
notebook and experiment by yourself. I
tried to keep all the explanation very
simple and easy to understand. So thank
you so much. I'll see you in the next
video.
[Music]
