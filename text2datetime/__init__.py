# Copyright (c) 2014-2016 Timothy Savannah All Rights Reserved under LGPLv2.1.
#  You should have received a copy of this with the source distribution as LICENSE.
#  If not, the current license can be found at https://github.com/kata198/text2datetime/blob/master/LICENSE
'''
    text2datetime - Convert a text string to a datetime object. Supports relative-to-now modifiers, various timestamps, and words.
'''

# vim: set ts=4 sw=4 expandtab :

import datetime
import re

try:
    from dateutil.relativedelta import relativedelta
except ImportError as e:
    import sys
    sys.stderr.write('text2datetime requires the python-dateutil module.\n')
    raise e


__version__ = '1.0.0'
__version_tuple__ = (1, 0, 0)

__all__ = ('FORMAT_HELP_MSG', 'text2datetime', 'applyFixedTimeComponent')


# Extensive help message describing the formats accepted.
FORMAT_HELP_MSG = '''Date should be in one of the following forms:

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

NOTES:

  Unless AM/PM is specified in formats that support it, hours are in 24-hour clock format, starting with 00=midnight, 23 = 11PM

'''   

# Regular expression for a single modification component, e.x. "+5d"
DATE_MODIFIER_RE = re.compile('^(?P<dir>[\+\-])(?P<num>[\d]+)(?P<mod>(mo)|(yr)|([ydhms]{1}))$')

# Message contained within ValueError for general parsing failures.
UNKNOWN_TIME_MSG = 'Cannot parse time: "%s". ' + FORMAT_HELP_MSG

# Error message for invalid format on a fixed time component.
FIXED_TIME_ERROR_STR = 'Fixed time component %s must be numerical hours:minutes:seconds or hours:minutes (e.x. 12:38)'


#################################
####      PUBLIC METHODS    #####
#################################
    

def text2datetime(timeStr, now=None, monthBeforeDay=True):
    '''
        text2datetime - Convert a time string to a datetime.datetime object. This method supports all the types of time strings described in text2datetime.FORMAT_HELP_MSG

        PUBLIC FUNCTION

        @param timeStr <str> - String of time.
        @param now <None/datetime.datetime> - Default None will use current time. Otherwise, calculate time relative to given datetime.
        @param monthBeforeDay <bool> - If True, American time format will be used when applicable (month/day/year). If False, European time (day/month/year) will be used when applicable.

        print ( text2datetime.FORMAT_HELP_MSG ) for information on the format of timeStr.

        @return <datetime.datetime> - Datetime object representing parsed time.
    ''' # %(FORMAT_HELP_MSG,)

    if now is None:
        now = datetime.datetime.now()
    elif not issubclass(now.__class__, datetime.datetime):
        raise ValueError('Argument "now" must be a datetime.datetime object, or None to use current date and time. Got: type=%s: %s' %(str(type(now)), repr(now)))

    timeStr = timeStr.strip()

    # Time Words 
    timeWordResult = applyTimeWords(now, timeStr)
    if timeWordResult is not None:
        return timeWordResult

    timeStr = _condenseAmPm(timeStr)

    # Relative Date Modifiers
    if '+' in timeStr or '-' in timeStr: 
        return applyRelativeTimeComponents(now, timeStr)

    # One of the remaining fixed string formats
    numSpaces = timeStr.count(' ')

    # If 4 spaces, try ctime including day of week
    if numSpaces == 4: 
        try:
            return datetime.datetime.strptime(timeStr, "%a %b %d %H:%M:%S %Y")
        except:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))
    # If 3 spaces, try ctime without day of week
    elif numSpaces == 3:
        try:
            return datetime.datetime.strptime(timeStr, "%b %d %H:%M:%S %Y")
        except:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))

    # American/European Date (mo/day/yr) or (day/mo/yr) with [optional time]
    elif timeStr.count('/') == 2:
        try:
            return getDatetimeFromDateStr(timeStr, monthBeforeDay)
        except ValueError:
            raise
    elif ':' in timeStr:
        # Just a plain time, modify today's date with that time
        try:
            return applyFixedTimeComponent(now, timeStr)
        except:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))
    else:
        raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))


