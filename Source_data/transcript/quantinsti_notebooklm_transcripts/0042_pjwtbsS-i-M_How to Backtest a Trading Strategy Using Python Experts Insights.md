---
title: "How to Backtest a Trading Strategy Using Python | Expert's Insights"
video_id: "pjwtbsS-i-M"
url: "https://www.youtube.com/watch?v=pjwtbsS-i-M"
duration: "6:30"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# How to Backtest a Trading Strategy Using Python | Expert's Insights

[Watch on YouTube](https://www.youtube.com/watch?v=pjwtbsS-i-M)

## Transcript

I'm going to show you is to use local
historical data to test. The difference
between previous is it's not the easiest
but it will be more reliable because you
have your historical data in your local
file so that you can run it. This is the
actually the result. You will see it in
my demo. Historical data farm is not
good at moment. Let's switch to let's me
make sure you can see the Jupyter
notebook. Right now I'm switching to the
Jupyter notebook again, but this time I
change my file a little bit. Let me
explain it quickly that I can. So what
you need to do is to choose the strategy
you want to back test. This time you
switch to data provider name to local
file which means you have your
historical data download to your local
and then you want to use it to back
test. You need to still need to choose a
end date start date for back testing.
This time you need to follow the
instruction to provide historical data
to ibridge pi. It's straightforward
because the file name is this one. You
want to provide it to spy. This is
minute bar. And you want to provide this
historical data to spy for daily
testing. Let's run it. And you can see
average price started to back test line
by line. And you can see the trading
robots bought some share, sold some
share, bought, sold at end. And to
visualize the result, let's run the next
slide. You can see is this one is back
testing date number is not a real date
but just simulation date. And the yaxis
is the account portfolio in dollar. The
default value right now is 200,000. You
can see the price go like this. And this
is how we back test using historical
data. The next demo is like this. The
next the idea of next demo is think
about the problem with this back testing
strategy is you need to have a minute
bar data. You need to provide a daily
bar data. The reason for that is average
pi simulate trace at 1 minute before
market close. However, it needs
historical data at 359 to simulate the
price. The difficulty for traders is
that minute bar is not easily available.
Think about if you go to Yahoo Finance,
they only have daily bar for the time
frame go back to year let's say 2000.
They don't provide minute bar. So it
caused some difficulty for traders to
simulate for a long back testing time
frame. To help you solve that problem,
average pi have another way to simulate
minute bar data. So the solution is you
provide data source name change to a
value called
simulated by daily bars. The default way
is whenever average P needs a minute bar
data, it will go to daily bar and use
the close price to simulate the minute
bar data. This one is a little bit
cheeky, but think about that. For
example, you need the trading price at
359 for a day, but you don't have it.
What you are you going to do? You're
going to say 359 is pretty close to the
close price. Let's go just use the close
price of daily bar to do the simulation
and it make things much easier. So,
let's run it. average pile will still do
the simulation but this time it does I I
did not provide the minute bar data. I
just gave it daily bar data and run it.
It still works. And how about the
result? You can see the result is pretty
close to the previous one. It's not
exactly same because I'm using the I'm
not using the real minion bar data at
359 but I use the close price. You can
see the shape is kind of similar to the
previous one. But hey, it's just
simulation. It's approximation there. So
we accept let me make sure right now I'm
switching to my presentation but right
now you should see the the page with two
chart to graph and this is the simulated
result only use daily bar. So I run the
simulation back to year 2000 and you can
see on the left side this one is spy
chart. If you buy and hold spy, this
will be the result in your account. You
can see it's not that smooth because the
market go up and down. However, if you
run buy low, sell high and run the back
testing from year 2000 to year 2020, you
can see your port portfolio looks like
this from 200,000 to 800,000. So
compared to this two chart you will see
wow buy low sell high is better than buy
and hold spy overall. The reason for
that we build a model even if the
correlation using the simplest linear
regression is not a big number. That's a
tiny number considering linear
regression model, but it still make
pretty good result overall.
[Music]
