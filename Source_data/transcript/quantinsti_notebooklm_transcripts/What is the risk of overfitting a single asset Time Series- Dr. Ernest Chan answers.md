---
title: "What is the risk of overfitting a single asset Time Series? Dr. Ernest Chan answers"
video_id: "S5Qk8WJjehQ"
url: "https://www.youtube.com/watch?v=S5Qk8WJjehQ"
duration: "3:22"
source: "NotebookLM YouTube transcript import"
---

# What is the risk of overfitting a single asset Time Series? Dr. Ernest Chan answers

[Watch on YouTube](https://www.youtube.com/watch?v=S5Qk8WJjehQ)

## Transcript

there is a question from Marty uh about um uh the risk of uh you know overfitting a a single asset time series uh and which which uh you know going to and how do we ensure that it will perform well in the out of sample data um that is of course a very uh general you know very important very uh Central problem uh and U many people would um use uh cross validation uh to make sure that uh you know when you build a model uh that it is uh working in a validation set instead of just on the training Set uh and it is also important to um actually uh perform um hyperparameter optimization uh as well as um back testing on the validation Set uh and you know in in terms of optimizing all aspects of the model so it is not just um uh the um uh training the Machine model machine learning model itself but also in optimizing its hyper parameters and also optimizing a trading strategy that utilize the output of the machine learning model that that need to be uh done at the validation level because once you have optimized the uh the the model on the validation Set uh you are you only have one chance to accept or reject that model on two out of sample data if that optimized model is rejected on the out of sample data you should stop working on it because if you then go back to further optimize your model your out of sample data is no longer out of sample so uh you know in general we need to make sure that the validation set will be used many many times in in optimizing all aspects of the model and trading strategy um once you done that uh you get only one chance to test it on the outo sample test and that's the way uh we reject a machine learning model so when you do machine learning uh in trading it is actually a enormously timec consuming process because you will reck so many models uh you know unlike in traditional um training strategy where you can you know every time you encounter something you can uh uh take that as a Improvement you know let's say your model have a draw down oh well maybe I can impose this RIS indicator or that R indicator to avoid it um in machine learning it is actually it's not very cure to do that because if you do that you are actually running straight into the data snooping problem and so you will find that you spend most of your time rejecting models
