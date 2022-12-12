from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Style
from PIL import Image

# root = Tk()
# root.title('EDM Troubleshooting')
# root.geometry('600x200')
# root.eval('tk::PlaceWindow . center')

# read in image
ui1_pic1 = Image.open("Pictures/ui1_pic1.png")
ui5_pic1 = Image.open('Pictures/ui5_pic1.png')
ui5_pic2 = Image.open('Pictures/ui5_pic2.png')
ui6_pic1 = Image.open('Pictures/ui6_pic1.png')
ui6_pic2 = Image.open('Pictures/ui6_pic2.png')
ui7_pic1 = Image.open('Pictures/ui7_pic1.png')
ui7_pic2 = Image.open('Pictures/ui7_pic2.png')
ui7_pic3 = Image.open('Pictures/ui7_pic3.png')
ui8_pic1 = Image.open('Pictures/ui8_pic1.png')
ui8_pic2 = Image.open('Pictures/ui8_pic2.png')


# def start():
#     top = Toplevel(root)
#     top.title('EDM Troubleshooting')
#     top.geometry('600x200')
#     x = root.winfo_x()
#     y = root.winfo_y()
#     top.geometry("+%d+%d" %(x,y))
#
#     l1 = Label(top, image='::tk::icons::question')
#     l1.grid(row=0, column=0)
#     l2 = Label(top, text="Do you know the file share directory that the files are being sent to?")
#     l2.grid(row=0, column=1, columnspan=4)
#
#     b1 = Button(top, text="Yes", command=coldfeedbatchprep())
#     b1.grid(row=1, column=1)
#     b2 = Button(top, text="No")
#     b2.grid(row=1, column=2)
#     b3 = Button(top, text="Exit")
#     b3.grid(row=1, column=3)


def coldfeedbatchprep():
    while True:
        user_input = input("Do you know the file share directory? y/n or e to exit.")
        if user_input == 'y':
            ui1()
            break
        elif user_input == 'n':
            print("Get the file share directory from the client and then re-run the program")
            break
        elif user_input == 'e':
            print("You are not exiting the program")
            break
        else:
            print("That was not one of the options, try again!")


