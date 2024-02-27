22/03/2024 - Review EPSS generation code, seperating CSV cleaning with EPSS adding code
I decide to gather all the data about cve from mitre rather than manually adding.
It's good to have a full database afterall. Even if we don't use them all up.
https://cve.mitre.org/data/downloads/index.html
I download the file as a CSV, then write a code to add the EPSS using that very same database
"""

26/02/2024 - Decided to chop the dataset for random sampling down to 300 cves
Turn out even with 300 cves the gathering rate through api was still painfully slow
was happy that by some miracle the code suggested by bing worked and now we got absolute random two TPGs with extreme complex config
(85 differents connections with 300 lines of HTPG-ing)
the flow of TPGs is as follow:

allitems.csv -(manual cleaning)-> handclean.csv -(filter for entry only)-> handclean-entryonly.csv -(add privilidge)-> handclean-entryonly-processed.csv -(randomly sampling 300)->
selected-300-entries.csv -(add EPSS)-> 300-entries-epss.csv -(auto generate environment)-> HTPG.csv + NTPG.csv

file that related to the process:
manual cleaning: via excel/WPS sheet
filter for entry only: via excel/WPS sheet
add privilidge: data-process-01.py
randomly sampling 300: data-select-rand.py
add EPSS: epss-retrieval-v2.py
auto generate environment: autoenvgenerator.py

Now all the work left is to merge all of these into a single tool for ease of use
future idea would be for this tool to run once in a while for updating agent learning material

Our professor also suggest the change in graphing so this may not even get used at all
"""

