#!/usr/bin/env python
# coding=utf-8

from xml.dom.expatbuilder import FragmentBuilder
from aeneas.exacttiming import TimeValue
from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task
from aeneas.task import TaskConfiguration
from aeneas.textfile import TextFileFormat
import aeneas.globalconstants as gc

# create Task object
config = TaskConfiguration()
config[gc.PPN_TASK_LANGUAGE] = Language.ENG
config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.PLAIN
config[gc.PPN_TASK_OS_FILE_FORMAT] = SyncMapFormat.JSON
task = Task()
task.configuration = config

task.audio_file_path_absolute = u"/Users/danielread/Downloads/.mp3"
#task.text_file_path_absolute = u"/Users/danielread/Downloads/.txt"

# Add text file programmatically, using id of chapter to retrieve fragments
chapterId = ""

import requests
import json
url = "http://localhost:3090/chapters/" + chapterId
res = requests.get(url)
res = json.loads(res.content)

lines = []
for paragraph in res["chapter"]["paragraphs"]:
  for line in paragraph:
    lines.append(line)

assert len(lines) < 1000, "Text must be fewer than 1000 fragments"

from aeneas.textfile import TextFile
from aeneas.textfile import TextFragment

textfile = TextFile()
for idx, line in enumerate(lines):
  textfile.add_fragment(TextFragment(u"f" + str(idx).zfill(4), Language.DEU, [line], [line]))

task.text_file = textfile

# process Task
ExecuteTask(task).execute()

sentenceStartTimes = ([(float)(f.begin) for f in task.sync_map.fragments])

# # First element relates to "HEAD", always 0
del sentenceStartTimes[0]

# # Last element is always "TAIL"
sentenceStartTimes.pop()

patchDict = {"sentenceStartTimes": sentenceStartTimes}

response = requests.patch(url, headers={'content-type': 'application/json'}, data=json.dumps(patchDict))
print("Response status " + str(response.status_code))
assert response.status_code == 200, "Patch request failed, status code " + str(response.status_code) + ", content: " + response.content

response = json.loads(response.content)
print(response["chapter"]["sentenceStartTimes"])