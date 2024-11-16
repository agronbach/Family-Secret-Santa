import smtplib
import logging
import secret
from datetime import datetime
import copy
import random
#from collections import Counter
from itertools import islice

# Setup logfile in case program crashes
#logging.basicConfig(filename='Magic Hat Log File.log',level=logging.DEBUG)
logging.basicConfig(filename='Magic Hat Log File.log',level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler()) # output all messages to console too
currentYear = datetime.now().year

# Read in Gifters list of dicts "database"
import json
#with open ('GifternamesTest.json', 'r') as f:
with open ('Gifternames.json', 'r') as f:
    Gifters = json.load(f)

gifterNames = [name['Name'] for name in Gifters]
gifterEmails = [name['Email'] for name in Gifters]
gifterNameEmails = {}
for gifterName in gifterNames:
    for gifterEmail in gifterEmails:
        gifterNameEmails[gifterName] = gifterEmail
        gifterEmails.remove(gifterEmail)
        break

giftOut = {}

for i in range(0, len(gifterNames)):
    # Ensure that no one is able to match with themselves or anyone on their restricted names list
    valid_giftees = [name for name in gifterNames if name not in Gifters[i].values()]
    giftOut[gifterNames[i]] = valid_giftees

    logging.info(f"{gifterNames[i]}: {len(valid_giftees)} possibile recipients: "+str(valid_giftees))

    #Sort giftOut by least number of possible valid giftees first
    giftOut = dict(sorted(giftOut.items(), key=lambda x: len(x[1]), reverse = False))
    logging.debug("Sorted giftOut to process least restricted gifters first: "+str(giftOut))

#Create new gifting list
def giftList ():

    def backtrack(assignedGifters, giverReceivers):
        if not giverReceivers:
            logging.info("Found a valid list! Attempting to send emails...")
            logging.debug("Found a valid list! Attempting to send emails for: "+str(assignedGifters))
            emailNames(assignedGifters.keys(), assignedGifters.values())
            return True # Found a valid gift list!
        
        #Sort giverReceivers by least number of possible valid giftees first
        giverReceivers = dict(sorted(giverReceivers.items(), key=lambda x: len(x[1])))
        logging.debug(">>>>>>>>>>>>>>>>>>Sorted giverReceivers to process most restricted gifters first: "+str(giverReceivers))

        # Check if multiple gifters share same fewer possibleReceivers, impossible to find valid gift list
        if len(giverReceivers.keys()) > 1: # Ensure we have multiple gifters left!
            firstGifter = list(giverReceivers.keys())[0]
            impossible = True
            for i in islice(giverReceivers.keys(), len(giverReceivers[firstGifter])+1):
                if sorted(giverReceivers[firstGifter]) != sorted(giverReceivers[i]):
                    impossible = False

            if impossible:
                logging.debug("<<<<<<<<<<<<<<<<<<Encountered too many gifters with the same possibleReceivers, backtracking...")
                return False

        logging.debug(">>>>>>>>>>>>>>>>>>Starting assignment loop with giverReceivers as: "+str(giverReceivers)+", and assignedGifters as: "+str(assignedGifters))
        for giver, possibleReceivers in giverReceivers.items():
            logging.debug(">>>>>>>>>Checking giver("+str(giver)+"), with giverReceivers as: "+str(giverReceivers)+", and assignedGifters as: "+str(assignedGifters))

            # Randomly shuffle possibleReceivers
            logging.debug("Before shuffle:"+str(possibleReceivers))
            random.shuffle(possibleReceivers)
            logging.debug("After shuffle:"+str(possibleReceivers))
            for receiver in possibleReceivers:
                logging.debug("Should "+str(giver)+" gift to "+str(receiver)+"?")
                
                tempAssignedGifters = copy.deepcopy(assignedGifters)
                tempGiverReceivers = copy.deepcopy(giverReceivers)
                # Try assigning each gifter a giftee
                tempAssignedGifters[giver] = receiver
                logging.debug("Added " + giver + " : " + receiver + " to tempAssignedGifters: "+str(tempAssignedGifters))
                #logging.debug("Before removing "+ giver + " from tempGiverReceivers: "+str(tempGiverReceivers))
                # Remove the giver we just assigned a receiver, they do not need to be assigned another receiver
                tempGiverReceivers.pop(giver, None)
                logging.debug("After removing giver("+ giver + ") from tempGiverReceivers: "+str(tempGiverReceivers))

                # Remove the receiver from everyone's possibleReceivers, they do not need to receive a second gift
                for giverIter, possibleReceiversIter in tempGiverReceivers.items():
                    for i in possibleReceiversIter:
                        if i == receiver:
                            #logging.debug("Before remove "+ receiver + " from " + giverIter + "'s possibleReceivers: "+str(possibleReceiversIter))
                            possibleReceiversIter.remove(receiver)
                            logging.debug("After removing rcver("+ receiver + ") from " + giverIter + "'s possibleReceivers:: "+str(possibleReceiversIter))
                            if len(possibleReceiversIter) < 1:
                                logging.debug("<<<<<<<<<<<<<<<<<<Invalid gift list, "+ giverIter +" has "+ str(len(possibleReceiversIter)) +", backtracking...")
                                return False
                
                # If this is a valid match, keep going
                logging.debug(giver+"->"+receiver+" is valid, calling backtrack with tempAssignedGifters:"+str(tempAssignedGifters)+", and tempGiverReceivers:"+str(tempGiverReceivers))
                if backtrack(copy.deepcopy(tempAssignedGifters), copy.deepcopy(tempGiverReceivers)):
                    return True
                # Backtrack if assignment didn't lead to a solution
                # Nothing to undo here as for receiver in possibleReceivers: loop will
                # now continue, and the next iteration will start by making new temporary
                # deepcopys of both assignedGifters and giverReceivers to try next choice with

        return False    

    assignedGifters = {}
    
    if backtrack(assignedGifters, giftOut):
        # Attempt to send emails using valid assignedGifters pairs
        logging.info("Found a valid list, emails successfully sent!")
        return True
    else:
        logging.info("No valid gift list found! Please check the restrictions and try again.")
        return False
    return

