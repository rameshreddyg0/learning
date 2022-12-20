import argparse
import constant
import os
import sys
import subprocess
import utilities

"""
Class Name :        class TerraformInitialize
Class Description : This class has implementation to initialize terraform at the given path with the passed initialization parameters
Class Methods :     __init__ : Initializes the path and parameters required for terraform initialization
            
"""
class TerraformInitialize:
    """
    Method Name :        __init__
    Method Description : Initializes the path and parameters required for terraform initialization
    Method Returns :     None
    
    """
    def __init__(self, cloud_provider, policy_type, artifact_dir, backend_file_path):
        self.cloud_provider = cloud_provider
        self.policy_type = policy_type
        self.artifact_dir = artifact_dir
        self.backend_file_path = backend_file_path

    """
    Method Name :        initialize
    Method Description : Changes the directory to the path specified and runs terraform init
    Method Returns :     None
    """
    def initialize(self):
        os.chdir("../{cloud_provider}/{policy_type}/".format(cloud_provider = self.cloud_provider, policy_type=self.policy_type))
        # os.environ['https_proxy'] = constant.HTTP_PROXY
        # os.environ['http_proxy'] = constant.HTTP_PROXY
        # os.environ['http_proxy'] = constant.NO_PROXY
        terraform_provider_cmd = ["terraform","providers"]
        p = subprocess.run(terraform_provider_cmd,capture_output=True)
        print(p.returncode)
        terraform_init_command_list = ["terraform","init","-backend-config=./{backend_file_path}/workspace.tfbackend".format(backend_file_path=self.backend_file_path),"-reconfigure", "-no-color"]
        p1 = subprocess.run(terraform_init_command_list, capture_output=True)

        if(p1.returncode == 0):
            utilities.print_success("Terraform Init Success")
            utilities.print_success(p1.stdout.decode())
            os.chdir("../../scripts")
            self.init_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Terraform_Init_Results.html", 'w')
            self.init_check.write(utilities.construct_html_success("Terraform Init Succeeded", p1.stdout.decode()))
            self.init_check.close()
        else:
            utilities.print_error("Terraform Init Failed")
            utilities.print_error(p1.returncode)
            utilities.print_error(p1.stderr.decode())
            utilities.print_error(p1.stdout.decode())
            os.chdir("../../scripts")
            self.init_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Terraform_Init_Results.html", 'w')
            self.init_check.write(utilities.construct_html_error("Terraform Init Failed", p1.stdout.decode(), p1.stderr.decode()))
            self.init_check.close()
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initializes Terraform")
    
    parser.add_argument("--policyType", dest="policy_type", help="Policy Type", required=False)
    parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required=True)
    parser.add_argument("--branch", dest="branch", help="Branch", required=True)
    parser.add_argument("--artifact_dir", dest="artifact_dir", help="Artifact Directory", required=True)

    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider
    policy_type = parsed_args.policy_type
    artifact_dir = parsed_args.artifact_dir

    branch = parsed_args.branch
    backend_file_path = "dev"
    if branch == "main":
        backend_file_path = "prod"

    #Create Object
    terraform_init = TerraformInitialize(cloud_provider, policy_type, artifact_dir, backend_file_path)
    terraform_init.initialize()