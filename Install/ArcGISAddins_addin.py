import arcpy
import pythonaddins
import json
import requests
import string
import random
from zipfile import ZipFile
import os

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
        global layer
        global username
        global password
        try:
            username
            password
            layer
        except NameError:
            pythonaddins.MessageBox("Please fill all boxes.", 'INFO', 0)

        # Create schema of selected layer
        try:
            for lyr in arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT")):
                if lyr.name == layer:
                    fields = arcpy.ListFields(lyr.dataSource)
                    sourceNameList = lyr.dataSource.split("\\")
                    sourceLayerName = sourceNameList[len(sourceNameList)-1]
                    schema = {}
                    for field in fields:
                        schema[field.name] = field.type
                    url = "https://72.215.195.71:4203/azgiv/layerStatus"
                    params = {"username": username, "password": password, "schema": json.dumps(schema), "layer": sourceLayerName}
                    r = requests.get(url = url, params = params, verify = False)
                    content = r.content
                    statusCode = r.status_code
                    if statusCode == 200:
                        content = json.loads(r.content)
                        processId = self.randomString()
                        # Write file to local machine
                        arcpy.CreateFileGDB_management("C:\Users\Gistic\Downloads\AZGIVDownload", processId + ".gdb")
                        outputPath = "C:\Users\Gistic\Downloads\AZGIVDownload\\" + processId + ".gdb"
                        print outputPath
                        arcpy.FeatureClassToGeodatabase_conversion([lyr.dataSource], outputPath)
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
                        userId = content["userId"]
                        userSubscriptionId = content["userSubscriptionId"]
                        contentDict = content["spec"]
                        contentDict["files"][0]["layers"][0]["name"] = sourceLayerName
                        spec = json.dumps(contentDict)

                        
                        url2 = "https://72.215.195.71:4203/azgiv/fileArcgis"
                        payload = {"userId": userId, "userSubscriptionId": userSubscriptionId, "spec": spec, "email": username}
                        zipFileName = processId + ".zip"
                        zipFile = open(zipPath, 'rb')
                        files = {"uploads": zipFile}
                        try:
                            r2 = requests.post(url = url2, data = payload, files=files)
                            if r2.status_code == 200:
                                pythonaddins.MessageBox("Your upload is initiated. Please wait for email.", "INFO", 0)
                            elif r2.status_code == 500:
                                pythonaddins.MessageBox(r2.content, "ERROR", 0)
                            else:
                                pythonaddins.MessageBox("Unknown error.", "ERROR", 0)
                        finally:
                            zipFile.close()
                    elif statusCode == 500:
                        pythonaddins.MessageBox(content, "ERROR", 0)
                    else:
                        pythonaddins.MessageBox("Unknown error.", "ERROR", 0)
        except Exception as e:
            pythonaddins.MessageBox(str(e), "ERROR", 0)
            raise


