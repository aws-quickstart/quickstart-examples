#!/usr/bin/env python
import sys
import argparse
from typing import DefaultDict
import yaml
from yaml.error import YAMLError

parser = argparse.ArgumentParser()

parser.add_argument("path", nargs='?', default="templates/linux-bastion.template", help="Provide a path to the template file", type=str)
parser.add_argument("outPath", nargs='?', default="temp/py_manifest.yaml", help="Provide a destination path for the output file", type=str)
parser.add_argument("-v", "--verboseManifest", help="Include help comments in the manifest", action="store_true")
args = parser.parse_args()
# print(args.path)
# print(args.verboseManifest)

class CtParameter(yaml.YAMLObject):
    yaml_tag = u'!Parameters'
    def __init__(self, name):
        self.name = name
        pass
    def method(self, arg):
        return True

try:
    yaml.add_multi_constructor('!', lambda loader, suffix, node: None)
    # Read Yaml file
    cfn = yaml.full_load(open(args.path, 'r'))
    # Container for each parameter object
    parameters = []
    # Get data for each parameter
    for n in cfn['Parameters']:
        ctParm = CtParameter(n)
        #ctParm.name = n
        for i in cfn['Parameters'][n]:
            setattr(ctParm, i, cfn['Parameters'][n][i])
        # Append the parameter data to the list
        parameters.append(ctParm)

    # Create the manifest file and write the document
    m = open(args.outPath, "w+")
    m.write("---\n")
    m.write("region: [The region where Customization for Control Tower is deployed]\n")
    m.write("version: 2021-03-15\n")
    m.write("resources:\n")
    m.write("  - name: [The name for this deployment]\n")
    m.write("    description: " + cfn['Description'] + "\n")
    m.write("    resource_file: [The s3 path where the template is located.]\n")
    m.write("    parameters:\n")

    parameters.sort(key=lambda x: x.name)
    for p in parameters:
        if args.verboseManifest:
            if hasattr(p,"Description"):
                m.write("      # Description: " + p.Description + "\n")
            if hasattr(p,"AllowedPattern"):
                m.write("      # AllowedPattern: " + p.AllowedPattern + "\n")
            if hasattr(p,"AllowedValues"):
                m.write("      # AllowedValues: " + ' '.join(str(v) for v in p.AllowedValues) + "\n")
            if hasattr(p,"ConstraintDescription"):
                m.write("      # ConstraintDescription: " + p.ConstraintDescription + "\n")
            if hasattr(p,"MaxLength"):
                m.write("      # MaxLength: " + p.MaxLength + "\n")
            if hasattr(p,"MaxValue"):
                m.write("      # MaxValue: " + p.MaxValue + "\n")
            if hasattr(p,"MinLength"):
                m.write("      # MinLength: " + p.MinLength + "\n")
            if hasattr(p,"MinValue"):
                m.write("      # MinValue: " + p.MinValue + "\n")
            if hasattr(p,"NoEcho"):
                m.write("      # NoEcho: " + p.NoEcho + "\n")
            if hasattr(p,"Type"):
                m.write("      # Type: " + p.Type + "\n")
        m.write("      - parameter_key: " + p.name + "\n")
        if hasattr(p,"Default"):
                m.write("        parameter_value: " + str(p.Default) + "\n")
        else:
            m.write("        parameter_value: \n")
    m.write("    deploy_method: stack_set\n")
    m.write("    deployment_targets:\n")
    m.write("      organizational_units:\n")
    m.write("        - [Enter your Organizational Unit]\n")
    m.write("    regions:\n")
    m.write("      - [The region where you wish to deploy this workload]\n")


except YAMLError as exc:
    print(exc)
