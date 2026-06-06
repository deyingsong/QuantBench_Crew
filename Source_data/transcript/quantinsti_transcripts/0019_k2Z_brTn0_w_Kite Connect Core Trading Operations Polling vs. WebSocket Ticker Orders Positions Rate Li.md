---
title: "Kite Connect Core Trading Operations: Polling vs. WebSocket Ticker, Orders, Positions & Rate Limits"
video_id: "k2Z_brTn0_w"
url: "https://www.youtube.com/watch?v=k2Z_brTn0_w"
duration: "26:17"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Kite Connect Core Trading Operations: Polling vs. WebSocket Ticker, Orders, Positions & Rate Limits

[Watch on YouTube](https://www.youtube.com/watch?v=k2Z_brTn0_w)

## Transcript

Welcome to this video on Kite Connect
API Essentials, core trading operations.
Consider this scenario.
You want to place a buy order for
Infosys based on its last traded price.
How will you extract the last traded
price?
This can be done using the method
kite.ltp.
This is done in two ways.
You can either pass the exchange and
trading symbol of Infosys in the format
exchange symbol.
Or you can simply pass the instrument
token of Infosys as input to the
kite.ltp method.
But what is an instrument token? And how
to extract the instrument token of
Infosys?
An instrument token is a unique
numerical identifier assigned by
Zerodha. This is assigned to each
tradeable instrument like stocks,
options, or futures across all exchanges
and segments.
You can download the full list of
instruments tradeable on Zerodha and
filter the trading symbol in fee.
First, make sure you are logged in and
have access to the Kite API.
Then, the first step is to download the
full list of all tradeable instruments.
This list is also called the master
file.
This is crucial for finding the correct
instrument tokens that belong to
tradeable instruments for placing orders
or fetching data.
Here we use the kite.instruments
method. This single call fetches the
entire list which we can load into a
pandas data frame. As you can see, it
contains over 94,000 instruments each
with details like its trading symbol, a
unique instrument token, and the
exchange it belongs to.
Filter the instruments by the exchange
and trading symbol. Since we want to get
the instrument token of Infosys for
trading in NSE,
the exchange is NSE and the symbol is
INFY.
This instrument token can be used to
extract the last traded price.
But what if you want to buy Infosys
based on open, high, and low prices over
the day?
You can extract these prices using the
method kite.ohlc.
Sometimes traders would want to study
the buy and sell orders for the trading
symbol and would want to make trading
decisions based on that.
This data is called quote.
The data that shows top five pending
orders called as bids and sell orders
also called as ask in the market is
called as market depth.
This gives you insight into the current
supply and demand.
You can get the market depth data by
using the method kite.quote.
This returns a dictionary that contains
all of this information.
What if you want to get live prices of
multiple instruments?
You can just pass the list of
instruments tokens or the list of
exchange symbol combinations to either
of the three methods discussed so far.
For example, let's create a list of
instruments in the format exchange
symbol.
This returns a dictionary that contains
all of this information.
This can be passed as input to get the
live data.
And that's it. Now you know how to get
the full list of instruments from
Zerodha using Python.
Have you ever used the Kite mobile app
or Kite web application?
If so, you've likely noticed that prices
update instantly. This is because the
Kite application receives a continuous
live stream of data.
But how will your Python code retrieve
the live price of, say, Reliance
Industries?
As we've learned in the previous
sections, the Python code will call the
method kite.ltp to get the last traded
price.
This is how it works.
The Python code is querying the server
for the price of Reliance using kite.ltp
method.
Hey server, what's the price of
Reliance?
It's 2,800 rupee.
10 seconds pass.
Okay, what about now? Any change?
Still 2,800 rupees.
A price change occurs, but the code
remains unaware of it.
Python code after 10 seconds.
How about now?
It changed to 2,801.
This method is known as polling.
Your Python code must ask the server for
the price and then the server sends the
price back.
Therefore, this approach introduces a
delay. You only receive the new price
when you request it, not the exact
moment it changes.
Polling can be suitable for
low-frequency trading strategies.
If your strategy requires checking for a
price change every minute, every hour,
or even less frequently, polling is an
acceptable approach.
On the other hand, if you need instant
updates, then web socket becomes the
ideal solution.
Instead of your Python code having to
ask the server for the price, a web
socket establishes a two-way connection.
Any change in price is instantly
communicated by the server. It is
similar to a phone call between your
Python code and the server.
Kite Connect uses the Kite Ticker class
to establish a direct and continuous
connection to the server. This is how
web socket communication works between
your Python code and the server.
Hey Python code, just letting you know
the price of Reliance has just increased
to 2,801
and 50 paise.
Python code receives the message and
processes the information.
Oh wait, another update.
The price is now
2,801
and 75 paise.
The Python code starts working on the
updated price.
Server after 1 second.
The price is reduced to 2,801
and 50 paise.
And the server sends all the changes in
price to the Python code.
See the difference?
The server doesn't wait to be asked.
The moment new information is available,
it sends that data directly to your
Python code.
When you want to get live market data
instantly for a set of stocks,
instead of polling the server, you open
a web socket connection.
You inform the server, "Hey, I'm
interested in these 10 stocks."
From that moment on, whenever there's a
trade, a change in the bid or ask price
for any of those stocks,
the Kite server instantly sends a tiny
packet of data down that open line to
your Python code.
Instantly.
So, let's recap.
In polling, your Python code keeps
asking the server for updates.
This approach works well for
low-frequency trading, whereas web
sockets allow the server to send updates
the moment they happen.
This eliminates the need to ask.
This is helpful for your trading
strategy to react quickly to price
changes.
In Kite Connect, you use the Kite Ticker
class to work with web sockets.
Web sockets are essential for real-time
applications and low-latency trading
strategies.
Our goal is simple.
We'll connect to web socket and get a
live stream of price updates for a
specific stock. Let's say Reliance,
which has the NSE instrument token
738561.
We'll see every single tick, every price
change as it happens on the exchange
printed right on our screen.
Don't worry, I'll walk you through every
single line of code.
Let's get started.
All right, here we are in our code
editor.
The first thing we need to do is import
the necessary library.
We import Kite Ticker, which is the
specific tool for web sockets, and
logging to help us see status messages.
Next, you'll need your API key and
access token.
As we covered in an earlier video, you
get an access token to log in
programmatically.
Finally, we create an object called KWS.
This KWS object is our main tool. Think
of it as initializing the web socket
connection. We've told it who we are
with the API key and token, but we
haven't dialed the number just yet.
Now, for the most important part, how do
we actually handle the data when it
comes flooding in? We do this using
something called callbacks. A callback
is a function that tells the web socket
to run automatically whenever a certain
event happens.
We need to define callback functions for
a few key events.
On tick. This is the main one. It runs
every time we receive a price update, a
tick.
On connect. This runs when our
connection is successfully established.
On close.
This runs if the connection is closed
for any reason. Let's write them.
Let's see how these codes work.
The on ticks function simply prints out
the data it receives. In a real trading
algos, this is where your strategy logic
would go.
The on connect function is the setup
function. Once we know the phone line is
open, we have to tell Zerodha what we
want to listen to.
We do that with ws.subscribe.
We pass it a list of instrument tokens.
Here, 738561
is the token for Reliance on the NSE.
We also use ws.set_mode.
This is useful for controlling how much
data you get. Use mode ltp if you only
need the last traded price. It's the
most lightweight. Use mode quote for the
open, high, low, and close prices. And
use mode full to get everything,
including market depth. I encourage you
to play around with these different
modes in the next notebook to see how
the data changes.
The on_close function is for handling
disconnections.
We've set everything up.
We've defined our functions.
We've assigned them as callbacks.
Now, there's only one thing left to do.
Make the call.
And that's it. The kite.ws.connect
command starts the process.
It will run in the background listening
for data and calling our on_tick
function every time a new price for
Reliance comes in.
And look at that. You can see the tick
data flowing in.
Each line is a Python dictionary
containing all the market data for that
instrument.
We have successfully tapped into the
live market feed.
Let's look at how you would typically
place a buy order on Zerodha's Kite
platform. At the same time, let's see
how the same action can be taken through
the Kite Connect API.
Let's select a stock from our watch
list. Let's go for Infosys.
On the left side of the screen, you can
see the Kite platform. And on the right
side, we have our code. In the Python
code, we use the Kite.place_order
method to place orders.
Let's map the order parameters in our
code one by one.
Here, you can see that we've selected
regular. This is your order variety.
Similarly, in our code, we set the
variety as regular.
The exchange, typically NSE or BSE, is
usually pre-selected or you can choose
it. Setting the exchange parameter as
NSE tells the API to place the order on
NSE.
We also need to specify the symbol of
the stock that we are placing an order
for.
In this case, it's INFY for Infosys.
Transaction type buy.
This explicitly sets the order as a buy
order.
Here, you can see the quantity. Just
like typing one in the quantity field,
here we will mention the number of
shares that we want to buy.
You also need to choose your product
type. For instance, product CNC for
delivery-based trades.
Here, we are selecting long-term CNC for
delivery.
Finally, you select your order type.
You can select market to buy at the
current best available price, or you can
select limit to specify a particular
price.
Let's select market.
By adding order type as market, we are
basically telling the system to execute
at the current market price,
making this a market order.
Since this is a market order, price and
trigger price are set to none as these
are not applicable. To place an order
manually, once you've selected all the
parameters, you need to click the buy
button. In our code, we have already
specified this as a buy order. We can
simply run this code to place an order.
Once executed, the API returns a unique
order ID confirming the order has been
sent. With this, you have learned how to
place an order using the Kite Connect
API. It is as simple as placing an order
manually on the Zerodha platform.
How will we know whether the order was
successfully executed or not?
The kite.orders method can be used to
get this information.
This method will give you a list of all
orders you've placed during the day.
When we run kite.orders, the output
looks something like this.
As you can see, the output is quite
detailed and difficult to quickly go
through.
To make it more readable and easy to
understand,
let's convert this into a data frame
and display only the necessary
information. Now, the output clearly
shows whether an order status is
complete or open.
If our Infosys order is open, we can
still take action on it.
Now, imagine we placed a limit buy order
for Infosys at 1620 earlier hoping to
get it at a good price.
But now, the price has increased to
1630.
Our 1620 limit order might never get
filled, and we might miss a good entry
point.
This is where order modification tools
become useful. We can modify an open
order using the kite.modify_order
method.
This method requires the order variety,
the unique order ID,
and the new parameters, which in this
case is the price.
As you can see on screen,
the order has been successfully
modified.
Now, what if the Infosys stock takes a
turn?
Let's say Infosys announced a weak
earnings report, and now we are no
longer interested in going long.
To cancel that pending order, you simply
use the kite.cancel_order method.
Similar to modifying, this method also
uses the order variety
and the unique order ID to cancel that
specific order.
Here, you can see that the cancel
request was placed successfully.
On the Kite trading platform, you can
easily view your full order book and
trade book under the orders tab.
The API also provides similar
functionality.
To retrieve the order information for a
specific order, we need to use the
kite.orders_history
method with the order ID placed between
the brackets.
Similarly, to get a list of all your
executed trades for the day,
you use the kite.trades method. This is
your trade book
showing only the orders that were
actually filled.
You now have a complete set of tools for
managing your orders programmatically.
On screen, you can see all the methods
that you can use for a particular
request.
Feel free to hit pause to read them
carefully.
Once your orders are executed, they turn
into positions.
Understanding your trading positions is
important because they represent your
live exposure to the market. Your active
positions show your profit or loss.
In the previous video, we placed a buy
order for Infosys. Once that order is
executed, how do we check its current
value and whether we are making money or
losing it?
This video will show you how to get
information about your positions using
Python.
In trading, your positions refer to the
active trades you currently hold. Kite
Connect helps you differentiate between
two types. Day positions is a snapshot
of the buying and selling activity for
that particular day.
Net positions is the combined view of
all open trades. Getting a clear view of
these positions allows you to track your
profit or loss, understand your market
exposure, and manage risk effectively.
For our INFY example, we need to quickly
see if our buy order was successful and
what its current status is. To get all
your current positions, both day and
net, you use the kite.positions method.
When we run this code, the output looks
something like this.
As you can see, we've got the details of
all our positions divided into day and
net positions. Let us now convert this
into a data frame and display only the
necessary information.
As you can see, now the output neatly
separates your day positions and your
net positions. For each position, you
can see the trading symbol, the quantity
you hold, the last price, and most
importantly, your current P&L. Once
fetched, you can easily analyze this
data to understand your portfolio's
health.
For instance, you can simply sum up the
M2M column to get the total day
mark-to-market P&L. This provides an
immediate summary of your overall
performance. In addition to fetching
information about your positions, you
can also convert your positions. Let's
say you have an intraday position of
INFY MIS product type, and this position
is showing a significant profit. You
initially planned to square it off
today, but given the positive momentum,
you have now decided to hold it
overnight for delivery.
To perform this conversion, you use the
kite.convert_position
method.
You'll need to specify key details like
the trading symbol, exchange,
transaction type, the quantity you wish
to convert, the old product type, and
the new product type. With this, we've
covered the essentials of understanding
and managing your trading positions
using Python.
To summarize, you now know how to fetch
all your open trading positions with
kite.positions.
You can analyze their profit or loss.
And you can even convert them between
different product types using
kite.convert_position.
You learned about trading positions.
These are your active trades for the day
or those carried overnight.
For example, if you bought Infosys
shares for delivery, that was initially
recorded as a position on the trade day.
But holdings are different.
They refer to the shares you've bought
for delivery and are now stored in your
account.
These are your long-term investments.
So, when does that Infosys delivery
purchase show up in your holdings? It
typically appears in your holdings on
the T+1 day, meaning the next trading
day after your purchase.
Now, you've got these long-term
investments.
You might be asking, "How do I check
which stocks I own?
How can I see which ones are currently
profitable and which ones are not?"
To do this, you can use the holdings
method.
When you run this method, it will fetch
all the stocks present in your account.
As you can see, the raw data is very
detailed.
It has a lot of information.
But we just need key insights to check
our portfolio's health.
So, let's convert this into a data frame
and display only specific columns.
The output will look something like
this.
Each row now represents a different
stock you own.
For each stock, you can check its
quantity, average price, last traded
price, and the T&L.
You will also notice a column called T1
quantity.
This refers to shares you have bought
for delivery the day prior.
Now that you have this data about your
stocks, can you also check your overall
portfolio performance?
Yes, you can.
For instance, here we have calculated
the total invested value, total current
market value of all the holdings,
and the overall portfolio profit or
loss.
This gives you a clear snapshot of your
long-term investment performance.
If you're building a trading application
using Zerodha's Kite Connect API,
you're on your way to creating something
really powerful.
But there's a hidden roadblock that can
suddenly stop your entire program from
working.
It's called a rate limit.
Imagine your app is running perfectly,
fetching prices, analyzing data, and
then bam, nothing.
You're met with an error and your
connection is blocked.
What's happened?
You've likely hit the API rate limit.
So, what exactly is a rate limit?
Think of it like a fair use policy.
Zerodha's servers have to handle
requests from thousands of users at the
same time.
To make sure the system stays fast and
stable for everyone, they limit how many
requests any single user can make in a
short period.
If you go over that, the server will
temporarily stop listening to you to
prevent overload.
Let's see what this looks like in
practice.
Here in our notebook, we have a simple
but very bad piece of code.
It's trying to ask for the price of
Infosys 200 times one after another as
fast as it can in a loop.
This is the wrong way to do it.
Let's run this and watch what happens.
There it is.
See?
We got a few successful requests
through, but then the server cut us off.
The output shows we got several errors.
Our program is now unreliable because we
ignored the rules.
This is exactly what we want to avoid.
So, how do we fix this?
The best and most powerful solution is a
technique called batching.
Instead of asking for the price of one
stock at a time, what if we could ask
for the prices of many stocks all in one
go?
Instead of making 50 separate requests
for 50 different shares, we can make
just one request that asks for all 50.
Let's look at the code.
Here, we've created a list of 50
different company stocks we want to
track.
Now, instead of a loop, we use the
kite.ltp function and pass it the entire
list of 50 instruments.
This is just one line of code.
And look at that result.
We successfully got the price data for
all 50 instruments in a fraction of a
second.
And the best part? We only used one
single API request out of our limit of
10 per second. It's incredibly
efficient. And the best part?
Batching is fantastic.
But what if you need to repeatedly get
updated prices for the same set of
stocks?
If you put your batch request inside a
fast loop, you'll just end up hitting
the rate limit again.
The solution here is simple.
Throttling.
This is just a fancy word for slowing
down.
We need to tell our code to pause for a
moment between requests.
In this example, we want to get updates
every so often.
Look here. After we make our API call,
we add this line.
time.sleep(1)
This tells the program to literally
pause for 1 second before continuing to
the next step in the loop. By doing
this, we guarantee we're only making one
request per second, which is well within
the 10 request limit.
As you can see, every request is
successful.
No errors, no blocks.
The program is stable and reliable
simply because we told it to take a
little break.
And that's really all there is to it.
Building a robust trading app isn't just
about fancy logic. It's about being a
good citizen on the API.
By respecting the rate limits, you
ensure your application runs smoothly
without any nasty surprises.
