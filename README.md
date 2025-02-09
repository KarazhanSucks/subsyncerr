# subsyncerr

### Still in development and testing stage, using the project is _currently not_ recommended.

A containerized automated Bazarr-companion that synchronizes the subtitles downloaded by Bazarr using [sc0ty's subsync](https://github.com/sc0ty/subsync). Conditions are set in place for a successful sync that are quite strict, for in which case they aren't met, the subtitle will be blacklisted in Bazarr and a new subtitle will be downloaded. This will in turn leave you with close to 100% of your subtitles in sync.

## Features
* Non-English subtitles sync to already synced English subtitles, which gives the best results.
* Good turnout for Non-English subtitles.
* Blacklisting of bad subtitles, which 
* Logs for subsync and subcleaner, to make troubleshooting easier.
* [Language verification](https://github.com/mdcollins05/srt-lang-detect) on subtitles against language code in filename.
* [Subtitle ad-remover](https://github.com/KBlixt/subcleaner) built-in, can be optionally enabled.

Written with some help from Claude 3.5-Sonnet, the best coding AI in the world at the time. Although it has come to a point where the AI is more just a tool where I mostly still need to rely on the basic programming skills I possess.

Other subtitle synchronizers tested only gave reliable results on English subtitles, and were impossible to interpret when synchroni

This project could not have come into fruition without these amazing [open-source projects](#credits), written by awesome people.

## What Motivated Me To Do This
After months of frustration, googling and dabbling with Bazarr and its built-in sync feature, which left me with many out-of-sync subtitles, I set out to
After dabbling with Bazarr, its built-in synchronization feature which revealed itself to be lackluster.
The project was at first called subaligner-bazarr, which later turned into subsync-bazarr, until I had the excellent idea to name it subsyncarr. Before proceeding I had to make really make sure it was not used, I was taken by surprise that a project by that name had already been taken. For this very reason I decided to name the project ``subsyncerr`` instead. I thought the ultimate way of things was not needing to worry about subtitles, just letting Plex auto-select your preferred language, and them being in sync.

## Installation
1. Download the container from the following Docker-repository: [tarzoq/subsyncerr](https://hub.docker.com/r/tarzoq/subsyncerr)
2. Create a new folder/share, allocate the folder to both Bazarr and the container using ``/subsyncerr`` as the container path.
3. Allocate the same media paths used by Bazarr to the container.
4. Add the following [Environment Variables](#environment-variables) along with their corresponding values: ``API_KEY`` & ``BAZARR_URL``
5. Resource limitations such as CPU-pinning for the container is highly recommended, subsync has no bounds. (I for example have it set to one isolated core)
6. Check the container's Docker-log, if all prerequisites are passed, the script will commence.
7. If all is working, the container will have added the ``addtosynclist-script`` to your newly created folder, simply this as a post exectution script in Bazarr: 
````
bash /subsyncerr/addtosynclist.bash '{{episode}}' '{{subtitles}}' '{{subtitles_language_code2}}' '{{subtitles_language_code3}}' '{{episode_language_code3}}' '{{subtitle_id}}' '{{provider}}' '{{series_id}}' '{{episode_id}}'
````

* Additionally you can choose to enable subcleaner (KBlixt), by setting the environment variable value "SUBCLEANER" to "True". (Supported languages are: English, Spanish, Portuguese, Dutch, Indonesian and Swedish)

## Docker-Compose
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
        TZ: Europe/Berlin
    cpuset: "5"
    restart: unless-stopped
````

## Environment Variables
| Variable | Description | Default value |
| --- | --- | --- |
| ``API_KEY`` | API key for Bazarr, required to blacklist and request new subtitles in case subtitle fails to sync properly | ``None`` |
| ``BAZARR_URL`` | IP address or hostname for Bazarr | ``http:localhost:6767`` |
| ``SUBCLEANER`` | True or False for if you want to enable subcleaner for the subtitles | ``False`` |
| ``SLEEP`` | Time interval between check list if it is empty, insert a number | ``300 (seconds)`` |
| ``WINDOW_SIZE`` | maximum amount of time spent synchronizing subtitle, lower this if subtitles take too long to finish | ``1800 (seconds)`` |

## Usage 
Whenever a subtitle gets added to ``failed.txt``, what I do is double-check to see if the subtitles are correct. In case the English subtitle is in sync and not requiring a manual sync, the non-English subtitles can simply be redownloaded in Bazarr, which will make them sync to the English subtitle.

## How It Works

## Flowchart
![](img/process_flowchart.png "Flowchart depicting fundamentally how everything fits together")
The process depicted in this flowchart is simplified to demonstrate the fundamentals required to understand how everything fits together.

## Files
| File | Description |
| --- | --- |
| ``addtosynclist.bash``| Script used by Bazarr to add subtitle-entries to |
| ``failed.txt`` | List which |
| ``main.py`` | Main script which runs subsync |
| ``retry.csv`` | Located in the ``logs`` directory |
| ``start.py`` | Script which checks all prerequisites, and if met will launch ``main.py`` |
| ``unsynced.csv`` | List for subtitles-entries |

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

## Operating System Support
As of this moment only Linux has been verified to work, the code includes some chmod file copy commands which I'm not sure fare so well with Windows. The code could be modified in those places to check for which operating system is in use and from there select the proper command for the operating system, this could be implemented if enough people request it.

## Subaligner and Subsync
This project actually started out with subaligner.

## Limitations
Please note that certain languages like Korean, Japanese and Chinese media files can't be processed by subsync, so if your library largely includes these languages, they will end up in ``failed.txt`` and you will need to manually sync them if necessary.

## Future Feature Ideas:
* Add a stopwatch right next to the "Processed, Remaining" row, which stops whenever the current process finishes, giving the user a good overview of how much time each processed subtitle has taken.
* Create a small server or have the ability to connect a server on the side to output the log to be used in apps like NZB360 to view current status.

## Disclaimer
A big reason I didn't feel comfortable deeming this project ready for regular use is because if big necessary changes happen to the code, it would take you to redownload all the subtitles to make use of the update.

## Inspirations
* [SubSyncStarter (drikqlis)](https://github.com/drikqlis/SubSyncStarter)
* [Concept, Reddit-user: ``pasm99``](https://www.reddit.com/r/bazarr/comments/106sbub/comment/juszb2v/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

## Credits
* [subsync (sc0ty)](https://github.com/sc0ty/subsync), for syncing the subtitles to audio and other subtitles for Non-English.
* [subcleaner (KBlixt)](https://github.com/KBlixt/subcleaner), for removing advertisements in subtitles.
* [srt-lang-detect (mdcollins05)](https://github.com/mdcollins05/srt-lang-detect), for verifying language in subtitle to language code in the filename.