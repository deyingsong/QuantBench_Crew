---
title: "600 AI Strategies to 10 Real Trades | AI Trading Masterclass"
video_id: "PQobaztIiCo"
url: "https://www.youtube.com/watch?v=PQobaztIiCo"
duration: "4:15"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# 600 AI Strategies to 10 Real Trades | AI Trading Masterclass

[Watch on YouTube](https://www.youtube.com/watch?v=PQobaztIiCo)

## Transcript

Over the course of this past 6 months,
I've developed over 600 trading
strategies. Maybe 50 can give you good
results in a back test. Actual live
strategies, playing for 600 down to say
over 10 [music]
useful strategies.
In code development, you still need the
domain knowledge, you still need the
insight, you still need to be able to
observe markets. I mean, when you
observe markets, then you translate into
available insights and you test them
through Python or back testing. But even
through back testing using AI, it still
does not gives you the optimal results.
You have to actually tweak it with your
own experience and iterate many, many
times. For example,
over the course of this past 6 months,
I've developed over 600
trading strategies. Some of them are
variants of initial ones. Of the 600, I
would say maybe 50
when you actually put through a back
test, they they kind of give you good
results in a back test.
But back tests are all different. You
have vector back tests, you have
event-based back tests. So, if you use
vector back test,
your results may you look excellent. But
when you do event-based back tests, they
drop a lot. So, once you cut that second
layer of back testing, then you have to
move on to something called paper back
testing live. And then finally using
paper money and then using actual money.
So, by the time you trickle down to
actual live strategies, playing for 600
down to say over 10 useful strategies.
But what you have to watch out for is
actually there's a lot of data snooping,
look ahead bias,
as well as the AI tries to give you a
lot of synthetic data. So, you have to
be careful about that.
And you have to write that into the
guidelines and memory so that you're not
repeat those mistakes. Often more than
not, when I started out, I found that a
lot of the data, a lot of the
performance were fake because it tries
to deliver something for you. You know,
whether or not it can do it, it will
still deliver the results.
Uh even if the probability or confidence
level is very low, it will deliver
results and the results may be fake. So,
be careful and check the results. Don't
uh develop with AI and back test using
uh local, for example, and assume it
works perfectly. It does not work that
way. You have to actually back test it,
use event-based back testing, uh do
paper trading, then small bits of live
trading. When you actually back test,
sometimes it gives you false results or
you have look ahead bias, so it's using
the conference data, it's using data
that it knows to project a strategy
forward, so it looks fantastic.
So, you have to make sure that it does
not have that look ahead bias. Uh that's
one important thing. And then, the other
thing is that when you actually do a
back test, it actually does the back
test
because it may not actually carry out
the back test. That's the second thing
I'll find out.
The third thing is that it also depends
on the back testing libraries I use.
So, why have you created the audit
layer? Just to ensure that despite
making, you know, spending some time
writing a decent prompt, we just want to
make sure that these kind of look ahead
bias doesn't creep in. There are no
failures, signal persistence failures,
so that is
is the signal of of a decent quality. We
want to make sure that that happens. And
so, we specify a bunch of things in
terms of how we want to audit our entire
strategy, all right? So, we set up a
bunch of categories, a bunch of
criteria, so we have multiple checks,
such as are there a lot of NaNs, is
there look ahead bias, and others. And
once you run that, it gives you an audit
report with regard to typical mistakes
have they occurred. And if it passes
through all these tests, then we can be
a little more confident that, okay, our
strategy looks all right, right? So,
once you complete that, you run a back
test in order to observe the results,
which I have done later.
And then you have performance metrics
that you work, okay?
