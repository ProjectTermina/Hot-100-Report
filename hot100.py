import billboard
import itertools
from datetime import date
from datetime import timedelta
import datetime

'''
{rank} = entry.rank
{artist} = entry.artist
{title} = entry.title
{weeks} = entry.weeks
{peak} = entry.peakPos
{lastPos} = entry.lastPos
{plural} = "s" if entry.weeks > 1 else ""
{delta} = -1*delta
'''

chartString = 'The [i]Billboard[/i] Hot 100 chart dated {chartDate} was released on {releaseDate}. This chart tracks United States airplay, sales, and streaming beginning on {startDate} and ending on {endDate}.\n'

topCount = 20
topHeader = 'These songs are in the top {topCount} this week:[list=1]'.format(topCount=topCount)
entryString = '[*][b]{artist}[/b] - "{title}", {weeks} week{plural} on chart, peaked at #{peak}'
topFooter = '[/list]\n'

newEntryHeader = 'These songs made their debut on the Hot 100 this week:[list]'
newEntryString = '[*][b]{artist}[/b] - "{title}" entered the chart for the first time at #{peak}.'
newEntryFooter = '[/list]\n'

reEntryHeader = 'These songs re-entered the chart this week:[list]'
reEntryString = '[*][b]{artist}[/b] - "{title}" re-entered the chart this week at #{rank}. It has spent {weeks} weeks on the chart, peaking at #{peak}.'
reEntryFooter = '[/list]\n'

unchartedHeader = 'These songs left the chart this week:[list]'
unchartedString = '[*][b]{artist}[/b] - "{title}" left the chart after {weeks} weeks. It peaked at #{peak} and its position last week was #{lastPos}.'
unchartedStringAtPeak = '[*][b]{artist}[/b] - "{title}" left the chart after {weeks} weeks from its peak position at #{peak}.'
unchartedStringOneWeek = '[*][b]{artist}[/b] - "{title}" left the chart after {weeks} week at #{peak}.'
unchartedFooter = '[/list]\n'

bigMovesHeader = 'These songs made big moves:[list]'
upString = '[*][b]{artist}[/b] - "{title}" rose {delta} spots from #{lastPos} to #{rank}. It has spent {weeks} weeks on the chart, peaking at #{peak}.'
downString = '[*][b]{artist}[/b] - "{title}" fell {delta} spots from #{lastPos} to #{rank}. It has spent {weeks} weeks on the chart, peaking at #{peak}.'
upStringCurrentlyPeaking = '[*][b]{artist}[/b] - "{title}" rose {delta} spots from #{lastPos} to #{rank}, its all-time peak. It has spent {weeks} weeks on the chart.'
downStringWasPeaking = '[*][b]{artist}[/b] - "{title}" fell {delta} spots to #{rank} from its all-time peak at #{lastPos}. It has spent {weeks} weeks on the chart.'
bigMovesFooter = '[/list]\n'

def getUnchartedEntries(previousChart: billboard.ChartData, thisChart: billboard.ChartData):
	'''
	Gets entries of previousChart which are not on thisChart.

	Arguments:
	previousChart -- a billboard.ChartData object representing the previous chart.
	thisChart -- a billboard.ChartData object representing the current chart.

	Return value:
	A list containing all billboard.ChartEntry objects from previousChart which are
	not present in thisChart.
	'''
	return [entry for entry in previousChart if (entry.title, entry.artist) not in
		[(entry.title, entry.artist) for entry in thisChart]
		]

def getNewEntries(chart: billboard.ChartData):
	'''
	Gets chart entries which are entering the chart for the first time.

	Arguments:
	chart -- a billboard.ChartData object.

	Return value:
	A list containing all chart entry objects for which the isNew property is true.
	'''
	return [entry for entry in chart if entry.isNew]

def getReEntries(previousChart: billboard.ChartData, thisChart: billboard.ChartData):
	'''
	Gets chart entries which are re-entering the chart.

	Arguments:
	previousChart -- a billboard.ChartData object representing the previous chart.
	thisChart -- a billboard.ChartData object representing the current chart.

	Return value:
	A list containing all billboard.ChartEntry objects from thisChart which are not
	present in previousChart, and have isNew=false.
	'''
	return [entry for entry in thisChart if (entry.title, entry.artist) not in
		[(entry.title, entry.artist) for entry in previousChart]
		and not entry.isNew
		]

def getUpwardsMoves(chart: billboard.ChartData):
	'''
	Gets chart entries which ranked much higher this week than last.

	Arguments:
	chart -- a billboard.ChartData object.

	Return value:
	A list of 2-tuples containing the chart entry object, followed by how much its
	rank increased. A positive value indicates a "higher" ranking, closer to #1.
	'''
	return [(entry,entry.lastPos-entry.rank) for entry in chart
		if entry.lastPos != 0
		and (
			(entry.rank+10 <= entry.lastPos and entry.rank <= 50)
			or (entry.rank+20 <= entry.lastPos)
			)
		]