def ui1():
    while True:
        try:
            user_input1 = int(input("""
            - You need to figure out which application (Batch Prep or AXRM) is processing these documents.
            - Go to the directory the client provided to see if there are files inside the directory.
            Select the number that applies:
                1. There are files in the directory ending in .error or .parse.
                2. There are files in the directory ending in .failedpdf or .cxpdf.
                3. There are no files in the directory.
                0. Exit application
            """))
            if user_input1 == 1:
                ui1_pic1.show()
                print("""
                This is a batch prep issue. 
                It's important to know the process that these documents take when batch prep processes them.
                    - First, the client or a third party will send these documents to the fileshare directory.
                        * CWx owns/controls the fileshare directory. 
                        * If the files aren't making it into the directory, for whatever reason, then send the ticket 
                          to CWx as they will need to see what's blocking the files from coming through. 
                    - Every 1 - 5 minutes, batch prep will check the directory to see if there are files to process.
                    - When batch prep detects the file, it will start to process the file according the the settings.
                        * There is more information regarding the advanced settings for batch prep below.  
                    - Once batch prep processes the document, it will send the file to the batch indexing service to
                      be processed into Millennium. 
                
                The image that popped open is a screenshot of the advanced settings for batch prep.
                    - I highlighted the important parts.
                        Yellow highlight:
                          - This is the file directory where Batch Prep is pointed to.
                          - This should match with the file directory the client gave you earlier.
                        Blue highlight:
                          - This setting tells you what batch prep will be looking for when it processes the files.
                          - In this example, Batch prep will read the file name.
                        Green highlight
                          - This is the order that the file name needs to follow so that batch prep 
                            can read the file successfully. 
                          - In this example, filename should be:
                            - batchclass_batchname_createdate_createtime_mrn_FIN_docalias_provider_trackingnbr
                    
                    - There is a known defect inside the advanced settings for batch prep:
                        – When trying to update a setting inside the advanced settings box, a message stating: 
                            "Check the required fields" pops up; this is a defect. The jira is below.
                        -https://jira2.cerner.com/browse/DOCIMAGING-13599
                
                Now that you have the information, we can start troubleshooting. 
                    - Step 1:
                        - Find the server that batch prep is running on 
                            * The three usual servers are:
                                - ACIS 
                                - Batch server 
                                - ERMX 
                        - On the server running Batch Prep:
                            * Open CDIConfig
                            * Go to the services tab 
                            * Select the batch prep service 
                            * Open up the advanced settings and the directory containing the files so that you can 
                                compare the filename format in the advance setting vs. what is actually being sent in.
                """)
                ui2()
                break
            elif user_input1 == 2:
                print("""
                This means the document were processed by AXRM.
                
                Before starting to troubleshoot, lets go through the process the cold feed documents follow:
                    - The client or a third party sends the documents to the fileshare directory, same as batch prep.
                    - AXRM will process the document and send the document to the upload application.
                        * The upload app is listed in the report type properties setting. 
                        * The upload app will usually be ermx_auto or cdi_auto
                    - When the documents land in the auto queue, the batch indexing service will process the documents.
                        * If successful, the image is attached to the patient's chart. 
                            - To verify, you can go to the patient's chart in PowerChart and look for the image.
                            - Or, you can search for the batch using the trans log or pending document table.
                        * If the document failed, there was an issue attaching the document to the patient's chart.
                            - This could be due to MRN or FIN don't match a patient, the date of service is not in the 
                              correct date range, duplicate documents, etc.
                            - The document will be sent to cer_batchindex waiting for a user to correct the error.
                
                Tips:    
                    - If the documents are ending in .FAILEDPDF: 
                        * AXRM failed the documents.
                        * We will have to start at the beginning of the cold feed process mentioned above, which is:
                            - Documents being process in the fileshare directory by AXRM.
                            - Inside AXRM, there should be logs that will tell you what happened.
                    - If the documents are ending in .CXPDF:
                        * AXRM processed the documents successfully. 
                        * We can move on to the next step of the cold feed process, which is:
                            - The documents being sent to the upload app (AUTO queue).        
                    - Each report type has it's own script that it uses to read the file names, and its own logs.
                        * You can usually find these scripts and logs in (fyi: the directories backslash from the 
                          directories location because of the python code and the way it reads backslashes)
                            - C:-ERMXData-Scripts and C:-ERMXData-RPWorking, respectively.
                    - ERMX can only process one directory at a time. If there are documents in different directories, 
                      ERMX will process one directory until all the files have been processed, 
                      before moving on to the next directory.
                
                Useful wikis:
                    - Helpful to learn how to set up the report types and any setting configuration. 
                        * https://wiki.cerner.com/display/Content360/COLD+Feeds%3A+Build%2C+Configure%2C+Troubleshoot
                            - If documents are failing in AXRM, it is useful to go through the settings for the report type 
                              to make sure nothing is misconfigured.
                    - Useful information to learn how to read the scripts that AXRM uses to process the documents.
                        * https://wiki.cerner.com/display/Content360/COLD+Feed+Scripting+Examples
                 
                Reminder:
                    - CWx owns/controls the fileshare directory. 
                    - If the files aren't making it into the directory, for whatever reason, then send the ticket 
                      to CWx as they will need to see what's blocking the files from coming through. 
                        
                Now that you have that information, let's start to troubleshoot. 
                """)
                ui4()
                break
            elif user_input1 == 'e':
                print("You are not exiting the program")
                break
            else:
                print("That was not one of the options, try again!")
            break
        except:
            print("Invalid input. Please enter a number")


