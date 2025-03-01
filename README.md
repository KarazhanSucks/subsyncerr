# subsyncerr
### Still in development and testing stage, using the project is _currently not_ recommended.

A containerized automated Bazarr-companion that synchronizes the subtitles downloaded by Bazarr using [sc0ty's subsync](https://github.com/sc0ty/subsync). Conditions are set in place for a successful sync that are quite strict, for in which case they aren't met, the subtitle will be blacklisted in Bazarr and a new subtitle will be downloaded. This will in turn leave you with close to 100% of your subtitles in sync.

## Features
* Great turnout for non-English subtitles, thanks to ``subsync's`` ability to sync them to already synced English subtitles, which evidently achieve more reliable results.
* Simple concept, aimed to work as universally as possible, while also keeping the setup process easy to follow.
* Blacklisting of bad unsyncable subtitles, only leaving successfully synced subtitles.
* Prerequisites for file permissions and Bazarr API-access before running ``main.py``, to ensure everything works as expected.
* Logs stored for ``subsync`` and ``subcleaner``, making troubleshooting easier.
* Downloaded subtitles get added as entries in a ``CSV``-file, enabling Bazarr to work independently from ``subsyncerr``.
* Separate ``CSV-file`` used for temporarily storing bad subtitles to blacklist while Bazarr-API is unreachable, ensuring that nothing gets swept under the rug.
* Although rare, subtitles that can't be synced by ``subsync`` because of either a bad media file or an unsupported language, will get added as an entry in ``failed.txt``, a list for subtitles requiring manual intervention.
* [Language verification](https://github.com/mdcollins05/srt-lang-detect) on subtitles against language code in filename, which in my experience is deemed necessary.
* [Subtitle ad-remover](https://github.com/KBlixt/subcleaner) built-in, can be optionally enabled.

This project could not have come into fruition without these amazing [open-source projects](#credits), written by awesome people.

## Installation
1. Pull the container from the following Docker-repository: [tarzoq/subsyncerr](https://hub.docker.com/r/tarzoq/subsyncerr)
2. Create a new folder/share, allocate the folder to both Bazarr and the container using ``/subsyncerr`` as the container path.
3. Allocate the same media paths used by Bazarr to the container.
4. Add the following [Environment Variables](#environment-variables) along with their corresponding values: ``API_KEY`` & ``BAZARR_URL``
    * Additionally you can choose to enable subcleaner (KBlixt), by setting the environment variable value "SUBCLEANER" to "True". (Supported languages are: English, Spanish, Portuguese, Dutch, Indonesian and Swedish)
5. ``CPU-pinning`` for the container is highly recommended, subsync uses all it can get. (I for example have it set to one isolated core)
6. Check the container's Docker-log, if all prerequisites are passed, ``main.py`` will commence.
7. The container will now have added all necessary files, including the ``addtosynclist``-script to your newly created folder. Last step, simply add this as a post exectution script in Bazarr: 
    ````
    bash /subsyncerr/addtosynclist.bash '{{episode}}' '{{subtitles}}' '{{subtitles_language_code2}}' '{{subtitles_language_code3}}' '{{episode_language_code3}}' '{{subtitle_id}}' '{{provider}}' '{{series_id}}' '{{episode_id}}'
    ````

### Docker-Compose
````
version: "3.8"
services:
  subsyncerr:
    image: tarzoq/subsyncerr:latest
    container_name: subsyncerr
    volumes:
      - /folder/path:/subsyncerr
      - /media/path:/container/path
    environment:
        API_KEY: None
        BAZARR_URL: http://localhost:6767
        SUBCLEANER: True # Optional, False by default
        TZ: Europe/Berlin
    cpuset: "5"
    restart: unless-stopped
````

## Environment Variables
| Variable | Required | Description | Default value |
| --- | --- | --- | --- |
| ``API_KEY`` | Yes | API key for Bazarr, required to blacklist and request new subtitles in case subtitles fail to synchronize. | ``None`` |
| ``BAZARR_URL`` | Yes | IP address/hostname and port for Bazarr. | ``http:localhost:6767`` |
| ``SUBCLEANER`` | No | True or False for if you want to enable ``subcleaner`` when processing subtitles. | ``False`` |
| ``SLEEP`` | No | Time interval for how often to check ``unsynced.csv`` for new entries when it is empty. | ``300 (seconds)`` |
| ``WINDOW_SIZE`` | No | Maximum window of time for ``subsync`` to spend synchronizing subtitles, lower this if you think subtitles take too long to finish (wouldn't recommend for most people). | ``1800 (seconds)`` |

## What Motivated Me To Do This
It all started when I got into using Plex along with the *arrs, but more specifically, Bazarr. It was not unusual for me to sit down to watch something, only for the subtitles to be completely out-of-sync. If you're anything like me, you'd rather have no subtitles than subtitles that are so out-of-sync they need to be manually disabled.

With other people using my server, I recognized the significance to this issue. The feeling of unreliability when pressing play, anxiously hoping the subtitle would be in sync, fueled my frustration, forcing me to set out for a solution.

My first quest started by dabbling with Bazarr and its built-in sync feature (``ffsubsync``). At first I felt hope in thinking I had found the solution. However, as someone with English as their second-language, it quickly revealed that the results for non-English subtitles were quite futile.

This expanded my search to Reddit, GitHub

Which left me with many out-of-sync subtitles, I set out to
After dabbling with Bazarr, its built-in synchronization feature which revealed itself to be lackluster.

My main goal was to come up with a solution for out-of-sync non-English subtitles.



The project was at first called subaligner-bazarr, which later turned into subsync-bazarr, until I had the excellent idea to name it subsyncarr. Before proceeding I had to make really make sure it was available, and I was taken by surprise that a project by that name had already been taken. For this very reason I decided to name the project ``subsyncerr`` instead. I thought the ultimate way of things was not needing to worry about subtitles, just letting Plex auto-select your preferred language, and them being in sync.

## Usage 
Whenever a subtitle gets added to ``failed.txt``, what I do is double-check to see if the subtitles are correct. In case the English subtitle is in sync and not requiring a manual sync, the non-English subtitles can simply be redownloaded in Bazarr, which will make them sync to the English subtitle.

Other subtitle synchronizers tested only gave reliable results on English subtitles, and were impossible to interpret when synchroni



## How It Works

## Flowchart
![](img/process_flowchart.png "Flowchart depicting fundamentally how everything fits together")
The process depicted in this flowchart is simplified to demonstrate the fundamentals required to understand how everything fits together.

## Files
| File | Description |
| --- | --- |
| ``addtosynclist.bash``| Script used by Bazarr to add subtitle-entries to |
| ``failed.txt`` | List of subtitles for which media file couldn't be processed by subsync |
| ``main.py`` | Main script which does all the magic |
| ``retry.csv`` | Located in the ``logs`` directory |
| ``start.py`` | Script which checks all prerequisites, and if met will launch ``main.py`` |
| ``unsynced.csv`` | List of subtitles-entries which are yet to be processed |

## Folder structure
```
/subsyncerr
├── addtosynclist.bash
├── failed.txt
├── unsynced.csv
└── /logs
    ├── retry.csv
    ├── /subcleaner
    └── /subsync
```

When processing a non-English subtitle, it will first look in ``unsynced.csv`` for an English counterpart. If that is found, that is processed first. If it doesn't exist in the list but does as a file, it will sync to that subtitle file. If neither of those are true, it will sync the non-English subtitle directly to the audio, just like it would and English subtitle. The results however from  my testing is that syncing the non-English subtitle directly to the audio yields much worse results than the English subtitle would. For this very reason the script will redownload all non-English subtitles when an English subtitles has been synced. This also works out well if an English subtitle is upgraded, which in my experience probably leads to similar or better results when synced.

In my testing, I arrived at the conclusion that non-English subtitles synced to the English subtitles yielded the best results.

In some cases the minimum point requirement is not enough to stop out of sync subtitles from getting through, basically they still get a high points just an in sync subtitle would. This is something caused directly by subsync, which makes it impossible for me to fix in the script.

## What To Do With Subtitles In ``failed.txt``
Whenever a subtitle gets added to failed.txt it is because the error outputted by subsync characterized through an observable pattern, couldn't process the media file properly. Either get another media file or sync manually.

The only supported audio track languages are Chinese, Dutch, English, French, German, Italian, Russian and Spanish. Media files in any other language will most likely result in the subtitles being added to failed.txt.

## Operating System Support
As of this moment only Linux has been verified to work, the code includes some chmod file commands which I'm not sure fare so well with Windows. The code could be modified in those places to check for which operating system is in use and from there select the appropriate command for the system, this could be implemented if enough people request it.

I personally am running this on Unraid.

## Subaligner and Subsync
This project actually started out with subaligner.

## Limitations
Please note that certain languages like Korean, Japanese and Chinese media files can't be processed by subsync, so if your library largely includes these languages, they will end up in ``failed.txt`` and you will need to manually sync them if necessary.

## Future Feature Ideas:
* Add a stopwatch right next to the "Processed, Remaining" row, which stops whenever the current process finishes, giving the user a good overview of how much time each processed subtitle has taken.
* Create a small server or have the ability to connect a server on the side to output the log to be used in apps like NZB360 to view current status.
* Add notification module for when subtitle gets added to failed.txt

## Disclaimer
A big reason I didn't feel comfortable deeming this project ready for regular use is because if big necessary changes happen to the code, it would take you to redownload all the subtitles to make use of the update.

Have you ever felt anxious about sitting down with family or friends, about to watch a newly added movie, but having no comfort in knowing if the subtitles are going to be in sync? Then you have come to the right place! I used to feel the exact same way. The available options at the time, like the built-in ffsubsync in Bazarr, was very hit or miss, and being from a different country, non-English subtitles were even worse.

## Inspirations
* [SubSyncStarter (drikqlis)](https://github.com/drikqlis/SubSyncStarter), inspired the act of blacklisting subtitles.
* [Concept, Reddit-user:](https://www.reddit.com/r/bazarr/comments/106sbub/comment/juszb2v/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) ``pasm99``

## Credits
Written with some help from Claude 3.5-Sonnet, the best coding AI in the world at the time. Although it has come to a point where the AI is more just a tool where I mostly still need to rely on the basic programming skills I possess.

* [subsync (sc0ty)](https://github.com/sc0ty/subsync), for syncing the subtitles to audio and other subtitles for non-English.
* [subcleaner (KBlixt)](https://github.com/KBlixt/subcleaner), for removing advertisements in subtitles.
* [srt-lang-detect (mdcollins05)](https://github.com/mdcollins05/srt-lang-detect), for verifying language in subtitle to language code in the filename.