class Download(object):
    """Implementation for init.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        global layer
        global username
        global password
        try:
            username
            password
            layer
        except NameError:
            pythonaddins.MessageBox("Please fill all boxes.", 'INFO', 0)

        # Create schema of selected layer
        try:
            for lyr in arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT")):
                if lyr.name == layer:
                    fields = arcpy.ListFields(lyr.dataSource)
                    sourceNameList = lyr.dataSource.split("\\")
                    sourceLayerName = sourceNameList[len(sourceNameList)-1]
                    schema = {}
                    for field in fields:
                        schema[field.name] = field.type
                    url = "https://72.215.195.71:4203/azgiv/layerStatus"
                    params = {"username": username, "password": password, "schema": json.dumps(schema), "layer": sourceLayerName}
                    r = requests.get(url = url, params = params, verify = False)
                    statusCode = r.status_code
                    content = r.content
                    if statusCode == 200:
                        content = json.loads(r.content)
                        userId = content["userId"]
                        userSubscriptionId = content["userSubscriptionId"]
                        layerId = content["layerId"]
                        customerId = content["customerId"]

                        
                        url2 = "https://72.215.195.71:4203/azgiv/qcFeatureReportQuery"
                        params2 = {"idOnly": "true", "glyId": layerId}
                        r2 = requests.get(url = url2, params = params2)
                        if r2.status_code == 200:
                            content2 = json.loads(r2.content)
                            query = content2["payload"]["content"]["sql"]
                            url3 = "https://72.215.195.71:4203/azgiv/azgivDownloadArcgis"
                            params3 = {"query": query}
                            r3 = requests.get(url = url3, params = params3)
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
                                    arcpy.AddJoin_management(lyr.name, "NGUID", "C:\Users\Gistic\Downloads\AZGIVDownload\\" + fileName,"nguid")
                                    pythonaddins.MessageBox("Please check your file at azgivdownload", "INFO", 0)
                                else:
                                    pythonaddins.MessageBox("Please get your file at " + content3, "INFO", 0)
                            elif r3.status_code == 500:
                                pythonaddins.MessageBox(r3.content, "ERROR", 0)
                            else:
                                pythonaddins.MessageBox("Unknown error.", "ERROR", 0)
                        elif r2.status_code == 500:
                            pythonaddins.MessageBox(r2.content, "ERROR", 0)
                        else:
                            pythonaddins.MessageBox("Unknown error.", "ERROR", 0)
                    elif statusCode == 500:
                        pythonaddins.MessageBox(content, "ERROR", 0)
                    else:
                        pythonaddins.MessageBox("Unknown error.", "ERROR", 0)
        except Exception as e:
            pythonaddins.MessageBox(str(e), "ERROR", 0)
            raise        

class Qc(object):
    """Implementation for init.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        global layer
        global username
        global password
        try:
            username
            password
            layer
        except NameError:
            pythonaddins.MessageBox("Please fill all boxes.", 'INFO', 0)

        # Create schema of selected layer
        try:
            for lyr in arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT")):
                if lyr.name == layer:
                    fields = arcpy.ListFields(lyr.dataSource)
                    sourceNameList = lyr.dataSource.split("\\")
                    sourceLayerName = sourceNameList[len(sourceNameList)-1]
                    schema = {}
                    for field in fields:
                        schema[field.name] = field.type
                    url = "https://72.215.195.71:4203/azgiv/layerStatus"
                    params = {"username": username, "password": password, "schema": json.dumps(schema), "layer": sourceLayerName}
                    r = requests.get(url = url, params = params, verify = False)
                    statusCode = r.status_code
                    content = r.content
                    if statusCode == 200:
                        content = json.loads(r.content)
                        userId = content["userId"]
                        userSubscriptionId = content["userSubscriptionId"]
                        layerId = content["layerId"]
                        customerId = content["customerId"]

                        
                        url2 = "https://72.215.195.71:4203/azgiv/qcLayersArcgis"
                        payload = {"userId": userId, "userSubscriptionId": userSubscriptionId, "layerId": layerId, "customerId": customerId, "email": username}
                        r2 = requests.post(url = url2, data = payload)
                        if r2.status_code == 200:
                            pythonaddins.MessageBox("Your layer is being qced. Please wait for email", "INFO", 0)
                        elif statusCode == 500:
                            pythonaddins.MessageBox(r2.content, "ERROR", 0)
                        else:
                            pythonaddins.MessageBox("Unknown error.", "ERROR", 0)
                    elif statusCode == 500:
                        pythonaddins.MessageBox(content, "ERROR", 0)
                    else:
                        pythonaddins.MessageBox("Unknown error.", "ERROR", 0)
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
        print "editing"
        #for attr in dir(self):
        #   if hasattr( self, attr ):
        #       print( "obj.%s = %s" % (attr, getattr(self, attr)))
        global password
        print text
        password = text
        print self.value
        self.value = "******"
        print self.value
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
        global layer
        global username
        global password
        try:
            username
            password
            layer
        except NameError:
            pythonaddins.MessageBox("Please fill all boxes.", 'INFO', 0)

        # Create schema of selected layer
        try:
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
            raise        
        
