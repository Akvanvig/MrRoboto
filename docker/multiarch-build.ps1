# Requires powershell 7

# Variables
Param (
  [string[]]$platforms = @("arm64v8","amd64"),
  [string]$repoDir = "D:\Git-Prosjekter\Discord-bot-py_k3s\discord-bot-py",
  [string]$username = "akvanvig",
  [string]$repository = "ghcr.io"
)

# Functions
$buildImage = {
  param($platform, $username, $repository)
  $path = Get-Location
  docker build --no-cache -t "$repository/$username/mrroboto_no-audio:$platform" -f ./docker/bot.dockerfile . --build-arg ARCH=$platform *>&1 >> "$path\$repository-$platform.log"
  Write-Output "Saved output for job $platform to $path\$repository-$platform.log"
  $dict = @{platform = $platform; username = $username; repository = $repository}
  return $dict
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
$timer =  [system.diagnostics.stopwatch]::StartNew()
Foreach ($platform in $platforms){
  Start-Job $buildImage -WorkingDirectory $repoDir -ArgumentList $platform,$username,$repository
}
Write-Output ""

## Check if images created
Do {
  Start-Sleep 1
  $completed = Get-Job -State "Completed"
  ## Save logs to file and remove jobs
  If ($completed) {
    Write-Host -NoNewLine "`r"
    $completed | Foreach-Object {
      $name = $_.name
      $result = Receive-Job -name $name
      Write-Output $result[0]
      Remove-Job -name $name
      $totalSecs =  [math]::Round($timer.Elapsed.TotalSeconds,0)
      Write-Output "$($result.platform) completed in $totalSecs seconds"
      docker push "$($result.repository)/$($result.username)/mrroboto_no-audio:$($result.platform)"
      $totalSecs =  [math]::Round($timer.Elapsed.TotalSeconds,0)
      Write-Output "$($result.platform) pushed to repo in $totalSecs seconds"
      Write-Output ""
    }
  }
$totalSecs =  [math]::Round($timer.Elapsed.TotalSeconds,0)
Write-Host -NoNewLine "`rScript has been running for $totalSecs seconds"
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

docker manifest rm $repository/$username/roboto
$expression = "docker manifest create $repository/$username/roboto:latest"
Foreach ($platform in $platforms){
  $expression = "$expression $("--amend $repository/$username/mrroboto_no-audio:$platform")"
}

Invoke-Expression $expression
docker manifest push "$repository/$username/roboto:latest"

$totalSecs =  [math]::Round($timer.Elapsed.TotalSeconds,0)
Write-Output "All tasks finished $totalSecs seconds"
