Param([switch]$Dim)
$monitor = Get-WmiObject -ns root/wmi -class wmiMonitorBrightNessMethods
if ($Dim) {
	$monitor.WmiSetBrightness(1,0)
}
else {
	$monitor.WmiSetBrightness(1,70)
}
