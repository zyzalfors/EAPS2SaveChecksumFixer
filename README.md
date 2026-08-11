# EA PS2 Save Checksum Fixer
This command-line tool repairs checksums in save files for several Electronic Arts PlayStation 2 games.

Some EA PS2 games use a common checksum routine—with some exceptions for Need for Speed Underground/Most Wanted—to guarantee the integrity of save data. After modifying a save file with an editor or manually changing its contents, the checksum may no longer match the data, causing the game to reject the save or report it as corrupted. This tool recalculates and fixes the checksums so that modified saves can be recognized by the game again.

Currently supported PS2 games:
* Need for Speed Underground
* Need for Speed Underground 2
* Need for Speed Most Wanted
* Need for Speed Carbon
* Need for Speed ProStreet
* The Godfather
