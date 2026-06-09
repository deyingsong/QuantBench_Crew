---
title: "Look-Ahead Bias - Future Data  | Financial Data Science | Dr. Ernest P. Chan"
video_id: "az7M5X3BEWU"
url: "https://www.youtube.com/watch?v=az7M5X3BEWU"
duration: "3:13"
source: "NotebookLM YouTube transcript import"
---

# Look-Ahead Bias - Future Data  | Financial Data Science | Dr. Ernest P. Chan

[Watch on YouTube](https://www.youtube.com/watch?v=az7M5X3BEWU)

## Transcript

Welcome to this video lesson onlook-ahead bias.After completing this, you will beable to define look-ahead bias andits effects and identify the casesthat have a look-ahead bias.Let’s understand this concept withthe help of an example.Anna has a very simple strategy fromthe USD-MXN futures.In the historical Olaf data,she has found a difference betweenthe spot price and the futuressettlement price, which results ina good arbitrage opportunity.For example, consider a hypotheticalcommodity with the spot price at $100and the futures settlement price at $105,and the futures will expire the next day.I can sell a futures contract at $105.Then I would buy the spot at $100.The next day, I will deliverthe asset to the futures buyer sincethe future expired.Thus, I earned $5 from this transaction.Isn’t that an amazing strategy?And the strategy backtesting, concursthat by showing excellent results.Elsa, who isn’t impressed withextremely good results,decides to do a thorough backtest.But, she uses intraday data,or minute level data, instead ofthe Olaf data used by Anna.And lo and behold,it performs pathetically!So what was it that Anna was doing wrong?On further investigation,Anna realised that the USD-MXN spotclose price from Olaf data was completelydifferent from that of Elsa.Why would that happen?Anna was unknowingly makinga very big mistake.The spot and settlement prices usedin the strategy were sampled attwo different times.The futures settlement price isobtained at 15:00 ET at Sven,while the spot price is obtainedat 17:00 ET by the Olaf data.This is a problem!She was inadvertently looking2 hours in the future.She was making trading decisionsat 3 pm based on the spot pricedata of 5 pm.Thus, her backtest showed excellentresults with the use of informationfrom the future.This is not possible in real trading.Anna had introduced look-ahead biasin her strategy.Look-ahead bias is the use ofinformation and analysis before thetime it would have actually occurred.This gives false often desirableresults in backtests and simulations.There is always only a certain setof data available at any given pointin time.We need to make sure we are not usingdata that will only be availablein the future.
