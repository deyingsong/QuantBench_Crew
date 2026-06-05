---
title: "Algo Trading Tradestation Tip - At$ Keyword"
video_id: "c1Xcbfsx7wo"
url: "https://www.youtube.com/watch?v=c1Xcbfsx7wo"
duration: "3:48"
source: "NotebookLM YouTube transcript import"
---

# Algo Trading Tradestation Tip - At$ Keyword

[Watch on YouTube](https://www.youtube.com/watch?v=c1Xcbfsx7wo)

## Transcript

hi there I'm Champion Trader Kevin Davey and today my trade station tip is on the at dollar sign keyword you might be saying what is that let's get started so another trade station tip is if you had a situation where you want to set your stop at the low of your entry bar now you could go through some complicated code to do it uh that's the way I used to do it that's the way I thought it had to be done uh it's a little tricky turns out there's a much easier way and I've been using trade station for 20 years up until about a month ago I never even knew this existed so how you can do it instead of doing something like this which doesn't work because this low will move with the low of every bar so you can't do that and if you instead of using low you made a variable that grabbed the entry bar low uh sometimes that's problematic what's much easier than all that is to use the at dollar sign keyword so you say sell next bar you have to specify the entry so you have to say from which entry it's coming from you have to name your entries that's the only thing you have to do differently there and then you have the at dollar sign low stop and so what the at dollar sign does is it then ties that low to the the low of the entry bar pretty neat and a lot easier than some other way using variables and this seems to work pretty well so the that dollar sign keyword will fix the price whether it's a low high open or close to whatever it is on the entry bar as long as you name the entry and make sure your sell order is also referring to that entry now one caution here because this is using a stop order depending on the rest of your strategy you might have other stop order you might have limit orders and you might need look inside bar back testing depending on your bar size of course to make sure that everything is calculated correctly so people who don't use look inside bar back testing and have stop orders a lot of times the strategy back test engine will make wrong assumptions because it doesn't know and you'll get misleading back test results so if you're going to use this keyword word I'd recommend using look inside bar back testing well if you like these tips and if you want me to keep providing some hit the like button subscribe to this channel leave a comment what's your favorite keyword that's a good tip for others maybe I'll make a video on it I'm Champion trer Kevin Davey have a great day
