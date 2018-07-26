# TODO: download a complete ANR (maybe multiple files needed?)
# TODO: test for Internet connection to the server
# TODO: update when language stuff is done

import requests
import json

CHOSEN_LANG = 'en'
LANGUAGE = { 
    'null': "",
    'fr': "1",
    'en': "2",
    'de': "3",
    'nl': "4",
}


class MonarcConnector:

    def __init__(self):
        self.loadLoginSettings()
        self.testLogin()

    def getInformation(self,url):
        head = {'token': self.user_token}
        information = requests.get((self.base_url+url), headers=head)
        return information.content.decode()

    def getUserRoles(self):
        # get user roles
        url = "api/users-roles"
        return self.getInformation(url)

    def getFullAnrList(self):
        # get the ANR list for the registered user
        url = "api/client-anr"
        return json.loads(self.getInformation(url))['anrs']

    def testLogin(self):
        try:
            # if file exists load the token
            with open("settingsFile.cfg","r") as tokenfile:
                fileContents = json.loads(tokenfile.read())
                self.user_token = fileContents['token']
                self.user_id = fileContents['uid']
                self.user_lang = fileContents['language']
                
        except FileNotFoundError as e:
            # if file does not exist then one has to login anyways!
            print (e.strerror)
            self.login()
        else:
            url = "api/users-roles"
            if self.getInformation(url) == "":
                # if the return is empty, the token is invalid so login again!
                self.login()

    def loadLoginSettings(self):
        # TODO: Test if file exists
        with open("loginInfo.cfg", 'r') as loginInfoFile:
            loginInfo = json.loads(loginInfoFile.read())
        
        self.loginData = {'login': loginInfo['username'], 
                    'password': loginInfo['password']}
        self.base_url = loginInfo['url']

    def login(self):
        # TODO: what happens if user/pwd combination is wrong
        
        respLogin = json.loads(requests.post(self.base_url+"auth",data=self.loginData).content.decode())
        self.user_token = respLogin['token']
        with open("settingsFile.cfg", 'w') as settingsFile:
            settingsFile.write(json.dumps(respLogin))
            settingsFile.flush()

    def loadAllInfoRisks(self,anrNumber):
        url = "api/client-anr/"+str(anrNumber)+"/risks?limit=-1"
        return self.getInformation(url)
    
    def loadAllOpRisks(self,anrNumber):
        url = "api/client-anr/"+str(anrNumber)+"/risksop"
        return self.getInformation(url)

    def loadScales(self,anrNumber):
        url = "api/client-anr/"+str(anrNumber)+"/scales"
        return self.getInformation(url)

    def loadScalesDescription(self,anrNumber,scaleID):
        url = "api/client-anr/"+str(anrNumber)+"/scales/"+str(scaleID)+"/comments"
        return self.getInformation(url)

    def loadScalesNames(self, anrNumber):
        url = "api/client-anr/"+str(anrNumber)+"/scales-types"
        return self.getInformation(url)

    def getEvaluationTable(self,anrNumber):
        theScales = json.loads(self.loadScales(analysis['id']))
        scaleNames = json.loads(self.loadScalesNames(analysis['id']))
        scaleNamesExtracted = {}
        for sn in scaleNames["types"]:
            if sn['label1'] == None:
                continue
            scaleNamesExtracted[sn['id']] = sn['label'+str(LANGUAGE[CHOSEN_LANG])]


        evalTable = {
            "headers": scaleNamesExtracted,

        }

        for s in theScales['scales']:

            theDetails = json.loads(self.loadScalesDescription(analysis['id'],s['id']))

            for c in theDetails['comments']:
                if c['scaleImpactType'] != None:
                    entry = {"val":c['val'], "description":c['comment'+str(LANGUAGE[CHOSEN_LANG])]}
                    if c['scaleImpactType']['id'] not in evalTable:
                        evalTable[c['scaleImpactType']['id']] = []
                    evalTable[c['scaleImpactType']['id']].append(entry)
                    
                    #print (" +", scaleNamesExtracted[c['scaleImpactType']['id']], c['val'], c['comment1'])
                    pass
        return evalTable



