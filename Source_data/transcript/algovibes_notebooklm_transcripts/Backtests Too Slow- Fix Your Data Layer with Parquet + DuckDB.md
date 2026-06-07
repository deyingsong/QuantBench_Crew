---
title: "Backtests Too Slow? Fix Your Data Layer with Parquet + DuckDB"
video_id: "Tbo_QgYY6Tw"
url: "https://www.youtube.com/watch?v=Tbo_QgYY6Tw"
duration: "3:19"
source: "NotebookLM YouTube transcript import"
---

# Backtests Too Slow? Fix Your Data Layer with Parquet + DuckDB

[Watch on YouTube](https://www.youtube.com/watch?v=Tbo_QgYY6Tw)

## Transcript

if you do back testing trading strategies in general or statistical analysis in Python you've probably noticed something annoying The more data you have the slower your research becomes And it's not because your strategies are slow It's because loading price data is slow So in this video I'll show you a very practical fix a simple local data layout that makes loading market data fast clean and repeatable Instead of one giant CSV or one giant SQL table we'll store data like this Each symbol day is just its own small file If I update today's data I overwrite one file If I query last week I touch seven files or five files dependent on the asset No global tables no mergers no cleanup Inside those files we use P P is just a compact binary format that loads faster than CSV and doesn't waste time passing text And and because it stores data by columns if I only ask for timestamps and prices only those columns are read To query these files I use duct DB It lets me run normal SQL directly on par files No database server no import step So let me show you the whole thing in code It's simpler than it sounds First I download one minute bars with Y Finance and add two columns a symbol column and a date column The date column is only used to decide which file the data goes into Next I group by symbol and date and write each group as one P file If I run this again tomorrow only tomorrow's files change Nothing else gets touched After running this loop my disk now contains a clean local data store And now the fun part I query all those p files directly with SQL syntax This returns my intraday time series across multiple days as if it were one table But under the hood only the files and columns I asked for were read That's the entire data layer Small files fast loads clean updates Once you have this building EG indicators analysis machine learning stuff and back tests on top becomes much easier and much faster That's what we'll do potentially next
