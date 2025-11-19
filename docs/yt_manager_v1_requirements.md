# manage youtube videos

a application that i can add a video url to a list and the app will
1. download information (title, channel, pub date, duration) from the google api
2. download the video file via the ytdlp integration
3. store the file_path of the downloaded file.

then i can click a button and the downloaded file can be
a. sent to a video player to be played
b. deleted
c. saved to a new folder

## video status fields (status, download, viewed)

status
- new: (default) the video has been added to the table
- open: the video has been accepted
- down: the file has been downloaded
- archive: the file has been moved to the archive folder
- closed: the file was never downloaded (skipped) or was deleted
- error: if there is an error with this video. (ex. file cannot be found, google api error, ytdlp download failed) this is set. and a corresponding "error message" field is set.

download
- no: (default) not downloaded
- yes: please download
- down: the video has been downloaded

viewed
- no: (default) the video has not been sent to a player
- yes: the video has 

## timestamp fields

- create_dt: the timestamp for the the video record being added to the db
- modified_dt: the timestamp for the last time the video record was modified.
- published_dt: the data that the video was published to youtube
- download_dt: the timestamp for when this video was downloaded
- view_dt: timestamp for when this video was sent to the media player
- delete_dt: timestamp for when the video was deleted

## technical dev stack

- python
- sqlite: the database
- google youtube api: use this to get the information about the video
- tkinter: use tkinter for the UI functions
- yt-dlp: use this to dowload the videos

## Suggested file\folder scheme

yt-manager/

	app/
		__init__.py
		config.py                       # configuration logic
		config/
			ytdlp-config.txt            # config file for the ytdlp executable
		core/
			__init__.py
			videos.py                   # class to encapsulate all video parameters and methods
			channels.py                 # class to encapsulate all channel parameters and methods
			app.py                      # main class to orchestrate all of the logic
			google.py                   # class to encapsulate all the google data api interactions
			ytdlp.py                    # class to encapsulate all the ytdlp interactions
		db/
			__init__.py
			video.py                    # class to abstract all the db interactions
			yt-manager.db               # the sqlite db file
		ui/                             # the Tkinter logic should live here
		cli/                            # an interface for command-line logic
		utils/
			logger.py                   # a file to set up logging to my personal specs.
			file_tools.py               # collects tools to interact with the filesystem
			video_player.py             # collects the tools to play videos
			open_db.bat                 # a windows batch file that can be used to open the sqlite file in "DB Browser for SQLite"
	
	tests/
	docs/
	
	pyproject.toml
	README.md
	.env

## ytdlp

- the actual executable for ytdlp stored outside of this app but is available on the windows PATH
- this app will maintain it's own config file for the tool and will pass the location to the config file as a command-line arg.
- this tool can execute a command when it completes a download. So our app will need a command-line option to catch that command so that we can record where the video file was saved.

## tkinter

- there will be other screens in the future but for this phase there is only one screen "Video Queue"

### Video Queue Elements

1) a field and button to add a new video to the queue.
2) a "table" to manage the videos in the queue. (where status = new, open, down or error)
	- for each video there is a row in the table with
	a. videoid
	b. status
	c. title
	d. channel
	e. play button
	f. del button
	g. archive button
3) there is a refresh button to refresh the table.
4) there is a buton to open a "DB Browser" tool (the path to the exe will be in the config) and pass in the path to the sqlite db file.

### Add a video to the queue.

when a video is added from this interface these are the things that will happen.

1) set the status to open
2) use the google interface to get the metadata for the video.
3) use the ytdlp interface to download the file.
4) refresh the table.

 