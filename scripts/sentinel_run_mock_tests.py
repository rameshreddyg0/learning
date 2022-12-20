 #!/usr/bin/env python3

import argparse
import constant
import construct_html_table
import os
import sys
import subprocess
from sentinel_validate import SentinelNomenclature
import utilities

"""
Class Name :        SentinelMockRun
Class Description : This class has implementation to retrieve the list of policies for which mock test can be run
Class Method :      __init__ : Initialized the object with provided cloud platform, mounting workspace and container
                    sentinel_run_mocks : Runs the mock tests for the policies in given cloud provider
"""
class SentinelMockRun:
    """
    Method Name :        __init__
    Method Description : Creates the object and stores the details like cloud provider and container image to be created
    Method Returns :     None
    """
    def __init__(self, cloud_provider, artifact_dir):
        self.cloud_provider = cloud_provider
        self.artifact_dir = artifact_dir
        sentinel_nomenclature_obj = SentinelNomenclature(self.cloud_provider)
        self.sentinel_validation_results = sentinel_nomenclature_obj.validate_sentinels()

    def sentinel_run_mocks(self):

        utilities.print_notification("\n********** Running the Sentinel Mock Tests **********\n")
        list_of_sentinel_policies_to_run = self.sentinel_validation_results[constant.SENTINEL_POLICIES_TO_RUN]

        policies_mock_run_failed = []
        policies_mock_run_succeeded = []
        policies_mock_test_fail_logs = []

        for file_path in list_of_sentinel_policies_to_run:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            #Run each sentinel policy

            # Below command is for environments where we are using docker image for executing sentinel commands
            # p2 = subprocess.run(utilities.getDockerContainerCmd(self.mountingWorkspace, self.sentinelContainer) + 'test -verbose '+file_path, capture_output=True, shell=True)
            
            # Below command is for running in Git Hub Actions where we spin up required Image 
            sentinel_test_command_list = ['sentinel', 'test', '-verbose', file_path]
            p2 = subprocess.run(sentinel_test_command_list, capture_output=True)
            
            if(p2.returncode == 0):
                policies_mock_run_succeeded.append([self.cloud_provider, file_name])
                #utilities.print_success(p2.stdout.decode())
            else:
                #utilities.print_warning(p2.stdout.decode())
                policies_mock_run_failed.append([self.cloud_provider, file_name])
                policies_mock_test_fail_logs.append(p2.stdout.decode())
        
        cloud_provider_str = "Cloud Provider"
        if policies_mock_run_succeeded:
            headers = ["Cloud Provider", "Mock Test Successful"]
            #utilities.tabulate_content(headers, policies_mock_run_succeeded, True)
            #Trying to prepare the artifacts under artifact folder
            self.mock_run = open(self.artifact_dir+"/"+self.cloud_provider+"_sentinel_Mock_Run_Results.html", 'w')
            #Creating Content for the HTML Page for artifacts using construct_html_table.py
            htmlcode = construct_html_table.table(rows = policies_mock_run_succeeded, header_row = [ cloud_provider_str, 'Mock Test Successful'], flag = constant.SUCCESS)
            self.mock_run.write(htmlcode)
            self.mock_run.close()
            
        
        if policies_mock_run_failed:
            headers = ["Cloud Provider", "Mock Test Failed"]
            #utilities.tabulate_content(headers, policies_mock_run_failed, False)
            #Trying to prepare the artifacts under artifact folder
            self.mock_run = open(self.artifact_dir+"/"+self.cloud_provider+"_sentinel_Mock_Run_Results.html", 'a')
            self.mock_run.write("<br/>")
            #Creating Content for the HTML Page for artifacts using construct_html_table.py
            htmlcode = construct_html_table.table(rows = policies_mock_run_failed, header_row = [ cloud_provider_str, 'Mock Test Failed'], flag = constant.ERRORS)
            self.mock_run.write(htmlcode)
            self.mock_run.close()
            
        if policies_mock_test_fail_logs:
            for errMessage in policies_mock_test_fail_logs:
                utilities.print_error(errMessage)
            sys.exit(1)

        utilities.print_success("\n********** Completed Running Sentinel Mock Tests **********\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description ="Gather Sentinel Container Image, cloud platform, runs the mocks for sentinel policies for given cloud platform")

    parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required=True)
    parser.add_argument('--artifact_dir', dest="artifact_dir", help="Artifact Directory", required=True)

    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider
    artifact_dir = parsed_args.artifact_dir

    #Create Object
    policy_check_obj = SentinelMockRun(cloud_provider, artifact_dir) 
    sentinel_validation_results = policy_check_obj.sentinel_run_mocks()

    #utilities.printNotification("Completed running Sentinel mock testing for  "+cloud_provider)
