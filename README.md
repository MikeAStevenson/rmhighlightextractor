# rmhighlightextractor
 
rmhighlightextractor is a Python script that can be used to extract highlights from PDFs downloaded from the ReMarkable Cloud API. Tested with Python version 3.10.5.

App is tested using ZIP files downloaded from the API using rMAPI located here: https://github.com/juruen/rmapi. They have extensive documentation on how to setup rMAPI and examples of how to download files.

## Output Types

Currently there are two output types supported. CSV and screen (straight to the terminal). More may be added in the future.

### Screen (default)

Outputs highlights found to the screen using Python's pprint. Data is somewhat cleaned up, but this is just to present what is found (for now).


### CSV

Outputs highlights found to a destination csv file with Author(s), Title, Highlights, and the Page ID (will replace with page number down the road).

## Examples

### Screen output

The command by default will output to screen, example of command can be found below and sample of output. 

```
python .\rmhighlightextractor.py -rd "C:\temp\rmtmpdir\"
```

Will output something similar to this (top part cut off):

![image](https://user-images.githubusercontent.com/1132116/183554344-0d7717ed-2d81-4e0d-851a-370b758df82f.png)


### CSV output

Example of CSV command:

```
python .\rmhighlightextractor.py -rd "C:\temp\rmtmpdir\" -ot csv -o "C:\temp\rmhighlights.csv"
```