def ui2():
    while True:
        user_input2 = input("""
        Do the values in the filename for the .error pdf match the Batch Prep filename settings in CDIConfig? 
        y/n or e to exit
        
        """)
        if user_input2 == 'y':
            print("""
            The filename is not the issue. 
                
            Now that we confirmed the filename is not the issue. Let's move on to step two for troubleshooting.
                - Step 2:
                    * We need to recreate the issue so that we can see the error that is being thrown by batch prep.
                    * To recreate the issue, delete the .error at the end of the file. 
                        - This will allow batch prep to reprocess the file.  
                    * After deleting the .error, we need to open up the app that collects the logs for batch prep.
                        - Hit the start menu 
                        - Search for 'msgviewwin' and open up the application.
                        - When open, hit file -> load private file -> select cdi.mlg file.
                        - When the failed batch prep file has been reprocessed, if you don't see the error in the 
                          cdi.mlg file, hit refresh in 'msgviewwin' to pull in the recently thrown logs.
                            * You should see the error message in cdi.mlg file.
                    * The error messages for Batch Prep are pretty self-explanatory. Below I listed some of the error
                      messages that I've seen. 
                    
            Error messages I've seen:
                - An unknown error (#5) has occurred querying service CDI_BatchIndexSvc. Access is denied
                    - https://dragondrop.cerner.com/615853-millennium-cerner-document-imaging-cdiconfig-access-denied-2
                - Access Denied
                    - Check the PDF's security settings. 
                        * The settings could be preventing the prep service to process the document.
                    - Check batch prep's account in the 'services' and CDIConfig apps.
                        * In CDIConfig, batch prep usually runs with the cerner, or another admin account.
                        * In 'services,' batch prep usually runs with the cernerasp <client mnemonic>cpdisvc account
                - Wrong file format
                    - For example, I had a ticket where they sent word documents instead of PDFs. 
                    - Batch Prep can't process word documents.
                    - I can only process file extensions that end in three letters, such as:
                        * pdf, txt, xml
                - The batch preparation service failed to lock file such as '<some file name>_Endo_Cart\dmag.xml'
                    - SR 447015418
                        - Two folders were already processed, but someone resent the same folders, causing the issue. 
                        - When batch prep tried to process the duplicate folders, it couldn't rename the folder to 
                            .done since it already existed. 
                        - I removed the duplicate folders, and the other batches started processing.
            """)
            break
        elif user_input2 == 'n':
            print("""
            You found the issue. 
            Make sure the filename settings line up with the document filename being processed.
            """)
            break
        elif user_input2 == 'e':
            print("You are not exiting the program")
            break
        else:
            print('Please enter y for yes, n for no, or e to exit program.')


def ui3():
    while True:
        try:
            user_input3 = int(input("""
            Which file extension do the files have? 
            Select the number that applies:
                1 - .CXPDF
                2 - .FAILEDPDF
                3 - No files
                0 - Exit application
            """))
            if user_input3 == 1:
                print("""
                .CXPDF means that the files were processed successfully by AXRM. 
                    - The issue isn't with ApplicationXtender, and we can move on to the next step in the cold feed 
                      process. 
                    
                Next Step:
                    - The files will be sent to the ERMX_AUTO, CDI_AUTO, or CEROTG queue, depending on the domain setup. 
                        * If the client's domain is single app architecture (CEROTG) 
                            - Single App Architecture means that instead sending files to different queues (ERMX_AUTO, 
                              ERMX_MAN, CDI_AUTO, CDI_MAN, etc.), the files are sent to one application, or queue
                              (CEROTG), where it will be processed. 
                                * Everything happens in this one app (or queue) in order to minimize the amount of 
                                  moving parts that the documents go through and to create a single point of error, 
                                  instead of having to search through multiple applications to find where the error took
                                  place.  
                        * If the client's domain is legacy architecture (CDI_AUTO or ERMX_AUTO)
                            - The legacy architecture will send the documents to CDI_AUTO to be processed.
                            - If the document fails inside the AUTO queue, the documents will be sent to the MAN queue.
                            - If successful, the document is sent to CEROTG. 
                    - Go to the report types, right-click on the report type you've been working on and go to upload. 
                        * You will see the queue that these documents were sent to.
                        * The first screenshot that opened up shows this setting. 
                """)
                ui6_pic1.show()
                print("""
                Open up Document manager on the ERMX or ACIS server.
                 - Run a blank query for the auto queue that files were sent to to see if the files are in there.
                 - The screenshot that opened up second shows how to run this.
                """)
                ui6_pic2.show()
                ui7()
                break
            elif user_input3 == 2:
                ui3_1()
                break
            elif user_input3 == 3:
                print()
                break
            else:
                print("That was not one of the options, try again!")
            break
        except:
            print("Invalid input. Please enter a number")


