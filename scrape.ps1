Param(
    [System.IO.DirectoryInfo]$SaveLocation = "./dump",
    [System.IO.FileInfo]$JsonInput = "./things.json"
)

$JsonInput = Resolve-Path $JsonInput | Select-Object -ExpandProperty Path
$SaveLoc = Resolve-Path $SaveLocation | Select-Object -ExpandProperty Path
$things = Get-Content $JsonInput | ConvertFrom-Json
$things |
    ForEach-Object -Parallel {
        Invoke-WebRequest -Uri $_.Url -SessionVariable Session | Out-Null
        $OutDir = Join-Path $using:SaveLoc ("$($_.number) - $($_.title)" -replace ":", ' - ' -replace '(/|\\|\.|\?|!|<|>|"|\||*)', '')
        New-Item -Path $OutDir -ItemType Directory -Force | Out-Null
        for($i = 0; $i -lt $_.images.count; $i++) {
            Write-Host "Fetching gallery $($_.title) image $($i + 1)"
            Invoke-WebRequest -Uri $_.images[$i] -OutFile (Join-Path $OutDir "$($i + 1).jpg") -Headers @{Referer = $_.Url}
        }
    }
