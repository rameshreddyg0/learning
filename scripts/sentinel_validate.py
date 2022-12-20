#!/usr/bin/env python3

import argparse
import constant
import os


"""
Class Name :        SentinelNomenclature
Class Description : This class implements the state in terms of cloud provider and 
                    has methods to perform the Sentinel Nomenclature check for the policies in cloud platform provided
Class Methods :     __init__ : Initialized the object with provided cloud platform
                    validate_sentinels : Performs the sentinel Nomenclature check for the policies in cloud platfomr provided
"""
class SentinelNomenclature:
    """
    Method Name :        __init__
    Method Description : Performs the Sentinel Nomenclature check for the policies in cloud platform provided
    Method Returns :     A dictionary with the Sentinel policies that are well formed, that have no tests to run and policies 
                         that does not share same name with the directory
    """
    def __init__(self, cloud_provider):
        self.cloud_provider = cloud_provider

    def validate_sentinels(self):
        root_to_start_walk = "../{cloud_provider}/sentinel/".format(cloud_provider = self.cloud_provider)
        sentinel_validation_results = dict()
        policy_map = []

        list_of_sentinel_policies_to_run = []
        list_of_policies_without_test_data = []
        list_of_policies_incorrectly_named = []

        list_of_sentinel_policies_to_run_cloud = []
        list_of_policies_without_test_data_cloud = []
        list_of_policies_incorrectly_named_cloud = []
        
        is_test_dir_present = False
  
        for root, dirs, files in os.walk(root_to_start_walk):
            is_test_dir_present = False
    
            if "test" in dirs:
                # Ignore the sentinel files inside 'test' directory
                dirs.remove("test")
                # Reset the flag to assume to indicate nomenclature handshake
                is_test_dir_present = True
            
            if "sample_deployment" in dirs:
                # Ignore the 'sample_deployment' directory
                dirs.remove("sample_deployment")     

            for file in files:
                dir_name = os.path.basename(os.path.dirname(root+'/'+file))
                file_name = os.path.splitext(os.path.basename(file))[0]
                policy_map = [file_name,self.cloud_provider]
        
                if file.endswith(".sentinel"): 
                    # Sentinel file found in directory : Check if it shares same name with directory
                    #utilities.print_notification("Sentinel File : "+file_name+ " in the directory : "+dir_name)
                    if dir_name == file_name:       
                        if is_test_dir_present:
                            list_of_sentinel_policies_to_run.append(os.path.join(root, file))
                            list_of_sentinel_policies_to_run_cloud.append(policy_map)
                        else:
                            #utilities.printError("Nomenclature Violation: The Policy does not have test cases for mock run")
                            list_of_policies_without_test_data.append(os.path.join(root, file))
                            list_of_policies_without_test_data_cloud.append(policy_map)
                    else:
                        #utilities.printError("Nomenclature Violation : Policy sentinel file does not share same name as directory: {file_name}".format(file_name = file_name))
                        list_of_policies_incorrectly_named.append(os.path.join(root, file))  
                        list_of_policies_incorrectly_named_cloud.append(policy_map)

        sentinel_validation_results[constant.SENTINEL_POLICIES_TO_RUN] = list_of_sentinel_policies_to_run
        sentinel_validation_results[constant.SENTINEL_NOMENCLATURE_VIOLATION_NAME_MISMATCH] = list_of_policies_incorrectly_named
        sentinel_validation_results[constant.SENTINEL_NOMENCLATURE_VIOLATION_TESTS_ABSENT] = list_of_policies_without_test_data
  
        sentinel_validation_results[constant.SENTINEL_POLICIES_TO_RUN_CLOUD] = list_of_sentinel_policies_to_run_cloud
        sentinel_validation_results[constant.SENTINEL_NOMENCLATURE_VIOLATION_NAME_MISMATCH_CLOUD] = list_of_policies_incorrectly_named_cloud
        sentinel_validation_results[constant.SENTINEL_NOMENCLATURE_VIOLATION_TESTS_ABSENT_CLOUD] = list_of_policies_without_test_data_cloud

        return sentinel_validation_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Sentinel Policy")

    parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required =True)

    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider

    #Create Object
    policy_check_obj = SentinelNomenclature(cloud_provider) 
    sentinel_validation_results = policy_check_obj.validate_sentinels()

    #utilities.print_notification("Sentinel Policy Checks Completed for "+cloud_provider)
