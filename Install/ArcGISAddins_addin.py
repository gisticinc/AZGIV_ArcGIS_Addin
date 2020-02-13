import arcpy
import pythonaddins
import json
import requests
import string
import random
from zipfile import ZipFile
import os
"""import urllib3"""
"""urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)"""
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def checkCustomer(customerId, username, password):
    print "in check customer"
    print customerId
    url = "https://72.215.195.71:4203/azgiv/userInfo"
    params = {"username": username, "password": password}
    print username
    print password
    r = requests.get(url = url, params = params, verify = False)
    content = r.content
    print content
    statusCode = r.status_code
    print statusCode
    if statusCode == 200:
        content = json.loads(r.content)
        customerIdsLocal = content["customerIds"]
        if customerIdSelected not in customerIdsLocal:
            raise Exception("The agency is not your client. Please click the login button and pick your agency.")
    elif statusCode == 500:
        raise Exception(content)
    else:
        raise Exception("Unknown error")

def checkLayer(customerId, layer):
    for lyr in arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT")):
        if lyr.name == layer:
            fields = arcpy.ListFields(lyr.dataSource)
            sourceNameList = lyr.dataSource.split("\\")
            sourceLayerName = sourceNameList[len(sourceNameList)-1]
            layerName = None
            try:
                index = sourceLayerName.rindex(".")
                layerName = sourceLayerName[0:index]
            except Exception as e:
                print str(e)
                layerName = sourceLayerName
            schema = {}
            for field in fields:
                schema[field.name] = field.type
            url = "https://72.215.195.71:4203/azgiv/layerStatus"
            params = {"customerId": customerId, "schema": json.dumps(schema), "layer": layerName}
            r = requests.get(url = url, params = params, verify = False)
            content = r.content
            statusCode = r.status_code
            if statusCode == 200:
                newContent = json.loads(content)
                newContent["dataSource"] = lyr.dataSource
                newContent["sourceLayerName"] = sourceLayerName
                return newContent
            elif statusCode == 500:
                raise Exception(content)
            else:
                raise Exception("Unknown error")

def cleanUserInfo():
    global userId
    global userSubscriptionId
    global customerIds
    global customerNames
    global customerIdSelected
    try:
        userId
        del userId
    except NameError:
        print "undefined"
    try:
        userSubscriptionId
        del userSubscriptionId
    except NameError:
        print "undefined"
    try:
        customerIds
        del customerIds
    except NameError:
        print "undefined"
    try:
        customerNames
        del customerNames
    except NameError:
        print "undefined"
    try:
        customerIdSelected
        del customerIdSelected
    except NameError:
        print "undefined"
    global userId
    global userSubscriptionId
    global customerIds
    global customerNames
    global customerIdSelected
    

def login():
    global username
    global password
    global userId
    global userSubscriptionId
    global customerIds
    global customerNames
    global customerIdSelected
    try:
        username
        password
    except NameError:
        raise Exception("Please fill username and password.")

    url = "https://72.215.195.71:4203/azgiv/userInfo"
    params = {"username": username, "password": password}
    r = requests.get(url = url, params = params, verify = False)
    content = r.content
    statusCode = r.status_code
    if statusCode == 200:
        content = json.loads(r.content)
        userId = content["userId"]
        userSubscriptionId = content["userSubscriptionId"]
        customerIds = content["customerIds"]
        customerNames = content["customerNames"]
        if not content["isIntegrator"]:
            customerIdSelected = customerIds[0]
    elif statusCode == 500:
        raise Exception(content)
    else:
        raise Exception("Unknown error.")
    


class Login(object):
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        login()


class Customer(object):
    """Implementation for customer.combobox (ComboBox)"""
    def __init__(self):
        self.items = []
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWW'
        self.width = 'WWWWWWWWWWW'
        
    def onSelChange(self, selection):
        global customerName
        global customerIds
        global customerNames
        global customerIdSelected
        customerName = selection
        for i in range(len(customerIds)):
            if customerNames[i] == selection:
                customerIdSelected = customerIds[i]
    def onEditChange(self, text):
        global customerName
        print text
        try:
            customerIdSelected
            del customerIdSelected
        except:
            print "undefined"
        global customerIdSelected
        customerName = text
        for i in range(len(customerIds)):
            if customerNames[i] == text:
                customerIdSelected = customerIds[i]
    def onFocus(self, focused):
        global customerNames
        global customerIds
        self.items = customerNames
    def onEnter(self):
        pass
    def refresh(self):
        pass
    
