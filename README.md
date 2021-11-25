# Social Computing Final Project

This is the preprocessing script for the Social Computing final project, which translates text to English, cleans it, and lemmatizes it.

The steps to run the script are as follows.

1. Pull this repo onto your machine (make sure you have [lfs](https://git-lfs.github.com/) installed with Git).
2. Download the <i>ENTIRE</i> campaign folder from the Google Drive (for example, the [russia_jun2020](https://drive.google.com/drive/folders/1k8irJtv-ueEWq3bVeKZdApZeTy_wErT4?usp=sharing) or [russia_oct2018](https://drive.google.com/drive/folders/1n1yeuWUm-YOAznE1WWb94dOU0fSqMkfb?usp=sharing) folders) and move the whole folder into the /data directory.
3. Install required packages using the requirements.txt file (for example, with pip3 install -r requirements.txt).
4. Run the script. This will take close to 2-4 days depending on your machine. A convenient way to run this is with: 

**chmod +x preprocessing.py**

**nohup ./preprocessing.py *campaign_folder_name* > output.log &**

^This will run the script in the background and log output to the text file output.log. The progress of the script can be checked with 

**cat output.log**

This will display some information about how many lines in total there are to process and how many have been processed so far. [This article](https://janakiev.com/blog/python-background/) has more information about how to interact with the background process, including finding its PID and if something goes wrong, how to kill it.