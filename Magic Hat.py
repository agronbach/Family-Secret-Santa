import smtplib
import logging
import secret
from datetime import datetime
import copy
import random

# Setup logfile in case program crashes
#logging.basicConfig(filename='Magic Hat Log File.log',level=logging.DEBUG)
logging.basicConfig(filename='Magic Hat Log File.log',level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler()) # output all messages to console too
currentYear = datetime.now().year

# Read in Gifters list of dicts "database"
import json
with open ('Gifternames.json', 'r') as f:
    Gifternames = json.load(f)
with open ('Gifteremails.json', 'r') as f:
    Gifteremails = json.load(f)
    
all_gifter_names = [gifter['Name'] for gifter in Gifternames]
gifterNameEmails = {item['Name']: item['Email'] for item in Gifteremails}

giftOut = {}

for gifter_dict in Gifternames:
    giver_name = gifter_dict['Name']
    restricted_names = set(gifter_dict.values())
    valid_giftees = [name for name in all_gifter_names if name not in restricted_names]
    giftOut[giver_name] = valid_giftees

    logging.info(f"{giver_name}: {len(valid_giftees)} possible recipients: "+str(valid_giftees))

#Sort giftOut by least number of possible valid giftees first
giftOut = dict(sorted(giftOut.items(), key=lambda x: len(x[1]), reverse = False))
logging.debug("Sorted giftOut to process most restricted gifters first: "+str(giftOut))

#Build this year's gift list (runs once at startup; the menu only emails it)
def giftList ():

    def backtrack(assignedGifters, giverReceivers):
        if not giverReceivers:
            logging.info("Found a valid list!")
            return assignedGifters
        
        #Sort giverReceivers by least number of possible valid giftees first
        giverReceivers = dict(sorted(giverReceivers.items(), key=lambda x: len(x[1]), reverse = False))
        logging.debug(">>>>>>>>>>>>>>>>>>Sorted giverReceivers to process most restricted gifters first: "+str(giverReceivers))

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
                logging.debug("Before removing "+ giver + " from tempGiverReceivers: "+str(tempGiverReceivers))
                # Remove the giver we just assigned a receiver, they do not need to be assigned another receiver
                tempGiverReceivers.pop(giver, None)
                logging.debug("After removing giver("+ giver + ") from tempGiverReceivers: "+str(tempGiverReceivers))

                # Remove the receiver from everyone's possibleReceivers, they do not need to receive a second gift
                for giverIter, possibleReceiversIter in tempGiverReceivers.items():
                    if receiver in possibleReceiversIter:
                        logging.debug("Before remove "+ receiver + " from " + giverIter + "'s possibleReceivers: "+str(possibleReceiversIter))
                        possibleReceiversIter.remove(receiver)
                        logging.debug("After removing rcver("+ receiver + ") from " + giverIter + "'s possibleReceivers:: "+str(possibleReceiversIter))
                        if len(possibleReceiversIter) < 1:
                            logging.debug("<<<<<<<<<<<<<<<<<<Invalid gift list, "+ giverIter +" has "+ str(len(possibleReceiversIter)) +", backtracking...")
                            return False
                
                # If this is a valid match, keep going
                logging.debug(giver+"->"+receiver+" is valid, calling backtrack with tempAssignedGifters:"+str(tempAssignedGifters)+", and tempGiverReceivers:"+str(tempGiverReceivers))
                tempResult = backtrack(copy.deepcopy(tempAssignedGifters), copy.deepcopy(tempGiverReceivers))
                if tempResult:
                    return tempResult
                # Backtrack if assignment didn't lead to a solution
                # Nothing to undo here as for receiver in possibleReceivers: loop will
                # now continue, and the next iteration will start by making new temporary
                # deepcopys of both assignedGifters and giverReceivers to try next choice with

        return False    

    assignedGifters = {}
    
    result = backtrack(assignedGifters, giftOut)
    if not result:
        logging.info("No valid gift list found! Please check the restrictions and try again.")
    return result

