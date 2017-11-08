#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re

log.debug("File "+__name__+" loaded")

class LlxTime(Detector):

    _PROVIDES = ['TIME','NTP_INFO']
    _NEEDS = ["HELPER_UNCOMMENT","HELPER_EXECUTE"]

    def run(self,*args,**kwargs):
        output={}

        timedatectl=self.execute(run='timedatectl',stderr=None)

        m=re.search(r'Local time:\s\w+ (?P<TIMESW>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s\w+)',timedatectl)
        if m:
            output.update(m.groupdict())
        m = re.search(r'RTC time:\s\w+ (?P<TIMEHW>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', timedatectl)
        if m:
            output.update(m.groupdict())
        m = re.search(r'Time zone: (?P<TIMEZONE>.*)', timedatectl)
        if m:
            output.update(m.groupdict())
        m = re.search(r'Network time on: (?P<NTPENABLED>yes|no)', timedatectl)
        if m:
            output.update(m.groupdict())
        m = re.search(r'NTP synchronized: (?P<NTPSYNC>yes|no)', timedatectl)
        if m:
            output.update(m.groupdict())

        synced = False
        try:
            ntp_st = self.execute(run="ntpq -pn", stderr=None)
            for line in ntp_st.split("\n"):
                m = re.search(r'^\*(?P<SYNCSERVER>\d+\.\d+\.\d+\.\d+)', line)
                if m:
                    if output['NTPENABLED'] == 'yes' and output['NTPSYNC'] == 'yes':
                        synced = True
                        output.update(m.groupdict())
                        break
        except Exception as e:
            ntp_st = str(e)

        return {'TIME':output,'NTP_INFO':{'STATE':{'synced':synced,'status':ntp_st.strip()},'CONFIG':self.uncomment('/etc/ntp.conf')}}