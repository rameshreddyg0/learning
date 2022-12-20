import argparse
import constant
import json
import os
import requests
import sys
import subprocess
import utilities

"""
Class Name        : TerraformApply
Class Description : This class runs terraform apply command
"""
class TerraformApply:
    """
    Method Name        : __init__
    Method Description : Initializes the PolicySetDeployment object with cloud provider, deployment properties, branch on which the object is invoked 
                         and validate if deployment has to proceed
    Method Arguments   : self : Object of the class on which this method is invoked
    """
    def __init__(self, cloud_provider, policy_type, apply_through_api, artifact_dir):
        self.cloud_provider = cloud_provider
        self.policy_type = policy_type
        self.apply_through_api = apply_through_api
        self.artifact_dir = artifact_dir
        if apply_through_api:
            self.tfe_api_token = os.environ['TOKEN']
            self.content_type = "application/vnd.api+json"
            self.run_id = os.environ['run-idUrl'].split("runs/")[1].strip()
        
    """
    Method Name :        apply
    Method Description : Changes the directory to the path specified and runs terraform apply
    Method Returns :     None
    """
    def apply(self):
        if not self.apply_through_api:
            os.chdir("../{cloud_provider}/{policy_type}/".format(cloud_provider = self.cloud_provider, policy_type = self.policy_type))
            terraform_apply_command_list = ['terraform', 'apply', '-auto-approve', '-no-color']
            p1 = subprocess.run(terraform_apply_command_list, capture_output=True)

            if(p1.returncode ==0):
                utilities.print_success(p1.stdout.decode())
                os.chdir("../../scripts")
                self.apply_result = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+constant.APPLY_RESULT_HTML, 'w')
                self.apply_result.write(utilities.construct_html_success("Terraform Apply Succeeded", p1.stdout.decode()))
                self.apply_result.close()
            else:
                os.chdir("../../scripts")
                utilities.print_error("Terraform Apply Failed for {cloud_provider}-{policy_type}".format(cloud_provider = self.cloud_provider, policy_type=self.policy_type))
                utilities.print_error(p1.stdout.decode())
                utilities.print_error(p1.stderr.decode())
                self.apply_result = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+constant.APPLY_RESULT_HTML, 'w')
                self.apply_result.write(utilities.construct_html_error("Terraform Apply Failed for {cloud_provider}-{policy_type}".format(cloud_provider = self.cloud_provider, policy_type=self.policy_type), p1.stdout.decode(), p1.stderr.decode()))
                self.apply_result.close()
                sys.exit(1)
        else:
            uri = 'https://app.terraform.io/api/v2/organizations/aexp/workspaces/gcp-native-control'
            session = requests.Session()
            utilities.set_api_token(session, self.tfe_api_token)
            utilities.set_content_type(session, self.content_type)

            response = session.get(uri)
            utilities.print_notification(response)
            response_json = json.loads(response.text)
            utilities.print_notification(response_json)
            run_id = response_json["data"]["relationships"]["current-run"]["data"]["id"]
            utilities.print_notification(run_id)  

            if response.status_code == 200:
                utilities.print_success("Successfully Accssesed TFE Workspace")
            elif response.status_code == 404:
                utilities.print_error("TFE Response Failure: Organization not found, or user unauthorized to perform action")
                os.chdir("../../scripts")
                error_message = "Failed to Open {0}. Please make sure JSON is well formed".format(self.deployment_properties_json_file)
                self.apply_result = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+constant.APPLY_RESULT_HTML, 'w')
                self.apply_result.write(utilities.construct_html_message_error(error_message))
                self.apply_result.close()
                if not(response_json[constant.ERRORS] is None):
                    for error in response_json[constant.ERRORS]:
                        utilities.print_error(constant.ERROR_SUMMARY+error[constant.TITLE])
                        utilities.print_error(constant.ERROR_DETAIL+error[constant.DETAIL])
                sys.exit(1)
            else:
                utilities.print_error(constant.UNKNOWN_ERROR)
                if not(response_json[constant.ERRORS] is None):
                    for error in response_json[constant.ERRORS]:
                        utilities.print_error(constant.ERROR_SUMMARY+error[constant.TITLE])
                        utilities.print_error(constant.ERROR_DETAIL+error[constant.DETAIL])
                sys.exit(1)

            uri_apply = 'https://app.terraform.io/api/v2/runs/{runId}/actions/apply'.format(runId = self.run_id)
            session_apply = requests.Session()
            utilities.set_api_token(session_apply, self.tfe_api_token)
            utilities.set_content_type(session_apply, self.content_type)

            response_apply = session_apply.post(uri_apply)
            utilities.print_notification(response_apply)
            response_apply_json = json.loads(response_apply.text)
            utilities.print_notification(response_apply_json)

            if response_apply.status_code == 200:
                utilities.print_success("Successfully Retreived Apply Response")
            elif response_apply.status_code == 404:
                utilities.print_error(constant.TF_APPLY_RESPONSE_FAILURE)
                # if not (response_apply_json[constant.ERRORS] is None):
                #     for error in response_apply_json[constant.ERRORS]:
                #         utilities.print_error(constant.ERROR_DETAIL+error[constant.TITLE])
                sys.exit(1)
            elif response_apply.status_code == 409:
                utilities.print_error(constant.TF_APPLY_RESPONSE_FAILURE)
                if not (response_apply_json[constant.ERRORS] is None):
                    for error in response_apply_json[constant.ERRORS]:
                        utilities.print_error(constant.ERROR_SUMMARY+error[constant.TITLE])
                #sys.exit(1)           
            else:
                utilities.print_error(constant.UNKNOWN_ERROR)
                if not (response_apply_json[constant.ERRORS is None]):
                    for error in response_apply_json[constant.ERRORS]:
                        utilities.print_error(constant.ERROR_SUMMARY+error[constant.TITLE])
                #sys.exit(1)
            
            uri_apply_logs = 'https://app.terraform.io/api/v2/runs/{runId}/apply'.format(runId = self.run_id) 
            session_apply_logs = requests.Session()
            utilities.set_api_token(session_apply_logs, self.tfe_api_token)
            response_apply_logs = session_apply_logs.get(uri_apply_logs)
            print(response_apply_logs)
            response_apply_logs_json = json.loadds(response_apply_logs.text)
            print(response_apply_logs_json)

            if response_apply_logs.status_code == 200:
                utilities.print_success("Successfully Retreived Terraform Apply Logs")
            elif response_apply_logs.status_code == 404:
                utilities.print_error(constant.TF_APPLY_RESPONSE_FAILURE)
                if not (response_apply_logs_json[constant.ERRORS] is None):
                    for error in response_apply_logs_json[constant.ERRORS]:
                        utilities.print_error(constant.ERROR_SUMMARY+error[constant.TITLE])
                sys.exit(1)
            else:
                utilities.print_error(constant.UNKNOWN_ERROR)
                if not (response_apply_logs_json[constant.ERRORS] is None):
                    for error in response_apply_logs_json[constant.ERRORS]:
                        utilities.print_error(constant.ERROR_SUMMARY+error[constant.TITLE])
                sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply Terraform Changes')

    parser.add_argument("--policyType", dest="policy_type", help="Policy Type", required=True)
    parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required=True)
    parser.add_argument("--artifact_dir", dest="artifact_dir", help="Artifact Directory", required=True)

    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider
    policy_type = parsed_args.policy_type
    artifact_dir = parsed_args.artifact_dir

    apply_through_api = False

    #Create Object
    terraform_apply = TerraformApply(cloud_provider, policy_type, apply_through_api, artifact_dir)
    #Create or Update policy Set for different Cloud Providers
    terraform_apply.apply()