class MonarcConnectorExtended(MonarcConnector):

    def getEvaluationTable(self,anrNumber):
        theScales = json.loads(self.loadScales(analysis['id']))
        scaleNames = json.loads(self.loadScalesNames(analysis['id']))
        scaleNamesExtracted = {}
        for sn in scaleNames["types"]:
            if sn['label1'] == None:
                continue
            scaleNamesExtracted[sn['id']] = sn['label'+str(LANGUAGE[CHOSEN_LANG])]


        evalTable = {
            "headers": scaleNamesExtracted,

        }

        for s in theScales['scales']:

            theDetails = json.loads(self.loadScalesDescription(analysis['id'],s['id']))

            for c in theDetails['comments']:
                if c['scaleImpactType'] != None:
                    entry = {"val":c['val'], "description":c['comment'+str(LANGUAGE[CHOSEN_LANG])]}
                    if c['scaleImpactType']['id'] not in evalTable:
                        evalTable[c['scaleImpactType']['id']] = []
                    evalTable[c['scaleImpactType']['id']].append(entry)
                    
                    #print (" +", scaleNamesExtracted[c['scaleImpactType']['id']], c['val'], c['comment1'])
                    pass
        return evalTable





if __name__ == "__main__":
    monarcConn = MonarcConnectorExtended()

    anrList = monarcConn.getFullAnrList()

    for analysis in anrList:
        #print (analysis['id'], analysis['label1'], analysis['description1'], "created by", analysis['creator'])

        allRisks = json.loads(monarcConn.loadAllInfoRisks(analysis['id']))

        i=0
        '''
        for risk in allRisks['risks']:
            i+=1
            #print (risk['id'], json.dumps(risk, indent=4))
            comment = risk['comment']
            if comment != None:
                comment = comment.replace("\n","/")
            else:
                comment = ""
            print (str(i)+".", risk['asset'], risk['threatCode'], risk['vulnCode'], comment)
        '''
        
        '''
        theScales = json.loads(monarcConn.loadScales(analysis['id']))
        #print(json.dumps(theScales,indent=4))
        

        scaleNames = json.loads(monarcConn.loadScalesNames(analysis['id']))
        #print (json.dumps(scaleNames, indent=4))
        scaleNamesExtracted = {}
        for sn in scaleNames["types"]:
            scaleNamesExtracted[sn['id']] = sn['label1']

        #print (json.dumps(final, indent=4))
        #print (json.dumps(theScales, indent=4))
        for s in theScales['scales']:
            #print (s['type'], s['min'],"to",s['max'])
            #print (json.dumps(s,indent=4))
            theDetails = json.loads(monarcConn.loadScalesDescription(analysis['id'],s['id']))
            #print (json.dumps(theDetails,indent=4))
            #index = 1
            
            #print (json.dumps(theDetails['comments'],indent=4))

            for c in theDetails['comments']:
                if c['scaleImpactType'] != None:
                    print (" +", scaleNamesExtracted[c['scaleImpactType']['id']], c['val'], c['comment1'])
                #print (json.dumps(c,indent=4))
                #print("  +", c['val'], c['comment1'])
                #index = index % len(final)+1
                #print()
                # print (json.dumps(c))
                pass
        '''

        theTable = monarcConn.getEvaluationTable(analysis['id'])

        # print (json.dumps(theTable,indent=4))

        for h in theTable['headers']:
            print()
            print (theTable['headers'][h])
            if h != "headers":
                for l in theTable[h]:
                    print ("   ",l['val'],l['description'])
                

        '''
        if analysis['id'] == 481:
            xx = json.dumps(analysis, indent=4)
            print (xx)
        '''