class Upload(object):
    """Implementation for init.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def randomString(stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(16))
    def onClick(self):
        try:
            login()
            global layer
            global username
            global password
            global customerIdSelected
            global userId
            global userSubscriptionId
            try:
                username
                password
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                layer
            except NameError:
                raise Exception("Please pick a layer.")
            try:
                customerIdSelected
            except NameError:
                try:
                    customerName
                except NameError:
                    raise Exception("Data owner agency not defined.  Please pick a client agency from the dropdown list and upload again")
                if customerName == "":
                    raise Exception("Data owner agency not defined.  Please pick a client agency from the dropdown list and upload again")
                raise Exception("Data owner agency entered is not your client or does not exist. Please pick a client agency from the dropwdown list and upload again" )

            # Create schema of selected layer
            checkCustomer(customerIdSelected, username, password)
            content = checkLayer(customerIdSelected, layer)
            processId = self.randomString()
            # Write file to local machine
            arcpy.CreateFileGDB_management("C:\Users\Gistic\Downloads\AZGIVDownload", processId + ".gdb")
            outputPath = "C:\Users\Gistic\Downloads\AZGIVDownload\\" + processId + ".gdb"
            print outputPath
            arcpy.FeatureClassToGeodatabase_conversion([content["dataSource"]], outputPath)
            zipPath = "C:\Users\Gistic\Downloads\AZGIVDownload\\" + processId + ".zip"
            with ZipFile(zipPath, "w") as zipObj:
                # Iterate over all the files in directory
                for folderName, subfolders, filenames in os.walk(outputPath):
                    for filename in filenames:
                        #create complete filepath of file in directory
                        filePath = os.path.join(folderName, filename)
                        # Add file to zip
                        zipObj.write(filePath)
            # Construct specification
                        
            contentDict = content["spec"]
            contentDict["files"][0]["layers"][0]["name"] = content["sourceLayerName"]
            spec = json.dumps(contentDict)
            url2 = "https://72.215.195.71:4203/azgiv/fileArcgis"
            payload = {"userId": userId, "userSubscriptionId": userSubscriptionId, "spec": spec, "email": username}
            zipFileName = processId + ".zip"
            zipFile = open(zipPath, 'rb')
            files = {"uploads": zipFile}
            try:
                r2 = requests.post(url = url2, data = payload, files=files, verify=False)
                if r2.status_code == 200:
                    pythonaddins.MessageBox("Upload is in progress. An email notification will be sent upon completion.", "INFO", 0)
                elif r2.status_code == 500:
                    raise(r2.content)
                else:
                    raise("Unknown error.")
            except Exception as e:
                raise e
            finally:
                zipFile.close()
        except Exception as e:
            print e
            pythonaddins.MessageBox(str(e), "ERROR", 0)
            raise


class Download(object):
    """Implementation for init.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        try:
            login()
            global layer
            global username
            global password
            global customerIdSelected
            global userId
            global userSubscriptionId
            try:
                username
                password
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                layer
            except NameError:
                raise Exception("Please pick a layer.")
            try:
                customerIdSelected
            except NameError:
                try:
                    customerName
                except NameError:
                    raise Exception("Data owner agency not defined.  Please pick a client agency from the dropdown list and upload again")
                if customerName == "":
                    raise Exception("Data owner agency not defined.  Please pick a client agency from the dropdown list and upload again")
                raise Exception("Data owner agency entered is not your client or does not exist. Please pick a client agency from the dropwdown list and upload again" )

            # Create schema of selected layer
        
            checkCustomer(customerIdSelected, username, password)
            content = checkLayer(customerIdSelected, layer)
            layerId = content["layerId"]
            customerId = content["customerId"]

                        
            url2 = "https://72.215.195.71:4203/azgiv/qcFeatureReportQuery"
            params2 = {"idOnly": "true", "glyId": layerId}
            r2 = requests.get(url = url2, params = params2, verify = False)
            if r2.status_code == 200:
                content2 = json.loads(r2.content)
                query = content2["payload"]["content"]["sql"]
                url3 = "https://72.215.195.71:4203/azgiv/azgivDownloadArcgis"
                params3 = {"query": query}
                r3 = requests.get(url = url3, params = params3, verify = False)
                if r3.status_code == 200:
                    content3 = r3.content
                    # pythonaddins.MessageBox("Please get your file at " + content3, "INFO", 0)
                    url4 = content3
                    print url4
                    r4 = requests.get(url4, verify=False)
                    if r4.status_code == 200:
                        fileNameList = content3.split("/")
                        fileName = fileNameList[len(fileNameList)-1]
                        with open("C:\Users\Gistic\Downloads\AZGIVDownload\\" + fileName, "w+") as f:
                            f.write(r4.content)
                        arcpy.AddJoin_management(layer, "NGUID", "C:\Users\Gistic\Downloads\AZGIVDownload\\" + fileName,"nguid")
                        pythonaddins.MessageBox("Please check your file at azgivdownload", "INFO", 0)
                    else:
                        pythonaddins.MessageBox("Please get your file at " + content3, "INFO", 0)
                elif r3.status_code == 500:
                    raise Exception(r3.content)
                else:
                    raise Exception("Unknown error.")
            elif r2.status_code == 500:
                raise Exception(r2.content)
            else:
                raise Exception("Unknown error.")
        except Exception as e:
            pythonaddins.MessageBox(str(e), "ERROR", 0)
            raise