def applyRelativeTimeComponents(datetimeObj, timeStr):
    '''
        applyRelativeTimeComponents - Apply the provided relative adjustments to the given datetime.datetime object.

        For more information on the supported relative components, see text2datetime.FORMAT_HELP_MSG

        This method only supports relative time components (like +4mo +5d). For all possible time strings, use the text2datetime method.

        @param datetimeObj <datetime.datetime> - The datetime which serves as the starting point. Use datetime.datetime.now() to calculate relative to current date and time.
        @param timeStr <str> - A string of relative components (like +5d for plus five days, or -2h for minus two hours.) See text2datetime.FORMAT_HELP_MSG for details.

        @return <datetime.datetime> - A datetime object representing the date and time derived after applying all the relative components to the provided datetime.
    '''
    components = [x for x in timeStr.split(' ') if x]
    
    # Functions used to add/sub to date with relative time deltas
    componentAdd = lambda dateObj, rdelta : dateObj + rdelta
    componentSub = lambda dateObj, rdelta : dateObj - rdelta

    numComponents = len(components)
    for i in range(numComponents):
        component = components[i]

        matchObj = DATE_MODIFIER_RE.match(component)
        if matchObj is None:
            # If on final item, it may be a time modifier
            if i + 1 == numComponents and ':' in component:
                datetimeObj = applyFixedTimeComponent(datetimeObj, component)
                continue
            else:
                raise ValueError('Could not parse time modifier component: %s. It should be in the format +## followed by (yr=years, mo=months, d=days, h=hours, m=minutes, s=seconds). Example: +5d = 5 days, +2mo = 2 months.' %(component,))

        # Matched, now apply modifier
        groupDict = matchObj.groupdict()
        (direction, num, mod) = (groupDict['dir'], groupDict['num'], groupDict['mod'])
        if direction == '+':
            doComponent = componentAdd
        else:
            doComponent = componentSub
            
        if mod == 'd':
            datetimeObj = doComponent(datetimeObj, relativedelta(days=int(num)))
        elif mod == 'mo':
            datetimeObj = doComponent(datetimeObj, relativedelta(months=int(num)))
        elif mod == 'm':
            datetimeObj = doComponent(datetimeObj, relativedelta(minutes=int(num)))
        elif mod == 'h':
            datetimeObj = doComponent(datetimeObj, relativedelta(hours=int(num)))
        elif mod in ('y', 'yr'):
            datetimeObj = doComponent(datetimeObj, relativedelta(months=int(num)*12))
        elif mod == 's':
            datetimeObj = doComponent(datetimeObj, relativedelta(seconds=int(num)))

    # Return our completed date
    return datetimeObj


def applyFixedTimeComponent(datetimeObj, fixedTimeStr):
    '''
        applyFixedTimeComponent - Update a datetime object, replacing the time portion with the given time string.

        PUBLIC FUNCTION

        Time string is at minimum hours and minutes, with optional seconds and optional AM/PM.

        @param datetimeObj <datetime.datetime> - Datetime
        @param fixedTimeStr <str> - Time String as hours:minutes or hours:minutes:seconds, with optional AM/PM suffix.

        @return <datetime.datetime> - datetimeObj with time replaced.
    '''
    if fixedTimeStr.count(':') not in (1, 2):
        raise ValueError(FIXED_TIME_ERROR_STR %(fixedTimeStr,))

    (fixedTimeStr, hoursMod) = _stripAmPm(fixedTimeStr)

    fixedTimeSplit = fixedTimeStr.split(':')

    hours = fixedTimeSplit[0]
    minutes = fixedTimeSplit[1]
    if len(fixedTimeSplit) > 2:
        seconds = fixedTimeSplit[2]
    else:
        seconds = '0'

    if not hours.isdigit() or not minutes.isdigit() or not seconds.isdigit():
        raise ValueError(FIXED_TIME_ERROR_STR %(fixedTimeStr,))

    hours = hoursMod(int(hours))
    
    return datetime.datetime(year=datetimeObj.year, month=datetimeObj.month, day=datetimeObj.day, hour=hours, minute=int(minutes), second=int(seconds))


