---
title: "How to get LIVE cryptocurrency data with Python using the Binance API / ERROR FIXING"
video_id: "OX5eDJDtqhc"
url: "https://www.youtube.com/watch?v=OX5eDJDtqhc"
duration: "3:26"
source: "NotebookLM YouTube transcript import"
---

# How to get LIVE cryptocurrency data with Python using the Binance API / ERROR FIXING

[Watch on YouTube](https://www.youtube.com/watch?v=OX5eDJDtqhc)

## Transcript

hi guys so just real quick a lot of you had some issues with getting the live stream run they are getting error messages after some time and i want to show you an alternative approach and i just ask you to try it out and give you feedback if this solution is working out for you so this is the python binance documentation and i'm simply copy pasting the code here right and if you're working so you can if you're working with an ide or raw python you can just take this as it is right so of course you have to install some necessary libraries like async io if you're using jupyter you have to do some amendments so i'm just structuring it like so by the way we also need pandas so we have it like so this is the trade socket so we can just use bitcoin usdt and now we have the problem if we would execute that like so we can error messages that a event loop is already running right you can by the way check that by using syngio get event loop and then you will see that there is a running event loop here but anyhow you can fix that by just importing nest sync io of course you have to install it beforehand and then just use nes essence io dot apply and with these fixes you can just use it like so so let's execute that and you'll see that we're getting live data for the bitcoin right so yeah just please test it out if this is working for you and let it run for like uh some some minutes or hours and please give me feedback if this is working out for you so i was working with this create frame function so it's pretty straightforward to implement that let me quickly just copy paste it for my other screen so this was the function by the way this is happening because the loop is still running so normally you would just use loop stop but then the kernel will die most probably yes but this doesn't matter we're just restarting it then execute that and now we are just using create frame on this and then we are getting the known output here right so yeah again please try it out uh give me feedback and then i will use this approach in the next bots right so yeah i would highly appreciate if you if you if you just give me um feedback on that thank you very much for watching and yeah i'm looking forward to seeing the upcoming videos bye
