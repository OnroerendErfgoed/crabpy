import requests
import tarfile
import os

from shutil import copyfile, rmtree

version = "0.3.1"

download_url = (
    "https://github.com/OnroerendErfgoed/deelgemeenten/archive/v%s.tar.gz" % version
)

localfile = "v%s.tar.gz" % version

r = requests.get(download_url, stream=True)

with open(localfile, "wb") as f:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)

tar = tarfile.open(localfile)
tar.extractall()
tar.close()

datafile = "deelgemeenten-%s/data/json/deelgemeenten.json" % version

copyfile(datafile, "../crabpy/data/deelgemeenten.json")
os.remove(localfile)
rmtree("deelgemeenten-%s" % version)
