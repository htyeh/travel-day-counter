#!/usr/bin/env python3
import json
import pandas as pd
from collections import defaultdict
from datetime import date


class TravelDayCounter:
    def __init__(self, config):
        '''
        Args:
            config (str): path of configuration json file
        Attributes:
            self.country2days (str -> int): country to total duration of stay
            self.country2percent (str -> str): country to percentage of days spent
            self.country2rank (str -> int): country to its ranking based on length of stay
            self.country2firstvisit (str -> datetime.date): country to first visited date
            self.country2lastvisit (str -> datetime.date): country to last visited date
            self.visityear2countries (str -> list): year to countries visited in the year
            self.num_visited_countries (int)
            self.days_home (int)
            self.years_home (float)
            self.days_abroad (int)
            self.years_abroad (float)
            self.residency_period (int): in days
        Config attributes:
            self.source (str)
            self.lang (str)
            self.track_home (bool)
            self.home_code (str)
            self.home_name (str)
            self.track_residency (bool)
            self.residency_code (str)
            self.residency_name (str)
            self.residency_begin (str)
            self.table_style (str)
            self.report_style (str)
        '''
        with open(config) as config_data:
            self.__dict__.update(json.load(config_data))

        self.country2days, self.country2firstvisit, self.country2lastvisit, self.visityear2countries = self.create_visit_history(self.source)
        self.country2percent = self.create_country2percent(self.country2days)
        self.country2rank = self.create_country2rank(self.country2days)
        self.num_visited_countries = len(self.country2days)

        self.days_home = self.country2days[self.home_code]
        self.years_home = round(self.days_home/365, 1)
        self.days_abroad = sum(days for country, days in self.country2days.items() if country != self.home_code)
        self.years_abroad = round(self.days_abroad/365, 1)
        self.residency_period = self.day_count(start_date=self.residency_begin)

    def create_visit_history(self, source):
        '''
        Returns:
            country2days (str -> int)
            country2firstvisit (str -> datetime.date)
            country2lastvisit (str -> datetime.date)
            visityear2countries (str -> list)
        '''
        country2days = defaultdict(int)
        country2firstvisit = dict()
        country2lastvisit = dict()
        visityear2countries = defaultdict(list)

        df = pd.read_csv(source)
        entry_count = len(df)
        # dates = list(df['DATE'])
        # countries = list(df['ENTERED'])
        for i in range(entry_count):
            '''
            entry_date: date in the current line
            departure_date: entry_date of the following line
            delta: length of stay for country of the current line
            '''
            entry_y, entry_m, entry_d = df['DATE'][i].split('-')
            entry_date = date(int(entry_y), int(entry_m), int(entry_d))
            country = df['ENTERED'][i]
            try:
                depart_y, depart_m, depart_d = df['DATE'][i+1].split('-')
                departure_date = date(int(depart_y), int(depart_m), int(depart_d))
            except KeyError:
                depart_y = str(date.today().year)
                departure_date = date.today()
            delta = departure_date - entry_date
            country2days[country] += delta.days
            country2lastvisit[country] = departure_date
            if country not in country2firstvisit:
                country2firstvisit[country] = entry_date
            # use list instead of set to preserve order of visit for the report
            if country not in visityear2countries[entry_y]:
                visityear2countries[entry_y].append(country)
            if country not in visityear2countries[depart_y]:
                visityear2countries[depart_y].append(country)
        return country2days, country2firstvisit, country2lastvisit, visityear2countries

    def create_country2percent(self, country2days):
        total_days = sum(country2days.values())
        country2percent = dict()
        for country, days in country2days.items():
            country2percent[country] = str(round((days/total_days)*100, 1))+'%'
        return country2percent

    def create_country2rank(self, country2days):
        country2rank = dict()
        current_rank = 0
        current_max_days = float('inf')
        rank_diff = 0 # +1 each time parallel ranking occurs
        sorted_c2d = sorted(country2days.items(), key=lambda x:x[1], reverse=True)
        for country, days in sorted_c2d:
            if days < current_max_days:
                current_rank = current_rank+rank_diff+1
                country2rank[country] = current_rank
                current_max_days = days
                rank_diff = 0
            else:
                country2rank[country] = current_rank
                rank_diff += 1
        return country2rank

    def shortened_table(self, threshold=7):
        '''
        Returns:
            shortenedd_c2d (str -> int)
            rest_days (int): sum of stays shorter than threshold
            rest_percent (str): percentage of short stays summed
        '''
        shortened_c2d = {country:day for country, day in self.country2days.items() if day >= threshold}
        rest_days = sum(day for day in self.country2days.values() if day < threshold)
        rest_percent = str(round((rest_days/sum(self.country2days.values()))*100, 1))+'%'
        return shortened_c2d, rest_days, rest_percent

    def day_count(self, start_date):
        ''' returns num of days elapsed from start_date (format 'yyyy-mm-dd') '''
        year, month, day = start_date.split('-')
        start_date = date(int(year), int(month), int(day))
        delta = date.today() - start_date
        return delta.days

    def bold(self, text):
        return f'\033[1m{text}\033[0m'

    def print_header(self):
        if self.lang == 'en':
            print('Travel Day Counter')
            print(str(self.num_visited_countries) + ' countries visited until ' + str(date.today()) + '\n')
        elif self.lang == 'ko':
            print('방문한 나라에 체류 기간')
            print(str(date.today()) + '까지 방문한 ' + str(self.num_visited_countries) + '개의 국가\n')
        elif self.lang == 'ko-hanja':
            print('訪問한 나라에 滯留期間')
            print(str(date.today()) + '까지 訪問한 ' + str(self.num_visited_countries) + '個의 國家\n')
        elif self.lang == 'zh':
            print('到訪國家停留紀錄')
            print('至' + str(date.today()) + '已訪問' + str(self.num_visited_countries) + '個國家\n')

    def print_in_n_out_stats(self):
        if self.lang == 'en':
            print('Inside', self.home_name+':' if self.home_name else self.home_code+':', self.days_home, 'days (' + str(self.years_home) + ' years, ' + str(round((self.days_home/(self.days_home+self.days_abroad))*100, 1))+'%)')
            print('Outside', self.home_name+':' if self.home_name else self.home_code + ':', self.days_abroad, 'days (' + str(self.years_abroad) + ' years, ' + str(round((self.days_abroad/(self.days_home+self.days_abroad))*100, 1))+'%)')
        elif self.lang == 'ko':
            print(self.home_name if self.home_name else self.home_code, '내:', self.days_home, '일', '(' + str(self.years_home) + ' 년, ' + str(round((self.days_home/(self.days_home+self.days_abroad))*100, 1))+'%)')
            print(self.home_name if self.home_name else self.home_code, '외:', self.days_abroad, '일', '(' + str(self.years_abroad) + ' 년, ' + str(round((self.days_abroad/(self.days_home+self.days_abroad))*100, 1))+'%)')
        elif self.lang == 'ko-hanja':
            print(self.home_name if self.home_name else self.home_code, '內:', self.days_home, '日', '(' + str(self.years_home) + ' 年, ' + str(round((self.days_home/(self.days_home+self.days_abroad))*100, 1))+'%)')
            print(self.home_name if self.home_name else self.home_code, '外:', self.days_abroad, '日', '(' + str(self.years_abroad) + ' 年, ' + str(round((self.days_abroad/(self.days_home+self.days_abroad))*100, 1))+'%)')
        elif self.lang == 'zh':
            print(self.home_name+'內' if self.home_name else self.home_code+'內', self.days_home, '天（' + str(self.years_home) + '年，' + str(round((self.days_home/(self.days_home+self.days_abroad))*100, 1))+'%）')
            print(self.home_name+'外' if self.home_name else self.home_code+'外', self.days_abroad, '天（' + str(self.years_abroad) + '年，' + str(round((self.days_abroad/(self.days_home+self.days_abroad))*100, 1))+'%）')

    def print_residency_stats(self):
        if self.lang == 'en':
            print('Residency in ' + self.residency_name + ':', int(self.residency_period/365), 'year(s)', self.residency_period%365, 'day(s)\n')
        elif self.lang == 'ko':
            print(self.residency_name + '에 합법적 거주기간:', int(self.residency_period/365), '년', self.residency_period%365, '일\n')
        elif self.lang == 'ko-hanja':
            print(self.residency_name + '에 合法的居住期間:', int(self.residency_period/365), '年', self.residency_period%365, '日\n')
        elif self.lang == 'zh':
            print(self.residency_name + '合法居留時間', int(self.residency_period/365), '年', self.residency_period%365, '天\n')

    def print_table(self):
        if self.lang == 'en':
            print('\t'.join(['COUNTRY', 'DAYS', '%', 'RANK.', 'FIRST VISIT', 'LAST VISIT']))
            if self.table_style == 'full':
                for country, days in sorted(self.country2days.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country]), str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
            elif self.table_style == 'short':
                shortened_c2d, rest_days, rest_percent = self.shortened_table()
                for country, days in sorted(shortened_c2d.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country]), str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
                print('\t'.join(['OTHER', str(rest_days), rest_percent]))
        elif self.lang == 'ko':
            print('\t'.join(['국가', '일수', '퍼센트', '순위', '처음 방문 날짜', '마지막 방문 날짜']))
            if self.table_style == 'full':
                for country, days in sorted(self.country2days.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country])+'위', str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
            elif self.table_style == 'short':
                shortened_c2d, rest_days, rest_percent = self.shortened_table()
                for country, days in sorted(shortened_c2d.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country])+'위', str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
                print('\t'.join(['기타', str(rest_days), rest_percent]))
        elif self.lang == 'ko-hanja':
            print('\t'.join(['國家', '日數', '퍼센트', '順位', '처음 訪問 날짜', '마지막 訪問 날짜']))
            if self.table_style == 'full':
                for country, days in sorted(self.country2days.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country])+'位', str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
            elif self.table_style == 'short':
                shortened_c2d, rest_days, rest_percent = self.shortened_table()
                for country, days in sorted(shortened_c2d.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country])+'位', str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
                print('\t'.join(['其他', str(rest_days), rest_percent]))
        elif self.lang == 'zh':
            print('\t'.join(['國家', '天數', '百分比', '排名', '最初訪問日', '最近訪問日']))
            if self.table_style == 'full':
                for country, days in sorted(self.country2days.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country]), str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
            elif self.table_style == 'short':
                shortened_c2d, rest_days, rest_percent = self.shortened_table()
                for country, days in sorted(shortened_c2d.items(), key=lambda x:x[1], reverse=True):
                    print('\t'.join([country, str(days), self.country2percent[country], str(self.country2rank[country]), str(self.country2firstvisit[country]), str(self.country2lastvisit[country])]))
                print('\t'.join(['其他', str(rest_days), rest_percent]))

    def print_report(self):
        if self.report_style == 'chrono':
            all_visited_countries = []
            if self.lang == 'en':
                print('\nChronological Report')
            elif self.lang == 'ko':
                print('\n연대순 방문 기록')
            elif self.lang == 'ko-hanja':
                print('\n年代順訪問記錄')
            elif self.lang == 'zh':
                print('\n年度訪問紀錄')
            for year, country_list in sorted(self.visityear2countries.items()):
                new_countries = [country for country in country_list if country not in all_visited_countries]
                all_visited_countries += new_countries
                print('['+year+']', ' '.join([self.bold(country) if country in new_countries else country for country in country_list]))

    def output(self):
        self.print_header()
        if self.track_home:
            self.print_in_n_out_stats()
        if self.track_residency:
            self.print_residency_stats()
        self.print_table()
        self.print_report()


TDC = TravelDayCounter(config='config.json')
TDC.output()
