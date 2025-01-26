# subsync-bazarr
Currently still in development and testing stage, using the project is _not_ currently recommended.

A Docker container consisting of

Written with some help from Claude 3.5-Sonnet, the best coding AI in the world at the time. Although it has come to a point where the AI is more just a tool where I mostly still need to rely on the basic programming skills I possess.

This project could not have come into fruition without these amazing [open-source projects](#credits), written by awesome people.

## What Motivated Me To Do This
After dabbling with Bazarr, its built-in synchronization feature which reaveled itself to be lackluster.

## Installation
1. Download the container from the following Docker-repository: [tarzoq/subsync-bazarr](https://hub.docker.com/r/tarzoq/subsync-bazarr)
2. Create a new folder, then allocate the folder to both Bazarr and the container using ``/subsync-bazarr`` as the container path.
3. Allocate the same media paths as used by Bazarr to the container.
4. Add the following [Environment Variables](#environment-variables) along with their corresponding values: ``API_KEY`` & ``BAZARR_URL``
5. Resource limitations such as CPU-pinning for the container is highly recommended, subsync isn't shy on using processing power. (I for example have it set to one isolated core)
6. Check the container's log, if all prerequisites pass, the script will commence.
7. If all works, add [this](#things-to-add) as a post exectution script in Bazarr.

* Additionally, you can choose to enable subcleaner (KBlixt), by setting the environment variable value "SUBCLEANER" to "true". (Supported languages are: English, Spanish, Portuguese, Dutch, Indonesian and Swedish)

## Environment Variables
| Variable | Description | Default value |
| --- | --- | --- |
| ``API_KEY`` | API key for Bazarr, required to blacklist and request new subtitles in case subaligner receives an error | ``None`` |
| ``BAZARR_URL`` | IP address or hostname for Bazarr | ``http:localhost:6767`` |
| ``SUBCLEANER`` | True or False for if you want subcleaner to process the subtitles | ``False`` |
| ``SLEEP`` | Time interval between check list if it is empty, insert a number | ``300 seconds`` |
| ``WINDOW_SIZE`` | maximum amount of time spent synchronizing subtitle, lower this if subtitles take too long to finish | ``1800 seconds`` |

## Usage
Whenever

## How It Works

### Flowchart
![](img/process_flowchart.png "Flowchart depicting the process")
The process depicted in this flowchart is simplified to demonstrate the fundamentals required to understand how everything fits together.

### Files
| File | Description |
| --- | --- |
| ``addtosynclist.bash``| Script used by Bazarr to add subtitle-entries to |
| ``failed.txt`` | List which |
| ``main.py`` | Main script which runs subsync |
| ``retry.csv`` | Located in the ``logs`` directory |
| ``start.py`` | Script which checks all prerequisites, and if met will launch ``main.py`` |
| ``unsynced.csv`` | List for subtitles-entries |

### What To Do When Subtitles Fail
Whenever a subtitle gets added to failed.txt, it is because the error outputted by subsync depicted through an observable pattern that no subtitle-file in the world could sync to the media file.

## Operating System Support
As of this moment only Linux has been verified to work, the code includes some chmod file copy commands which I'm not sure fare so well with Windows. The code could be modified in those places to check for which operating system is in use and from there select the proper command for the operating system, this could be implemented if enough people request it.

## Subaligner and Subsync
This project actually started out with subaligner.

## Things To Add:
* Add a stopwatch right next to the "Processed, Remaining" row, which stops whenever the current process finishes, giving the user a good overview of how much time each processed subtitle has taken.
* Create a small server or have the ability to connect a server on the side to output the log to be used in apps like NZB360 to view current status.

````
bash /subsync-bazarr/addtosynclist.bash '{{episode}}' '{{subtitles}}' '{{subtitles_language_code2}}' '{{subtitles_language_code3}}' '{{episode_language_code3}}' '{{subtitle_id}}' '{{provider}}' '{{series_id}}' '{{episode_id}}'
````

# Credits
* [subsync (sc0ty)](https://github.com/sc0ty/subsync)
* [subcleaner (KBlixt)](https://github.com/KBlixt/subcleaner)
* [srt-lang-detect (mdcollins05)](https://github.com/mdcollins05/srt-lang-detect)