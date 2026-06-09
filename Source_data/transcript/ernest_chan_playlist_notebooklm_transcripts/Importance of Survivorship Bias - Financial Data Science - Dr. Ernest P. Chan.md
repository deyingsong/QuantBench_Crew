---
title: "Importance of Survivorship Bias | Financial Data Science | Dr. Ernest P. Chan"
video_id: "GyEbt9zUhAM"
url: "https://www.youtube.com/watch?v=GyEbt9zUhAM"
duration: "2:56"
source: "NotebookLM YouTube transcript import"
---

# Importance of Survivorship Bias | Financial Data Science | Dr. Ernest P. Chan

[Watch on YouTube](https://www.youtube.com/watch?v=GyEbt9zUhAM)

## Transcript

welcome to this video on survivorship bias after completing this video you will be able to define survivorship bias explain the importance of survivorship bias and how to solve it during back testing the strategy we often tend to Baptist on the current stock universe instead of the historical stock universe that is we use the stock universe that has survived until today to Baptist ignoring the stocks that no longer exists today due to various reasons such as bankruptcies acquisitions and delisting this is known as survivorship bias but why is it important in back-testing to consider the stocks that no longer exist today back testing a strategy using data with survivorship bias results in unrealistic and inflated results see this example of buy low priced stocks strategy in this strategy from a 1000 stock universe you buy 10 stocks with the lowest price at the beginning of the year and sell those 10 stocks at the end of the year the screen shows 10 stocks with the lowest price at the start of the year 2001 this data is without survivorship bias all these stocks were delisted between 2nd January 2001 and 2nd January 2002 except MDM the terminal prices the last traded price back-testing buy low priced stocks strategy on this data results in a total portfolio return of minus 44% however if we create a list of the 10 lowest price stock which survived during the period in the year 2001 then we get the list shown on the screen the results of buy low price stock strategy are astonishing 388 % these returns are highly unrealistic as difficult to predict which stocks will survive and which stock will not so it is important to use data without survivorship bias for accurate back testing results but the real issue is how to ensure or create survivorship bias free data one of the approaches is to buy expensive survivorship bias free data some of the examples of such databases are shown on the screen another method is to collect your data day by day which can be used for back testing however this method is very time-consuming another approach is to use only recent data not more than three years old that's all for this video in the upcoming sections you will learn to deal with sentiments data