def ui3_1():
    while True:
        ui5_pic1.show()
        user_input3_1 = input("""
            On the ermx server and open AXRM (ApplicationXtenderReportsMgmtAdmin) 
                - Go to Report Processors -> local computer -> logs -> failed logs or select the report type log you are 
                  investigation. 
                - The screenshot that opened up shows what to look for. 
                    - The report log and the failed files inside. 
                
            Do you see the error logs for the documents that failed? y/n or e to exit.
            """)
        if user_input3_1 == 'y':
            print("""
            In the report logs, open one of the failed logs to see the error.
                - The screenshot that opened up shows an example.
                - The error in the screenshot:
                    * ERROR	12/7/2022 16:55:20	INDEXING Validation error. Page 1: Invalid field value. 
                      Field: DATE_OF_SERVICE -- 15/47/
                    * This error means that the file name format doesn't match the way the script is reading the 
                      filename. You will need to go look at the script and see what is wrong with the filename format.
                
            DragonDrop article:
            https://dragondrop.cerner.com/1351526-cold-feed-failing-due-to-error-with-dos-but-dont-see-what-the-problem-is
            
            Other possible error messages:
                - ERROR 8/2/2006 12:56:57 STORAGE This AX application is currently being modified by another user.
                    - https://dragondrop.cerner.com/98825-millennium-cerner-document-imaging-armx-not-processing-reports
                    - https://jira2.cerner.com/browse/DOCIMAGING-11231
                - ERROR5/18/2017 07:24:11INDEXINGNo index records created. Report processing failed
                    - https://dragondrop.cerner.com/339628-millennium-cerner-document-imaging-file-fails-to-process-in-cold-feed
                - ERROR 10/7/2019 12:49:40 UPLOAD Can't create PDF file. This operation is not permitted.
                    - https://dragondrop.cerner.com/1235754-axrm-cold-feed-unable-to-process-pdfs-with-security
                - ERROR	5/25/2022 09:45:28	INDEXING	Validation error. Page 1: Invalid field value. 
                  Field: TRACKING_NBR -- 10277729_10710963_20220517180201960_F_IRFPAI_F_IRFPAI
                    - The filename was being entered for the tracking number, 
                      but the filename was too big for the field, causing the documents to fail.
                    - We changed the tracking number variable from the filename to the MRN + Encounter, 
                      and it processed through successfully.
                - ERROR	3/29/2022 13:55:27	INDEXING	Incorrect application fields
                    - SR 442650237
                        - The 'BREEZE' report type was set to PFT_AUTO instead of CDI_ERMX, 
                          causing the data fields not to match up.
                        - I changed the upload database from PFT_AUTO to CDI_ERMX, updated the data fields, 
                          and documents started to process correctly
                """)
            ui5_pic2.show()
            break
        elif user_input3_1 == 'n':
            print("""
            AXRM removes the logs from the application after a few days, but leaves the logs in the 
            C:-ERMXData-RPWorking directory. 
                - The RPWorking directory could be confusing so instead I recreate the issue.
                
            To recreate the issue,
                - Go to the fileshare directory.
                - Select a file with the .FAILEDPDF
                - Rename the document to it's original filename
                    * The usual steps for this goes as followed:
                        - Change the .FAILEDPDF extension to .PDF
                        - Remove the unique identifier that AXRM places at the beginning of the filename
                            * [xxxx_]original_file_name.[FAILED]PDF
                            * Remove everything between the []
                - Once the file has been renamed, AXRM will reprocess the document and produce the logs you need.
                - Once the file fails again, go to the logs and look for the error message.
            
            Other possible error messages:
                - ERROR 8/2/2006 12:56:57 STORAGE This AX application is currently being modified by another user.
                    - https://dragondrop.cerner.com/98825-millennium-cerner-document-imaging-armx-not-processing-reports
                    - https://jira2.cerner.com/browse/DOCIMAGING-11231
                - ERROR5/18/2017 07:24:11INDEXINGNo index records created. Report processing failed
                    - https://dragondrop.cerner.com/339628-millennium-cerner-document-imaging-file-fails-to-process-in-cold-feed
                - ERROR 10/7/2019 12:49:40 UPLOAD Can't create PDF file. This operation is not permitted.
                    - https://dragondrop.cerner.com/1235754-axrm-cold-feed-unable-to-process-pdfs-with-security
                - ERROR	5/25/2022 09:45:28	INDEXING	Validation error. Page 1: Invalid field value. 
                  Field: TRACKING_NBR -- 10277729_10710963_20220517180201960_F_IRFPAI_F_IRFPAI
                    - The filename was being entered for the tracking number, 
                      but the filename was too big for the field, causing the documents to fail.
                    - We changed the tracking number variable from the filename to the MRN + Encounter, 
                      and it processed through successfully.
                - ERROR	3/29/2022 13:55:27	INDEXING	Incorrect application fields
                    - SR 442650237
                        - The 'BREEZE' report type was set to PFT_AUTO instead of CDI_ERMX, 
                          causing the data fields not to match up.
                        - I changed the upload database from PFT_AUTO to CDI_ERMX, updated the data fields, 
                          and documents started to process correctly
                - ERROR	12/7/2022 16:55:20	INDEXING Validation error. Page 1: Invalid field value. 
                      Field: DATE_OF_SERVICE -- 15/47/
                    * This error means that the file name format doesn't match the way the script is reading the 
                      filename. You will need to go look at the script and see what is wrong with the filename format.
            
            DragonDrop article:
            https://dragondrop.cerner.com/1351526-cold-feed-failing-due-to-error-with-dos-but-dont-see-what-the-problem-is
            """)
            break
        elif user_input3_1 == 'e':
            print("You are not exiting the program")
            break
        else:
            print('Please enter y for yes, n for no, or e to exit program.')


