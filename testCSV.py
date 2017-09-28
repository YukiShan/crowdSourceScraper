import csv
import os

os.chdir("/Users/ssli/Documents/Research/crowdsourceScraper/io/same_cat_v2")
strContents = "Need you to post our pre-written review for Large Dog Wheelchair.Go to this link for additional info: https://docs.google.com/document/d/123GaRxXL7IUi9HJm7N_fCKI9DMfD3fM6yHK23ZUeXXQ/edit?usp=sharingDuplicate reviews will be marked unsatisfied."

with open("src.csv",'r') as f:
    reader = csv.DictReader(f)
    for src in reader:    	          	
        if strContents.find(src['NAME']) != -1:
            print(src['ID']) 
        # if strContents.find(line['NAME']) != -1:
        # 	print(line) 