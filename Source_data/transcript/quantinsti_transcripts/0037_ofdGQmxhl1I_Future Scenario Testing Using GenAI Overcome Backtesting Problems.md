---
title: "Future Scenario Testing Using GenAI: Overcome Backtesting Problems"
video_id: "ofdGQmxhl1I"
url: "https://www.youtube.com/watch?v=ofdGQmxhl1I"
duration: "18:26"
caption_language: "en"
caption_source: "youtube-transcript-api"
---

# Future Scenario Testing Using GenAI: Overcome Backtesting Problems

[Watch on YouTube](https://www.youtube.com/watch?v=ofdGQmxhl1I)

## Transcript

One of the goals of today's webinar is
to differentiate between generative AI
and L. There is a common company common
company common company commonly held
notion that you know LM and Gen AI
synonymous. I want to disabuse you of
that notion. They are quite different.
Genai is a much more general framework
that can be very fruitful for trading. I
have heard from the mouth of some of the
most senior quans in some of the largest
asset managers. All they can talk about
is applying chai for trading and it is
not really confined to using arrow
because that is actually old news. So I
also should mention that this is this
talk is based on some of the things I
learned from our new book generative AI
for trading and asset management which
will be available on Amazon towards the
end of this month. Um so I have a
co-author Hamlet Medina that is the true
expert. I myself is merely a you might
call a student of geni whereas m hamlet
is truly the teacher and I'm very
grateful that he agreed to collaborate
with me. In fact I learned a lot about
gen I have no idea what generi
generative AI was at a high level until
I I read Hamlet's chapters. So I'm I'm
you know this is one of the great
pleasure of collaborating on writing
books because you actually learn from
your co-author a lot and also
fortuitously we pick a good name for
this book uh because it has a good
acronym called Gotham. So that's the
easy to remember. Let's test if LM has
you know give any sensible answer. So if
you type mirror mirror who is the best
algorithmic trading author of them all
it would return me. And from here you
can see how easy it is for the LM to
hallucinate. So don't believe everything
you read from you know any of the
chatbots.
What is gen AI versus discriminative AI?
Well, what is discriminate anyway?
Discriminate AI or another term for it
is supervised learning is actually
something that we all do whenever you
run a linear regression. That's
discriminative AI or supervised
learning. In probabilistic term, it is
to say what is the probability that you
will get a certain outcome Y. So Y is
what we call the target variable or the
label and X often times called the
features or the predictors or the the
coariantss.
So X if we know X, we're supposed to be
able to predict Y with some probability.
That's what all of us have been taught
what machine learning is traditionally.
That's what all the hedge fund have been
using until maybe 2023,
you know, until 2022 when open AI
suddenly burst into the scene, right?
Everybody understood AI as being you
know at least in the asset management
industry as being a discriminative or
supervised learning or at most generally
you know some people might use a
reinforcement learning some people might
use you know a gang you know generative
adversarial model but generally speaking
we focus on prediction that's what we AI
has been used in in in finance anyway
well can AI asked the following
question.
What about P of X? What about the
distribution of your f features or your
predictors?
What about P X based on Y? That is say
given that you know the outcome. Let's
say historically you know outcome. What
about the conditional distribution of X
in general? What about the distribution
of X and Y? Right? I mean all these
probabilities are related by base rule
as as you you must know. So they are
related but we seldom ask these
questions in supervised learning. We
always focus on P of Y given X. If you
are, you know, training your data on
thousands of samples and only one sample
has this outlier, typically your model
will not care about this outlier
and it will produce an answer as if this
outlier doesn't exist. But if your
feature that you feed into your AI model
is one of these outliers, we certainly
want to know. We don't want to blindly
trust a model that are built on a bunch
of values and that has never seen this
outline. So the traditional discriminary
model has this limitation that whatever
you stick in as a predictor it will give
an answer even though that answer can be
completely misleading because actually
the data was the model was not trained
or have not been sufficiently trained on
these outliers. That's happened quite
often in finance.
The second reason why the importance of
a building a probability distribution of
the features is important is that well
you want to be able to simulate new
samples. Why do you want to simulate new
samples? We'll find out that if you can
simulate the distribution of X well you
can use it for a lot of downstream use.
Risk management is one of them.
Optimization is another one. Right? So
without knowing the distribution of X
you cannot simulate new sample. You can
only simulate you know the label Y but
that is meaningless because the Y you
know all about prediction. All finance
is about knowing certain things. How do
we predict is is not saying that oh by
the way the market always go up. Yeah
sure the market always go up on average
but does it go up when there is
25% tariff? Does it go up when the
Treasury bond goes over 4%. You know,
that is the condition. You know, we we
in finance and trading looking for this
condition. We're not just looking for
the the unconditional distribution of
the of the the target variable. That's
anybody know that market go up forever.
But what about this current particular
circumstance? That is the conditional
model that we're interested in. And if
you don't have a distribution of X, you
cannot generate these kind of samples in
the that is regime appropriate that is
environmentally aware
given
what we know is the outcome. What is the
distribution of the features? So usual
AI we would ask X might be images of
dogs and cats, right? This is images of
cats.
But what about the distribution of eggs
when we know that the it is a dog? Well,
we want to learn that. We want to know
we we want to learn from dog pictures
what constitute a dog conditioned on the
fact that it is a dog. What is the
distribution of the images? That's what
you know all this chatbot gave us,
right? We say give me an image of a dog.
Show me an image of a cat. Well, that is
the prompt. But given the prompt, what
would be the image look like? And that's
what JAI gave us in finance. You know,
if you apply the same analogy to
finance, you would say here the X would
be let's say a return series, right? And
you know, if you don't have any
condition, the return series for the US
for example index is always going
positive. You know, maybe average 10
average excess return of let's say 7%
right a year. But we want to know
what is the distribution of X when we
are in a bare market. That's the
conditional. That's the point. We are
not interested in just modeling the
unconditional distribution of returns.
We are interested in say well now that
we are in a bare market let's say you
know down 10% from the high water mark
what would be the subsequent return of
series look like? What would be the
conditional
distribution of the returns? That's what
a geni will give you. What is the point
of getting all these conditional
distribution?
Well, risk management is one of them.
Traditionally,
risk management is based on VA for
example or CR.
They are all bas based on simple
parametric probabilistics model.
Maybe somebody think they're smart and
they say well they're outliers and fat
tail so let's use a t distributions
instead of gaussian distribution or some
people say well you have to take into
account the tail dependence on different
asset in your portfolio as well so let's
use copulus instead of um uh you know
this this simple multivaried
distribution all of that is great but
it doesn't take into account the
condition all These parametric models
basically unconditioned models.
Can you ask your coppers well what
happened when tariff is 75% and when the
bond is over 4% and when blah blah blah
blah blah. Well copulous typically
cannot help you because this is too
complicated. It's too complicated to
model but they are not too complicated
for geni to model. That is where Gen AI
excel in is to model the prob
conditional probability distributions
when you have a complicated set of
prompts or conditions. The other second
downstream application that might be
that is very useful is scenario testing.
That's beyond back testing, right? I
mean back testing only tests your
trading strategy based on the
historically realized return which is
very limited.
But trading is about the future. It's
not what happened in 2008. It's not what
happened in 2020. It's not even what
happened in 20 25 March. It is about
what's going to happen tomorrow. That's
what's important. Who cares what
happened in the past? I want to know
what happened tomorrow. But the
condition that are in place now is very
complicated. it you know we may not have
seen the exact circumstance in the past
or maybe you have seen it for one or two
days how do we
simulate that scenario that's again
where geni can help it is that genai can
generate number of possible scenarios
based on a very complicated set of
prompts
in you know I call it promps but really
it is a number of conditions of the
market you know you can enter any
indicator you want and you can generate
a time series that are conditioned on
this on this market circumstance. And
with this simulated series, you can test
your trading strategy, stress test your
trading strategy. Is it is it going to
lose money under this circumstance? Is
it going to stop out? Is it going to
result in a margin call? Would entering
at a lower threshold be better? All
these questions can be answered with
this sort of genai simulation
and they cannot be that cannot be fully
answered based on a strict back testing
approach because hey in back test you
might have seen these kind of situation
like what happened yesterday maybe just
maybe one sample during COVID or two
sample right and that is not something
that we can count on from a optimization
or risk management point of view for
example using deep reinforcement
learning to optimize your trading
strategy or optimal optimize your
portfolio capital allocation.
The procedure typically is you first
pre-train your model with a large amount
of data.
That is the beauty about Grand AI is
that you can do this pre-training on
data that may not be immediately
relevant to you.
You may be a forex trader. Well, you
should pre-train your model on equity
data and futures data as well. You might
be a born trader no matter pre-train
your data on stock and f and and futures
because that build up a model where it
is kind of aware of how financial
markets move they can have outliers they
can have this and they can have that and
you know so that's eliminate the problem
of data scarcity I mean in finance in in
application of AI to finance that's a
major problem is that there's not enough
data particular at a daily frequency by
applying pre-training you overcome that
problem because you can train on
everything under the sun. I have read a
paper that even train a time series
prediction model on non-financial data
on like electricity demand data. But
this paper that I cited below stock GBT
that is trained only on financial data
and it showed that it worked the
pre-trained model work. Now it shows you
the potential of a pre-trained model
because then you can fine-tune it with
time series that is specific to the
asset of interest. You train on stock
data, you can fine-tune it with forex
data and see how well it worked on forex
trading. And that is the beauty of genai
as well is overcome the scarcity
problem. Outlier detection is a is an
important feature of genai and that is
particularly important in finance
because there are lots of outliers in
finance. It's hardly normal. So how do
we do that? Well, in traditional
discriminatory AI, as I said, if you
stick in an X, no matter whether it's an
outlier, you are bound to get a Y
or probability for Y, no matter what.
But in Gen AI, we are concerned about P
of X too. We are concerned about P of X
and we are concerned about P of X and Y.
So if P of X is nearly zero that means
sorry by you have not trained your model
on these kind of outliers well P of X
and Y will be close to zero. we we we we
can't we don't have that probability and
so if that's the case we won't trust any
prediction of P of Y given X you just
haven't seen this X why bother to have a
conditional distribution of P why it's
misleading
right it's it's good you know it it
tells you that you shouldn't trust your
machine learning model but also that
also point to the benefits of
pre-training because if you pre-train
your model with a large sample of
on all asset class. Well, it would have
seen these kind of outliers somewhere
and so you can have a much more
reasonable estimate of P of X or P of X
given Y or P of Y given X and and so on
and so forth. And that is again another
benefit of pre-training.
It allows you to come up with P of X um
even if it doesn't it has this that's
this sort of event has not happened for
your asset class but it might have you
know maybe you're trading forex and you
have never seen this but it has already
happened in a bond market so you will
guess what is the consequence of given X
what's Y because it has happened in the
bond market you just haven't seen it in
the forest market yet and so on and so
forth right so you know If you are only
training your model on the forex market,
you may not have been able to give a
reasonable assessment of what might be
the outcome. Why? But hey, you know,
your model is being trained on all kinds
of weird outcomes in all kinds of
markets. So now you have a much better
sort of evidence or you have a much
better chance of guessing what would
happen in the forex market if this were
to occur.
So that's the sort of high level
justification for us to dwell on geni.
Why we should study geni? You might call
the day that geni was born is when
transformer was invented and transformer
and the attention mechanism was invented
at Google. The attention mechanism is a
great advance over the traditional
STDMGU methodology to deal with this
gradient problem because the attention
is mechanism apply weights to different
inputs. I mean the gates in LSTM and RGU
also apply weights but it in a less sort
of surgical way in a less precise way
whereas attention apply weights to
multiple different inputs and those
weights you can train them
using supervised train learning. So the
way I like to think about attention is
that it is a feature selection mechanism
right you know you know maybe a lot of
you are familiar with treebased models
you know decision tree regression trees
but the tension is such a mechanism it
does apply feature selection to neural
but more importantly better than those
features selection algorithm that was
discussed for the tree treebased models
This is a samplewise feature selection.
That means that the feature selection
depends on the sample. It's not just
depend on the the variable itself. It
depends on the actual value of that
variable. And that is one crucial
advantage of the attention mechanism
versus the traditional feature
selection. And it is the only mechanism
that apply that can work in in the
network based models.
[Music]
