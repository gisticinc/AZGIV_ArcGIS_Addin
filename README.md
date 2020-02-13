# AZGIV ArcGIS Python Add-in

The ArcGIS add-in for AZGIV is designed to allow users to access the core AZGIV functions, such as, Layer Upload, QC, QC Report Download/Link, and View Synchronization, etc., entirely within the ArcMap environment.

## Installation

1. Clone or download the package,
2. Execute the **AZGIV_ArcGIS_Addin.esriaddin** file in the directory on a Window machine where ArcGIS for Desktop is installed,
3. Open ArcMap, and
4. Click the **Customize menue**. On the **toolbar** list, check **AZGIV**.

## Change version

The Adin supports ArcGIS Version 10.7. If your ArcGIS for Desktop is not 10.7, please follow the steps to update:

1. Open the **config.xml** file in the directory with your favorite text editor.
2. Locate the `version="10.7"` in the first line.
3. Change the version to your local installation of ArcGIS for Desktop.
4. Save your change and close **config.xml**.
5. Execute the building script by double click the **makeaddin.py** in the directory.
6. Follow the step 2,3,4 in the installation section.

## Two Types of Users

### Agency User

For user from an agency:
1. Select a layer to upload to AZGIV
2. Enter your AZGIV username and password
3. Click one of action buttons on the right of the tool bar.

### Integrator User

For an integrator user: 
1. Select a layer to upload to AZGIV
2. Enter your AZGIV username and password
3. Click the Login button next to the Password field.
4. Select a client Agency
5. Click one of action buttons on the right of the tool bar.

## Functions

1. **Zoom** Synchronizes your ArcMap map view with the map view in an active AZGIV session
2. **Upload** Uploads the selected layer in your current ArcMAP session to the AZGIV cloud
3. **QC** Runs the QC process on the selected layer and generates report. The result can be reviewed in AZGIV application.
4. **Download** Downloads the QC report generated in the QC run. User can get the report in **AZGIVDownload** directory, which is in window user's default downloads folder. The report is automatically joined to the layer in ArcMap. User can review it in ArcMap or remove the join.

## Other Resources
- AZGIV Addin Short Video: https://www.youtube.com/watch?v=2RBDui05B7g
- AZGIV QA Video: https://www.youtube.com/watch?v=a_JROsWp6go&t=243s
- AZGIV Intro Video: https://www.youtube.com/watch?v=Jk3ajAF603Y
