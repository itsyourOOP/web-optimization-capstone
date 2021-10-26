
#export DISPLAY=:1
#Xvfb $DISPLAY -screen 0 1024x768x16 &

#./chrome78/chrome --remote-debugging-port=9222 --renderer-process-limit=1 --aggressive-cache-discard --disable-cache --disable-application-cache --disable-offline-load-stale-cache --disk-cache-size=0


#./chrome78/chrome --remote-debugging-port=9222 --renderer-process-limit=1 --disable-cache --disable-application-cache

./chrome78/chrome --no-zygote --no-sandbox --headless --disable-gpu --remote-debugging-port=9222 --renderer-process-limit=1 --disable-cache --disable-application-cache --disk-cache-size=0
