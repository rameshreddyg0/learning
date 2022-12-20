#!/usr/bin/env python3

import argparse
import constant
import construct_html_table
import hcl 
import os
import sys
import utilities
from tabulate import tabulate

failed_policies = []
def validate_sentinel_hcl(cloud_provider, artifact_dir):	


	missing_references = False
	missing_references_policies = []
	hcl_file_path = f'../{cloud_provider}/sentinel/sentinel.hcl'
	
	utilities.print_notification("Sentnel file: "+hcl_file_path)
	
	if (os.path.isfile(hcl_file_path) == True):
		utilities.print_success("Sentinel File Present")
		sentinel_validate = open(artifact_dir+"/"+cloud_provider+constant.SENTINEL_VALIDATE_RESULT_HTML, 'a')
		success_message = "Sentinel File Present"
		sentinel_validate.write(utilities.construct_html_message_success(success_message))
		sentinel_validate.close()
	else:
		utilities.print_error("Sentinel Fle Not Found")
		sentinel_validate = open(artifact_dir+"/"+cloud_provider+constant.SENTINEL_VALIDATE_RESULT_HTML, 'a')
		error_message = "Sentinel File Present"
		sentinel_validate.write(utilities.construct_html_message_error(error_message))
		sentinel_validate.close()
		sys.exit(1)
		
	try:
		with open(hcl_file_path, 'r') as fp:
			try:
				policies_in_hcl_file = hcl.load(fp)['policy']
			except OSError :
				utilities.print_error("Invalid HCL file Configuration in {0}".format(hcl_file_path))
				sentinel_validate = open(artifact_dir+"/"+cloud_provider+constant.SENTINEL_VALIDATE_RESULT_HTML, 'a')
				error_message = "Invalid HCL file Configuration in {0}".format(hcl_file_path)
				sentinel_validate.write(utilities.construct_html_message_error(error_message))
				sentinel_validate.close()
				sys.exit(1)
	except (IOError, OSError) :
		utilities.print_error("Sentinel HCL file not found in path {0}".format(hcl_file_path))
		sentinel_validate = open(artifact_dir+"/"+cloud_provider+constant.SENTINEL_VALIDATE_RESULT_HTML, 'a')
		error_message = "Sentinel HCL file not found in path {0}".format(hcl_file_path)
		sentinel_validate.write(utilities.construct_html_message_error(error_message))
		sentinel_validate.close()
		sys.exit(1)


	policies_in_json = policies_in_hcl_file.items()
	for policy_name, policy_config in policies_in_json:
		# ignore the first occurance of dot(.) in the path given in source of sentinel file
		path_in_hcl_without_dot = policy_config['source'].split(".", 1)
		file_path = f'../{cloud_provider}/sentinel'+path_in_hcl_without_dot[1]
		#utilities.print_notification("File Path: "+file_path)
		if (os.path.isfile(file_path) == False):
			missing_references = True
			missing_references_policies.append(file_path)
			#utilities.print_warning("Reference to sentinel policy does not exist for: "+file_path)
						
	if (missing_references == True):
		utilities.print_notification("Please make sure all references to policies mentioned in hcl does exist")
		for missing_reference in missing_references_policies:
			# utilities.print_warning(missing_references)
			array_num = [missing_reference]
			failed_policies.append(array_num)

	if failed_policies:
		headers = ["Missing Refrence in sentinel.hcl"]
		utilities.print_error(tabulate(failed_policies, headers, tablefmt="pretty"))
		sentinel_validation = open(artifact_dir+"/"+cloud_provider+constant.SENTINEL_VALIDATE_RESULT_HTML, 'a')
		htmlcode = construct_html_table.table(rows = failed_policies, header_row = ["Missing Refrence in sentinel.hcl"], flag = constant.ERRORS)
		sentinel_validation.write(htmlcode)
		sentinel_validation.close()
		#Bubble up the failure and hard stop the build
		sys.exit(1)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Verify if references mentioned in HCL file are valid")
	parser.add_argument("--cloud", dest="cloud_provider", help="Validate HCL file", required=True)
	parser.add_argument("--artifact_dir", dest="artifact_dir", help="Artifact Directory", required=True)

	parsed_args = parser.parse_args()
	cloud_provider = parsed_args.cloud_provider
	artifact_dir = parsed_args.artifact_dir
	validate_sentinel_hcl(cloud_provider, artifact_dir)
	utilities.print_notification("Sentinel HCL file validation completed")
