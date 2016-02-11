# text2datetime
Python module to convert relative or absolute text to datetime, like "+12h" to 12 hours in future.

This is provided by the function text2datetime.text2datetime


Date should be in one of the following forms:

 - *Relative Modifiers*

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

		"today"         - Beginning of today (00:00:00)
		"today end"     - End of today (23:59:59)
		"tomorrow"      - Beginning of tomorrow
		"tomorrow end"  - End of tomorrow
		"yesterday"     - Beginning of yesterday
		"yesterday end" - End of yesterday

  - *ctime format*

   Ctime format with optional day of week

		3-letter-day) [3-letter-month] [2-digit date] [2-hour]:[2-minute]:[2-second] [4-digit Year]

     Example: Wed Jan 28 12:28:13 2015

  - *American Slash Format*

	numeric Month/Date/Year with optional time as hour:minute or hour:minute:second. Clock is a 24-hour clock, 00=midnight, unless "PM" or "AM" is at the end.

    e.x.: 1/28/2015   or  1/28/2015  12:28:13

  - *Time Only*

	time as hour:minute or hour:minute:second will use current date. Clock is a 24 hour clock, 00=midnight, unless "PM" or "AM" is at the end.

NOTES:

	Unless AM/PM is specified in formats that support it, hours are in 23-hour clock format, starting with 00=midnight, 23 = 11PM



