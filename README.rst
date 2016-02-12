text2datetime
=============
Python module which can convert an extensive number of ways to represent time with strings to datetime objects

Some examples include:

"Tomorrow 5:00AM" - for tomorrow at 5am

"+3yr +2d" - For three years and two days in future

"-5mo 16:00" - For 5 months ago at 16:00 hours (4PM)

"1/8/2015" - Depending on monthBeforeDate flag, could be Jan 8th or August 1st, 2015.



The primary function which supports converting all of these various texts is *text2datetime.text2datetime*

**text2datetime method**


	def text2datetime(timeStr, now=None, monthBeforeDay=True):


timeStr - The text to convert to a datetime.datetime object

now - Defaults to now, but you can calculate relative to a different date if you provide a datetime.datetime here

monthBeforeDay - For relevant formats, True will have the expected format be month-before-day (American format), False will have day before month (European format).


**Other Methods**

While text2datetime supports interpreting all known forms of date and time strings, there are individual public methods for each form you may also use.

See http://htmlpreview.github.io/?https://github.com/kata198/text2datetime/blob/master/doc/text2datetime.html for pydoc of all methods.


Supported Formats
-----------------


Date should be in one of the following forms:

 -  *Relative Modifiers*

	Relative modifiers represent a delta from current time, current date.


	Each modifier starts with a direction (+ or -), then a number, then a unit.


	Example:  +3d  means '3 days from this very second'


	Available modifiers:


		y   = years

		yr  = years

		mo  = months

		d   = days

		h   = hours

		m   = minutes

		s   = seconds


	You may use relative modifiers and have a final entry be a fixed time,

	for example "+3d 12:00:00" would be noon three days from now.


 - *Fixed String*

	One of the following fixed strings:


		"now"           - Right now (to the second)

		"today"         - Beginning of today (00:00:00)

		"tomorrow"      - Beginning of tomorrow

		"yesterday"     - Beginning of yesterday


	Can optionally be followed with a time, as hour:minute or hour:minute:second, otherwise midnight (00:00:00) is used. Clock is 24-hour clock, 00=midnight, unless "PM" or "AM" is at the end.


	Example: "tomorrow 5:00PM"


 - *ctime format*


	Ctime format with optional day of week


		(3-letter-day) [3-letter-month] [2-digit date] [2-hour]:[2-minute]:[2-second] [4-digit Year]


	Example: Wed Jan 28 12:28:13 2015


 - *American Date Format*


	numeric Month/Day/Year with optional time as hour:minute or hour:minute:second. Clock is a 24-hour clock, 00=midnight, unless "PM" or "AM" is at the end.


	e.x.: 1/28/2015   or  1/28/2015  12:28:13


	This is used when monthBeforeDay=True (default) in text2datetime, getDatetimeFromDateStr when monthBeforeDay=True, and getDatetimeFromAmericanTime


 - *European Date Format*


	numeric Day/Month/Year with optional time as hour:minute or hour:minute:second. Clock is a 24-hour clock, 00=midnight, unless "PM" or "AM" is at the end.


	e.x.: 28/1/2015   or  28/1/2015  12:28:13


	This is used when monthBeforeDay=False in text2datetime, getDatetimeFromDateStr when monthBeforeDay=False, and getDatetimeFromEuropeanTime


 - *Time Only*


	time as hour:minute or hour:minute:second will use current date. Clock is a 24 hour clock, 00=midnight, unless "PM" or "AM" is at the end.


**NOTES:**


	Unless AM/PM is specified in formats that support it, hours are in 24-hour clock format, starting with 00=midnight, 23 = 11PM



