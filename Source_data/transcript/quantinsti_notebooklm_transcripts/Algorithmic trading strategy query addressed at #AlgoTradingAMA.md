---
title: "Algorithmic trading strategy query addressed at #AlgoTradingAMA"
video_id: "aYVlD4f7PUA"
url: "https://www.youtube.com/watch?v=aYVlD4f7PUA"
duration: "2:12"
source: "NotebookLM YouTube transcript import"
---

# Algorithmic trading strategy query addressed at #AlgoTradingAMA

[Watch on YouTube](https://www.youtube.com/watch?v=aYVlD4f7PUA)

## Transcript

next question I create a system wherein the hit ratio is 45% average profit to average loss is 1.75 trades are 2 to 3 month 2 to 3 per month but there are back to back losses at times even seen up to 7 losses in a row this particular difficulty stops me from increasing my trading quantity even when capital is positive can you suggest a solution so I have only limited information here but what I suspect or what I would guess here is that it's something in which the back testing parameters or the output we notice that you are optimizing there can be some room of optimization there so there are things like so-so in back in the contouring strategies you look at this sort in ratio as well as your different ratios which are there and the one basic thing which almost every trader looks at is the drawdown so when you are doing it there's one concept of again a basic concept but not that popular which is the in-sample and out-of-sample trading and which is that you do not optimize your back testing on the whole data set that is available to you you break it down into in sample data and out-of-sample data in the in-sample data you do all the optimizations that you want to do and then you run that strategy on the out-of-sample data which on which it has not been optimized for and you check how the performance is in your case how the drawdown is right so if the drawdown is too high then you need to curb a bit of volatility in your strategy so so which is the risk which is probably too high in case if it is giving results which are showing back-to-back big losses in the out-of-sample data so that's something that might help you and you can you can get more confident of scaling of your strategy with your positive capital
