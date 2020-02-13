# AZGIV ArcGIS Python Add-ins

This is a ArcGIS tool bar with AZGIV upload, qc, download and zoom functions. It is designed to allow users working on AZGIV in ArcMap environment.

## Installation

1. Clone or download the package to your disk.
2. Execute the **AZGIV_ArcGIS_Addin.esriaddin** file in the directory on a windows machine with ArcGIS for Desktop.
3. Open your ArcMap.
4. Click the **Customize menue**. On the **toolbar** list, check **AZGIV**.

## Change version

The default version is 10.7. If your ArcGIS for Desktop is not 10.7, please follow the steps to update:
1. Open the **config.xml** file in the directory with your favorite text editor.
2. Locate the `version="10.7"` in the first line.
3. Change the version to your local installation of ArcGIS for Desktop.
4. Save your change and close **config.xml**.
5. Execute the building script by double click the **makeaddin.py** in the directory.
6. Follow the step 2,3,4 in the installation section.

## Authentication

### Agency

If you are agency, please fill in your AZGIV username and password at first. Then you will be able to run upload, qc, download on the selected layer.

### Integrator

If you are integrator, after fill in username and password, please hit the login button and pick the Agency you are working for from the list. Then you will be able to run upload, qc, download on the selected layer.

## Functions

1. **Zoom** function navigates your ArcMap to the extent specified in AZGIV application.
2. **Upload** function updates the selected layer in AZGIV cloud with your local data.
3. **QC** function implements qc rules and generates report for the selected layer. The result can be reviewed in AZGIV application.
4. **Download** function downloads qc report of the selected layer. User can get the report in **AZGIVDownload** directory, which is in window user's default downloads folder. And, the report is automatically joined to the layer in ArcMap. User can review it in ArcMap or remove the join.
