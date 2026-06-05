---
title: "Algo Trading - Cringe Moments 4"
video_id: "pYiis0prxSU"
url: "https://www.youtube.com/watch?v=pYiis0prxSU"
duration: "3:35"
source: "NotebookLM YouTube transcript import"
---

# Algo Trading - Cringe Moments 4

[Watch on YouTube](https://www.youtube.com/watch?v=pYiis0prxSU)

## Transcript

hi there i'm champion trader kevin davey and here's another cringy moment in algo trading okay let's talk about cringy things in algo trading what do i mean by that well it's things i've seen over the years things i've probably done myself that are just like oh i can't believe somebody did that and this cringey moment is the number of iterations and the number of variables that people use when they're creating back tests this makes me cringe here's an example i put a bunch of strategies into a chart and i optimize them all i think i have about 12 variables here so and i have over 2 billion 2 billion iterations i bet something's going to work right lots of people do this and they think oh i'll let it run all week and this has got to be a great way to do it well one you don't even want to do this and two you wouldn't want to run all 2 billion you'd probably use what's called genetic optimization and when you do that you can get down a lot better as far as less runs but that's not really solving the problem right people think it is because oh well now i save time by doing this uh the whole cringy part is you started out with way too complicated of an approach with way too many variables and way too many iterations but for the sake of this video i ran it here's what i get this is a pretty nice looking equity curve this was from genetic optimization and you could say hey this is good i'm going to start trading this well again i've said it over and over again back tests really don't matter what really matters is the live performance and there's the live performance for you so i stopped optimizing right at the start of that blue period here's what it looks like since then it's a dog you'd never want to trade this right but if you just looked at the back test you'd think you had something good so the point here and this is just one example but the point here is when you have too many iterations and too many variables you are curve fitting you are over optimizing you're fitting the past and the future is not going to be like the past and you probably will end up with a strategy that falls apart might take a little while you see this one it took a little while to fall apart but eventually it falls apart so cringy moment in algo trading is using too many rules too many variables too many iterations avoid that and you'll be much better off i'm kevin davey thanks for watching you
