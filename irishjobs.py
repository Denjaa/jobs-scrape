import sqlite3
import requests
import argparse
import warnings
from lxml import html


# ignore ssl problem while sending requests
warnings.filterwarnings('ignore')

class IrishJobs:
    def __init__(self, town_code, title):
        self.town_code = town_code.strip()
        self.title = title.strip().replace(' ', '+')
        self.temporary = list()

        self.connection = sqlite3.connect("jobs.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS jobs (
									position VARCHAR(255),
                                    salary VARCHAR(255),
                                    employer VARCHAR(225),
                                    date_updated VARCHAR(255),
                                    location VARCHAR(255),
                                    description VARCHAR(255),
                                    link_description VARCHAR(255));
							""")
        self.connection.commit()

    def return_content(self, page_number = 1):
        self.URL = "https://www.irishjobs.ie/ShowResults.aspx?Keywords={}&autosuggestEndpoint=%2fautosuggest&Location={}&Category=&Recruiter=Company%2cAgency&btnSubmit=Search&Page={}".format(str(self.title),str(self.town_code), str(page_number))
        self.response = requests.get(self.URL, verify = False)
        self.content = html.fromstring(self.response.content)
        return self.content

    def activate(self):
        self.content = self.return_content()
        self.bottom_pages_list = self.content.xpath('//*[@id="pagination"]//text()')

        if len(self.bottom_pages_list) > 0:
            for number in self.bottom_pages_list:
                try: self.temporary.append(int(number))
                except: pass

            self.max_page = int(max(self.temporary))
            for i in range(1, self.max_page + 1, 1):
                self.content = self.return_content(page_number = i)
                self.box_length = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div/div')
                for j in range(len(self.box_length) + 1):
                    try:
                        try: self.position = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div[2]/div[{}]/div/div[2]/div[2]/h2/a//text()'.format(j))[0]
                        except: self.position = ''

                        try: self.salary = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div[2]/div[{}]/div/div[3]/ul/li[1]//text()'.format(j))[0]
                        except: self.salary = ''

                        try: self.employer = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div[2]/div[{}]/div/div[2]/div[2]/h3/a//text()'.foramt(j))[0]
                        except: self.employer = ''

                        try: self.date_updated = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div[2]/div[{}]/div/div[3]/ul/li[2]//text()'.format(j))[0]
                        except: self.date_updated = ''

                        try: self.location = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div[2]/div[{}]/div/div[3]/ul/li[3]//text()'.format(j))
                        except: self.location = ''
                        self.location = [l.replace('\r', '').replace('\n', '').replace('  ', '').replace('\xa0/', '') for l in self.location]
                        self.location = [l for l in self.location if l != '']
                        self.location = ' | '.join(self.location)

                        try: self.description = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div[2]/div[{}]/div/p/span//text()'.format(j))
                        except: self.description = ''

                        self.description = ' '.join(self.description)

                        try: self.link_to_position = self.content.xpath('//*[@id="page"]/div[2]/div[2]/div[2]/div[{}]/div/div[4]/a[2]/@href'.format(j))[0]
                        except: self.link_to_position = ''

                        if self.position != '' and self.salary != '':
                            self.checking_title_and_employer =  list(self.cursor.execute("""SELECT * FROM JOBS WHERE position = "{}" and employer = "{}" """.format(self.position, self.employer)))
                            if not self.checking_title_and_employer:
                                self.SQL_command =  """ INSERT INTO jobs VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}")
                                                    """.format(self.position, self.salary, self.employer,  self.date_updated, self.location, self.description, self.link_to_position)
                                self.cursor.execute(self.SQL_command)
                                self.connection.commit()
                    except: pass

argument = argparse.ArgumentParser()
argument.add_argument('-c', action = 'store', dest = 'town_code', help = 'Provide town code one from list: \
                                                                            0 - All locations, 102 - Dublin, 21 - Antrim, 22 - Armagh, 23 - Belfast, \
                                                                            2 - Carlow, 24 - Cavan, 41 - Clare, 42 - Cork, 25 - Derry, 26 - Donegal, \
                                                                            27 - Down, 28 - Fermagh, 61 - Galway, 44 - Kerry, 3 - Kildare, 4 - Kilkenny, \
                                                                            5 - Laois, 63 - Leitrim, 45 - Limerick, 6 - Longford, 7 - Louth, 64 - Mayo, \
                                                                            8 - Meath, 29 - Monaghan, 9 - Offaly, 65 - Roscommon,  66 - Sligo, 47 - Tipperary \
                                                                            30 - Tyrone, 48 - Waterford, 10 - Westmeath, 11 - Wexford, 12 - Wicklow', default = False)
argument.add_argument('-t', action = 'store', dest = 'title', help = 'Title you are looking for eg: Data Scientist, Python', default = False)
argumentation = argument.parse_args()

if argumentation.town_code and argumentation.title:
    print ('Please wait while getting data...')
    IrishJobs(town_code = argumentation.town_code, title = argumentation.title).activate()
else: print ('Please enter the details requited or run the help function to identify town codes available')
