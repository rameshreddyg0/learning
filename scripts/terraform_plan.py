import argparse
import os
import sys
import subprocess
import utilities

"""
Class Name :        class TerraformPlan
Class Description : This class has implementation to run terraform plan
Class Methods :     __init__ : Initializes the path and parameters required for terraform plan
"""
class TerraformPlan:
    """
    Method Name :        __init__
    Method Description : Initializes the path and parameters required for terraform plan execution
    Method Returns :     None
    """
    def __init__(self, cloud_provider, policy_type, artifact_dir):
        self.cloud_provider = cloud_provider
        self.artifact_dir = artifact_dir
        self.policy_type = policy_type

    """
    Method Name :        plan
    Method Description : Changes the directory to the path specified and runs terraform plan
    Method Returns :     None
    """
    def plan(self):
        os.chdir("../{cloud_provider}/{policyType}/".format(cloud_provider = self.cloud_provider, policyType=self.policy_type))
        terraform_plan_command_list = ["terraform", "plan", "-no-color"]
        p1 = subprocess.run(terraform_plan_command_list, capture_output=True)

        if(p1.returncode == 0):
            utilities.print_success(p1.stdout.decode())
            utilities.print_success("Terraform Plan Success")
            os.chdir("../../scripts")
            self.plan_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Terraform_Plan_Results.html", 'w')
            self.plan_check.write(utilities.construct_html_success("Terraform Plan Succeeded", p1.stdout.decode()))
            self.plan_check.close()
        else:
            utilities.print_error("Terraform Plan Failed for {cloud_provider}-{policyType}".format(cloud_provider = self.cloud_provider, policyType = self.policy_type))
            utilities.print_error(p1.stdout.decode())
            utilities.print_error("Error Message")
            utilities.print_error(p1.stderr.decode())
            utilities.print_error(p1.returncode)
            os.chdir("../../scripts")
            self.init_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Terraform_Plan_Results.html", 'w')
            self.init_check.write(utilities.construct_html_error("Terraform Plan Failed", p1.stdout.decode(), p1.stderr.decode()))
            self.init_check.close()
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Terraform Plan")


    parser.add_argument("--policyType", dest="policy_type", help="Policy Type", required=False)
    parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required=True)
    parser.add_argument("--artifact_dir", dest="artifact_dir", help="Artifact Directory", required=True)

    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider
    artifact_dir = parsed_args.artifact_dir
    policy_type = parsed_args.policy_type

    #Create Object
    terraform_plan = TerraformPlan(cloud_provider, policy_type, artifact_dir)
    terraform_plan.plan()