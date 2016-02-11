# Copyright (c) 2014-2016 Timothy Savannah All Rights Reserved under LGPLv2.1.
#  You should have received a copy of this with the source distribution as LICENSE.
#  If not, the current license can be found at https://github.com/kata198/text2datetime/blob/master/LICENSE

# vim: set ts=4 sw=4 expandtab :

import datetime
import re

from dateutil.relativedelta import relativedelta

DATE_MODIFIER_RE = re.compile('^(?P<dir>[\+\-])(?P<num>[\d]+)(?P<mod>(mo)|(yr)|([ydhms]{1}))$')


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


'''   

UNKNOWN_TIME_MSG = 'Cannot parse time: "%s". ' + FORMAT_HELP_MSG
    

def text2datetime(timeStr):
    '''
        text2datetime - Convert a time string to a datetime.datetime object.

        @param timeStr <str> - String of time.

        print ( text2datetime.FORMAT_HELP_MSG ) for information on the format of timeStr.

        @return <datetime.datetime> - Datetime object representing parsed time.
    ''' # %(FORMAT_HELP_MSG,)

    now = datetime.datetime.now()
    timeStrLower = timeStr.lower()

    # Fixed Strings
    ret = _tryFixedStrings(timeStrLower, now)
    if ret is not None:
        return ret

    timeStr = _condenseAmPm(timeStr)

    # Relative Date Modifiers
    if '+' in timeStr or '-' in timeStr: 
        ret = now

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
                    ret = applyFixedTimeComponent(ret, component)
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
                ret = doComponent(ret, relativedelta(days=int(num)))
            elif mod == 'mo':
                ret = doComponent(ret, relativedelta(months=int(num)))
            elif mod == 'm':
                ret = doComponent(ret, relativedelta(minutes=int(num)))
            elif mod == 'h':
                ret = doComponent(ret, relativedelta(hours=int(num)))
            elif mod in ('y', 'yr'):
                ret = doComponent(ret, relativedelta(months=int(num)*12))
            elif mod == 's':
                ret = doComponent(ret, relativedelta(seconds=int(num)))

        # Return our completed date
        return ret

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

    # American Date (mo/day/yr) [optional time]
    elif timeStr.count('/') == 2: 

        # If has space, includes time.
        if timeStr.count(' ') == 1: 
            if len(timeStr.split(' ')[0].split('/')[-1]) == 4:
                yearModifier = 'Y'
            else:
                yearModifier = 'y'

            colonCount = timeStr.count(':')
            if colonCount == 2:
                timeModifier = '%H:%M:%S'
            elif colonCount == 1:
                timeModifier = '%H:%M'
            else:
                raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))

            if timeStr[-2:].upper() in ('AM', 'PM'):
                timeModifier += '%p'

            try:
                return datetime.datetime.strptime(timeStr, '%m/%d/%' + yearModifier + ' ' + timeModifier)
            except:
                raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))
        # No space, assume time as 00:00:00
        else: 
            if len(timeStr.split('/')[-1]) == 4:
                yearModifier = 'Y'
            else:
                yearModifier = 'y'
            try:
                return datetime.datetime.strptime(timeStr + ' 00:00:00', '%m/%d/%' + yearModifier + ' %H:%M:%S')
            except:
                raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))
    else:
        # Just a plain time, modify today's date with that time
        try:
            return applyFixedTimeComponent(now, timeStr)
        except:
            raise ValueError(UNKNOWN_TIME_MSG % (timeStr,))





_fixedTimeErrorStr = 'Fixed time component %s must be numerical hours:minutes:seconds or hours:minutes (e.x. 12:38)'

def applyFixedTimeComponent(datetimeObj, fixedTimeStr):
    '''
        applyFixedTimeComponent - Update a datetime object, replacing the time portion with the given time string.

        Time string is at minimum hours and minutes, with optional seconds and optional AM/PM.

        @param datetimeObj <datetime.datetime> - Datetime
        @param fixedTimeStr <str> - Time String

        @return <datetime.datetime> - datetimeObj with tiem replaced.
    '''
    if fixedTimeStr.count(':') not in (1, 2):
        raise ValueError(_fixedTimeErrorStr %(fixedTimeStr,))

    (fixedTimeStr, hoursMod) = _stripAmPm(fixedTimeStr)

    fixedTimeSplit = fixedTimeStr.split(':')

    hours = fixedTimeSplit[0]
    minutes = fixedTimeSplit[1]
    if len(fixedTimeSplit) > 2:
        seconds = fixedTimeSplit[2]
    else:
        seconds = '0'

    if not hours.isdigit() or not minutes.isdigit() or not seconds.isdigit():
        raise ValueError(_fixedTimeErrorStr %(fixedTimeStr,))

    hours = hoursMod(int(hours))
    
    return datetime.datetime(year=datetimeObj.year, month=datetimeObj.month, day=datetimeObj.day, hour=hours, minute=int(minutes), second=int(seconds))


def _condenseAmPm(fixedTimeStr):
    '''
        If there is a trailing space between the time and AM/PM, remove that space.
    '''
    if len(fixedTimeStr) < 3:
        return fixedTimeStr

    lastThree = fixedTimeStr[-3:].upper()

    if lastThree in (' AM', ' PM'):
        return fixedTimeStr[:-3] + fixedTimeStr[-2:]

    return fixedTimeStr


def _amFunc(hours):
    '''
        _amFunc - Function for am times
    '''
    if hours > 12:
        raise ValueError('Hours must be <= 12 when using "AM" or "PM"')
    elif hours == 12:
        return 0
    return hours

def _pmFunc(hours):
    '''
        _pmFunc - Function for pm times
    '''
    if hours > 12:
        raise ValueError('Hours must be <= 12 when using "AM" or "PM"')
    elif hours == 12:
        return 12
    return hours + 12

def _stripAmPm(fixedTimeStr):
    '''
        _stripAmPm - Strips "AM" or "PM" with optional leading space off the end, and returns an associated function to modify hours

        @return tuple ( stripped time str, hours function )
    '''
        
    if fixedTimeStr[-1] in ('m', 'M') and len(fixedTimeStr) >= 2:
        condensed = _condenseAmPm(fixedTimeStr)
        otherChar = fixedTimeStr[-2].upper()

        if otherChar == 'A':
            return ( condensed[:-2], _amFunc)
        elif otherChar == 'P':
            return ( condensed[:-2], _pmFunc)

    return (fixedTimeStr, lambda hours : hours)


def _tryFixedStrings(timeStrLower, now):
    '''
        _tryFixedStrings - Try the various fixed strings supported
    '''
    if timeStrLower == 'now':
        return now
    elif timeStrLower == 'today':
        return datetime.datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0)
    elif timeStrLower == 'today end':
        return datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23, minute=59, second=59)
    elif timeStrLower == 'tomorrow':
        tomorrow = now + relativedelta(days=1)
        return datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0, second=0)
    elif timeStrLower == 'tomorrow end':
        tomorrow = now + relativedelta(days=1)
        return datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=23, minute=59, second=59)
    elif timeStrLower == 'yesterday':
        yesterday = now - relativedelta(days=1)
        return datetime.datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=0, minute=0, second=0)
    elif timeStrLower == 'yesterday end':
        yesterday = now - relativedelta(days=1)
        return datetime.datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=23, minute=59, second=59)

    return None
