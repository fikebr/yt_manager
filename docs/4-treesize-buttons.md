# Add treesize buttons to the button bar

1) in the ui folder rename main_window.py to video_queue.py. this leaves space for future forms.

update run_ui.py with the new file name

2) on the video_queue form. add two buttons next to the 'open db' button... 'Tree New' & 'Tree Archive'

these buttons will open the treesize app pass in the DOWNLOAD_DIR or ARCHIVE_DIR from settings.
the path to the treesize app will be stored in settings.py

TREESIZE = E:/PortableApps/PortableApps/TreeSizeFreePortable/TreeSizeFreePortable.exe

when executing treesize we are not trying to capture output or exit codes and we do not want to wait for the tool to close. just run the command 