import jdatetime

def jalali_to_gregorian(jy, jm, jd):
    return jdatetime.date(jy, jm, jd).togregorian()