def ui4():
    while True:
        try:
            user_input4 = int(input("""
            What is the issue the client is experience? 
            Select the number that applies:
                1 - Documents not making it into Millennium/failing in AXRM/Missing documents.
                2 - Cold feed documents failing to cer_batchindex.
                3 - Duplicate cold feed documents in Millennium.
                4 - Other
                0 - to exit
            """))
            if user_input4 == 1:
                print("""
                If the document never made it to Millennium, failed inside AXRM, or missing from the patient's chart, 
                start at the beginning of the process mentioned earlier.
                    - Go to the file directory that the files were sent to.
                """)
                ui3()
            elif user_input4 == 2:
                print("""
                - To figure out why the documents failed, grab one of the blob handles, go to a Citrix server, open discernvisualdeveloper and search for the blob handle in the trans log or pending document table.
                    - Select *
                      From cdi_trans_log c
                      Where c.blob_handle = '[put blob handle here and erase the #1.00 at the end]*'
                      With uar_code(m,d)
                - Find the MAN_QUEUE_CAT_CD and MAN_QUEUE_ERR_CD fields to see the reason why the document failed.
                 """)
                print("""
                Common errors:
                    - DOS error:
                        - The date of service is not between the allotted time range set inside CDIConfig -> Event Validation.
                        -The screenshot below reads as followed
                            - The DOS sent with the document looks for the 'Discharge date' for the encounter, if that's not available, it will look for the 'admit date' and so on.
                        - If the document is failing due to DOS, then the DOS is outside the 720 days in the past or future from the discharge date.
                """)
                ui8_pic1.show()
                print("""
                - Encounter error:
                    - The batch indexing service couldn't match a patient with the MRN, and FIN.
                    - The MRN, FIN, or both are incorrect.
                    - To test, go to powerchart and search for the MRN.
                        - If a patient comes up, add the FIN number and search again.
                            - If a patient comes up, then make sure this is an active MRN and FIN.
                                - Tips:
                                    - MRNs inside of a paratheses (MRN), then its not an active MRN
                                    - I believe this goes for FINs also, but not 100%
                            - If a patient doesn't come up after you search for the MRN and FIN together, then search only using the FIN number
                                - If the FIN number doesn't find a patient, the FIN is wrong.
                            - If no patient comes up, then the MRN is wrong.
                - Versioning error:
                    - The document that was processed matched another document currently inside Millennium, which caused it to fail.
                    - In CDIConfig -> Event Validation, the 'Versioning Match Fields' section shows what the Batch Indexing service is searching for to see if this is a duplicate/different version of a document.
                """)
                ui8_pic2.show()
                break
            elif user_input4 == 3:
                print("""
                - There are a couple of defects with the old legacy architecture that cause duplicate documents.
                    1. AXRM or AX Release script is still writing a document to a CDI_AUTO application, Batch Index service may find the document, successfully index it and copy it to CEROTG, and create the Millennium references to it. But then the delete from the auto queue will fail because the document is still locked in the sending system.
                        - https://jira2.cerner.com/browse/DOCIMAGING-12278
                    2. Versioned documents with performing provider remain in Batch Index queue
                        - https://jira2.cerner.com/browse/DOCIMAGING-13271?filter=70688&jql=project%20in%20(PATESIG%2C%20EDM%2C%20DOCIMAGING)%20AND%20issuetype%20%3D%20Defect%20AND%20text%20~%20%22batch%20indexing%20auto%22%20ORDER%20BY%20created%20DESC
                    3. Auto-versioning fails if the incoming document doesn't have a blob handle and blob_uid is required in CEROTG
                        -https://jira2.cerner.com/browse/DOCIMAGING-10892
                """)
                break
            elif user_input4 == 0:
                print("You are exiting this program.")
                break
            else:
                print("That was not one of the options, try again!")
            break
        except:
            print("Invalid input. Please enter a number")


