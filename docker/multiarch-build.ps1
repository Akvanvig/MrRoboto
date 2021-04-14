# Requires powershell 7

# Variables
$platforms = "arm64v8","amd64"
$repoDir = "C:\Git-Prosjekter\Discord-bot-py_k3s\discord-bot-py"
$username = "akvanvig"
$repository = "ghcr.io"

# Functions
$buildImage = {
  param($platform, $username, $repository)
  docker build --no-cache -t "$repository/$username/mrroboto:$platform" -f ./docker/bot.dockerfile . --build-arg ARCH=$platform
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
Do {
  Start-Sleep 15
  Write-Output $out
  $completed = Get-Job -State "Completed"
  ## Save logs to file and remove jobs
  If ($completed) {
    $completed | Foreach-Object {
      $name = $_.name
      $path = Get-Location
      Receive-Job -name $name *>&1 >> "$path\$name.log"
      Remove-Job -name $name
      Write-Output "Saved output for job $name to $path\$name.log"
    }
  }
} While (Get-Job -State "Running")

## Check if any tasks failed
If ($(Get-Job).Count -ne 0) {
  Write-Output "You likely have failed jobs, check logs with:"
  $out = Get-Job
  Foreach ($job in $out) {
    Write-Output "  Receive-Job -name $($job.name)"
  }
}
Write-Output "----"
Write-Output "All jobs finished"
Write-Output "----"

$expressionA = "docker manifest create $repository/$username/mrroboto:latest"
$expressionB = "docker manifest create $repository/$username/mrroboto_no-audio:latest"
Foreach ($platform in $platforms){
  $expressionA = "$expressionA $("--amend $repository/$username/mrroboto:$platform")"
  $expressionB = "$expressionB $("--amend $repository/$username/mrroboto:$platform")"
}

Invoke-Expression $expressionA
Invoke-Expression $expressionB
docker manifest push "$repository/$username/mrroboto:latest"
docker manifest push "$repository/$username/mrroboto_no-audio:latest"
