#!/usr/bin/env python3

import argparse
import constant
import os
import sys
from sentinel_validate import SentinelNomenclature
import construct_html_table
import utilities

"""
Class Name : SentinelNomenclatureCheck
Class Description : This class has implementation to invoke sentinel nomenclature check on policies and list the policies to run mock tests
Class Method : __init__ : Initialized the object with provider cloud platform, mounting workspace and container
               sentinel_validate_and_list_policies : Invokes Sentinel Nomenclature check for the policies in cloud provided 
               and prints the respective details
"""
class SentinelNomenclatureCheck:
    """
    Method Name : __init__
    Method Description : Creates the object and stores the details like cloud provider and container image to be created
    Method Returns : None
    """
    def __init__(self, cloud_provider, artifact_dir):
        self.cloud_provider = cloud_provider
        sentinelNomenclatureobj = SentinelNomenclature(self.cloud_provider)
        self.sentinel_validation_results = sentinelNomenclatureobj.validate_sentinels()
        self.artifact_dir = artifact_dir

    def sentinel_nomenclature_name_check(self):
        utilities.print_notification("\n**************** Running Sentinel Nomenclature Check For Name ****************\n")
        list_of_policies_incorrectly_named = self.sentinel_validation_results[constant.SENTINEL_NOMENCLATURE_VIOLATION_NAME_MISMATCH_CLOUD]

        if list_of_policies_incorrectly_named:
            #utilities.print_error("\n Sentinel Nomenclature Failure : Following Policy Names does not match with respective Policy folder name")
            #headers = ["Sentinel Nomenclature Failure : Name Mismatch", constant.CLOUD_PROVIDER]
            #Trying to prepare the artifacts under artifact folder
            self.name_mismatch = open(self.artifact_dir+"/"+self.cloud_provider+"_sentinel_Name_Mismatch.html", 'w')
            #Creating Content for the HTML Page for artifacts using construct_html_table.py
            htmlcode = construct_html_table.table(rows = list_of_policies_incorrectly_named, header_row = ["Sentinel Nomenclature Failure : Name Mismatch", "Cloud Provider"], flag = constant.ERRORS)
            self.name_mismatch.write(htmlcode)
            self.name_mismatch.close()
            #utilities.tabulate_content(headers, list_of_policies_incorrectly_named, False)  
            #sys.exit(1)

        utilities.print_success("\n********** Completed Running Sentinel Nomenclature Check for Name **********\n")
        
    def sentinel_nomenclature_tests_check(self):
        utilities.print_notification(" \n********** Running the Sentinel Nomenclature Check for Tests **********\n")
        list_of_policies_without_test_data = self.sentinel_validation_results[constant.SENTINEL_NOMENCLATURE_VIOLATION_TESTS_ABSENT_CLOUD]
        
        if list_of_policies_without_test_data:
            #utilities.print_error("\n Sentinel Nomenclature Failure : Following Policies does not have tests for mock run\n")
            #headers = ["Sentinel Nomenclature Failure : Test Data Missing", constant.CLOUD_PROVIDER]
            #utilities.tabulate_content(headers, list_of_policies_without_test_data, False)
            #Trying to prepare the artifacts under artifact folder
            self.test_data = open(self.artifact_dir+"/"+self.cloud_provider+"_sentinel_Test_Data_Missing.html", 'w')
            #Creating Content for the HTML Page for artifacts using construct_html_table.py
            htmlcode = construct_html_table.table(rows = list_of_policies_without_test_data, header_row = ["Sentinel Nomenclature Failure : Test Data Missing", "Cloud Provider"], flag = constant.ERRORS)
            self.test_data.write(htmlcode)
            self.test_data.close()
            #sys.exit(1)

        utilities.print_success("\n ********** Completed Running Sentinel Nomenclature Check for Tests **********\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gather required flags to perform nomenclature check")
    parser.add_argument("--cloud", dest="cloud_provider", type=str, help="constant.CLOUD_PROVIDER", required=True)
    parser.add_argument('--nomenclaturecheck_name', dest="nomenclature_check_name", help="Flag for Nomenclature Name Check", required=False)
    parser.add_argument('--nomenclaturecheck_tests', dest="nomenclature_check_tests", help="Flag for Nomenclature Tests Check", required=False)
    parser.add_argument('--artifact_dir', dest="artifact_dir", help="Artifact Directory", required=True)

    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider
    nomenclature_check_name = parsed_args.nomenclature_check_name
    nomenclature_check_tests = parsed_args.nomenclature_check_tests
    artifact_dir = parsed_args.artifact_dir

    #Create Object 
    # TODO : The condidtions needs to be evaluated on boolean basis. Relook at receiving the command line parameters
    policyCheckObj = SentinelNomenclatureCheck(cloud_provider, artifact_dir)
    if nomenclature_check_name == "True":
        policyCheckObj.sentinel_nomenclature_name_check()
    elif  nomenclature_check_tests == "True":
        policyCheckObj.sentinel_nomenclature_tests_check()
    else:
        utilities.print_error("Either Invalid or insufficient arguments passed for Nomenclature check for "+cloud_provider)

