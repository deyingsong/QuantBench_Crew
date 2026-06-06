---
title: "Advanced Order Types & Comprehensive Risk Management: Algo Trading with Zerodha (Part 5/5)"
video_id: "Bti-usPrZt4"
url: "https://www.youtube.com/watch?v=Bti-usPrZt4"
duration: "12:12"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Advanced Order Types & Comprehensive Risk Management: Algo Trading with Zerodha (Part 5/5)

[Watch on YouTube](https://www.youtube.com/watch?v=Bti-usPrZt4)

## Transcript

Hey everyone, ever wonder how protraders
stay in the game? It's all about risk
management. Risk management in trading
is essentially protecting your capital
from big unexpected losses. It's not
about avoiding losses entirely. They are
part of the game, but about controlling
their size. Think of it as your
financial seat belt in the volatile
world of trading. Let's look at
stop-loss, one of the important pillars
in the realm of risk management.
What exactly is a stop-loss?
The easiest way to think about it
is as an insurance policy for your
trade.
It's a pending order you place that
automatically exits your position if the
price moves against you to a certain
level.
Imagine you buy a stock at 100 rupees
hoping it will go to 110 rupees. But
what if it goes down instead? You need a
plan. You might decide if this stock
drops to 95 rupees, I want to sell and
cut my losses. That 95 rupees level is
your stop-loss.
This prevents a small, manageable loss
from turning into a catastrophic one.
In algorithmic trading, we don't do this
manually. We program the system to do it
for us.
Now, Zerodha gives us two ways to do
this. SL and SLM.
First, let's talk about the stop-loss
limit order or SL. An SL order has two
prices. A trigger price. This is the
price that wakes up your order. Using
our example, the trigger price would be
95. When the stock hits 95 rupees, your
sell order is sent to the exchange.
A limit price. This is the minimum price
you are willing to accept. You might set
this at say 94 rupees and 90 pes.
This means when the stock hits 95
rupees, your sell order is placed but it
will only execute at 94 rupees and 90
pesa or a better price that is higher.
The pro is that you have control over
the exit price. The con is that if the
market gaps down violently,
say from 95 rupees and 10 pes to 94
rupees and 50 pesa in a split second,
your order at 94 rupees and 90 pesa
might never get filled, leaving you in a
losing trade.
Now, let's look at the stop-loss market
order or SLM.
This one is simpler. It only has one
price, a trigger price. Just like
before, let's say it's 95 rupees. When
the stock hits 95 rupees, a market order
to sell is instantly sent to the
exchange. The pro is guaranteed
execution. Once the trigger is hit, your
position will be sold at the next
available price.
The con is something called slippage. In
a volatile market, that next available
price might be 94 rupees and 80 pesa or
94 rupees and50 pes, which is lower than
your trigger. You get out for sure, but
the price might be slightly worse than
you hoped.
So, which one to use? A simple rule of
thumb, for highly liquid stocks with low
volatility, an SL order is fine. For
more volatile stocks or when you
absolutely must exit, an SLM order is
often safer.
All right, theory's over. Let's see how
to actually implement this using the
Kite Connect API. I'm going to switch
over to my Jupyter notebook.
Okay, let's assume we've already
authenticated with Kite Connect.
Now, imagine we've just bought 10 shares
of Infosys at 1,650 rupees. Our trading
plan says we must place a stop-loss at
1,630 rupees.
First, let's place an SLM order, which
is the most common for guaranteed exits.
Let's break that down. Transaction type
is sell because we're exiting a long
position. Order type is SLM. And notice
the two key parameters.
Trigger price is set to our stop-loss
level of 1,630 rupees. And crucially,
the price is set to zero. That's how the
API knows it's a market order. Now, what
if we wanted to place an SL limit order
instead?
We want to trigger at 1,630 rupees, but
not sell for less than 1,629 rupees and
50 pes. The code is very similar. See
the difference. Order type is now SL
and the price parameter is set to our
limit price of 1,629 rupees and50 pes.
This creates that small buffer we talked
about. It's that simple.
And that's a wrap on our first advanced
order type. Let's quickly recap what we
covered.
You know the critical distinction
between an SLM order for a guaranteed
exit and an SL order for a price
controlled exit.
And most importantly, you saw how to
implement both of them using just a few
lines of Python code.
A cover order or CO is a two-legged
order. It combines your initial entry
order, which can be a market or limit
order, and a compulsory stop-loss order.
Think of it as buying a ticket to a
high-speed race and the organizers tell
you that you must wear a helmet. The
stop-loss is your helmet. It's not
optional. This is fantastic because it
forces trading discipline.
You cannot place a cover order without
defining your exit point for a loss.
Let's see how to code this.
Placing a cover order is very
straightforward. The main difference is
we need to set the variety parameter to
CO and provide a trigger price for our
mandatory stop-loss. And that's it. The
API call looks familiar, but by setting
variety to CO, we've told the broker to
create that two-legged order. Once our
buy order executes, a sell stop-loss
order will be automatically waiting.
So, let's recap. The cover order is a
disciplined two-in-one package for your
entry and mandatory stop-loss, enforcing
good risk management from the start.
The GTT is without a doubt one of the
most useful features Zeroda offers for
swing and positional traders.
A GTT is not an order that sits on the
exchange. Instead, it's a trigger
instruction that you give to Zerodha and
it stays active on their servers for up
to one year. When your trigger condition
is met, Zerodha places a limit order on
the exchange on your behalf.
This is perfect for set it and forget it
scenarios.
There are two main types of GTTS.
Single leg GTT. This is one trigger for
one action. For example, if Infosys
drops below 1,500 rupee, buy 10 shares
of Infosys.
Or if my stock in my holdings, say Vanta
goes above 300 rupees, place a sell
order. OCO or one cancels other GTT. In
this, you can set two triggers on an
existing holding. A target above the
current price and a stop-loss below it.
If the target is hit, the stop-loss
trigger is automatically cancelled and
vice versa.
It's like a bracket order, but for your
long-term investments.
The API for this is different. We don't
use place order. We use a special place
GTT method. Let's jump into the notebook
to see how it works.
First, let's create a single leg GTT to
buy a stock on a dip. Let's say we want
to buy TCS if it ever falls to 3,000
rupees.
Let's break down this code.
First, we define the actual order we
want to place inside a list of
dictionaries called orders. You can see
we specify the symbol, quantity,
product, and the limit price inside this
dictionary.
Then in the place gtt call we set the
trigger type to single and provide the
trigger values. We have used the list to
define the trigger value of our desired
price of 3,000 rupee. Then pass in the
orders list we had defined before. We
also provide the last price which is a
requirement for placing GTTS.
Now for the one cancels other GTT. Let's
say we own shares of HTFC Bank and we
want to set a target at 2,300 rupees and
a stop-loss at 1,700 rupees. For the
OCO, we extend the single GTT concept.
We define two orders in our orders list.
One for our target at 2,300 rupees and
one for our stop-loss at 1,700 rupees.
In the place GTT call, we set the
trigger type to OCO and provide both
trigger values in the trigger values
list corresponding to our stop-loss and
target. Please ensure you specify the
values correctly, else it will result in
an error. First, you need to specify the
stop-loss trigger and then the target
trigger. The API then links these two
orders, ensuring that if one executes,
the other is automatically cancelled.
Next up is the aftermarket order or AMO.
This does exactly what it says. It lets
you place orders after the market has
closed. These orders are collected by
the broker and sent to the exchange the
next morning when the market opens. It's
perfect if you've done your analysis in
the evening and want to have your order
ready for the next day without having to
be at your screen. The code is a
standard place order call just with a
different variety. It's that easy. Just
change the variety to ammo and you're
all set for the next trading session.
Placing one massive order can move the
price against you, a problem called
price impact. Today we're learning the
solution, the iceberg order, a
specialist tool designed to execute
large trades discreetly. The name
iceberg is the perfect analogy. You only
show the small tip of your order to the
market while the massive chunk remains
hidden. It works by taking your large
parent order and breaking it into
several smaller child orders or legs.
Only one leg is active on the exchange
at a time. When it fills, the next one
is automatically sent to the market. It
looks like a series of small unrelated
trades, which minimizes your price
impact.
Let's see the code. We'll buy 2,000
shares of ITC, but split into four legs.
That's it. You just set the variety to
iceberg, define your total quantity, and
specify how many iceberg legs to split
it into. The system handles the rest.
So, the iceberg order is your go-to tool
for executing large volumes without
revealing your full intention to the
market.
Congratulations, you've successfully
completed the course. You now have the
skills to automate your strategies using
Zerodha's Kite Connect.
This course has provided you with all
the building blocks to set up an
end-to-end algorithmic trading system.
Thank you.
