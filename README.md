# subsync-bazarr
subsync (sc0ty) + subcleaner (KBlixt)
<br />

Written with the help of Claude 3.5-Sonnet, the best coding AI in the world at the time.

# Environment Variables
~~~
API_KEY = API key for Bazarr, required to blacklist and request new subtitles in case subaligner receives an error
~~~
~~~
BAZARR_URL = IP address or hostname for Bazarr (default is: http:localhost:6767)
~~~
~~~
SUBCLEANER = true or false for if you want subcleaner to process the subtitles (default is false)
~~~
~~~
SLEEP = time waiting to check list if it is empty, insert a number (default 300 seconds)
~~~
~~~
WINDOW_SIZE = maximum amount of time spent synchronizing subtitle, lower this if subtitles take too long to finish (default 1800 seconds)
~~~
<br />

# Things to fix:
Add a stopwatch right next to the "Processed, Remaining" row, which stops whenever the current process finishes, giving the user a good overview of how much time each processed subtitle has taken.


Create a small server or have the ability to connect a server on the side to output the log to be used in apps like NZB360 to view current status.


~~~
bash /subaligner-bazarr/addtosynclist.bash '{{episode}}' '{{subtitles}}' '{{subtitles_language_code2}}' '{{subtitles_language_code3}}' '{{episode_language_code3}}' '{{subtitle_id}}' '{{provider}}' '{{series_id}}' '{{episode_id}}'
~~~
