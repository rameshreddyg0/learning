 #!/usr/bin/env python3

import argparse
import constant
import os
import sys
import subprocess
import construct_html_table
from sentinel_validate import SentinelNomenclature
import utilities

"""
Class Name : SentinelFormatCheck
Class Description : This class has implementation to invoke sentinel nomenclature check on policies and list the policies to run mock tests
Class Method : __init__ : Initialized the object with provider cloud platform, mounting workspace and container
               sentinel_validate_and_list_policies : Invokes Sentinel Nomenclature check for the policies in cloud provided 
               and prints the respective details
"""
class SentinelFormatCheck:
    """
    Method Name : __init__
    Method Description : Creates the object and stores the details like cloud provider and container image to be created
    Method Returns : None
    """
    def __init__(self, cloud_provider, artifact_dir):
        self.cloud_provider = cloud_provider
        self.artifact_dir = artifact_dir
        sentinelNomenclatureObj = SentinelNomenclature(self.cloud_provider)
        self.sentinel_validation_results = sentinelNomenclatureObj.validate_sentinels()

    def sentinel_format_check(self):
        utilities.print_notification("\n********** Running the Sentinel Format Check **********\n")
        list_of_sentinel_policies_to_run = self.sentinel_validation_results[constant.SENTINEL_POLICIES_TO_RUN]

        policies_format_check_failed = []
        policies_format_check_succeeded = []
        policies_format_check_fail_logs = []

        for file_path in list_of_sentinel_policies_to_run:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            sentinel_format_command_list = ['sentinel', 'fmt', '-check=false', file_path]

            # Below command is for environments where we are using docker image for executing sentinel commands
            #p1 = subprocess.run(utilities.getDockerContainerCmd(self.mountingWorkspace, self.sentinelContainer) + 'fmt -check=false '+file_path, capture_output=True, shell=True)

            p1 = subprocess.run(sentinel_format_command_list, capture_output=True)
            
            if(p1.returncode == 0):
                policies_format_check_succeeded.append([self.cloud_provider, file_name])
                #utilities.print_success(p1.stdout.decode())
    
            else:
                #utilities.print_warning(p1.stdout.decode())
                policies_format_check_failed.append([self.cloud_provider, file_name])
                policies_format_check_fail_logs.append(p1.stdout.decode())
                policies_format_check_fail_logs.append(p1.stderr.decode())  
        
        if policies_format_check_succeeded:
            #headers = ["Cloud Provider", "Sentinel Format Check Success"]
            #Trying to prepare the artifacts under artifact folder
            self.format_check = open(self.artifact_dir+"/"+self.cloud_provider+"_sentinel_Format_Check_Results.html", 'w')
            #Creating Content for the HTML Page for artifacts using construct_html_table.py
            htmlcode = construct_html_table.table(rows = policies_format_check_succeeded, header_row = [ 'Cloud Provider', 'Sentinel Format Check Successful'], flag = constant.SUCCESS)
            self.format_check.write(htmlcode)
            self.format_check.close()
            #utilities.tabulate_content(headers, policies_format_check_succeeded, True)
        
        if policies_format_check_failed:
            #utilities.print_error("\n Sentinel Format Check Failure: Following Policies failed Format Check")
            headers = ["Cloud Provider", "Sentinel Format Check Failure"]
            utilities.tabulate_content(headers, policies_format_check_failed, False)
            #Trying to prepare the artifacts under artifact folder
            self.format_check = open(self.artifact_dir+"/"+self.cloud_provider+"_sentinel_Format_Check_Results.html", 'a')
            self.format_check.write("<br/>")
            #Creating Content for the HTML Page for artifacts using construct_html_table.py
            htmlcode = construct_html_table.table(rows = policies_format_check_failed, header_row = [ 'Cloud Provider', 'Sentinel Format Check Failed'], flag = constant.ERRORS)
            self.format_check.write(htmlcode)
            self.format_check.close()
            #utilities.tabulate_content(headers, policies_format_check_failed, False)
        
        if policies_format_check_fail_logs:
            for errMessage in policies_format_check_fail_logs:
                utilities.print_error(errMessage)
            # sys.exit(1)
        
        utilities.print_success("\n ************ Completed Sentinel Format Check ************\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description ="Gather cloud platform, list and validate the sentinel policies for given cloud platform")

    parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required=True)
    parser.add_argument('--artifact_dir', dest="artifact_dir", help="Artifact Directory", required=True)
    
    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider
    artifact_dir = parsed_args.artifact_dir

    #Create Object
    policyCheckObj = SentinelFormatCheck(cloud_provider, artifact_dir)
    policyCheckObj.sentinel_format_check()



    #utilities.print_notification("Sentinel Policies format check completed for "+cloud_provider)