def getDownwardsMoves(chart: billboard.ChartData):
	'''
	Gets chart entries which ranked much lower this week than last.

	Arguments:
	chart -- a billboard.ChartData object.

	Return value:
	A list of 2-tuples containing the chart entry object, followed by how much its
	rank decreased. A negative value indicates a "lower" ranking, farther from #1.
	'''
	return [(entry,entry.lastPos-entry.rank) for entry in chart
		if entry.lastPos != 0
		and ( 
			(entry.rank >= entry.lastPos+10 and entry.rank <= 50)
			or (entry.rank >= entry.lastPos+20)
			)
		]

def getBigMoves(chart: billboard.ChartData):
	'''
	Gets chart entries which ranked much higher or lower this week than last.

	Arguments:
	chart -- a billboard.ChartData object.

	Return value:
	A list of 2-tuples containing the chart entry object, followed by how much its
	rank changed. A positive value indicates a "higher" ranking, closer to #1. A
	negative value indicates a "lower" ranking, farther away from #1.
	'''
	return sorted(
		getUpwardsMoves(chart) + getDownwardsMoves(chart),
		key=lambda entryAndDelta: entryAndDelta[0].rank
		)

def analyze(date: datetime.date):
	'''
	Prints an analysis of the Billboard Hot 100 chart for the provided date.

	Arguments:
	date -- a date object whose chart to analyze.
	'''
	thisChart = billboard.ChartData('hot-100', date=date.strftime("%Y-%m-%d"))
	lastChart = billboard.ChartData('hot-100', date=(date - timedelta(days=7)).strftime("%Y-%m-%d"))

	chartDate = datetime.datetime.strptime(thisChart.date, "%Y-%m-%d")
	releaseDate = chartDate - timedelta(days=4)
	startDate = chartDate - timedelta(days=15)
	endDate = chartDate - timedelta(days=9)

	# %e is system-dependent -- replace with %d if needed
	print(chartString.format(
		chartDate=chartDate.strftime('%A, %B %e, %Y').replace("  "," "),
		releaseDate=releaseDate.strftime('%A, %B %e, %Y').replace("  "," "),
		startDate=startDate.strftime('%A, %B %e, %Y').replace("  "," "),
		endDate=endDate.strftime('%A, %B %e, %Y').replace("  "," ")
		))

	print(topHeader)
	for entry in thisChart[:topCount]:
		print(entryString.format(
			rank=entry.rank,
			artist=entry.artist,
			title=entry.title,
			weeks=entry.weeks,
			peak=entry.peakPos,
			lastPos=entry.rank,
			plural="s" if entry.weeks > 1 else ""))
	print(topFooter)

	print(unchartedHeader)
	for entry in getUnchartedEntries(previousChart=lastChart, thisChart=thisChart):
		announceString = None
		if (entry.weeks == 1):
			announceString = unchartedStringOneWeek
		elif (entry.rank == entry.peakPos):
			announceString = unchartedStringAtPeak
		else:
			announceString = unchartedString
		print(announceString.format(
			rank=entry.rank,
			artist=entry.artist,
			title=entry.title,
			weeks=entry.weeks,
			peak=entry.peakPos,
			lastPos=entry.rank,
			))
	print(unchartedFooter)
	
	print(newEntryHeader)
	for entry in getNewEntries(thisChart):
		print(newEntryString.format(
			rank=entry.rank,
			artist=entry.artist,
			title=entry.title,
			weeks=entry.weeks,
			peak=entry.peakPos,
			lastPos=entry.lastPos,
			plural="s" if entry.weeks > 1 else ""))
	print(newEntryFooter)
	
	print(reEntryHeader)
	for entry in getReEntries(lastChart, thisChart):
		print(reEntryString.format(
			rank=entry.rank,
			artist=entry.artist,
			title=entry.title,
			weeks=entry.weeks,
			peak=entry.peakPos,
			lastPos=entry.lastPos,
			plural="s" if entry.weeks > 1 else ""))
	print(reEntryFooter)

	print(bigMovesHeader)
	for entry,delta in getBigMoves(thisChart):
		announceString = None
		if delta > 0 and entry.rank == entry.peakPos:
			announceString = upStringCurrentlyPeaking
		elif delta > 0:
			announceString = upString
		elif delta < 0 and entry.lastPos == entry.peakPos:
			announceString = downStringWasPeaking
		elif delta < 0:
			announceString = downString
		print(announceString.format(
			rank=entry.rank,
			artist=entry.artist,
			title=entry.title,
			weeks=entry.weeks,
			peak=entry.peakPos,
			lastPos=entry.lastPos,
			delta=abs(delta)))
	print(bigMovesFooter)

analyze(date.today())
