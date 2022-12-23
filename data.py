question_dict = [
    {
        "question": """What is the issue the client is experience?""",
        "question_nbr": 0,
        "answers": [
            "Documents not making it into Millennium/Missing documents.",
            "Cold feed documents failing to cer_batchindex.",
            "Duplicate cold feed documents in Millennium.",
            "Question Context/Resources"
        ],
        "next_question": [
            True,
            False,
            False,
            True
        ],
        "next_question_nbr": [
            1,
            None,
            None,
            0
        ],
        "additional_text": [
            "If the document never made it to Millennium, or missing from the patient's chart, we need to " +
            "start investigating at the beginning of the cold feed process.",
            """* Since the documents are in cer_batchindex:
    -> This means that the batch indexing service failed to process these documents. 
    -> We need to figure out why these documents failed.  

* To figure out why the documents failed, 
    -> Go to a Citrix server
    -> We need to grab the blob handle from one of the documents in cer_batchindex
        * This can be done multiple ways...
            -> You can get the blob from cer_batchindex
            -> You can get the blob handle from Document Manager by searching the MAN queue
            -> Sometimes the client will provide a blob handle 
    -> Open discernvisualdeveloper 
    -> Search for the blob handle in the trans log using one of the scripts below.
        * Trans log table
            -> Select *
              From cdi_trans_log c
              Where c.blob_handle = '[blob_handle]'
              with uar_code(m), format(date,";;Q"), time=30
              
        * If the document is not on the trans log table, search the pending document table.
            -> select * 
               from cdi_pending_document c
               where c.blob_handle = '[blob_handle]'
               with uar_code(m), format(date,";;Q"), time=30
              
* Once you have found the transaction
    -> On the trans_log table
        * Find the MAN_QUEUE_CAT_CD and MAN_QUEUE_ERR_CD fields to see the reason why the document failed. 

* Common errors:
    - DOS error:
        - The date of service is not between the allotted time range set inside CDIConfig - Event Validation
        - The first screenshot shows the event validation. Below is a little description.
            - The DOS sent with the document looks for the 'Discharge date' for the encounter
            - If the discharge date is not available, it will look for the 'admit date'
                - It will continue this pattern until it finds a date.
            - The *past (in days) and *future (in days) means that the DOS sent with the document must fall
              between the 'Discharge Date' (or whatever date the batch indexing service finds 
              on the account) and 720 days in the future and past.
                * For example:
                    - If the 'Discharge date' is 12/12/2022
                        - The DOS sent with the document must be between:
                            * Future - 12/1/2024
                            * Past - 12/22/2022
        - If the document is failing due to DOS, then the DOS is outside the 720 days in the past or future 
          from the discharge date.

    - Encounter error:
        - The batch indexing service couldn't match a patient with the MRN, and FIN.
        - The MRN, FIN, or both are incorrect.
        - To test, go to powerchart and search for the MRN.
            - If a patient comes up, add the FIN number and search again.
                - If a patient comes up, then make sure this is an active MRN and FIN.
                    - Tips:
                        - MRNs inside of a parentheses (MRN), then its not an active MRN
                        - I believe this goes for FINs also, but not 100% sure
                - If a patient doesn't come up after you search for the MRN and FIN together, 
                    - Search only using the FIN number
                    - If the FIN number doesn't find a patient, the FIN is wrong.
                - If no patient comes up, then the MRN is wrong.

    - Versioning error:
        - The document that was processed matched another document currently inside Millennium, 
          which caused it to fail.
        - In CDIConfig -> Event Validation, the 'Versioning Match Fields' section shows what the 
          Batch Indexing service is searching for to see if this is a 
          duplicate/different version of a document.


                * If the documents are not on the pending document table or in the MAN queue, 
                  the documents were processed successfully.
                    - Check the trans log for the missing documents. 
                    - If you see that it was processed to the patient's chart (usually you can tell on the trans log
                      table because it will have an action type flag of 0 (submitted) or 5 (document capture)): 
                        * Get the patient's name from the trans log table and go search PowerChart for the h_image. 
                        * If the person's name is not there, 
                            - Grab the person_id and search the person table to find the encounter info.
                                - Select *
                                  from person p
                                  where p.person_id = '[person_id]'
                                  with uar_code(m,d)
                            - You can also use the person_id to pull up the encounter numbers for this patient.
                                * Select *
                                  from encounter e
                                  where e.person_id = '[person_id]'
                                  with uar_code(m,d)
                        * Once you have the encounter number or person name, you should be able to find the patient
                          in PowerChart and look for the document.""",
            """Duplicate documents is usually an issue with Batch Indexing Service and not AXRM or Batch Prep. 

There are a few of reasons why there could be duplicate cold feed documents. 
    1. Duplicate documents are being sent to the directory that the documents are being processed in.
        - Batch Prep has a function to not process duplicate documents sent to the directory. 
            - When batch prep notices a duplicate document, it will add .duplicate to the ending to show 
              that the document was a duplicate. 
            - We can rule out that Batch Prep is causing the duplicate documents
        - AXRM does not have a function to determine if a document has been sent already.
            - If the client is sending duplicate documents to the fileshare and AXRM is processing the 
              documents, then this could be why there are duplicate documents on the account. 

    2. There are a couple of defects with the old legacy architecture that cause duplicate documents.
        * AXRM or AX Release script is still writing a document to a CDI_AUTO application, 
           Batch Index service may find the document, successfully index it and copy it to CEROTG, and 
           create the Millennium references to it. But then the delete from the auto queue will fail 
           because the document is still locked in the sending system.
            - https://jira2.cerner.com/browse/DOCIMAGING-12278
        * Versioned documents with performing provider remain in Batch Index queue
            - https://jira2.cerner.com/browse/DOCIMAGING-13271
        * Auto-versioning fails if the incoming document doesn't have a blob handle and blob_uid is 
           required in CEROTG.
            - https://jira2.cerner.com/browse/DOCIMAGING-10892

    3. Two Batch Indexing services pointing to the same AUTO queue.
        * To be sure this isn't the case
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
                        * This script will show the server the batch indexing service is running on.

    * Once you have found the server, 
        - Open CDIConfig and look through each batch indexing services' settings to make sure that 
          there aren't two indexing services pointing to the same AUTO
        - If there two indexing services pointing to the same AUTO queue
            * Contact CWx and let them know that this isn't allowed and they need to turn on off or 
              change the AUTO queue for one of the services so there aren't two pointing to the same 
              queue.""",
            """Cold feed documents are usually processed one of two way, AXRM or Batch prep. 
    - Both applications work the same. They both read the data sent with the files, usually in the file name or txt file
    - The files are sent with information such as MRN, FIN, Date of Service, etc. 

The point of this question is to figure out where to start the troubleshooting process.
    - Documents not making it into Millennium/Missing documents.
        * This option will start at the beginning of the cold feed process and work our way through the workflow to 
locate the missing documents.
    - Cold feed documents failing to cer_batchindex
        * This option is there if the client knows they are in cer_batchindex 
        * This option will start the investigation at cer_batchindex and work our way backwards through the process
to see where these documents failed. 
    - Duplicate cold feed documents in Millennium
        * Cold feed documents are usually duplicated one of two ways:
            - Batch indexing service duplicated the documents 
            - The client/third party sent in duplicate documents
        * This option will help analyze each option. 
        
Here is a brief summary of AXRM and Batch Prep. 
    1. ApplicationXtenderReportsMgmt (AXRM)
        - This application is on the ERMX server. 
        - It uses three different services.
            * AppXtenderReportsMgmtConfig
            * AppXtenderReportsMgmtPrintStreamProcessor
            * AppXtenderReportsMgmtReportProcessor
            
    - AXRM Workflow:
        * The client or a third party sends the documents to a fileshare directory.
            - CWx owns/controls the fileshare directory. 
            - If the files aren't making it into the directory, for whatever reason, then send the ticket 
              to CWx as they will need to see what's blocking the files from coming through. 
        * AXRM will pick up, & process the file. 
            - If successful, it will export the file to the report type's designated AX app (generally ERMX_AUTO) 
                * When the documents land in the auto queue, the batch indexing service will process the documents.
                    - If successful, it creates the clinical or nonclinical event and stores the images into CEROTG
                        * To verify, you can go to the patient's chart in PowerChart and look for the image.
                        * You can search for the batch using the trans log or pending document table.
                        * You can search for the file in Document Manager
                    - If the document failed, there was an issue matching the document to a patient. 
                        * This could be due to MRN or FIN don't match a patient, the date of service is not in the 
                          correct date range, duplicate documents, etc.
                        * The document will be sent to cer_batchindex waiting for a user to correct the error.
            - If something went wrong, the file extension will be renamed to ".FAILEDPDF" within the source directory
             
        - Useful Wikis:
            * Explains to AXRM process
                - https://wiki.cerner.com/display/public/reference/All+About+COLD+Feeds+for+CPDI+Using+AXRM
            * How to configure AXRM report types
                - https://wiki.cerner.com/display/Content360/COLD+Feeds%3A+Build%2C+Configure%2C+Troubleshoot
            * How to read and write the page processing script AXRM uses to process the documents
                - https://wiki.cerner.com/pages/viewpage.action?spaceKey=Content360&title=AXRM%20Standards%20and%20Samples
                    
    2. Batch Prep
        - This service is usually on the ACIS, Batch, or ERMX server. 
        
        - Workflow:
            - First, the client or a third party will send these documents to the fileshare directory.
                * CWx owns/controls the fileshare directory. 
                * If the files aren't making it into the directory, for whatever reason, then send the ticket 
                  to CWx as they will need to see what's blocking the files from coming through. 
            - Every 1 - 5 minutes, batch prep will check the directory to see if there are files to process.
            - When batch prep detects the file, it will start to process the file according the settings in CDIConfig. 
            - Once batch prep processes the document, it will send the file the AUTO queue for batch indexing
            - When the documents land in the auto queue, the batch indexing service will process the documents.
                - If successful, the file is attached to the patient's chart. 
                    * To verify, you can go to the patient's chart in PowerChart and look for the image.
                    * Or, you can search for the batch using the trans log or pending document table.
                - If the document failed, there was an issue attaching the document to the patient's chart.
                    * This could be due to MRN or FIN don't match a patient, the date of service is not in the 
                      correct date range, duplicate documents, etc.
                    * The document will be sent to cer_batchindex waiting for a user to correct the error.
                    
        - Useful Wikis:
            * Gives a broad overview of the CPDI batch capture process.
                - https://wiki.cerner.com/display/public/reference/About+CDI+Batch+Capture
            * Explains the different tabs in CDIConfig and how to configure them. 
                - https://wiki.cerner.com/display/public/reference/Configure+CDI+Configuration+Tool
                - Batch prep settings are in the services tab inside CDIConfig.
        - Known Defects:
            * When trying to update a setting inside the advanced settings box in CDIConfig, a message stating:
                - "Check the required fields" pops up; this is a defect. 
                    * https://jira2.cerner.com/browse/DOCIMAGING-13599"""
        ]
    },
    {
        "question": """Do you know the file share directory?""",
        "question_nbr": 1,
        "answers": [
            "Yes",
            "No",
            "Unsure",
            "Resources"
        ],
        "next_question": [
            True,
            False,
            False,
            True
        ],
        "next_question_nbr": [
            2,
            None,
            None,
            1
        ],
        "additional_text": [
            """You need to figure out which application (Batch Prep or AXRM) is processing these documents.
    - Go to the directory the client provided to see if there are files inside the directory.
        * There should either be:
            - .error and/or .parse files
            - .failedpdf and/or .cxpdf 
            - nothing in the directory""",
            "Get the file share directory from the client and then re-run the program",
            "...",
            "Resources"
        ]
    },
    {
        "question": """Select the one that applies:""",
        "question_nbr": 2,
        "answers": [
            "There are files in the directory ending in .error or .parse.",
            "There are files in the directory ending in .failedpdf or .cxpdf.",
            "No files in directory",
            "Resources"
        ],
        "next_question": [
            True,
            True,
            False,
            True
        ],
        "next_question_nbr": [
            3,
            5,
            None,
            2
        ],
        "additional_text": [
            """This is a Batch Prep issue.
    - This service is usually on the ACIS, Batch, or ERMX server. 
    - Workflow:
        - First, the client or a third party will send these documents to the fileshare directory.
            * CWx owns/controls the fileshare directory. 
            * If the files aren't making it into the directory, for whatever reason, then send the ticket 
              to CWx as they will need to see what's blocking the files from coming through. 
        - Every 1 - 5 minutes, batch prep will check the directory to see if there are files to process.
        - When batch prep detects the file, it will start to process the file according the settings in CDIConfig. 
        - Once batch prep processes the document, it will send the file the AUTO queue for batch indexing
        - When the documents land in the auto queue, the batch indexing service will process the documents.
            - If successful, the file is attached to the patient's chart. 
                * To verify, you can go to the patient's chart in PowerChart and look for the image.
                * Or, you can search for the batch using the trans log or pending document table.
            - If the document failed, there was an issue attaching the document to the patient's chart.
                * This could be due to MRN or FIN don't match a patient, the date of service is not in the 
                  correct date range, duplicate documents, etc.
                * The document will be sent to cer_batchindex waiting for a user to correct the error.
    - Useful Wikis:
        * Gives a broad overview of the CPDI batch capture process.
            - https://wiki.cerner.com/display/public/reference/About+CDI+Batch+Capture
        * Explains the different tabs in CDIConfig and how to configure them. 
            - https://wiki.cerner.com/display/public/reference/Configure+CDI+Configuration+Tool
            - Batch prep settings are in the services tab inside CDIConfig.
    - Known Defects:
        * When trying to update a setting inside the advanced settings box in CDIConfig, a message stating:
            - "Check the required fields" pops up; this is a defect. 
                * https://jira2.cerner.com/browse/DOCIMAGING-13599

Now that you have the information, we can start troubleshooting.""",
            """This means the document were processed by ApplicationXtenderReportsMgmt (AXRM)
    - This application is on the ERMX server. 
    - It uses three different services.
        * AppXtenderReportsMgmtConfig
        * AppXtenderReportsMgmtPrintStreamProcessor
        * AppXtenderReportsMgmtReportProcessor
        
Workflow:
    * The client or a third party sends the documents to a fileshare directory.
        - CWx owns/controls the fileshare directory. 
        - If the files aren't making it into the directory, for whatever reason, then send the ticket 
          to CWx as they will need to see what's blocking the files from coming through. 
    * AXRM will pick up, & process the file. 
        - If successful, it will export the file to the report type's designated AX app (generally ERMX_AUTO) 
            * When the documents land in the auto queue, the batch indexing service will process the documents.
                - If successful, it creates the clinical or nonclinical event and stores the images into CEROTG
                    * To verify, you can go to the patient's chart in PowerChart and look for the image.
                    * You can search for the batch using the trans log or pending document table.
                    * You can search for the file in Document Manager
                - If the document failed, there was an issue matching the document to a patient. 
                    * This could be due to MRN or FIN don't match a patient, the date of service is not in the 
                      correct date range, duplicate documents, etc.
                    * The document will be sent to cer_batchindex waiting for a user to correct the error.
        - If something went wrong, the file extension will be renamed to ".FAILEDPDF" within the source directory 

Useful Wikis:
    * Explains to AXRM process
        - https://wiki.cerner.com/display/public/reference/All+About+COLD+Feeds+for+CPDI+Using+AXRM
    * How to configure AXRM report types
        - https://wiki.cerner.com/display/Content360/COLD+Feeds%3A+Build%2C+Configure%2C+Troubleshoot
    * How to read and write the page processing script AXRM uses to process the documents
        - https://wiki.cerner.com/pages/viewpage.action?spaceKey=Content360&title=AXRM%20Standards%20and%20Samples
    * Useful information to learn how to read the scripts that AXRM uses to process the documents.
        - https://wiki.cerner.com/display/Content360/COLD+Feed+Scripting+Examples

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
        * You can usually find these scripts and logs in:
            - C:'\\'ERMXData'\\'Scripts and C:'\\'ERMXData'\\'RPWorking, respectively.
    - ERMX can only process one directory at a time. If there are documents in different directories, 
      ERMX will process one directory until all the files have been processed, before moving on to the next directory.

Reminder:
    - CWx owns/controls the fileshare directory. 
    - If the files aren't making it into the directory, for whatever reason, then send the ticket 
      to CWx as they will need to see what's blocking the files from coming through. 

Now that you have that information, let's start to troubleshoot.""",
            """If there are no files in the directory 
    - This means that AXRM or Batch prep deleted the processed documents due to the settings

If there are no files and you don't know if the documents failed or processed successfully
    - If the client provided a file name or blob handle, 
        - Try searching for the file in the trans log, pending document table, or Document Manager
        - This will hopefully help figure out what happened to the documents. 

    - If you don't have a file name or want to search for the file in discernvisualdeveloper,
        - Have the client resend a document (test doc or real doc) to the directory to test.
    - Once the client sends the document and you recreate the issue.
        * If the documents fails or process successfully, 
            - go back through the this program again to get to this question.""",
            """Batch Prep Workflow and info:
    - First, the client or a third party will send these documents to the fileshare directory.
        * CWx owns/controls the fileshare directory. 
        * If the files aren't making it into the directory, for whatever reason, then send the ticket 
          to CWx as they will need to see what's blocking the files from coming through. 
    - Every 1 - 5 minutes, batch prep will check the directory to see if there are files to process.
    - When batch prep detects the file, it will start to process the file according the settings in CDIConfig. 
    - Once batch prep processes the document, it will send the file the AUTO queue for batch indexing
    - When the documents land in the auto queue, the batch indexing service will process the documents.
        - If successful, the file is attached to the patient's chart. 
            * To verify, you can go to the patient's chart in PowerChart and look for the image.
            * Or, you can search for the batch using the trans log or pending document table.
        - If the document failed, there was an issue attaching the document to the patient's chart.
            * This could be due to MRN or FIN don't match a patient, the date of service is not in the 
              correct date range, duplicate documents, etc.
            * The document will be sent to cer_batchindex waiting for a user to correct the error.
- Useful Wikis:
    * Gives a broad overview of the CPDI batch capture process.
        - https://wiki.cerner.com/display/public/reference/About+CDI+Batch+Capture
    * Explains the different tabs in CDIConfig and how to configure them. 
        - https://wiki.cerner.com/display/public/reference/Configure+CDI+Configuration+Tool
        - Batch prep settings are in the services tab inside CDIConfig.
- Known Defects:
    * When trying to update a setting inside the advanced settings box in CDIConfig, a message stating:
        - "Check the required fields" pops up; this is a defect. 
            * https://jira2.cerner.com/browse/DOCIMAGING-13599
            
AXRM Workflow:
    * The client or a third party sends the documents to a fileshare directory.
        - CWx owns/controls the fileshare directory. 
        - If the files aren't making it into the directory, for whatever reason, then send the ticket 
          to CWx as they will need to see what's blocking the files from coming through. 
    * AXRM will pick up, & process the file. 
        - If successful, it will export the file to the report type's designated AX app (generally ERMX_AUTO) 
            * When the documents land in the auto queue, the batch indexing service will process the documents.
                - If successful, it creates the clinical or nonclinical event and stores the images into CEROTG
                    * To verify, you can go to the patient's chart in PowerChart and look for the image.
                    * You can search for the batch using the trans log or pending document table.
                    * You can search for the file in Document Manager
                - If the document failed, there was an issue matching the document to a patient. 
                    * This could be due to MRN or FIN don't match a patient, the date of service is not in the 
                      correct date range, duplicate documents, etc.
                    * The document will be sent to cer_batchindex waiting for a user to correct the error.
        - If something went wrong, the file extension will be renamed to ".FAILEDPDF" within the source directory 

- Useful Wikis:
    * Explains to AXRM process
        - https://wiki.cerner.com/display/public/reference/All+About+COLD+Feeds+for+CPDI+Using+AXRM
    * How to configure AXRM report types
        - https://wiki.cerner.com/display/Content360/COLD+Feeds%3A+Build%2C+Configure%2C+Troubleshoot
    * How to read and write the page processing script AXRM uses to process the documents
        - https://wiki.cerner.com/pages/viewpage.action?spaceKey=Content360&title=AXRM%20Standards%20and%20Samples
    * Useful information to learn how to read the scripts that AXRM uses to process the documents.
        - https://wiki.cerner.com/display/Content360/COLD+Feed+Scripting+Examples"""
        ]
    },
    {
        "question": """Select the one that applies:""",
        "question_nbr": 3,
        "answers": [
            "Some or all files in the directory ending with .error",
            "Only .parse files in the directory",
            "...",
            "Resources"
        ],
        "next_question": [
            False,
            True,
            False,
            True
        ],
        "next_question_nbr": [
            None,
            7,
            None,
            3
        ],
        "additional_text": [
            """If you see .error files, that means Batch Prep failed these documents. 
    - Step 1:
        - Find the server that batch prep is running on 
            * The three usual servers are:
                - ACIS 
                - Batch server 
                - ERMX 
        - On the server running Batch Prep:
            * Open the Windows Registry from Start -> Run -> regedit.exe
                - Browse to HKEY_LOCAL_MACHINE'\\'SOFTWARE'\\'Cerner'\\'CDI'\\'CDI_BatchPrepSvc
                    - Find the entry with the AUTO queue in the settings section and note the Key name
                    - In the source option, take a look at the settings and see if the file name matches these settings

If the settings and file name match, let's move on to step two.
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
        - Check the PDFs security settings. 
            * The settings could be preventing the prep service to process the document.
        - Check batch prep's account in the 'services' and CDIConfig apps.
            * In CDIConfig, batch prep usually runs with the cerner, or another admin account.
            * In 'services,' batch prep usually runs with the cernerasp'\\'<client mnemonic>'\\'cpdisvc account
    - Wrong file format
        - For example, I had a ticket where they sent word documents instead of PDFs. 
        - Batch Prep can't process word documents.
    - The batch preparation service failed to lock file such as '<some file name>_Endo_Cart'\\'dmag.xml'
        - SR 447015418
            - Two folders were already processed, but someone resent the same folders, causing the issue. 
            - When batch prep tried to process the duplicate folders, it couldn't rename the folder to 
                .done since it already existed. 
            - I removed the duplicate folders, and the other batches started processing.

Once you've recreated the issue and identified the root issue, all that is left is to figure out how to
resolve the problem. """,
            """If you only see .parse files inside the directory, 
    - This means that Batch prep processed these documents successfully
    - The issue isn't with Batch Prep, which means these documents should be in the AUTO, MAN or CEROTG queue.
        * Note:
            - There are two different architectures that clients could be set up with.
                1. Single App Architecture - only uses the CEROTG queue 
                    - This architecture means that instead sending files to different queues (ERMX_AUTO, ERMX_MAN, 
CDI_AUTO, CDI_MAN, etc.), the files are sent to one application, or queue (CEROTG), where it will be processed. 
                        * Everything happens in this one app (or queue) in order to minimize the amount of moving parts   
                2. Legacy Architecture (CDI_AUTO or ERMX_AUTO)
                    - The legacy architecture will send the documents to CDI_AUTO to be processed.
                        * If the document fails inside the AUTO queue, the documents will be sent to the MAN queue.
                        * If successful, the document is sent to CEROTG. 

Troubleshoot:
    - Go through these steps until you locate the documents.
        Step 1: Go to Document Manager and do a blank query on the AUTO queue
            * If you see documents in the auto queue, this is a legacy architecture. 
                - This means that batch indexing hasn't processed these documents. 
            * If nothing is there, move to step 2
        
        Step 2: Do a blank query on the MAN queue
            * If you see the documents in the MAN queue, this is a legacy architecture.
                - This means batch indexing failed these documents and should be in cer_batchindex waiting to process
            * If nothing is there, move to step 3
            
        Step 3: Go to Citrix server and open discernvisualdeveloper. Run the scripts below.
            - Run this script to find documents waiting to be processed by the batch indexing service 
                * SELECT DOCUMENTS = COUNT(CPD.BLOB_HANDLE)  
                , CPB.BATCH_NAME  
                , CAB.BATCHCLASS_NAME  
                FROM CDI_PENDING_DOCUMENT CPD  
                , CDI_PENDING_BATCH CPB  
                , CDI_AC_BATCHCLASS CAB  
                PLAN CPD WHERE CPD.ACTIVE_IND = 1  
                               AND CPD.PROCESS_LOCATION_FLAG = 1  
                JOIN CPB WHERE CPD.CDI_PENDING_BATCH_ID = CPB.CDI_PENDING_BATCH_ID  
                JOIN CAB WHERE CPB.CDI_AC_BATCHCLASS_ID = CAB.CDI_AC_BATCHCLASS_ID  
                GROUP BY CPB.BATCH_NAME, CAB.BATCHCLASS_NAME  
                ORDER BY COUNT(CPD.BLOB_HANDLE) DESC 
            - Run this script to find documents in manual queue
                * SELECT DOCUMENTS = COUNT(CPD.BLOB_HANDLE)  
                , CPB.BATCH_NAME  
                , CAB.BATCHCLASS_NAME  
                FROM CDI_PENDING_DOCUMENT CPD  
                , CDI_PENDING_BATCH CPB  
                , CDI_AC_BATCHCLASS CAB  
                PLAN CPD WHERE CPD.ACTIVE_IND = 1  
                               AND CPD.PROCESS_LOCATION_FLAG = 2  
                JOIN CPB WHERE CPD.CDI_PENDING_BATCH_ID = CPB.CDI_PENDING_BATCH_ID  
                JOIN CAB WHERE CPB.CDI_AC_BATCHCLASS_ID = CAB.CDI_AC_BATCHCLASS_ID  
                GROUP BY CPB.BATCH_NAME, CAB.BATCHCLASS_NAME  
                ORDER BY COUNT(CPD.BLOB_HANDLE) DESC
            - If the documents you are looking for aren't in the results for either script, 
                * They probably processed successfully.""",
            """...""",
            """Resources for .error:
    - PowerShell command to remove .error from files for reprocessing:
        * 'Dir *.PDF.error | rename-item -newname { [io.path]::ChangeExtension($_.name, "") }
    - Error messages for batch prep:
        - An unknown error (#5) has occurred querying service CDI_BatchIndexSvc. Access is denied
            - https://dragondrop.cerner.com/615853-millennium-cerner-document-imaging-cdiconfig-access-denied-2
        - Access Denied
            - Check the PDFs security settings. 
                * The settings could be preventing the prep service to process the document.
            - Check batch prep's account in the 'services' and CDIConfig apps.
                * In CDIConfig, batch prep usually runs with the cerner, or another admin account.
                * In 'services,' batch prep usually runs with the cernerasp'\\'<client mnemonic>'\\'cpdisvc account
        - Wrong file format
            - For example, I had a ticket where they sent word documents instead of PDFs. 
            - Batch Prep can't process word documents.
        - The batch preparation service failed to lock file such as '<some file name>_Endo_Cart'\\'dmag.xml'
            - SR 447015418
                - Two folders were already processed, but someone resent the same folders, causing the issue. 
                - When batch prep tried to process the duplicate folders, it couldn't rename the folder to 
                    .done since it already existed. 
                - I removed the duplicate folders, and the other batches started processing.

Scripts       
    - Run this script to find documents waiting to be processed by the batch indexing service 
                * SELECT DOCUMENTS = COUNT(CPD.BLOB_HANDLE)  
                , CPB.BATCH_NAME  
                , CAB.BATCHCLASS_NAME  
                FROM CDI_PENDING_DOCUMENT CPD  
                , CDI_PENDING_BATCH CPB  
                , CDI_AC_BATCHCLASS CAB  
                PLAN CPD WHERE CPD.ACTIVE_IND = 1  
                               AND CPD.PROCESS_LOCATION_FLAG = 1  
                JOIN CPB WHERE CPD.CDI_PENDING_BATCH_ID = CPB.CDI_PENDING_BATCH_ID  
                JOIN CAB WHERE CPB.CDI_AC_BATCHCLASS_ID = CAB.CDI_AC_BATCHCLASS_ID  
                GROUP BY CPB.BATCH_NAME, CAB.BATCHCLASS_NAME  
                ORDER BY COUNT(CPD.BLOB_HANDLE) DESC 
            - Run this script to find documents in manual queue
                * SELECT DOCUMENTS = COUNT(CPD.BLOB_HANDLE)  
                , CPB.BATCH_NAME  
                , CAB.BATCHCLASS_NAME  
                FROM CDI_PENDING_DOCUMENT CPD  
                , CDI_PENDING_BATCH CPB  
                , CDI_AC_BATCHCLASS CAB  
                PLAN CPD WHERE CPD.ACTIVE_IND = 1  
                               AND CPD.PROCESS_LOCATION_FLAG = 2  
                JOIN CPB WHERE CPD.CDI_PENDING_BATCH_ID = CPB.CDI_PENDING_BATCH_ID  
                JOIN CAB WHERE CPB.CDI_AC_BATCHCLASS_ID = CAB.CDI_AC_BATCHCLASS_ID  
                GROUP BY CPB.BATCH_NAME, CAB.BATCHCLASS_NAME  
                ORDER BY COUNT(CPD.BLOB_HANDLE) DESC"""
        ]
    },
    {
        "question": """What example do you have?""",
        "question_nbr": 4,
        "answers": [
            "The client provided a filename",
            "The client provided a patient example",
            "The client provided the date that the files were sent",
            "Resources"
        ],
        "next_question": [
            False,
            False,
            False,
            True
        ],
        "next_question_nbr": [
            None,
            None,
            None,
            4
        ],
        "additional_text": [
            """If the client provided the filename, we can start looking for it in Millennium. 
    - Step 1:
        - If you have a filename example, find the server that batch prep is running on 
            - The three usual servers are:
                    - ACIS 
                    - Batch server 
                    - ERMX 
            - On the server running Batch Prep:
                * Open CDIConfig
                * Go to the services tab 
                * Select the batch prep service 
                * Open up the advanced settings and take a look at the filename convention
                    - The screenshot that opened up, the filename convention is highlighted in green.
                    - Looking at the filename convention in the screenshot, I can see the batch name is 
                      the second field in the file name.
                    - Using the filename example that the client provided
                        - Grab the batch name (second data field)

    - Step 2:
        - Go to a Citrix server
        - Open discernvisualdeveloper
            - Search for file name
                - trans log table
                    - select * 
                      from cdi_trans_log c
                      where c.batch_name = '[batch name from file]'
                      with uar_code(m,d)
                - pending document table
                    - select *
                      from cdi_pending_document cp
                      where cp.batch_name = '[batch name from file]'
                      with uar_code(m,d)

    - Step 3:
        - Once you found the file in the trans log table or pending document table
            - The query should provide more information on what the status of the document is. 
            - If it was processed successfully, if the document was received, etc.

    - Step 4: 
        - Open PowerChart
        - Go to the patient's chart and look to see if the document is there. 
            - There have been instances where the document was processed on 10/20, but showing up on the
              patient's chart under the 10/15 date, causing the client not to be able to find the 
              document on the patient's chart. 
                - This is due to the date of service setting inside CDIConfig -> event validation tab.
                - The second screenshot that popped up shows this setting. """,
            """If the user provided a patient that the cold feed document isn't on the patient's chart, there a couple 
of ways to look for the document.

    1. Go to the patient's chart in PowerChart and look 
        - I have had a few tickets where the document was on the patient's chart, just showing up on the
          wrong date, or in a different area than the client was expecting it to be. 

    2. If the .parse files are still in the fileshare directory
        - You can search the MRN or FIN in the directory to see if the document is still there so you 
          can grab the filename and search in discernvisualdeveloper for the record. 
        - If the file is there, go to a Citrix server
            - Open discernvisualdeveloper
            - Search for file name
                - trans log table
                    - select * 
                      from cdi_trans_log c
                      where c.batch_name = '[batch name from file]'
                      with uar_code(m,d)
                - pending document table
                    - select *
                      from cdi_pending_document cp
                      where cp.batch_name = '[batch name from file]'
                      with uar_code(m,d)
            - Once you have found the document in Discernvisualdeveloper, this can give you more info
              about where the document is. 

    3. Go to a Citrix server and open discernvisualdeveloper
        - Do a broad general search to see if you can find the document
        - for example, if the batch prep filenames are all uniform you can search half of the name plus
          any additional information you want to add to the search. 
            - select *
              from cdi_trans_log c
              where c.batch_name = 'EXP_130822_2022-*' ;this is an example uniform name for a client 
              and c.MRN = xxxxx ; if the client provided a MRN you can add this
              and c.financial_nbr = xxxx ; if client provided FIN 
              and c.person_id = (select p.person_id
                                 from person p
                                 where p.name_first_key = cnvtupper('[enter patient's first name]')
                                 and p.name_lask_key = cnvtupper('[enter patient's last name]'))
              with uar_code(m,d)

            * The select from person table will help if you have the patient's first and last name.
                - The script will pull the person id and then search the trans log table for that person
                  id and batch name, which will help narrow down the search.""",
            """If you have a date range, you can try to find the document using the date range and batch name
    - Go to a Citrix server
            - Open discernvisualdeveloper
                - Search for file name between two dates
                    - trans log table
                        - select * 
                          from cdi_trans_log c
                          where c.batch_name = 'EXP_130822_2022-*' ;this is an example from a client 
                          and c.action_dt_tm >= cnvtdatetime('17-Oct-2022 00:00:00') ; change date
                          and c.action_dt_tm <= cnvtdatetime('20-Oct-2022 00:00:00') ; change date
                          with uar_code(m,d)

            - Open PowerChart
                - Search for the document using the date the client gave in the notes tab """,
            "Resources"
        ]
    },
    {
        "question": """Which file extension do the files have?""",
        "question_nbr": 5,
        "answers": [
            "CXPDF",
            "FAILDEDPDF",
            "Unsure - Resources/Links",
            "Resources"
        ],
        "next_question": [
            True,
            False,
            False,
            True
        ],
        "next_question_nbr": [
            7,
            None,
            None,
            5
        ],
        "additional_text": [
            """.CXPDF means that the files were processed successfully by AXRM. 
    - The issue isn't with ApplicationXtender, which means these documents should be in the AUTO, MAN or CEROTG queue.
        * Note:
            - There are two different architectures that clients could be set up with.
                1. Single App Architecture - only uses the CEROTG queue 
                    - This architecture means that instead sending files to different queues (ERMX_AUTO, ERMX_MAN, 
CDI_AUTO, CDI_MAN, etc.), the files are sent to one application, or queue (CEROTG), where it will be processed. 
                        * Everything happens in this one app (or queue) in order to minimize the amount of moving parts   
                2. Legacy Architecture (CDI_AUTO or ERMX_AUTO)
                    - The legacy architecture will send the documents to CDI_AUTO to be processed.
                        * If the document fails inside the AUTO queue, the documents will be sent to the MAN queue.
                        * If successful, the document is sent to CEROTG. 

Troubleshoot:
    - Go through these steps until you locate the documents.
        Step 1: Go to Document Manager and do a blank query on the AUTO queue
            * If you see documents in the auto queue, this is a legacy architecture. 
                - This means that batch indexing hasn't processed these documents. 
            * If nothing is there, move to step 2
        
        Step 2: Do a blank query on the MAN queue
            * If you see the documents in the MAN queue, this is a legacy architecture.
                - This means batch indexing failed these documents and should be in cer_batchindex waiting to process
            * If nothing is there, move to step 3
            
        Step 3: Go to Citrix server and open discernvisualdeveloper. Run the scripts below.
            - Run this script to find documents waiting to be processed by the batch indexing service 
                * SELECT DOCUMENTS = COUNT(CPD.BLOB_HANDLE)  
                , CPB.BATCH_NAME  
                , CAB.BATCHCLASS_NAME  
                FROM CDI_PENDING_DOCUMENT CPD  
                , CDI_PENDING_BATCH CPB  
                , CDI_AC_BATCHCLASS CAB  
                PLAN CPD WHERE CPD.ACTIVE_IND = 1  
                               AND CPD.PROCESS_LOCATION_FLAG = 1  
                JOIN CPB WHERE CPD.CDI_PENDING_BATCH_ID = CPB.CDI_PENDING_BATCH_ID  
                JOIN CAB WHERE CPB.CDI_AC_BATCHCLASS_ID = CAB.CDI_AC_BATCHCLASS_ID  
                GROUP BY CPB.BATCH_NAME, CAB.BATCHCLASS_NAME  
                ORDER BY COUNT(CPD.BLOB_HANDLE) DESC 
            - Run this script to find documents in manual queue
                * SELECT DOCUMENTS = COUNT(CPD.BLOB_HANDLE)  
                , CPB.BATCH_NAME  
                , CAB.BATCHCLASS_NAME  
                FROM CDI_PENDING_DOCUMENT CPD  
                , CDI_PENDING_BATCH CPB  
                , CDI_AC_BATCHCLASS CAB  
                PLAN CPD WHERE CPD.ACTIVE_IND = 1  
                               AND CPD.PROCESS_LOCATION_FLAG = 2  
                JOIN CPB WHERE CPD.CDI_PENDING_BATCH_ID = CPB.CDI_PENDING_BATCH_ID  
                JOIN CAB WHERE CPB.CDI_AC_BATCHCLASS_ID = CAB.CDI_AC_BATCHCLASS_ID  
                GROUP BY CPB.BATCH_NAME, CAB.BATCHCLASS_NAME  
                ORDER BY COUNT(CPD.BLOB_HANDLE) DESC
            - If the documents you are looking for aren't in the results for either script, 
                * They probably processed successfully.""",
            """FAILEDPDF files means AXRM failed these documents so we can start our investigation there. 
        
- Step 1:
    * Go to the ERMX server and open AXRM (ApplicationXtenderReportsMgmtAdmin) 
    * Go to Report Processors -> local computer -> logs -> failed logs or select the report type log that have failed
files 
    * If you see the failed logs still in AXRM, open on up and it will show and error like below:
        - ERROR	12/7/2022 16:55:20	INDEXING Validation error. Page 1: Invalid field value. 
Field: DATE_OF_SERVICE -- 15/47/
            - This error means that the file name format doesn't match the way the script is reading the filename. 
                * You will need to go look at the script and see what is wrong with the filename format.
            - First dragondrop article below has info on how to resolve this error. 
    * If you don't see any failed logs, go to step 2

- Step 2: recreate the issue
    * To recreate the issue,
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
        
DragonDrop articles:
    - Article for the error example above
        * https://dragondrop.cerner.com/1351526-cold-feed-failing-due-to-error-with-dos-but-dont-see-what-the-problem-is

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
              and documents started to process correctly""",
            """...""",
            """AXRM error messages:
    - ERROR	12/7/2022 16:55:20	INDEXING Validation error. Page 1: Invalid field value. 
Field: DATE_OF_SERVICE -- 15/47/
            - This error means that the file name format doesn't match the way the script is reading the filename. 
                * You will need to go look at the script and see what is wrong with the filename format.
        - https://dragondrop.cerner.com/1351526-cold-feed-failing-due-to-error-with-dos-but-dont-see-what-the-problem-is
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
              and documents started to process correctly"""
        ]
    },
    {
        "question": """Do you see the error logs for the documents that failed?""",
        "question_nbr": 6,
        "answers": [
            "True",
            "False",
            "Unsure",
            "Resources"
        ],
        "next_question": [
            False,
            False,
            False,
            True
        ],
        "next_question_nbr": [
            None,
            None,
            None,
            6
        ],
        "additional_text": [
            """...""",
            '...',
            "Resources"
        ]
    },
    {
        "question": """Where are the documents?""",
        "question_nbr": 7,
        "answers": [
            "AUTO queue (legacy or single app architecture)",
            "MAN queue (legacy or single app architecture)",
            "CEROTG",
            "Resources"
        ],
        "next_question": [
            False,
            False,
            False,
            True
        ],
        "next_question_nbr": [
            None,
            None,
            None,
            7
        ],
        "additional_text": [
            """If the documents are stuck in the AUTO queue (legacy or single app), there are a couple things to check. 

1. Check to see if the batch indexing service is on.
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
            - Look to see if the batch indexing service is turned on and running with:
                * cernerasp'\\'<client mnemonic>'\\'cpdisvc account.
        * Open the Windows Registry from Start -> Run -> regedit.exe
            - Browse to HKEY_LOCAL_MACHINE'\\'SOFTWARE'\\'Cerner'\\'CDI
            - The first instance of the service is configured in the "General" key
            - Additional instances will have their own key, example "CDI_BatchIndexSvc_2"
            - Find the entry with the AUTO queue with the issue and note the Key name
            - If an entry is not found with the queue that is backed up it may not be installed at all. 
                *If it is not installed, you might need to install a CDI Batch Indexing Service to process the queue.

2. There are a few of defects with the old legacy architecture.
    i. AXRM or AX Release script is still writing a document to a CDI_AUTO application, 
       Batch Index service may find the document, successfully index it and copy it to CEROTG, 
       and create the Millennium references to it. But then the delete from the auto queue will fail 
       because the document is still locked in the sending system.
        - https://jira2.cerner.com/browse/DOCIMAGING-12278
    ii. Versioned documents with performing provider remain in Batch Index queue
        - https://jira2.cerner.com/browse/DOCIMAGING-13271
    iii. Auto-versioning fails if the incoming document doesn't have a blob handle and blob_uid 
         is required in CEROTG
            - https://jira2.cerner.com/browse/DOCIMAGING-10892""",
            """If the documents are in the MAN queue (legacy or single app):
    - This means that the batch indexing service failed this document during processing. 
    - To figure out why the documents failed, grab one of the blob handles
        - Go to a Citrix server
        - Open discernvisualdeveloper 
        - Search for the blob handle in the trans log using the script below.
            - Select *
              From cdi_trans_log c
              Where c.blob_handle = '[put blob handle here and erase the #1.00 at the end]*'
              With uar_code(m,d)
    - Find the MAN_QUEUE_CAT_CD and MAN_QUEUE_ERR_CD fields to see the reason why the document failed. 

Common errors:
    - DOS error:
        - The date of service is not between the allotted time range set inside CDIConfig - Event Validation
        - The first screenshot shows the event validation. Below is a little description.
            - The DOS sent with the document looks for the 'Discharge date' for the encounter
            - If the discharge date is not available, it will look for the 'admit date'
                - It will continue this pattern until it finds a date.
            - The *past (in days) and *future (in days) means that the DOS sent with the document must fall
              between the 'Discharge Date' (or whatever date the batch indexing service finds 
              on the account) and 720 days in the future and past.
                * For example:
                    - If the 'Discharge date' is 12/12/2022
                        - The DOS sent with the document must be between:
                            * Future - 12/1/2024
                            * Past - 12/22/2022
        - If the document is failing due to DOS, then the DOS is outside the 720 days in the past or future 
          from the discharge date.

    - Encounter error:
        - The batch indexing service couldn't match a patient with the MRN, and FIN.
        - The MRN, FIN, or both are incorrect.
        - To test, go to powerchart and search for the MRN.
            - If a patient comes up, add the FIN number and search again.
                - If a patient comes up, then make sure this is an active MRN and FIN.
                    - Tips:
                        - MRNs inside of a paratheses (MRN), then its not an active MRN
                        - I believe this goes for FINs also, but not 100% sure
                - If a patient doesn't come up after you search for the MRN and FIN together, 
                    - Search only using the FIN number
                    - If the FIN number doesn't find a patient, the FIN is wrong.
                - If no patient comes up, then the MRN is wrong.
    
    - Versioning error:
        - The document that was processed matched another document currently inside Millennium, 
          which caused it to fail.
        - In CDIConfig -> Event Validation, the 'Versioning Match Fields' section shows what the 
          Batch Indexing service is searching for to see if this is a 
          duplicate/different version of a document.
            * The second screenshot that opened up shows this setting.
    
            * If the documents are not on the pending document table or in the MAN queue, 
              the documents were processed successfully.
                - Check the trans log for the missing documents. 
                - If you see that it was processed to the patient's chart (usually you can tell on the trans log
                  table because it will have an action type flag of 0 (submitted) or 5 (document capture)): 
                    * Get the patient's name from the trans log table and go search PowerChart for the h_image. 
                    * If the person's name is not there, 
                        - Grab the person_id and search the person table to find the encounter info.
                            - Select *
                              from person p
                              where p.person_id = '[person_id]'
                              with uar_code(m,d)
                        - You can also use the person_id to pull up the encounter numbers for this patient.
                            * Select *
                              from encounter e
                              where e.person_id = '[person_id]'
                              with uar_code(m,d)
                    * Once you have the encounter number or person name, you should be able to find the patient
                      in PowerChart and look for the document.""",
            """The documents made it through the whole process and should be in Millennium.
    - Go check the trans log and pending document table to see if you can find the batch.
        - If there are no transaction logging for this batch, 
            - check to see if the transaction logging is turned on in CDIConfig -> options tab.
    - Go check PowerChart to see if you can find the document.
        - The document could be uploaded to a different day than it was processed 
            - It can seem like the h_image isn't on the chart, 
              but it is there, just not where the user was looking.""",
            """Useful Wikis:
    - How to troubleshoot Single App Architecture
        * https://wiki.cerner.com/display/CRC/Single+Application+Architecture+%28SAA%29+Troubleshooting
    - Single App CWx alarms
        * https://wiki.cerner.com/pages/releaseview.action?pageId=1340624741
        
Defects with the old legacy architecture.
    i. AXRM or AX Release script is still writing a document to a CDI_AUTO application, 
       Batch Index service may find the document, successfully index it and copy it to CEROTG, 
       and create the Millennium references to it. But then the delete from the auto queue will fail 
       because the document is still locked in the sending system.
        - https://jira2.cerner.com/browse/DOCIMAGING-12278
    ii. Versioned documents with performing provider remain in Batch Index queue
        - https://jira2.cerner.com/browse/DOCIMAGING-13271
    iii. Auto-versioning fails if the incoming document doesn't have a blob handle and blob_uid 
         is required in CEROTG
            - https://jira2.cerner.com/browse/DOCIMAGING-10892
            
Common errors that fail documents to cer_batchindex:
    - DOS error:
        - The date of service is not between the allotted time range set inside CDIConfig - Event Validation
        - The first screenshot shows the event validation. Below is a little description.
            - The DOS sent with the document looks for the 'Discharge date' for the encounter
            - If the discharge date is not available, it will look for the 'admit date'
                - It will continue this pattern until it finds a date.
            - The *past (in days) and *future (in days) means that the DOS sent with the document must fall
              between the 'Discharge Date' (or whatever date the batch indexing service finds 
              on the account) and 720 days in the future and past.
                * For example:
                    - If the 'Discharge date' is 12/12/2022
                        - The DOS sent with the document must be between:
                            * Future - 12/1/2024
                            * Past - 12/22/2022
        - If the document is failing due to DOS, then the DOS is outside the 720 days in the past or future 
          from the discharge date.

    - Encounter error:
        - The batch indexing service couldn't match a patient with the MRN, and FIN.
        - The MRN, FIN, or both are incorrect.
        - To test, go to powerchart and search for the MRN.
            - If a patient comes up, add the FIN number and search again.
                - If a patient comes up, then make sure this is an active MRN and FIN.
                    - Tips:
                        - MRNs inside of a paratheses (MRN), then its not an active MRN
                        - I believe this goes for FINs also, but not 100% sure
                - If a patient doesn't come up after you search for the MRN and FIN together, 
                    - Search only using the FIN number
                    - If the FIN number doesn't find a patient, the FIN is wrong.
                - If no patient comes up, then the MRN is wrong.
    
    - Versioning error:
        - The document that was processed matched another document currently inside Millennium, 
          which caused it to fail.
        - In CDIConfig -> Event Validation, the 'Versioning Match Fields' section shows what the 
          Batch Indexing service is searching for to see if this is a 
          duplicate/different version of a document.
            * The second screenshot that opened up shows this setting.
    
            * If the documents are not on the pending document table or in the MAN queue, 
              the documents were processed successfully.
                - Check the trans log for the missing documents. 
                - If you see that it was processed to the patient's chart (usually you can tell on the trans log
                  table because it will have an action type flag of 0 (submitted) or 5 (document capture)): 
                    * Get the patient's name from the trans log table and go search PowerChart for the h_image. 
                    * If the person's name is not there, 
                        - Grab the person_id and search the person table to find the encounter info.
                            - Select *
                              from person p
                              where p.person_id = '[person_id]'
                              with uar_code(m,d)
                        - You can also use the person_id to pull up the encounter numbers for this patient.
                            * Select *
                              from encounter e
                              where e.person_id = '[person_id]'
                              with uar_code(m,d)
                    * Once you have the encounter number or person name, you should be able to find the patient
                      in PowerChart and look for the document."""
        ]
    }
]

apps = [{
    "question": "Which Application are you having issues with?",
    "question_nbr": 0,
    "answers": [
        'Cold Feed',
        'Kofax',
        'Scanning',
        'ApplicationXtender'
    ],
    "application": [
        question_dict,
        question_dict,
        question_dict,
        question_dict
    ]
},
]
