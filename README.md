OS: Windows </br>
Movies (not TV)

Folder 1 = Source / Torrent Download folder (Remains untouched)

Folder 2 = Destination (Should be empty, no requirement tho)

(*Use move_arr_downloads_folder.py afterwards on Folder 1 to move it to a different drive, Hardlinks only work on the same drive.)
___________________________________________________________________________________________________________________
e.g.

Folder 1 contains:</br>
La.Collectionneuse.1967.FRENCH.1080p.BluRay.x264-CherryCoke.mkv

Folder 2 </br> 
empty

RUN SCRIPT

Folder 1 still contains:</br>
La.Collectionneuse.1967.FRENCH.1080p.BluRay.x264-CherryCoke.mkv

Folder 2: </br>
Folder [La Collectionneuse (1967)] -> File "La Collectionneuse (1967) BluRay-1080p.mkv"

For each Movie a new folder + file link is created.
___________________________________________________________________________________________________________________
Note: "Skipped Files" are also files which already been named perfectly. They are hardlinked! It just means they been skipped by initial processing.
Just to be sure still check if file count is the same in source and destination folder by the end.


SourceFolder
    |
    |- La.Collectionneuse.1967.FRENCH.1080p.BluRay.x264-CherryCoke.mkv
    |- Cats(2001)
          |-Cats.2001.mkv

DestinationFolder #Empty Folder on Start, files are Hardlinks
    |
    |- La Collectionneuse (1967)
              |- La Collectionneuse (1967) BluRay-1080p.mkv
    |- Cats (2001)
              |- Cats (2001) WebDL-720p.mkv
