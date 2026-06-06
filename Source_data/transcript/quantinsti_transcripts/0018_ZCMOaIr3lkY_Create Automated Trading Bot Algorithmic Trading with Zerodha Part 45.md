---
title: "Create Automated Trading Bot: Algorithmic Trading with Zerodha (Part 4/5)"
video_id: "ZCMOaIr3lkY"
url: "https://www.youtube.com/watch?v=ZCMOaIr3lkY"
duration: "10:13"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Create Automated Trading Bot: Algorithmic Trading with Zerodha (Part 4/5)

[Watch on YouTube](https://www.youtube.com/watch?v=ZCMOaIr3lkY)

## Transcript

In our last video, we successfully
connected to the Zeroda websocket and
got a live raw stream of tick data
printed to our screen. It was exciting,
but it was just a flood of numbers. So,
the big question is, what do we do with
all that data?
Here's the plan. We're going to modify
the Python script from our last session.
First, inside our on tick function,
we'll stop just printing the whole raw
data. Instead, we'll pull out the
specific last traded price, LTP.
Second, we'll store a recent history of
these prices in a simple list. Finally,
with every new tick that arrives, we'll
use our stored history to calculate the
10 tick simple moving average and print
it alongside the current price. The
number 10 is used here for illustration
purposes only. This will let us see live
if the current price is moving above or
below its recent average.
Let's jump into the code.
All right, here's the code we ended with
last time. It connects and prints
everything. The first change we need to
make is right here in the on tick
function. The tick variable that Zerodha
gives us is actually a list of ticks.
Even if you're subscribed to just one
stock, it comes in a list. So our first
step is to loop through it. Okay, let's
break down the change. Inside on ticks,
we now have a for loop. For each tick in
the ticks list, we're accessing it like
a Python dictionary. We're pulling out
the value associated with the key last
price. If you wanted the trading volume,
you could use tick volume. Or for market
depth, you could access tick depth. It's
all in there. For now, we're just
focused on the price. Let's run this.
See, much cleaner. We are now
successfully parsing the raw data and
isolating just the price.
Let's calculate our moving average.
To do that, we need to store the last
few prices. We'll use the LTP history
list we created earlier. We'll add the
new price to the list. Make sure the
list doesn't get too long. And if we
have enough data points, we'll calculate
the average. Let's walk through this
logic. We append every new price to our
LTP history list.
We then check if the list has become
longer than our desired SMA period of
10. If it has, we use pop zero to remove
the oldest price, keeping our window
moving. Finally, if the list has exactly
10 prices in it, we calculate the sum
and divide by the length to get our
average. We then print it out nicely
formatted. Let's run it and watch it
work.
And there you have it. For every new
tick, we are now calculating a live
short-term simple moving average. You
can see the current price and its
immediate trend right there.
So, in this video, we took a huge step
forward. We went from just seeing raw
data to processing it in real time.
We're going to turn our analysis into
actionable trading logic. Our goal is to
implement one of the most classic
trading strategies, the SMA crossover.
The logic is simple. When the stock's
price crosses from below the moving
average to above it, it can be a bullish
signal suggesting it's time to buy. When
the price crosses from above the moving
average to below it, it can be a bearish
signal suggesting it's time to sell.
We'll modify our script to detect these
exact moments and print a clear buy
signal or sell signal to the screen.
The flow will be tick arrives, calculate
SMA, check for crossover,
print signal only once. This makes it
easier to understand how the logic
flows.
We're not placing orders just yet, but
we're building the brain that will.
Okay, here's the code we finished with
last time. It does a good job of
calculating the SMA on every tick. Now,
we need to add the logic to compare the
price to the SMA. A common mistake is to
just check is the price above the
average on every tick. But that would
give us thousands of signals. We only
care about the exact moment the
crossover happens. To do that, we need
to keep track of the previous state.
Let's walk through these crucial changes
inside on ticks. First, we created a new
global variable position status. This
variable will remember whether the price
is currently above the SMA bull or below
it bare. This is our memory.
Inside the function, after we calculate
the SMA, we add our strategy logic. The
bullish signal check is key. If last
price is more than the SMA and position
status is equal to bare. This only
becomes true for one moment when the
price is now above the average but our
memory says it used to be below. That's
the crossover. When it happens, we print
our buy signal
and immediately update our position
status to bull so we don't fire the
signal again. The bearish signal works
the exact same way, just inverted.
I've also added a line to set the
initial status the first time we have
enough data.
Let's run this and see our signal
generator in action.
Okay, watch the logs. There you see that
the moment the LTP crossed above the
SMA, we got our bullish crossover buy
signal.
If the price now drops, we'll see the
sell signal.
And that is how you build a trading
strategy.
We are going to connect our trading
signals directly to Zeroda's order
placement system. When our script
generates a buy signal, it won't just
print it to the screen. It will send a
real buy order to the exchange. This is
the final step in creating a truly
automated end-to-end trading bot.
From this point on, the code can execute
real trades with real money. Please be
extremely careful. Test with a quantity
of one and understand the risks before
running this on a live account.
Here's the plan. We'll need two main
components from the kite connect
library. Kite ticker which we already
use for the live websocket data. Kite
connect which is the main object for
interacting with your account. This is
used for placing orders, checking your
holdings, modifying orders, and so on.
Our script will be modified so that when
the bullish crossover happens, we'll use
the kite connect object to place a buy
order. And when the bearish crossover
happens, we'll place a sell order to
close our position.
From this point, running the script will
place real trades. Always use the
minimum quantity of orders before live
deployment.
Okay, here's our signal generation
script. The first thing we need to do is
import and initialize the main kite
connect object right alongside our kite
ticker. A lot has changed, so let's
break it down carefully. First, we now
initialize kite connect and pass it our
API key and access token. This object is
our gateway for actions.
We've created a dedicated function place
market order. This makes our code clean.
It takes the symbol and transaction type
and uses kite.place order to send the
request. I've set it to place a regular
MIS market order for intraday trading.
It's wrapped in a try and accept block
which is crucial for handling any errors
if the order fails.
The biggest change is in on ticks. We've
replaced our old position status with
current position. The buy logic now
checks if last price greater than SMA
and current position is none. This
ensures we only try to buy if we don't
already have a position open. If the
condition is met, it calls our new order
function and sets our position to long.
The sell logic is for exiting our
position. It checks if last price less
than SMA and current position is long.
If we get a sell signal while holding a
position, it places a sell order and
resets our position to none making us
ready for the next buy signal.
There is an on order updates method
which communicates any changes in order
back. While the on orderer update
callback provides real-time
notifications for order status changes,
you can also use the orders or order
history methods to actively fetch the
current status of your orders as seen in
previous sections.
This simple state management prevents
the algo from firing off hundreds of
orders. And that's it.
If you run this script, it will watch
the market and the moment its conditions
are met, it will place trades on your
behalf.
You have officially built a complete
end-to-end automated trading system.
Congratulations. This is a huge
milestone, but it's also just the
beginning. From here, you can make your
system infinitely more sophisticated.
You could add a stop-loss and take
profit to your orders, manage multiple
positions at once, incorporate more
complex indicators, or even add error
handling to try and reconnect if the
websocket drops.
