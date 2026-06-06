---
title: "Algorithmic Trading in India with Zerodha Kite Connect: Complete Series Introduction (Part 1/5)"
video_id: "TK2OUe-CoWU"
url: "https://www.youtube.com/watch?v=TK2OUe-CoWU"
duration: "13:02"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Algorithmic Trading in India with Zerodha Kite Connect: Complete Series Introduction (Part 1/5)

[Watch on YouTube](https://www.youtube.com/watch?v=TK2OUe-CoWU)

## Transcript

Welcome to this course on algorithmic
trading with Zeroda Kite Connect.
Have you ever found yourself in this
situation? You're actively trading,
constantly monitoring market movements
and trying to react quickly to price
changes. You might be aiming for a
specific entry or exit point, but the
market moves too fast and you just miss
it. What if your trading could
essentially run itself? What if your
strategies could execute with speed,
logic, and precision even when you're
not actively watching every single tick?
This is where algorithmic trading comes
in. And this course will guide you on
how to automate your trades through
Zerodha's kite connect API.
Think about this. You've developed a
strategy that says, "Buy Tata Motors
when its price crosses above the 200day
moving average and sell when it crosses
below."
It has clear rules for entry and exit.
But imagine trying to catch that signal
across dozens of stocks all at once,
especially during those volatile market
hours.
Algo trading lets you transform those
rules into code. These rules are nothing
but trading signals that can be applied
across many instruments at once by
automating your strategy. Now consider
market volatility. It's 1:00 p.m. and a
major announcement related to
geopolitical tensions hits the news,
causing a sharp drop in the stock you
own. Your predefined plan was to hold,
but you feel a strong urge to panic
sell. How do you prevent emotional
responses while trading? Algorithmic
trading can help to minimize the impact
of emotional biases. Your rules are set
beforehand, maybe to hold until a
specific technical indicator signals an
exit. The system aims to follow these
rules, providing a disciplined approach
even in challenging market conditions.
By automating your trades, you are
trading based on logic, not fear. What
about managing multiple positions or
diverse strategies simultaneously?
Let's say you're trading equities based
on one strategy and options based on
another. Manually keeping track of every
detail, adjusting parameters like stop-
losses for each position, and monitoring
overall portfolio risk can get quite
complex. With algorithms, you can set
automatic stop- losses and profit
targets across your entire portfolio,
simplifying risk management. For
instance, imagine wanting to apply a
strict 1% stop-loss across 50 different
stocks and 20 option positions
simultaneously.
Doing that manually can be very
difficult. This frees you to monitor
more assets and expand your trading
activities which otherwise would be a
challenging task to achieve manually.
Throughout this course, we will take you
through the entire process of algo
trading with the help of Zerodha's kite
connect API. You'll learn how to start
things off by setting up your developer
account and logging in. How to retrieve
realtime market quotes and use
historical data for analysis. how to
place orders and how to access your
positions and holdings data. You will
also learn how to conceptualize a
strategy and back test it. This will
prepare you for live trading which is
also covered in this course. Lastly, you
will learn how to work with advanced
order types like aftermarket orders,
cover orders, and iceberg orders through
the API. All concepts will be explained
through clear video lessons. This course
is designed to help you bring more
structure and efficiency to your trading
with practical hands-on Jupyter
notebooks at every step to show you how
to automate your trade through the kite
connect API so you can easily follow
along adapt the code and customize it
for your own trading needs.
What is algorithmic trading? Have you
ever tried to track multiple stocks,
news headlines, and market trends all at
once, looking for perfect trading
opportunities? It's like trying to
manage multiple things at once. Nearly
impossible for a human. But what if you
find out that a huge part of today's
stock market trading isn't done by
people, but by incredibly fast and smart
computer programs, all with the help of
algorithms.
By the end of this video, you'll know
exactly what algo trading is.
What is algo trading? To put it simply,
algo trading is all about implementing
trading strategies in a disciplined
manner using computer programs. Think of
it like this. It's a way of trading
where we use scientific methods to pick
the right stocks.
We fetch its data and analyze it.
This helps us decide when to buy or
sell. And we do all this using computer
programs.
Let's say we create a rule that says buy
a stock when its 50-day moving average
crosses above its 200 day moving
average. Now, instead of manually
tracking this for every stock every day,
we can use a computer program that does
it for us. It will scan hundreds of
stocks, check these trading rules, and
place trades when the condition is met.
So, that's how algo trading works. But
how do we create these strategies? This
is where quantitative analysis comes in.
It sounds complicated, but the idea is
simple. It's about using math and
statistics to analyze past market data.
Based on our analysis, we predict how
the market might move in the future and
take trades accordingly.
You see it all the time during an IPL
match, right? The analysts on screen
show you Virat Kohl's run rate or how a
team scores in the last few overs. They
use this past data to predict who might
win. That's datadriven forecasting.
Quantitative analysis is the same thing
but for stocks. Instead of cricket
stats, we analyze historical data of
stocks. This allows us to make
datadriven trading decisions, taking the
emotion out of the equation.
In India, algorithmic trading has grown
rapidly over the past decade, especially
after SEBI allowed direct market access,
DMA, in 2008. Today, it's a huge part of
our market. As of 2025, ALOS now account
for 57% of all equity cash trades and
70% of futures and options trades on
exchanges like the NSE. That's a
significant increase compared to its
early days. This shows how widely
accepted and important algo trading has
become here. So we've seen that algo
trading is a systematic datadriven
approach that's already dominating the
Indian stock market. But why is it so
popular? What are its advantages over
the traditional manual way of trading?
While trading manually, traders might
define some rules to enter and exit a
trade. However, as the name suggests,
the trader might use their discretion
over the rules to take or pass the
trade. This decision can be influenced
by recent experiences, by instinct, or
by emotions.
What happens when the rules are
disregarded? As a rule, while driving a
car, your tires should have an optimum
level of air. Sure, you can drive a car
with a flat tire, but imagine the damage
it will cause. In a similar manner,
consider a discretionary trader who has
defined rules to exit if there is a loss
of 8% and not otherwise. But when you
are putting real money in the trade,
emotions can take over fast. You open a
position and the position is at a loss
of 5%. You get worried and you think it
will go down by another 5%. And exit
from the position immediately, but the
stock reverses and increases 10% above
your buy price. Thus, if you had trusted
your rules, you would have been making
gains instead of losses.
However, discretionary trading has its
own advantages. Sometimes the data
available for analysis can be incomplete
and external data suggest limited
chances of making a profit from the
trade and discretionary traders can use
their judgment to trade better. Since
the discretionary trader is required to
make a judgment on each buy and sell
decision, the trader is more likely to
become emotionally attached.
Human psychology plays an important part
too as demonstrated by the value
function. You can see that people
perceive gains and losses differently.
While you will be a little happy with a
10,000 gain, you will be doubly scared
when you hit a 10,000 loss. Simply
speaking, a loss hurts twice as much as
the happiness you get for a gain of the
same amount. Let's suppose you are
richer by 5,000 rupees than you are
today. Now you are offered two options.
A sure loss of a,000 rupees. A 50%
chance to lose 2,000 rupees and 50%
chance to lose 0 rupees. Logically, if
you take option A, you have restricted
your loss to a,000 rupees. Taking option
B means you are risking more money just
to have a chance to get back to zero. In
contrast, an algorithmic trader relies
on his strategy to make the correct
decision. He defines trading rules and
back tests it. He is confident in his
trading strategy as he has validated it.
This strategy is then converted into an
algorithm using a programming language
such as Python. The algorithm takes care
of the entry and exit of a trade. Humans
have limited time and brain power. Thus,
a discretionary trader is limited to
trade in two to three securities. On the
other hand, a systematic trader can
scale their strategy to apply on
hundreds to thousands of securities in
different markets.
Computers have become lightning fast
nowadays. Since a discretionary trader
relies on his own intuition, they are
limited to few assets and analysis
tools. An algorithmic trader can
meanwhile use his strategy on hundreds
of assets and pick the ones with maximum
potential.
A discretionary trader might be limited
by his own experience. Whereas a trader
who uses algorithmic trading will test
his strategy on various assets. Based on
the results, he would then deploy the
strategy.
While algorithmic trading offers these
strong advantages, it does require
certain skills. Building and keeping
these systems running needs technical
knowledge and this is exactly where this
playlist will help you. Let us now look
at the Zerodha ecosystem and then later
build your skills to trade
algorithmically.
Picture this. The market opens and while
you're still deciding your first move,
some traders have already executed
hundreds of orders all without touching
a single button.
So, how are they doing this? They do
this using something called an
application programming interface or
API. Let's understand Zerodha's trading
ecosystem which you might already be
familiar with. As a manual trader, you
can use Kite for your daily stock and
FNO trading. It's Zerodha's main trading
platform available on your web browser
or mobile phone. But let's say you want
to now invest in mutual funds too. For
this, you can use Coin. This lets you
buy mutual funds online and commission
free.
Now, how do you keep a track of all your
trades, investments, and get detailed
reports?
That's where console comes in. It's a
central dashboard for all your Zerodha
activities showing your portfolio,
profit and loss, and tax statements.
And if you want to learn more about the
stock market, trading strategies, or
even advanced concepts, you check out
Varsity. It offers in-depth, easy to
understand lessons for free.
For this course, our main focus will be
the kite connect API. This is what
allows you to build algorithmic trading
systems. So what exactly is the kite
connect API?
Think of it as a set of tools that
allows your computer program to directly
talk to Zerodha's trading system.
Instead of manually clicking buttons on
the Kite website or app, you can use
your Python code to accomplish tasks
like logging to your account, fetching
historical and real-time market data,
placing and managing all types of
orders, monitoring your trading
positions and your portfolio holdings.
In essence, Kite Connect helps you
automate your trading activities.
We have seen the advantages of algo
trading over manual trading. In the next
video, we will set up our own Zerodha
developer account and get one step
closer to building your own algorithmic
trading system. See you there.
