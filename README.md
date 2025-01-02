# subsync-bazarr
Currently still in development and testing stage, using the project is not recommended at the moment.

subsync (sc0ty) + subcleaner (KBlixt) + srt-lang-detect (mdcollins05)
<br />

once I'm satisified enough with my testing, I will soon get to write a proper README-file, and complete all steps required to get this quality of life improving script up and running.

Written with some help from Claude 3.5-Sonnet, the best coding AI in the world at the time. Although it has come to a point where the AI is more just a tool where I mostly still need to rely on the basic programming skills I possess.

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

# Operating System Support
As of this moment only Linux has been verified to work, the code includes some chmod file copy commands which I'm not sure fare so well with Windows. The code could be modified in those places to check for which operating system is in use and from there select the proper command for the operating system, this could be implemented if enough people request it.

# Things to fix:
Add a stopwatch right next to the "Processed, Remaining" row, which stops whenever the current process finishes, giving the user a good overview of how much time each processed subtitle has taken.


Create a small server or have the ability to connect a server on the side to output the log to be used in apps like NZB360 to view current status.


~~~
bash /subsync-bazarr/addtosynclist.bash '{{episode}}' '{{subtitles}}' '{{subtitles_language_code2}}' '{{subtitles_language_code3}}' '{{episode_language_code3}}' '{{subtitle_id}}' '{{provider}}' '{{series_id}}' '{{episode_id}}'
~~~