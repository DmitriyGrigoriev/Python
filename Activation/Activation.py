import random
import datetime
import binascii


def rand():
    r = random.randint(1, 100) / 100
    return r


def getrandomstring(lenght):
    string = ''
    for i in range(lenght):
        string += chr(min(ord(chr(int(rand() * 26))) + ord('A'), ord('Z')))

    return string


def getpaddedstring(string='', lenght=0):
    rndstring = string + getrandomstring(lenght - 1)
    string = chr(ord('Z') - len(string)) + rndstring[0:lenght - 1]

    return string


def encode(string='', key='') -> object:
    key = ''.join(key * 10)
    strchar = ''

    for i in range(len(string)):
        char1 = string[i]
        char2 = key[i]
        char = chr((ord(char1) + ord(char2) - 2 * ord('A') + 2) % 26 + ord('A'))
        strchar += char

    checksum = strchar + getchecksum(strchar)
    sret = "{0}-{1}-{2}-{3}-{4}-{5}".format(checksum[0:5],
                                            checksum[5:10],
                                            checksum[10:15],
                                            checksum[15:20],
                                            checksum[20:25],
                                            checksum[25:30])
    sret = sret.replace('--', '')

    return sret.upper()


def decode(string='', key=''):
    code = string.replace('-', '')
    code = code.strip()
    key = key.strip()
    key = key.replace('-', '')
    key = ''.join(key*10)
    retstr = ''

    currchecksum = code[-5:]
    decodestring = code[0:len(code)-5]
    calcchecksum = getchecksum(decodestring)

    if currchecksum == calcchecksum:
        for i in range(len(decodestring)):
            char1 = decodestring[i]
            char2 = key[i]
            char = chr((ord(char1) - ord(char2) - 2 * ord('A') - 2) % 26 + ord('A'))
            retstr += char

    return retstr


def getchecksum(string=''):
    hexdata = bytearray(string, 'utf-8')
    chrsum = str(binascii.crc32(hexdata))

    while len(chrsum) < 6:
        chrsum += '9'

    if len(chrsum) > 5:
        chrsum = chrsum[0:5]

    chrsumma = int(chrsum)
    chrsumstring = getpaddednumber(chrsumma, 5)
    return chrsumstring


def getpaddednumber(value: int = 0, lenght: int = 0) -> str:
    strvalue = getbase26value(value)
    string = getpaddedstring(strvalue, lenght)
    return string


def getbase26value(value: int = 0) -> str:
    string = ''
    i = 5

    while i >= 0:
        exponent = 26 ** i
        if exponent <= value:
            ntemp = int(value / exponent)
            string += chr(ord('A') + ntemp)
            value -= ntemp * exponent

        i -= 1

    if value > 0:
        string += chr(ord('A') + value)

    return string


def createactivationcode(registration: str = '', serial: str = '',
                         level: int = 0, licenses: int = 0, expiry: datetime = None) -> str:
    expirydays = expiry - datetime.datetime.strptime("2000.10.01", "%Y.%m.%d")
    string = ''
    productcode = ''
    for i in range(len(registration)):
        char = registration[i]
        if char.isalpha():
            productcode += char
        else:
            registration = registration[i:]
            break

    string += getpaddedstring(productcode, 5)
    string += getpaddednumber(int(registration), 7)
    string += getpaddednumber(level, 3)
    string += getpaddednumber(licenses, 5)
    string += getpaddednumber(expirydays.days, 5)
    activation = encode(string, serial.lstrip())

    return activation


def getregistrationfromactivation(activation: str = '', serial: str = '') -> str:
    strret = ''
    string = decode(activation, serial)

    if not string == '':
        productcode = getstringfromactivation(string[0:5])
        registration = str(getnumberfromactivation(string[5:12]))
        strret = productcode + registration

    return strret


def validateactivationcode(activation='', registration='', serial='') -> bool:
    registrationcode = getregistrationfromactivation(activation, serial)
    isactivation = isactivationvalid(activation)
    regcodevalid = registration == registrationcode

    return isactivation and regcodevalid


def isactivationvalid(activation=''):
    string = activation.replace('-', '')
    activation = string[0:25]
    checksum = getchecksum(activation)
    strret = checksum == string[-5:]

    return strret


def getnumberfromactivation(string=''):
    string = getstringfromactivation(string)
    lenght = len(string)
    value = 0.0

    for i in range(lenght, 0, -1):
        char = string[i-1]
        exponent = 26 ** (lenght - i)
        value += (ord(char) - ord('A')) * exponent

    return int(value)


def getstringfromactivation(string=''):
    lenght = string[0]
    lenght = ord('Z') - ord(lenght)
    string = string[1:1+lenght:]

    return string


def getlevelfromactivation(activation='', serial=''):
    string = decode(activation, serial)
    level = 0

    if not string == '':
        level = getnumberfromactivation(string[12:15])

    return level


def getlicensesfromactivation(activation='', serial=''):
    string = decode(activation, serial)
    licenses = 0
    if not string == '':
        licenses = getnumberfromactivation(string[15:20])

    return licenses


def getexpiryfromactivation(activation: str = '', serial: str = '') -> datetime:
    string = decode(activation, serial)
    expiry = None

    if not string == '':
        expirydays = getnumberfromactivation(string[20:26])
        expiry = datetime.timedelta(days=expirydays) + datetime.datetime.strptime("2000.10.01", "%Y.%m.%d")

    return expiry


def createrenewalcode(expiry: datetime = None, serial: str = '') -> str:
    expirydays = expiry - datetime.datetime.strptime("2000.10.01", "%Y.%m.%d")
    string = getpaddednumber(expirydays.days, 5)
    activation = encode(string, serial)

    return activation


def getexpiryfromrenewal(activation: str ='', serial: str = '') -> str:
    string = decode(activation, serial)
    expiry = None

    if not string == '':
        expirydays = getnumberfromactivation(string)
        expiry = datetime.timedelta(days=expirydays) + datetime.datetime.strptime("2000.10.01", "%Y.%m.%d")

    return expiry


def selftest():
    registration = 'FRWR21068'
    serial = '1259595718'
    level = 2
    licenses = 1
    expiry = datetime.datetime.now() + datetime.timedelta(days=30)
    activation = createactivationcode(registration, serial, level, licenses, expiry)
    # activation ='HSHQH-PRXQB-VAOWR-SREMG-IVHPD-VBVFN'

    iscodeverifyed = validateactivationcode(activation, registration, serial)
    print('Validate Activation Code:', iscodeverifyed)

    regcode = getregistrationfromactivation(activation, serial)
    print('Registration number:', regcode)

    reglevel = getlevelfromactivation(activation, serial)
    print('Level:', reglevel)

    reglicenses = getlicensesfromactivation(activation, serial)
    print('Licenses:', reglicenses)

    regexpiry = getexpiryfromactivation(activation, serial)
    print('Expiry date:', regexpiry)

    renewalcode = createrenewalcode(expiry, serial)
    print('Renewal Code:', renewalcode)

    renewalcode = createrenewalcode(expiry, serial)
    strexpiry = str(getexpiryfromrenewal(renewalcode, serial))
    print('Expiry from Renewal Code:', strexpiry)

    return activation


selftest()
