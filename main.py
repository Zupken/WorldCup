import time
import random
import sqlite3
import tabulate

GROUP_A = ['Russia', 'Saudi Arabia', 'Egypt', 'Uruguay']
GROUP_B = ['Portugal', 'Spain', 'Morocco', 'Iran']
GROUP_C = ['France', 'Australia', 'Peru', 'Denmark']
GROUP_D = ['Argentina', 'Iceland', 'Croatia', 'Nigeria']
GROUP_E = ['Brazil', 'Switzerland', 'Costa Rica', 'Serbia']
GROUP_F = ['Germany', 'Mexico', 'Sweden', 'Korea']
GROUP_G = ['Belgium', 'Panama', 'Tunisia', 'England']
GROUP_H = ['Poland', 'Senegal', 'Colombia', 'Japan']
GROUPS = [GROUP_A, GROUP_B, GROUP_C, GROUP_D, GROUP_E, GROUP_F, GROUP_G, GROUP_H]
PAIRS = [[GROUP_A, GROUP_B], [GROUP_C, GROUP_D], [GROUP_E, GROUP_F], [GROUP_G, GROUP_H]]

conn = sqlite3.connect('TEAMS.db')
c = conn.cursor()


class Teams:
    def __init__(self):
        self.CHARS = ['(', ')', ',']
        self.keys = ['PL', 'W', 'D', 'L', 'GS', 'GL', 'P', 'MP']
        self.teams = {}

    def create_groups(self):
        for group in GROUPS:
            for team in group:
                c.execute('SELECT strength FROM data WHERE team="{0}"'.format(team))
                strength = str(c.fetchone())
                strength = self.remove_chars(strength)
                self.teams[team] = {'strength': strength, 'GS': 0, 'GL': 0, 'P': 0, 'W': 0, 'D': 0, 'L': 0, 'MP': 0}

    def remove_chars(self, str):
        for char in str:
            if char in self.CHARS:
                str = str.replace(char, '')
        return str

    def show_all(self, team):
        items = {'name': team}
        for item in self.keys:
            items[item] = self.teams[team][item]
        return items


class Group:

    def __init__(self):
        self.queue = [(1, 2), (3, 4), (1, 3), (2, 4), (1, 4), (2, 3)]
        self.matches = 0
        self.round = 1

    def match(self, team_one, team_two):
        """Expect two variables as dict."""
        self.team_one = team_one
        self.team_two = team_two
        # Probability of score goal by team. Pattern: 0.3x+0.8-0.2y
        self.goal_chance_one = float(Teams.teams[team_one]['strength'])*0.3+0.8-float(Teams.teams[team_two]['strength'])*0.2
        self.goal_chance_two = float(Teams.teams[team_two]['strength'])*0.3+0.8-float(Teams.teams[team_one]['strength'])*0.2
        self.play_match()
        self.check_result()
        self.add_points()
        self.add_results()
        # print('MINUTE: {0} {1} {2}:{3} {4}'.format(str(minute), team_one, str(goals_one), str(goals_two), team_two))
        print('{0} {1}:{2} {3}'.format(self.team_one, str(self.goals_one), str(self.goals_two), self.team_two))
        # print(team_one, '\tGS:', Teams.teams[team_one]['GS'], '\tGL:', Teams.teams[team_one]['GL'], 'P:', Teams.teams[team_one]['P'])
        # print(team_two, '\tGS:', Teams.teams[team_two]['GS'], '\tGL:', Teams.teams[team_two]['GL'], 'P:', Teams.teams[team_two]['P'], '\n')

    def chose_teams(self):
        while self.queue:
            print('ROUND {0}'.format(self.round))
            for group in GROUPS:
                for numbers in self.queue:
                    self.match(group[numbers[0]-1], group[numbers[1]-1])
                    self.matches += 1
                    if self.matches % 2 == 0:
                        break
            self.queue = self.queue[2:]
            self.round += 1
            Table.show_table()

    def check_result(self):
        if self.goals_one > self.goals_two:
            self.points_one = 3
            self.points_two = 0
            self.result_one = 'W'
            self.result_two = 'L'
        elif self.goals_two > self.goals_one:
            self.points_one = 0
            self.points_two = 3
            self.result_one = 'L'
            self.result_two = 'W'
        else:
            self.points_one = 1
            self.points_two = 1
            self.result_one = 'D'
            self.result_two = 'D'

    def play_match(self):
        self.goals_one = 0
        self.goals_two = 0
        for minute in range(0, 91):
            number = random.randrange(0, 101)
            if number < self.goal_chance_one:
                self.goals_one += 1
            number = random.randrange(0, 101)
            if number < self.goal_chance_two:
                self.goals_two += 1

    def add_points(self):
            Teams.teams[self.team_one]['GS'] += self.goals_one
            Teams.teams[self.team_one]['GL'] += self.goals_two
            Teams.teams[self.team_one]['P'] += self.points_one

            Teams.teams[self.team_two]['GS'] += self.goals_two
            Teams.teams[self.team_two]['GL'] += self.goals_one
            Teams.teams[self.team_two]['P'] += self.points_two

    def add_results(self):
            if self.result_one == 'W':
                    Teams.teams[self.team_one]['W'] += 1
            elif self.result_one == 'L':
                    Teams.teams[self.team_one]['L'] += 1
            else:
                Teams.teams[self.team_one]['D'] += 1
            if self.result_two == 'W':
                    Teams.teams[self.team_two]['W'] += 1
            elif self.result_two == 'L':
                    Teams.teams[self.team_two]['L'] += 1
            else:
                Teams.teams[self.team_two]['D'] += 1
            Teams.teams[self.team_one]['MP'] += 1
            Teams.teams[self.team_two]['MP'] += 1


