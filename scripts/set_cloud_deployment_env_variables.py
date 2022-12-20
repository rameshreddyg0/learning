#!/usr/bin/env python3

import argparse
import constant
import json
import sys

if __name__ == "main":
      parser = argparse.ArgumentParser(description="Set Cloud Deployment Variables")

      parser.add_argument("--deploymentPropertiesFile", dest="deployment_properties_file", help="Deployment property File", required=True)

      parsed_args = parser.parse_args()
      deployment_property_file = parsed_args.deployment_properties_file     
      f = open(deployment_property_file)

      data = json.load(f)

      with open('cloudpolicydeployment.properties', 'w') as file:
        file.write(f"GCP_NATIVE_DEPLOYMNET={str(data['gcp'][constant.NATIVE][constant.TRIGGER_DEPLOYMENT])}\n")
        file.write(f"GCP_PRISMA_DEPLOYMNET={str(data['gcp'][constant.PRISMA][constant.TRIGGER_DEPLOYMENT])}\n")
        file.write(f"GCP_SENTINEL_DEPLOYMNET={str(data['gcp'][constant.SENTINEL][constant.TRIGGER_DEPLOYMENT])}\n")

        #closing File
      f.close()