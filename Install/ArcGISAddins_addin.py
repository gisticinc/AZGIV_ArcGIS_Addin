import arcpy
import pythonaddins
import json
import requests
import string
import random
from zipfile import ZipFile
import os
import distutils.dir_util
"""import urllib3"""
"""urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)"""
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import os

if os.name == 'nt':
    import ctypes
    from ctypes import windll, wintypes
    from uuid import UUID

    # ctypes GUID copied from MSDN sample code
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8)
        ] 

        def __init__(self, uuidstr):
            uuid = UUID(uuidstr)
            ctypes.Structure.__init__(self)
            self.Data1, self.Data2, self.Data3, \
                self.Data4[0], self.Data4[1], rest = uuid.fields
            for i in range(2, 8):
                self.Data4[i] = rest>>(8-i-1)*8 & 0xff

    SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID), wintypes.DWORD,
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
    ]

    def _get_known_folder_path(uuidstr):
        pathptr = ctypes.c_wchar_p()
        guid = GUID(uuidstr)
        if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
            raise ctypes.WinError()
        return pathptr.value

    FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'

    def get_download_folder():
        azgivPath = _get_known_folder_path(FOLDERID_Download) + "\AZGIVDownload"
        print "making dir"
        distutils.dir_util.mkpath(azgivPath)
        return azgivPath
else:
    def get_download_folder():
        home = os.path.expanduser("~")
        azgivPath = os.path.join(home, "Downloads\AZGIVDownload")
        print "making dir"
        distutils.dir_util.mkpath(azgivPath)
        return azgivPath

def checkVariable(var):
    try:
        var
    except NameError:
        raise
    if var is None:
        raise NameError

def checkCustomer(customerId, username, password):
    print "in check customer"
    print customerId
    url = "https://api.linearbench.com/azgiv/userInfo"
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
            url = "https://api.linearbench.com/azgiv/layerStatus"
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
    userId = None
    userSubscriptionId = None
    customerIds = None
    customerNames = None
    customerIdSelected = None

def login():
    global username
    global password
    global userId
    global userSubscriptionId
    global customerIds
    global customerNames
    global customerIdSelected
    try:
        checkVariable(username)
        checkVariable(password)
    except NameError:
        raise Exception("Please fill username and password.")

    url = "https://api.linearbench.com/azgiv/userInfo"
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
        global customerIdSelected
        print text
        customerIdSelected = None
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
                checkVariable(username)
                checkVariable(password)
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                checkVariable(layer)
            except NameError:
                raise Exception("Please pick a layer.")
            try:
                checkVariable(customerIdSelected)
            except NameError:
                try:
                    checkVariable(customerName)
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
            arcpy.CreateFileGDB_management(get_download_folder(), processId + ".gdb")
            outputPath = get_download_folder() + "\\" + processId + ".gdb"
            print outputPath
            arcpy.FeatureClassToGeodatabase_conversion([content["dataSource"]], outputPath)
            zipPath = get_download_folder() + "\\" + processId + ".zip"
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
            url2 = "https://api.linearbench.com/azgiv/fileArcgis"
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
                checkVariable(username)
                checkVariable(password)
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                checkVariable(layer)
            except NameError:
                raise Exception("Please pick a layer.")
            try:
                checkVariable(customerIdSelected)
            except NameError:
                try:
                    checkVariable(customerName)
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

                        
            url2 = "https://api.linearbench.com/azgiv/qcFeatureReportQuery"
            params2 = {"idOnly": "true", "glyId": layerId}
            r2 = requests.get(url = url2, params = params2, verify = False)
            if r2.status_code == 200:
                content2 = json.loads(r2.content)
                query = content2["payload"]["content"]["sql"]
                url3 = "https://api.linearbench.com/azgiv/azgivDownloadArcgis"
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
                        with open(get_download_folder() + "\\" + fileName, "w+") as f:
                            f.write(r4.content)
                        try:
                            url5 = "https://api.linearbench.com/azgiv/nguidStatusArcgis"
                            params5 = {"layerId": layerId}
                            r5 = requests.get(url = url5, params = params5, verify = False)
                            if r5.status_code == 200:
                                arcpy.AddJoin_management(layer, "NGUID", get_download_folder() + "\\" + fileName,"nguid")
                                pythonaddins.MessageBox("Please check your file at azgivdownload. The file is also joined to your layer.", "INFO", 0)
                            else:
                                raise Exception()
                        except:
                            pythonaddins.MessageBox("Please check your file at azgivdownload.", "INFO", 0)
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
                checkVariable(username)
                checkVariable(password)
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                checkVariable(layer)
            except NameError:
                raise Exception("Please pick a layer.")
            try:
                checkVariable(customerIdSelected)
            except NameError:
                try:
                    checkVariable(customerName)
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
            url2 = "https://api.linearbench.com/azgiv/qcLayersArcgis"
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
                checkVariable(username)
                checkVariable(password)
            except NameError:
                raise Exception("Please fill username and password.")
            try:
                checkVariable(layer)
            except NameError:
                raise Exception("Please pick a layer.")

            mxd = arcpy.mapping.MapDocument('current')
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            url = "https://api.linearbench.com/azgiv/extent"
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