def applyTimeWords(datetimeObj, timeStr):
    '''
        applyTimeWords - Apply one of several words that describe a time delta to the given datetime object. Example, "tomorrow"

        This method supports only time words, for all possible time transformations, use the text2datetime method.

        See text2datetime.FORMAT_HELP_MSG for all available words.

        @param datetimeObj - <datetime.datetime> - The origin datetime object
        @param timeStr <str> - One of several words that describe a relative delta, see text2datetime.FORMAT_HELP_MSG for all available words. Case insensitive.

        @return - <datetime.datetime/None> - The transformed datetime.datetime object if a valid word was given, otherwise None if there was no match.
    '''
    timeStrLower = timeStr.lower()
    items = timeStrLower.strip().split(' ', 1)
    ret = None

    firstItem = items[0]

    if firstItem == 'now':
        ret = datetimeObj
        if len(items) > 1:
            raise ValueError('Using "now" does not make sense with other modifiers.')
    elif firstItem == 'today':
        ret = datetime.datetime(year=datetimeObj.year, month=datetimeObj.month, day=datetimeObj.day, hour=0, minute=0, second=0)
    elif firstItem == 'tomorrow':
        tomorrow = datetimeObj + relativedelta(days=1)
        ret = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0, second=0)
    elif firstItem == 'yesterday':
        yesterday = datetimeObj - relativedelta(days=1)
        ret = datetime.datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=0, minute=0, second=0)

    if ret is not None:
        if len(items) > 1:
            ret = applyFixedTimeComponent(ret, items[1])
        return ret

    return None


def getDatetimeFromAmericanTime(timeStr):
    '''
        getDatetimeFromAmericanTime - Convert a string from American format (month/day/year), with an optional time, to a datetime object.

        PUBLIC FUNCTION - Specifically handles fixed date (and potentially time) formatted strings. For all possible time strings, use the text2datetime method.

        @param timeStr <str> - A string representing time in American format (month/day/year). Can also be followed by time, either in
            hours:minutes:seconds or hours:minutes. Uses a 24-hour clock unless "AM" or "PM" is provided at the end of timeStr. Year can be 2 or 4 digit.

        This function is equivalent to getDatetimeFromDateStr(timeStr, monthBeforeDay=True)

        @return <datetime.datetime> - A datetime object representing the converted time.
    '''
    return getDatetimeFromDateStr(timeStr, monthBeforeDay=True)

def getDatetimeFromEuropeanTime(timeStr):
    '''
        getDatetimeFromAmericanTime - Convert a string from European format (day/month/year), with an optional time, to a datetime object.

        PUBLIC FUNCTION - Specifically handles fixed date (and potentially time) formatted strings. For all possible time strings, use the text2datetime method.

        @param timeStr <str> - A string representing time in European format (day/month/year). Can also be followed by time, either in
            hours:minutes:seconds or hours:minutes. Uses a 24-hour clock unless "AM" or "PM" is provided at the end of timeStr. Year can be 2 or 4 digit.

        This function is equivalent to getDatetimeFromDateStr(timeStr, monthBeforeDay=False)

        @return <datetime.datetime> - A datetime object representing the converted time.
    '''
    return getDatetimeFromDateStr(timeStr, monthBeforeDay=False)



