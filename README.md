# Argument Parser #
Input <= sys.argv
	>>> for _ in argv
Output => arg, kwarg

# Command Format #
## jPython
	jpython		Customize Python intepreter

## DartBoard ##
	* Dart		Active send network packet into target
		- *PORT*	Assign scan port
		- TCP/UDP	Assign protocol
	* Board		Positive receive the network packet responsed from target
		- *.filter

## Web scanner ##
	* cms		CMS detector
	* form		Get *FORM* parameter
	* geo		Geographical getter
	* info		Basic web information getter
		- domain	Domain name
		- fav		favicon.ico
		- index		Scan type of index page
		- js		JS library
		- robots	Robots.txt getter
	* url		Sensitive URL scanner

## Global parameter ##
	* -d, --depth	(int)	Recursive Run with result
	* -D, --debug	(int)	Enable debug message
	* -f, --file	(file)	Parameter file included
	* -o, --outfile	(file)	tee to file
	* -j, --jobs	(int)	Run with multi-processer
	* -q, --quite			No stdout message
	* -v, -vv, -vvv			Verbous mode: [pretty, verbose, detail, raw data]

