#! /usr/local/bin/pwsh
[CmdletBinding()]
param (
    # This is the s3 path to the template file we will reference in the manifest file
    [Parameter()]
    [string]
    $templatePath = "templates/linux-bastion.template",
    [Parameter()]
    [string]
    $manifestPath = "temp/ps_manifest.yaml",
    [Parameter()]
    [string]
    $verboseManifest = $true
)
import-module powershell-yaml

# Read Yaml file
$cfn = Get-Content $templatePath | ConvertFrom-Yaml

class cfnParameter {
    [String]$pname
    [String]$default
    [String]$type
    [String]$description
    [String]$allowedValues
    [String]$allowedPattern
    [String]$constraintDescription
}
$parms = @()
foreach ($key in $cfn.Parameters.keys) {
    $ctParm = New-Object cfnParameter
    $ctParm.pname = $key
    $ctParm.default = $cfn.Parameters[$key].default
    $ctParm.type = $cfn.Parameters[$key].type
    $ctParm.description = $cfn.Parameters[$key].description
    $ctParm.allowedValues = $cfn.Parameters[$key].allowedValues
    $ctParm.allowedPattern = $cfn.Parameters[$key].allowedPattern
    $ctParm.ConstraintDescription = $cfn.Parameters[$key].ConstraintDescription
    $parms += $ctParm
}
#$parms
$manifestPath= '../temp/ps_manifest.yaml'
Set-Content -Path $manifestPath -Value '---'
#Add-Content -Path temp/manifest.yaml -Value '---'
Add-Content -Path $manifestPath -Value 'region: [The region where Customization for Control Tower is deployed]'
Add-Content -Path $manifestPath -Value 'version: 2021-03-15'
Add-Content -Path $manifestPath -Value 'resources:'
Add-Content -Path $manifestPath -Value '  - name: [The name for this deployment]'
Add-Content -Path $manifestPath -Value "    description: $($cfn.description)"
Add-Content -Path $manifestPath -Value '    resource_file: [The s3 path where the template is located.]'
Add-Content -Path $manifestPath -Value '    parameters:'
$parms = $parms | Sort-Object -Property pname
foreach ($parm in $parms) {
    if ($verboseManifest -eq $true) {
        if ($parm.description) { Add-Content -Path $manifestPath -Value "      # Description: $($parm.description)" }
        if ($parm.allowedPattern) { Add-Content -Path $manifestPath -Value "      # AllowedPattern: $($parm.allowedPattern)" }
        if ($parm.allowedValues) { Add-Content -Path $manifestPath -Value "      # AllowedValues: $($parm.allowedValues)" }
        if ($parm.constraintDescription) { Add-Content -Path $manifestPath -Value "      # ConstraintDescription: $($parm.constraintDescription)" }
        if ($parm.MaxLength) { Add-Content -Path $manifestPath -Value "      # MaxLength: $($parm.MaxLength)" }
        if ($parm.MaxValue) { Add-Content -Path $manifestPath -Value "      # MaxValue: $($parm.MaxValue)" }
        if ($parm.MinLength) { Add-Content -Path $manifestPath -Value "      # MinLength: $($parm.MinLength)" }
        if ($parm.MinValue) { Add-Content -Path $manifestPath -Value "      # MinValue: $($parm.MinValue)" }
        if ($parm.NoEcho) { Add-Content -Path $manifestPath -Value "      # NoEcho: $($parm.NoEcho)" }
        if ($parm.type) { Add-Content -Path $manifestPath -Value "      # Type: $($parm.type)" }
    }
    Add-Content -Path $manifestPath -Value "      - parameter_key: $($parm.pname)"
    Add-Content -Path $manifestPath -Value "        parameter_value: $($parm.default)"
}
Add-Content -Path $manifestPath -Value '    deploy_method: stack_set'
Add-Content -Path $manifestPath -Value '    deployment_targets: stack_set'
Add-Content -Path $manifestPath -Value '      organizational_units:'
Add-Content -Path $manifestPath -Value '        - [Enter your Organizational Unit]'
Add-Content -Path $manifestPath -Value '    regions:'
Add-Content -Path $manifestPath -Value '        - [The region where you wish to deploy this workload]'