def emailNames(gifterNames, gifteeNames):

    try:
        outFile = open('./'+str(currentYear)+' Output.txt', 'w+')
    except Exception as ex:
        logging.critical('Failed to open Output file, exiting...')
        logging.critical(ex, exc_info=True)
        exit

    subject = "Secret Santa " + str(currentYear)

    for i, (gifter, giftee) in enumerate(zip(gifterNames, gifteeNames)):
        outFile.write(gifter + " --> " + giftee + "\n")
        sent_to = str(gifterNameEmails[gifter])
        body = "Hello " + gifter + ",\n\nThe magic hat has decided that you will be gifting to " + giftee + " this year!\n\nThis is an automated message, but please feel free to reply if you have any questions or need " + giftee + "'s address.\n\n-One of Santa's Helpers"

        message = "From: "+secret.sent_from+"\r\nTo: "+sent_to+"\r\nSubject: "+subject+"\r\n\r\n"+body
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.set_debuglevel(1)
            server.starttls()
            server.login(secret.sent_from, secret.API_key)
            server.sendmail(secret.sent_from, sent_to, message)
            server.close()
            logging.debug('\nEmail subject ' + subject +' with body:\n' + body + '\n')
            logging.info('Sent to ' + gifter +' at '+sent_to+'!')
        except Exception as ex:
            logging.critical("Failed to send "+gifter+"'s email to: " + sent_to)
            logging.critical(ex, exc_info=True)
    logging.info("All emails successfully sent out!")
    outFile.close()
    return
    
#View current gifters
def viewGifters ():
    print ("Here are the current Gifters:\n")
    for gifter in Gifters:
        print (gifter['Name'])
    print ("There are " + str(len(Gifters)) + " total gifters this year")
    return

while (True):
    print ("\n\nWhat would you like to do?")
    print ("1: Create new "+str(currentYear)+" gift list")
    print ("2: View current Gifters")
    print ("3: Exit\n")

    #Get user input, ask until valid input
    while (True):
        try:
            choice = int(input("Enter your selection: "))
            break
        except ValueError:
            print ("Please enter an integer selection\n")

    if (choice == 1):
        giftList()
        break
    elif (choice == 2):
        viewGifters()
    elif (choice == 3):
        break
    else:
        print ("That was not a valid selection, please try again")
print ("Thank you, shutting down")

    
    