def getDatetimeFromDateStr(timeStr, monthBeforeDay):
    '''
        getDatetimeFromDateStr - Convert a string that contains a date (month/day/year or day/month/year), with an optional time, to a datetime object.

        PUBLIC FUNCTION - Specifically handles fixed date (and potentially time) formatted strings. For all possible time strings, use the text2datetime method.

        @param timeStr <str> - A string representing time containing a forward-slash separated date, optionally followed by time, either in
            hours:minutes:seconds or hours:minutes. Uses a 24-hour clock unless "AM" or "PM" is provided at the end of timeStr. Year can be 2 or 4 digit.

        @param monthBeforeDay <bool> - If True, date will be assumed month/day/year. If False, date will be assumed day/month/year.

        @return <datetime.datetime> - A datetime object representing the converted time.
    '''
    timeStr = _condenseAmPm(timeStr)


    numSpaces = timeStr.count(' ')

    if numSpaces >= 2:
        # We may have a " AM" or " PM", so condense it and see if we can get a valid time format
        timeStr = _condenseAmPm(timeStr)
        if numSpaces >= 2:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))

    if monthBeforeDay is True:
        dateFormat = "%m/%d"
    else:
        dateFormat = "%d/%m"

    # If has space, includes time.
    if numSpaces == 1:
        if len(timeStr.split(' ')[0].split('/')[-1]) == 4:
            yearFormat = 'Y'
        else:
            yearFormat = 'y'

        colonCount = timeStr.count(':')
        if colonCount == 2:
            timeFormat = '%H:%M:%S'
        elif colonCount == 1:
            timeFormat = '%H:%M'
        else:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))

        if timeStr[-2:].upper() in ('AM', 'PM'):
            timeFormat += '%p'

        try:
            return datetime.datetime.strptime(timeStr, dateFormat + '/%' + yearFormat + ' ' + timeFormat)
        except:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))
    # No space, assume time as 00:00:00
    else: 
        if len(timeStr.split('/')[-1]) == 4:
            yearFormat = 'Y'
        else:
            yearFormat = 'y'
        try:
            return datetime.datetime.strptime(timeStr + ' 00:00:00', dateFormat + '/%' + yearFormat + ' %H:%M:%S')
        except:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))



#################################
####     INTERNAL METHODS   #####
#################################


def _condenseAmPm(timeStr):
    '''
        _condenseAmPm - If there is a trailing space between the time and AM/PM, remove that space.

        @param timeStr <str> - A string representing a time

        @return <str> - The time string without the trailing whitespace between the time and "AM"/"PM"
    '''
    if len(timeStr) < 3:
        return timeStr

    lastThree = timeStr[-3:].upper()

    if lastThree in (' AM', ' PM'):
        return timeStr[:-3] + timeStr[-2:]

    return timeStr


def _convertAmTo24Hour(hours):
    '''
        _convertAmTo24Hour - Function for am times
    '''
    if hours > 12:
        raise ValueError('Hours must be <= 12 when using "AM" or "PM". Got: %s' %(str(hours),))
    elif hours == 12:
        return 0
    return hours

def _convertPmTo24Hour(hours):
    '''
        _convertPmTo24Hour - Function for pm times
    '''
    if hours > 12:
        raise ValueError('Hours must be <= 12 when using "AM" or "PM". Got: %s' %(str(hours),))
    elif hours == 12:
        return 12
    return hours + 12

def _stripAmPm(timeStr):
    '''
        _stripAmPm - Strips "AM" or "PM" with optional leading space off the end, and returns an associated function to modify hours

        @return tuple ( stripped time str, hours function )
    '''
        
    if timeStr[-1] in ('m', 'M') and len(timeStr) >= 2:
        condensed = _condenseAmPm(timeStr)
        otherChar = timeStr[-2].upper()

        if otherChar == 'A':
            return ( condensed[:-2], _convertAmTo24Hour)
        elif otherChar == 'P':
            return ( condensed[:-2], _convertPmTo24Hour)

    return (timeStr, lambda hours : hours)


