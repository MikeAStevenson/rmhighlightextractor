import json, sys, os
from zipfile import ZipFile
import pprint
import argparse
import csv

def main():
    parser = argparse.ArgumentParser(
            description='A program for reading exported .zip files from Remarkable and parsing to extract highlights. Tested on zips extracted using rmapi')
    parser.add_argument("-rd","--root_dir"
                , help="Root directory containing folders/files extracted from Remarkable",required=True)
    parser.add_argument("-ot", "--output_type"
                , help="Type of output to produce (to screen, csv file)."
                , choices=['csv','screen']
                , default='screen')
    parser.add_argument("-o","--output_file"
                , help="Output filename for file based outputs. Ignored for screen outputs")
    args = parser.parse_args()

    if args.output_type != 'screen' and args.output_file == None:
        parser.error('The --output_type of '+args.output_type+' requires --output_file')

    if not os.path.isdir(args.root_dir):
        print(args.root_dir, " is not a valid directory, exiting...")
        exit()

    #print(args)

    #print("Hello!!!")

    rootdir = args.root_dir

    myDocuments = []
    normalizedDocuments = []

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            # Check out the zips for the highlights
            if file.endswith(".zip"):
                # initialize empty object for use later
                myDocument = {}

                myDocument['filename'] = file

                fullPath = os.path.join(subdir, file)
                # Open zip
                with ZipFile(fullPath, 'r') as currZip:
                    for f in currZip.namelist():
                        # Get some info and metadata from .content file

                        if (f.endswith(".content")):
                            contentJson = json.load(currZip.open(f))
                            
                            # Grab info from metadata so we can output it later
                            myDocument['documentMetadata'] = contentJson['documentMetadata']
                            myDocument['pages'] = contentJson['pages']
                            myDocument['pageTags'] =  contentJson['pageTags']
                            myDocument['pageCount'] = contentJson['pageCount']
                            myDocument['originalPageCount'] = contentJson['originalPageCount']
                            myDocument['redirectionPageMap'] = contentJson['redirectionPageMap']

                            myDocument['rawHighlight'] = []
                        if ("highlights" in f):

                            # Read the higlights files to process them through
                            highlightJson = json.load(currZip.open(f))

                            #print(highlightJson)
                            for highlight in highlightJson['highlights']:
                                for x in highlight:
                                    myDocument['rawHighlight'].append(x)
                                    # split out filename so we can use it later to compare against metadata
                                    path, x = os.path.split(f)
                                    y, ext = os.path.splitext(x)
                                    myDocument['rawHighlight'][-1]['page'] = y
                    # add myDocument to array
                    myDocuments.append(myDocument)
    # Now that we're done reading the zips, process through the data
    for document in myDocuments:
        print("Working on...", document['filename'])
        authorString = ','.join(document['documentMetadata']['authors'])
        print("\tAuthors -", authorString)
        # Default to zip if not title
        titleString = document['filename']
        if ('title' in document['documentMetadata']):
            titleString = document['documentMetadata']['title']
        print("\tTitle -", titleString)

        normDoc = {}
        normDoc['Title'] = titleString
        normDoc['Author'] = authorString
        normDoc['highlights'] = []

        prevHighlight = None

        # Sort the highlights before we do anything
        #pprint.pprint(sorted(document['rawHighlight'], key= lambda x: (x['page'], x['start'])))
        document['rawHighlight'] = sorted(document['rawHighlight'], key= lambda x: (x['page'], x['start']))

        for highlight in document['rawHighlight']:
            # print(highlight)
            hPage = highlight['page']
            hStart = highlight['start']
            hLength = highlight['length']
            hColor = highlight['color']
            hText = highlight['text']

            nHighlight = {}
            nHighlight['page'] = hPage
            nHighlight['start'] = hStart
            nHighlight['color'] = hColor
            nHighlight['length'] = hLength
            nHighlight['text'] = hText
            nHighlight['end'] = hStart+hLength
            nHighlight['rows'] = 1
            nHighlight['add'] = True

            #print(nHighlight)

            addHighlight = True
            if (prevHighlight != None):
                prevEnd = prevHighlight['start'] + prevHighlight['length']
                if (prevHighlight['page'] == hPage and prevHighlight['color'] == hColor
                            and (hStart-prevEnd) <= 3):
                        # Don't add this one separately, append to the current one in the list
                        addHighlight = False
                        nHighlight['add'] = False
                        normDoc['highlights'][-1]['text'] = ' '+hText
                        normDoc['highlights'][-1]['length'] += hLength
                        normDoc['highlights'][-1]['rows'] += 1

            #print(nHighlight)
            if (addHighlight):
                normDoc['highlights'].append(nHighlight)

            prevHighlight = highlight
        #print(normDoc)
        normalizedDocuments.append(normDoc)
    simpleHighlights = []
    # Now go through and build output
    for doc in normalizedDocuments:
        for highlight in doc['highlights']:
            simpleHighlight  = {}
            simpleHighlight['Author'] = doc['Author']
            simpleHighlight['Title'] = doc['Title']
            simpleHighlight['Highlight'] = highlight['text']
            simpleHighlight['Page'] = highlight['page']
            simpleHighlights.append(simpleHighlight)
    if args.output_type == "screen":
        print("Outputting to screen...")
        pprint.pprint(simpleHighlights)
    elif args.output_type == "csv":
        print("Outputting to CSV...")
        with open(args.output_file, "w", encoding="utf8", newline='') as f:
            wr = csv.DictWriter(f, delimiter=",",fieldnames=list(simpleHighlights[0].keys()))
            wr.writeheader()
            wr.writerows(simpleHighlights)


if __name__ == "__main__":
    main()