class Table:

    def __init__(self):
        self.places = []
        self.team_one = ''
        self.team_two = ''

    def check_points(self):
        if self.points_one > self.points_two:
            self.winner = self.team_one
        elif self.points_two > self.points_one:
            self.winner = self.team_two
        else:
            self.check_difference()

    def check_difference(self):
        difference_one = Teams.teams[self.team_one]['GS'] - Teams.teams[self.team_one]['GL']
        difference_two = Teams.teams[self.team_two]['GS'] - Teams.teams[self.team_two]['GL']
        if difference_one > difference_two:
            self.winner = self.team_one
        elif difference_two > difference_one:
            self.winner = self.team_two
        else:
            self.check_gs()

    def check_gs(self):
        gs_one = Teams.teams[self.team_one]['GS']
        gs_two = Teams.teams[self.team_two]['GS']
        if gs_one > gs_two:
            self.winner = self.team_one
        elif gs_two > gs_one:
            self.winner = self.team_two
        else:
            self.winner = random.choice([self.team_one, self.team_two])

    def create_table(self):
        for group in GROUPS:
            self.places = {}
            self.new_places = []
            index = 0
            for team in group:
                self.places[team] = {'P': Teams.teams[team]['P'], 'PL': 1}
            for self.team_one in self.places:
                self.points_one = self.places[self.team_one]['P']
                iterator = iter(self.places)
                next(iterator)
                for i in range(0, index):
                    next(iterator)
                try:
                    while True:
                        self.winner = None
                        self.team_two = next(iterator)
                        self.points_two = self.places[self.team_two]['P']
                        self.check_points()
                        if self.winner == self.team_one:
                            self.places[self.team_two]['PL'] += 1
                        elif self.winner == self.team_two:
                            self.places[self.team_one]['PL'] += 1
                except StopIteration:
                    pass
                index += 1
            for name in self.places:
                Teams.teams[name]['PL'] = self.places[name]['PL']

    def show_table(self):
        self.create_table()
        for group in GROUPS:
            teams = []
            for team in group:
                teams.append(Teams.show_all(team))
            teams = sorted(teams, key=self.get_key)
            printable_teams = []
            for team in teams:
                printable_teams.append([team['name'], team['MP'], team['W'], team['D'], team['L'], team['GS'], team['GL'], team['GS']-team['GL'], team['P']])
                # print(tabulate.tabulate([[x for x in printable_teams]], headers=['Place', 'Name', 'Wins', 'Draws', 'Loses', 'GS', 'GL', 'Balance',]))
                # if len(team['name']) > 8:
                #     print(team['PL'], team['name'], '\t', team['W'], team['D'], team['L'], team['GS'], team['GL'], team['GS']-team['GL'])
                # elif len(team['name']) < 5:
                #     print(team['PL'], team['name'], '\t\t\t', team['W'], team['D'], team['L'], team['GS'], team['GL'], team['GS']-team['GL'])
                # else:
                #     print(team['PL'], team['name'], '\t\t', team['W'], '\t', team['D'], team['L'], team['GS'], '\t', team['GL'], team['GS']-team['GL'])
            print('')
            print(tabulate.tabulate([x for x in printable_teams],
                                    headers=['Name', 'MP', 'W', 'D', 'L', 'GP', 'GA', 'GA', 'Pts']))
    
    def get_key(self, item):
        return item['PL']


class Knockout:

    def __init__(self):
        self.matches = []
        self.first = True
        self.home = ['', '']

    def create_first_round(self):
        for pair in PAIRS:
            self.first = True
            self.home = ['', '']
            for group in pair:
                for team in group:
                    if Teams.teams[team]['PL'] == 1:
                        if self.first:
                            self.home[0] = team
                        else:
                            self.home[1] = [self.home[1], team]
                    elif Teams.teams[team]['PL'] == 2:
                        if self.first:
                            self.home[1] = team
                        else:
                            self.home[0] = [self.home[0], team]
                self.first = False
            print(self.home)
            self.matches += self.home
        print(self.matches)


Teams = Teams()
Group = Group()
Table = Table()
Knockout = Knockout()
# Table.create_table()
Teams.create_groups()
Group.chose_teams()
Knockout.create_first_round()