class Qc(object):
    """Implementation for init.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        try:
            login()
            global layer
            global username
            global password
            global customerIdSelected
            global userId
            global userSubscriptionId
            global customerName
            try:
                username
                password
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                layer
            except NameError:
                raise Exception("Please pick a layer.")
            try:
                customerIdSelected
            except NameError:
                try:
                    customerName
                except NameError:
                    raise Exception("Data owner agency not defined.  Please pick a client agency from the dropdown list and upload again")
                if customerName == "":
                    raise Exception("Data owner agency not defined.  Please pick a client agency from the dropdown list and upload again")
                raise Exception("Data owner agency entered is not your client or does not exist. Please pick a client agency from the dropwdown list and upload again" )

            # Create schema of selected layer
        
            checkCustomer(customerIdSelected, username, password)
            content = checkLayer(customerIdSelected, layer)
            layerId = content["layerId"]
            customerId = content["customerId"]                        
            url2 = "https://72.215.195.71:4203/azgiv/qcLayersArcgis"
            payload = {"userId": userId, "userSubscriptionId": userSubscriptionId, "layerId": layerId, "customerId": customerId, "email": username}
            r2 = requests.post(url = url2, data = payload, verify = False)
            if r2.status_code == 200:
                pythonaddins.MessageBox("Your layer is being qced. Please wait for email", "INFO", 0)
            elif statusCode == 500:
                raise Exception(r2.content)
            else:
                raise Exception("Unknown error.")
        except Exception as e:
            pythonaddins.MessageBox(str(e), "ERROR", 0)
            raise
            

class Layer(object):
    """Implementation for upload.combobox (ComboBox)"""
    def __init__(self):
        items = []
        for lyr in arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT")):
            items.append(lyr.name)
        self.items = items
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWW'
        self.width = 'WWWWWWWWWWW'
    def onSelChange(self, selection):
        global layer
        layer = selection
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        items = []
        for lyr in arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT")):
            items.append(lyr.name)
        self.items = items
    def onEnter(self):
        pass
    def refresh(self):
        pass

class Username(object):
    """Implementation for upload.combobox (ComboBox)"""
    def __init__(self):
        items = []
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWW'
        self.width = 'WWWWWWWWWWW'
    def onSelChange(self, selection):
        pass
    def onEditChange(self, text):
        cleanUserInfo()
        global username
        username = text
    def onFocus(self, focused):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass

class Password(object):
    """Implementation for upload.combobox (ComboBox)"""
    def __init__(self):
        items = []
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWW'
        self.width = 'WWWWWWWWWWW'
        self.saved = ''
    def onSelChange(self, selection):
        pass
    def onEditChange(self, text):
        cleanUserInfo()
        global password
        password = text
        self.value = "******"
    def onFocus(self, focused): 
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass

class Sync(object):
    """Implementation for sync.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.MessageBox("The sync feature is under construction.", "INFO", 0)

class Zoom(object):
    """Implementation for zoom.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            global layer
            global username
            global password
            try:
                username
                password
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                layer
            except NameError:
                raise Exception("Please pick a layer.")

            mxd = arcpy.mapping.MapDocument('current')
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            url = "https://72.215.195.71:4203/azgiv/extent"
            params = {'email': username, 'projection': df.spatialReference.factoryCode}
            r = requests.get(url = url, params = params, verify = False)
            data = r.json()
            print data
            xmin = data['xmin']
            ymin = data['ymin']
            xmax = data['xmax']
            ymax = data['ymax']
            ext = arcpy.Extent(xmin,ymin,xmax,ymax)
            df.extent = ext
        except Exception as e:
            pythonaddins.MessageBox(str(e), "ERROR", 0)     

