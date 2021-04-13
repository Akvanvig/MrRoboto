# Requires powershell 7

# Variables
$platforms = "arm64v8","amd64"
$repoDir = "C:\Git-Prosjekter\Discord-bot-py_k3s\discord-bot-py"
$username = "akvanvig"
$repository = "ghcr.io"

# Functions
$buildImage = {
  param($platform, $username, $repository)
  docker build --no-cache -t "$repository/$username/mrroboto_no-audio:$platform" -t "$repository/$username/mrroboto:$platform" -f ./docker/bot.dockerfile . --build-arg ARCH=$platform
}

# Pre-requisite tests
## Check powershell version
If ($host.Version.Major -lt 7){
  $version = $host.Version
  Write-Output "Version $version of powershell not supported, please upgrade to version 7 or later"
  Write-Output "https://docs.microsoft.com/en-us/powershell/scripting/windows-powershell/install/installing-windows-powershell?view=powershell-7.1#upgrading-existing-windows-powershell"
  exit
}


# Main
## Build and push images in separate processes
Foreach ($platform in $platforms){
  Start-Job $buildImage -WorkingDirectory $repoDir -ArgumentList $platform,$username,$repository
}

## Check if images created
While (Get-Job -State "Running") {
  $out = Get-Job
  Write-Output $out
  Start-Sleep 30
}

## Save logs to file and remove jobs
Get-Job | Foreach-Object {
  $name = $_.name
  $path = Get-Location
  Receive-Job -name $name *>&1 >> "$path\$name.log"
  Remove-Job -name $name
  Write-Output "Saved output for job $name to $path\$name.log"
}

Write-Output "----"
Write-Output "All jobs completed"

$expression = "docker manifest create $repository/$username/mrroboto:latest"
Foreach ($platform in $platforms){
  $expression = "$expression $('--amend "$repository/$username/mrroboto:$platform"')"
}

Invoke-Expression $expression
docker manifest push "$repository/$username/mrroboto:latest"