def emailNames(assignment_dict):
    try:
        outFile = open('./'+str(currentYear)+' Output.txt', 'w+')
    except Exception as ex:
        logging.critical("\nCRITICAL ERROR: FAILED TO OPEN OUTPUT FILE\n")
        logging.critical(ex, exc_info=True)
        input("Press Enter to exit...")
        raise SystemExit

    subject = "Secret Santa " + str(currentYear)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(secret.sent_from, secret.API_key)
    except Exception as ex:
        logging.critical("\nCRITICAL ERROR: FAILED TO LOGIN TO GMAIL, CHECK CREDENTIALS AND TRY AGAIN\n")
        logging.critical(ex, exc_info=True)
        input("Press Enter to exit...")
        outFile.close()
        raise SystemExit #If we can't send emails, exit!
    
    for gifter, giftee in assignment_dict.items():
        outFile.write(gifter + " --> " + giftee + "\n")
        sent_to = str(gifterNameEmails[gifter])
        body = "Hello " + gifter + ",\n\nThe magic hat has decided that you will be gifting to " + giftee + " this year!\n\nThis is an automated message, but please feel free to reply if you have any questions or need " + giftee + "'s address.\n\n-One of Santa's Helpers"
        message = "From: "+secret.sent_from+"\r\nTo: "+sent_to+"\r\nSubject: "+subject+"\r\n\r\n"+body
        try:    
            server.sendmail(secret.sent_from, sent_to, message)
            logging.debug('\nEmail subject ' + subject +' with body:\n' + body + '\n')
            logging.info('Sent to ' + gifter +' at '+sent_to+'!')
        except Exception as ex:
            logging.critical("\nCRITICAL ERROR: FAILED TO SEND "+gifter+"'s EMAIL TO: " + sent_to + "\n")
            logging.critical(ex, exc_info=True)
            input("Press Enter to exit...")
            server.quit()
            outFile.close()
            raise SystemExit #If we can't send emails, exit!
    logging.info("All emails successfully sent out!")
    try:
        server.quit()
    except Exception as ex:
        logging.critical("\nCRITICAL ERROR: UNABLE TO QUIT GMAIL SERVER CONNECTION\n")
        logging.critical(ex, exc_info=True)
        input("Press Enter to exit...")
        outFile.close()
        raise SystemExit
    try:
        outFile.close()
    except Exception as ex:
        logging.critical("\nCRITICAL ERROR: UNABLE TO CLOSE OUTFILE\n")
        logging.critical(ex, exc_info=True)
        input("Press Enter to exit...")
        raise SystemExit
    return
    
#View current gifters
def viewGifters ():
    print ("Here are the current Gifters:\n")
    for gifter in Gifternames:
        print (gifter['Name'])
    print ("There are " + str(len(Gifternames)) + " total gifters this year")
    return

# Build this year's list now so the menu only has to email it; exit hard if the game isn't playable
thisYearsList = giftList()
if not thisYearsList:
    logging.critical("\nCRITICAL ERROR: NO VALID GIFT LIST POSSIBLE - CHECK RESTRICTIONS\n")
    input("Press Enter to exit...")
    raise SystemExit

while (True):
    print ("\n\nWhat would you like to do?")
    print ("1: View current Gifters")
    print ("2: Email "+str(currentYear)+" gift list")
    print ("3: Exit\n")

    #Get user input, ask until valid input
    while (True):
        try:
            choice = int(input("Enter your selection: "))
            break
        except ValueError:
            print ("Please enter an integer selection\n")

    if (choice == 1):
        viewGifters()
    elif (choice == 2):
        emailNames(thisYearsList)
        break
    elif (choice == 3):
        break
    else:
        print ("That was not a valid selection, please try again")
print ("Thank you, shutting down")

    
    
