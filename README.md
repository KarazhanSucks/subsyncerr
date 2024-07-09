# subaligner-bazarr
subaligner (baxtree) + subsync (sc0ty) + subcleaner (KBlixt)

API_KEY = API key for Bazarr, this one is required and is used to blacklist and request new subtitles in case subaligner receives an error

BAZARR_URL = IP address or hostname for Bazarr (default is: http:localhost:6767)

SUBCLEANER = true or false for if you want subcleaner to process the subtitles (default is false)

SLEEP = time waiting to check list if it is empty, insert a number (default 300 seconds)


Things to fix:
Timestamp in main.py doesn't update time because placed in top of code where it is only processed once.
Change -mpt in subaligner from 360 to 1000, to support older slower computers that need more time to extract audio from video.
