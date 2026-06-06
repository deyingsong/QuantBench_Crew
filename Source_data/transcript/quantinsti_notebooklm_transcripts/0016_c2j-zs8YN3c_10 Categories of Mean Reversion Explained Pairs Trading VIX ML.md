---
title: "10 Categories of Mean Reversion Explained: Pairs Trading, VIX, & ML"
video_id: "c2j-zs8YN3c"
url: "https://www.youtube.com/watch?v=c2j-zs8YN3c"
duration: "16:46"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# 10 Categories of Mean Reversion Explained: Pairs Trading, VIX, & ML

[Watch on YouTube](https://www.youtube.com/watch?v=c2j-zs8YN3c)

## Transcript

Markets frequently overreact. Now when
I'm focusing upon short-term returns,
let's say a day-to-day return on a
certain day a stock falls by 5%. Now the
next day there is going to be a
short-term recovery and this kind of a
phenomenon seen very very often. I can
use a zcore. The number of standard
deviations something goes away from the
meat. Gold may sit quiet for months and
they break out explosively after a
central bank announcement and the mean
itself is shifted significantly.
Hi everyone, welcome to the channel. My
name is Mo and today we're going to be
talking about mean reversion trading
strategies.
Well, we've all heard of mean reversion
trading strategies. In trending markets,
most quantitative systems are designed
to capture unidirectional moves. Going
long enough trends and going short when
the trend is downwards. But markets
don't always trend. There are extended
periods where prices can oscillate
between a defined range. Think of an
index bouncing between 21,000 and 22,000
for weeks at a time. During such phases,
trend following systems often lose or
they often set IDF. That is where mean
reversion strategies come in.
In quantitative finance, mean reversion
refers to systematic methods that profit
from temporary deviations from an
equilibrium.
betting that prices, returns or
relationship between two instruments
revert back to their long-term average
or to their fair value. They are great
portfolio diversifiers. You see when a
mean reversion strategy is combined with
a trend following strategy they both
create a balance because one thrives on
a direction movement while the other
thrives on oscillation.
At the core of mean reversion lies the
concept of stationarity.
A process whose mean and variance remain
roughly stable over a period of time.
But when it comes to various other
things other than just the asset price,
there could be stationality in there as
well. For example, the returns or
spreads between correlated assets or
volatility for that matter. In this
video, we will explore 10 distinct
categories of mean reversion trading
strategies from the simple price system
to advanced statistical machine learning
frameworks each revealing a unique way
of markets reverting towards the
equilibri.
Let us get to the core idea of mean
reversion first.
Well, when it comes to time series, the
statistical implication behind mean
reversion is that variables that move
too far from an average tend to come
back. Now, how do I quantify this? This
is a subjective thing. In order to
quantify this, I can use a zcore. The
number of standard deviations something
goes away from the meat. In financial
terms, when an equity index makes a
large move, for example, an index drops
by 3% in one single day
without any major change in
fundamentals, the odds of such a
short-term rebound statistically
increases.
The mean acts as a gravitational anchor.
Price level mean reversion. This is the
simplest and the most intuitive form and
it assumes that price oscillates around
a dynamic mean such as a moving average.
Now what is a moving average? It is a
dynamic mean because it is a mean but it
always keeps changing because it's a
moving average. Now as a classic
example, Ballinger Bank strategy would
fit very well. For example, a stock,
let's say a stock like Apple drops and
goes down and it goes down below its
lower V. This is seen as an overreaction
or a temporary mispricing. Now, this can
correct back and remount back to its
mean. That is the assumption behind this
Mo. Such strategies would perform
actually very well in rangebound markets
but they would fail when markets are
actually trending very strongly in one
direction. That is why volatility
filters and stop-loss mechanisms are
very important when trading such
strategies.
Return mean reversion. Here we focus on
short-term returns rather than price
levels. Markets frequently overreact.
Now when I'm focusing upon short-term
returns, let's say a day-to-day return
on a certain day a stock falls by 5%.
Now the next day there is going to be a
short-term recovery and this kind of a
phenomenon seen very very often. This is
because the liquidity normalizes. This
sort of a negative autocorrelation in
returns reflects temporary imbalances,
liquidity shocks or behavioral
overreactions. It is statistically
utterly opposite of momentum
indicator-based mean reversion. Now let
us talk about strategies which use
technical analysis indicators and
mathematical calculations behind those
indicators are actually telling us that
there is some overextension in either
direction when it comes to the markets.
So for example, famously known
indicators such as RSI or the stochastic
oscillator would measure how far the
price has deviated from its recent
knocks. Now the computation behind each
and every indicator is different and
therefore the levels the strategy the
entry and exit rules behind that model
would also be different. For example, an
RSI below 20 would suggest that the over
pressure of selling has hovered in the
market and now there could be a time
where the market could rebound. Right?
So much stressed upon uh market in one
direction would snap back. On the other
hand, if the RSI has gone above 80 or
90, this would signal something highly
overbought. I it is very likely that the
prices can cool off. So in such cases in
this example which I gave you would
equally style for even intraday. Right?
These indicators translate into shiru
into numerical thresholds and help
detect short-term equilibrium shifts.
Now let us talk about a relative value
mean reversion. A relative value mean
reversion as the name suggests comes
from so relative the relationships
between multiple assets. The famously
known pairs trading strategy also falls
under this category. Pair trading would
involve a pair which is basically two
financial instruments but the same when
it when the number of instruments
increase can be called a cross-sectional
mean reversion. So in pair trading what
we do is we take two correlated assets
for example we take Coca-Cola and Pepsi
which usually move together and if they
temporarily diverge the spread between
these two assets becomes very tradable.
You go long on what is undervalued and
you go short on what is overvalued and
you expect the spread to converge or to
normalize back again. We mathematically
model the relationships and we can back
test how we can trade the deviations
from the spread
in cross-sectional mean reversion. The
concept would extend across many assets.
Here we would be buying the recent
underperformers for example and
shortening the outperformers and we
would expect the relative value price
convergence back again. fundamental or
factor mean reversion. In this case, the
reversion occurs to a fair value or to
factordriven expectations.
Suppose a stock's earning remains quite
strong. But if I look at the price to
earning ratio, it has dropped far below
its historical norms due to maybe some
short-term pessimism. Okay. Over a
period of time the price would revert
back and I would expect it to revert
back to its industry price to earnings
ratio or to historical normal. This is
the foundation of value investing and
factor residual reversion. In
quantitative models we measure these by
factor residuals returns explained by
exposures to known factors.
When those residuals become extreme,
they tend to revert.
This form of mean reversion usually
operates over weeks or months rather
than intraday. Volatility mean
reversion. Volatility is one of the most
reliable mean reverting quantities in
5x. Let's consider the VIX index or the
VIX index. Every time fear spikes at
wicks grows above 35 goes to the range
of 35 to 40 it eventually goes back down
coming back near 15. Okay. Now this
particular type of movement is also main
reverting and that decay is volatility
reversion in action. Traders exploit
this through volatility at trudge. They
want to sell options when the implied
volatility is abnormally high compared
to the realized volatility and they want
to buy options when is it is actually
very very low. However, volatility can
remain elevated for longer than expected
especially during systemic events. Hence
a robust hedging and dynamic position
sizing set of rules are very critical to
models trying to capture volatility
arbitrage.
Regiment dependent mean reversion.
Mean reversion works beautifully
but only under the right circumstances.
The effectiveness of a mean reversion
strategy could heavily depend on the
market regime in which we are looking at
the strategy performed. So during a
lower volatility regime or during a
rangebound phase these reversions
dominate and therefore the minverion
strategies tend to do very well. But
when at a macro level information
arrives or volatility surges,
those equilibrium assumptions don't hold
true in that phase of the market and
those assumptions tend to break up. For
example, gold may sit quiet for months
and they break out explosively after a
central bank announcement and the mean
it excel is shifted significantly.
To adapt to this change, quantitative
systems may employ regime shifting
models. For example, the hidden marco
model or volatility filters for that
matter to distinguish between mean
reverting states and the trending states
of the market. Machine learning enhanced
mean reversion. Machine learning has
expanded to the scope from what the
classical approach to mean reversion
was. So instead of fixed rules like
zcore being greater than two or lesser
than two, we can take a machine learning
model and it would learn the probability
and the speed of reversion based on
historical data. For instance, a
gradient boosting model might identify
those phases when volatility is high,
but crosset correlations still remain
stable. The odds of reversion are still
very high. But if correlation breaks
down, mean reversion would weaker.
Features often include polity, momentum,
distance from mean, autocorrelation,
and even regime indicators.
The output might predict both likelihood
and expected half-life of reversion.
This datadriven adaption makes machine
learning system more responsive to
nonlinear and evolving market dynamics.
Options and derivatives mean reversion.
You see when it comes to the implied
volatility surfaces in options markets,
mean reversion becomes a very very very
interesting strategy for that. When
implied volatility be spies after a
market shock, options become overpriced
relative to the realized volatility.
Panic would finally subside and implied
volatility would drift down and the
short wall trades would profit in such
situations. Conversely, when the markets
are calm and quiet and the implied
ladity is quite low, long ball trades
such as going low on stridles or going
on strangles would captured the upward
reversion. This behavior reflects the
volatility risk premium. Markets tend to
overpay for protection during times of
stress and underpay for protection
during times of complacency. Traders
often use options and other derivative
strategies to exploit this mean
reversion bias across volatility
regimes.
Number 10, high frequency on
microstructure mean reversion. You see
at the micro structure level mean
reversion is a byproduct of order flow
and liquidity.
When a burst of aggressive buyers push
the prices a few ticks higher, liquidity
providers would step in and give their
sell codes to the market and that would
finally push the price back to an
equilibrium. So moments later the
reverse would happen with selling
pressure. Now these sort of short very
very minute oscillations occur thousands
of time during the day and the tiny
repaling cycles that keep making the
market efficient are seen as an
opportunity by high frequency traders.
Now for high frequency traders each of
these micro reversions is an opportunity
capturing a fraction of a scent
repeatedly while managing execution risk
and inventory exposure.
To conclude,
mean reversion isn't just a single
trading rule.
It is a fundamental statistical behavior
underlying how markets function.
Spreads, prices, volatility, even
fundamental variables
all tend to revert to an equilibrium
once they are stretched too far.
Think of it as a market's rhythm of
overreaction, correction, and
restoration.
Understanding why and when this occurs
allows traders to identify
inefficiencies
and design strategies
resilient across different market
regimes. Ultimately, main reversion
reminds us that even in randomness,
market seeks balance. Chaos has a center
of gravity. Thank you for watching. I'll
see you in another tutorial.
