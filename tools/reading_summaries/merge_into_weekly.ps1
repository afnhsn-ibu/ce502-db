# Insert reading-summary slides into a CE 502 weekly deck's "Papers to Read" section.
#
#   powershell -File merge_into_weekly.ps1 -Weekly <weekly.pptx> -Summary <paper-slides.pptx> -After <slideNo>
#
# Normally called by run_week.py. The section footers already in the deck ("k / old") are
# renumbered to the new total and their progress bars resized. Saving keeps the deck's
# embedded fonts. Adapted from the DS 501 script.
param([string]$Weekly, [string]$Summary, [int]$After)
$ErrorActionPreference = 'Stop'

$Weekly = (Resolve-Path $Weekly).Path
$Summary = (Resolve-Path $Summary).Path
$ppt = New-Object -ComObject PowerPoint.Application
$p = $ppt.Presentations.Open($Weekly, $false, $false, $false)
try {
  function Get-Counter($slide) {
    foreach ($sh in $slide.Shapes) {
      if ($sh.HasTextFrame -and $sh.TextFrame.TextRange.Text -match '^\s*(\d+) / (\d+)\s*$') { return $sh }
    }
    return $null
  }

  $c = Get-Counter $p.Slides.Item($After)
  $null = $c.TextFrame.TextRange.Text -match '(\d+) / (\d+)'
  $oldTotal = [int]$Matches[2]
  $first = $After - [int]$Matches[1] + 1          # first slide of the section (the divider)
  $oldLast = $first + $oldTotal - 1

  $before = $p.Slides.Count
  $null = $p.Slides.InsertFromFile($Summary, $After)
  $added = $p.Slides.Count - $before
  $newTotal = $oldTotal + $added
  $newLast = $oldLast + $added

  $accent = 0xB5 + 0x49 * 256 + 0x1A * 65536      # B5491A as an Office BGR integer
  $slideW = $p.PageSetup.SlideWidth
  foreach ($i in @($first..$After) + @(($After + $added + 1)..$newLast)) {
    $sl = $p.Slides.Item($i)
    $c = Get-Counter $sl
    if ($c -eq $null) { continue }
    $null = $c.TextFrame.TextRange.Text -match '(\d+) / (\d+)'
    $k = [int]$Matches[1]
    if ($i -gt $After) { $k += $added }
    $c.TextFrame.TextRange.Text = "$k / $newTotal"
    foreach ($sh in $sl.Shapes) {
      if ($sh.Top -gt 530 -and $sh.Height -lt 8 -and $sh.Fill.ForeColor.RGB -eq $accent) { $sh.Width = $slideW * $k / $newTotal }
    }
  }
  $p.Save()
  "Inserted $added slides after slide $After; the section is now $newTotal slides (slides $first-$newLast)."
} finally {
  $p.Close()
  $ppt.Quit()
}
