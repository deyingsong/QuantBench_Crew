---
title: "You’re Probably Overestimating Your Python Skills"
video_id: "fCvxZyR6dnA"
url: "https://www.youtube.com/watch?v=fCvxZyR6dnA"
duration: "3:05"
source: "NotebookLM YouTube transcript import"
---

# You’re Probably Overestimating Your Python Skills

[Watch on YouTube](https://www.youtube.com/watch?v=fCvxZyR6dnA)

## Transcript

all right this is basically a Python skill check i'll show you a few snippets and for each one you should pause the video and decide what actually happens or what's wrong with it if you write Python regularly you should be able to reason through these most people can't so don't run the code pause think then unpause let's see how solid your Python really is first one imagine n is very big does this run at the same speed all the time or does it get slower and slower it gets slower and slower each loop creates a new list and copies everything into it when the list is small you don't notice when it gets big it becomes very slow second one if this runs on a lot of real data can you always trust the results not always floating point numbers are not exact when you add many of them small errors appear number three after this runs did we change A or only B we change A this slice does not create a new array it points to the same memory so changing B also changes A number four when this finishes do you always get the same number nope you don't updating X takes more than one step the two threads can mix their steps that means some updates are lost last one do these two calls create two cash entries or just one just one python treats two and 2.0 as equal keys so the cache cannot tell them apart if most of these failed easy that's good if a few surprised you that's normal and if all of them surprised you this video did its job