def ui5():
    while True:
        user_input5 = input("Do you see the files ending with .failedpdf? y/n or e for exit.")
        if user_input5 == 'y':
            print("In the report logs, open one of the failed logs to see the error")
            break
        elif user_input5 == 'n':
            print()
            break
        elif user_input5 == 'e':
            print("You are exiting this program.")
            break
        else:
            print("That was not one of the options, try again!")


def ui7():
    while True:
        user_input7 = input("Do you see the documents inside the AUTO queue? y/n or e for exit.")
        if user_input7 == 'y':
            print("""
            If the documents aren't processing through, or stuck in the AUTO queue, there are a few things to check. 
                * Note: 
                    - If you see documents in the auto queue, this is a legacy architecture. 
                    - The problem with these documents not processing is more than likely due to the
                      batch indexing service. 
                        * This helps narrow the investigation to a single service that could be causing the 
                          issues.
                      
                1. The batch indexing service pointing to this AUTO queue isn't on.
                    - Go look for the batch indexing service pointing to this queue.
                    - You can find the batch indexing services two ways.
                        i. Look through the servers they might be running on, which are the:
                            -ACIS server
                            -Document imaging (batch) server
                        ii. Go to discernvisualdeveloper on a Citrix server and run this script.
                            - SELECT A.APPLCTX, A.APPLICATION_DIR, A.APPLICATION_IMAGE, A.APPLICATION_NUMBER
                                    , A.APPLICATION_STATUS, A.APPLICATION_VERSION
                                    , A.APP_CTX_ID, A.AUTHORIZATION_IND
                                    , A.CLIENT_NODE_NAME, A.CLIENT_START_DT_TM, A.CLIENT_TZ, A.DEFAULT_LOCATION
                                    , A.DEVICE_ADDRESS, A.DEVICE_LOCATION, A.END_DT_TM, A.LOGDIRECTORY
                                    , A.NAME, A.PARMS_FLAG, A.PERSON_ID
                                    , A_POSITION_DISP = UAR_GET_CODE_DISPLAY(A.POSITION_CD)
                                    , A.ROWID, A.START_DT_TM, A.TCPIP_ADDRESS, A.UPDT_APPLCTX
                                    , A.UPDT_CNT, A.UPDT_DT_TM, A.UPDT_ID
                                    , A.UPDT_TASK, A.USERNAME
                            FROM APPLICATION_CONTEXT A
                            WHERE A.APPLICATION_NUMBER = 4273000
                            WITH NOCOUNTER, SEPARATOR=" ", FORMAT, MAXREC = 100
                                * This script will show you which server the batch indexing service is running on.
                    
                    - Log into the server batch indexing is on and make sure the service is running. 
                        * Open up the 'services' app.
                            - Look to see if the batch indexing service is turned on and running 
                              with the cernerasp-[<client mnemonic]cpdisvc account.
                            - The first screenshot that popped up shows the services running.
                        * Open up CDIConfig
                            - Go to services tab
                            - Select batch indexing service
                            - Make sure that the service is pointing to the correct AUTO queue.
                            - The second screenshot shows the batch indexing service pointing to the AUTO queue. 
                            - The third screenshot shows that there are multiple services.
                                * You can look at each of the indexing services' setting by hitting the dropdown and 
                                  going through each service.
                    
                2. If the service is on and pointing to the correct AUTO queue, make sure the cpdisvc account has 
                   the access it needs to process the documents.
                    * Go to HNAUser
                    * Search for the cpdisvc account
                    * Go to organizations and make sure the account has access to the correct facility. 
                        
                3. There are a couple of defects with the old legacy architecture.
                    i. AXRM or AX Release script is still writing a document to a CDI_AUTO application, 
                       Batch Index service may find the document, successfully index it and copy it to CEROTG, 
                       and create the Millennium references to it. But then the delete from the auto queue will fail 
                       because the document is still locked in the sending system.
                        - https://jira2.cerner.com/browse/DOCIMAGING-12278
                    ii. Versioned documents with performing provider remain in Batch Index queue
                        - https://jira2.cerner.com/browse/DOCIMAGING-13271?filter=70688&jql=project%20in%20(PATESIG%2C%20EDM%2C%20DOCIMAGING)%20AND%20issuetype%20%3D%20Defect%20AND%20text%20~%20%22batch%20indexing%20auto%22%20ORDER%20BY%20created%20DESC
                    iii. Auto-versioning fails if the incoming document doesn't have a blob handle and blob_uid 
                         is required in CEROTG
                            - https://jira2.cerner.com/browse/DOCIMAGING-10892
            """)
            ui7_pic1.show()
            ui7_pic2.show()
            ui7_pic3.show()
            break
        elif user_input7 == 'n':
            print("""
            - This can mean two things. 
                1. The documents were processed by the batch indexing service and are now in the MAN queue.
                    - Legacy architecture
                2. The documents could be in CEROTG 
                    - Single app architecture
                
            - To determine which architecture the domain is set up as,
                - In Document manager, run a blank query against the man queue to see if there are any documents inside.
                    * If there are documents in the MAN queue, batch indexing failed the document and it should be in 
                      cer_batchindex.
                    * If the document are not in the MAN queue, we need to check the pending document table to be sure.
                        - (get script to search pending document queue)
                        - If the documents are on the pending document table, then the documents still need to be 
                          processed in the AUTO queue. 
                            - Single App architecture 
                    * If the documents are not on the pending document table or in the MAN queue, 
                      the documents were processed successfully.
                        - Check the trans log for the missing documents. 
                        - If you see that it was processed to the patient's chart (usually you can tell because it will
                          have a action type flag of 0 or submitted): 
                            * Grab the encounter number (if there on the trans log record for this image)
                            * If the encounter number is not there, 
                                - Grab the person_id and search the person table to find the encounter info.
                                    - Select *
                                      from person p
                                      where p.person_id = '[person_id]'
                                      with uar_code(m,d)
                            * Once you have the encounter number, you should be able to go to the encounter in 
                              PowerChart and look for the document.
            """)
            break
        elif user_input7 == 'e':
            print("You are exiting this program.")
            break
        else:
            print("That was not one of the options, try again!")


