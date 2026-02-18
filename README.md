Lightweight Server Modpack Updater is a very simple tool I created to help players on my server consistently and easily update their modpacks.  Beware, this isn't really production-ready, since it's something I had originally thrown together in like 2 hours as a test for another project before releasing it here.  It serves as a sort of testbed for a more polished project coming soon...

For anyone wanting to use it for their own personal ends, there is ABSOLUTELY NO WARRANTY of any kind, nor can I be held liable for any issues or damages.  The license is technically ARR.  To use the tool, a server administrator should create or upload a Dropbox folder with all the mods in it.  This folder should also have a file called 'custom_launcher_metadata.json' and should have the following structure:
```json
{
  "modset": {
    "mc_version": "1.21.1 <or other mc version>",
    "modloader": "Neoforge <or other modloader>",
    "modloader_version": "21.1.200 <or other modloader version>"
  }
}
```
This file will give the tool a reference for downloading the versions and tools players will need to play.  The tool assumes you have Minecraft: Java Edition installed and will install everything else if it needs to.  If there are issues with the Java install, I recommend installing Java from `java.com/en/download`, then trying to re-run the tool.

Finally, because I know someone will try it, this tool is FOR JAVA EDITION ONLY - BEDROCK DOES NOT HAVE A MODDING FRAMEWORK IN THE SAME WAY.  IF YOU TRY TO USE THIS ON BEDROCK, IT WILL FAIL.

For server owners / admins, the Dropbox pack should be kept up-to-date with your current modpack and the version informtion in the custom metadata file.  The players' clients will then get this updated information when they run `do update` in the tool, after pasting in the Dropbox link.
