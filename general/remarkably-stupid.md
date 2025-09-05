# Remarkably Stupid: How I bricked my Remarkable

Recently I purchased a [Remarkable 2 Tablet](https://remarkable.com/products/remarkable-2). I really like the e-ink feel and look, plus I think the [technology](https://www.youtube.com/watch?v=Oqu1--AzM7U) is really interesting.

One of the really neat features about this tablet is that it allows SSH access, so "hacking" into the device is shockingly easy. I was hoping to convert it into some sort of a dynamic calendar that could be mounted onto my refridgerator with a cron job to update the calendar display.

### Cool Stuff

I bought the device and immediatly started messing with it. One of the first things I discovered was that the tracking data just gets sent to /dev/input/event0. I was immediatly able to simply stream this file onto my machine, send it to my browser with a webhook, and display the trackpad on my computer.

![example](https://gitlab.com/afandian/pipes-and-paper/-/raw/master/images/screenshot.jpg)

Image of a guy using it on Mac, I did this on linux and it worked the same.

### Not Cool Stuff

Of course, since I was able to get my remarkable display on my computer, I **HAD** to get my computer display on my remarkable. However, this approach would require my to alter the underlying program that is running the tablet to use images from my desktop.

I decided to insert a simple script into the systemd process running the main program to see if I could gather some data on how the program was working...

Well, there was a bug in whatever I wrote, which crashed the tablet. Unfortunately, since this process runs on startup, it now crashes within a few seconds of starting up. My hope was that I could run a script through SSH the very moment it boots up and before the crash, however, it appeared that SSH never had a chance to establish a connection... and that's how I turned it into a brick.

### Repair

The only thing that made me feel better, was the shear number of people that have done this, including some that have wrote a detailed guide on how to fix this. My understanding is that there are two partitions on the remarkable. Whenever the remarkable starts, it will be using one of those partitions, the other one is used for system updates. That way, if an update breaks the program the tablet can just switch to the partition that didn't get the update. So essentially, I either need to remove my bad file from the partition currently in use, or manually tell the tablet to use the other partition.

In order to do this, I'll need to build a custom pogo connector for the device, short the SBU1 and SBU2 pins of the USB-c connector to enable "recovery mode", and then use the pogo pins to surgically remove the file.

I've ordered the parts and now will just need to solder together the custom connector.

[Recovery Guide](https://github.com/ddvk/remarkable2-recovery)
