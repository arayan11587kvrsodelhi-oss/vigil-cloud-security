$cssPath = Get-ChildItem "dist\assets\index-*.css" | Select-Object -First 1 -ExpandProperty FullName
Write-Host "Scanning: $cssPath"
$css = Get-Content $cssPath -Raw
$hexes = [regex]::Matches($css, '#[0-9a-fA-F]{6}') | ForEach-Object { $_.Value } | Sort-Object -Unique
$blue = @()
foreach ($h in $hexes) {
  $r = [Convert]::ToInt32($h.Substring(1, 2), 16)
  $g = [Convert]::ToInt32($h.Substring(3, 2), 16)
  $b = [Convert]::ToInt32($h.Substring(5, 2), 16)
  # Blue-dominant and clearly saturated toward blue/cyan (not purple/pink/gray)
  if ($b -gt $r -and $b -gt $g -and ($b - $r) -gt 40) { $blue += "$h (r=$r g=$g b=$b)" }
}
if ($blue.Count -eq 0) { Write-Host "PASS: no blue/cyan dominant hex colors in built CSS." } else { Write-Host "FOUND BLUE:"; $blue | ForEach-Object { Write-Host "  $_" } }

# rgba scan
$rgba = [regex]::Matches($css, 'rgba\(\s*(\d+),\s*(\d+),\s*(\d+)') | ForEach-Object { $_.Value } | Sort-Object -Unique
$blueRgba = @()
foreach ($c in $rgba) {
  $m = [regex]::Match($c, 'rgba\(\s*(\d+),\s*(\d+),\s*(\d+)')
  $r = [int]$m.Groups[1].Value; $g = [int]$m.Groups[2].Value; $b = [int]$m.Groups[3].Value
  if ($b -gt $r -and $b -gt $g -and ($b - $r) -gt 40) { $blueRgba += "$c (r=$r g=$g b=$b)" }
}
if ($blueRgba.Count -eq 0) { Write-Host "PASS: no blue/cyan dominant rgba in built CSS." } else { Write-Host "FOUND BLUE RGBA:"; $blueRgba | ForEach-Object { Write-Host "  $_" } }