def ui8():
    while True:
        ui8 = input("Are there documents in the MAN queue? y/n or e to exit.")
        if ui8 == 'y':
            print("""
            - To figure out why the documents failed, grab one of the blob handles, go to a Citrix server, open discernvisualdeveloper and search for the blob handle in the trans log or pending document table.
                - Select *
                  From cdi_trans_log c
                  Where c.blob_handle = '[put blob handle here and erase the #1.00 at the end]*'
                  With uar_code(m,d)
            - Find the MAN_QUEUE_CAT_CD and MAN_QUEUE_ERR_CD fields to see the reason why the document failed.
            """)
            print("""
            Common errors:
                - DOS error:
                    - The date of service is not between the allotted time range set inside CDIConfig -> Event Validation.
                    -The screenshot below reads as followed
                        - The DOS sent with the document looks for the 'Discharge date' for the encounter, if that's not available, it will look for the 'admit date' and so on.
                    - If the document is failing due to DOS, then the DOS is outside the 720 days in the past or future from the discharge date.
            """)
            ui8_pic1.show()
            print("""
            - Encounter error:
                - The batch indexing service couldn't match a patient with the MRN, and FIN.
                - The MRN, FIN, or both are incorrect.
                - To test, go to powerchart and search for the MRN.
                    - If a patient comes up, add the FIN number and search again.
                        - If a patient comes up, then make sure this is an active MRN and FIN.
                            - Tips:
                                - MRNs inside of a paratheses (MRN), then its not an active MRN
                                - I believe this goes for FINs also, but not 100%
                        - If a patient doesn't come up after you search for the MRN and FIN together, then search only using the FIN number
                            - If the FIN number doesn't find a patient, the FIN is wrong.
                        - If no patient comes up, then the MRN is wrong.
            - Versioning error:
                - The document that was processed matched another document currently inside Millennium, which caused it to fail.
                - In CDIConfig -> Event Validation, the 'Versioning Match Fields' section shows what the Batch Indexing service is searching for to see if this is a duplicate/different version of a document.
            """)
            ui8_pic2.show()
            break
        elif ui8 == 'n':
            print("""
            - Go check the trans log and pending document table to see if you can find the batch.
                - If there are no transaction logging for this batch, check to see if the transaction logging is turned on in CDIConfig.
            - Go check PowerChart to see if you can find the document.
                - The document could be uploaded to a different day than it was processed,  so it can seem like the image isn't on the chart, but it is there, just not where the user was looking.
            """)
            break
        elif ui8 == 'e':
            print("You are exiting this program.")
            break
        else:
            print("That was not one of the options, try again!")


coldfeedbatchprep()

# Button(root, text="Let's get started!", padx=20, pady=20, command=start).pack(pady=20)
#
# root.mainloop()
