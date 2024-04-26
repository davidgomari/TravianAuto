import requests
from bs4 import BeautifulSoup
from time import sleep 
from datetime import datetime
from random import randint


# <------------ Configuration ------------>

username = ''
password = ''

# server url example: "http://z10000.warian.ir"
server_url = ''

# you should correct your villages's id.
# put your villages id in order.
villages_url = [
    f'{server_url}/dorf1.php?newdid=12573',
    f'{server_url}/dorf1.php?newdid=23785'
]

# < ---------- Want some help ? ---------->
# For some use cases, please refer to line 509.


# <----------------------------- Initializations ---------------------------------->

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
}
login_data = {
    'ft' : 'a4',
    'user' : f'{username}',
    'pw' : f'{password}',
    'w' : '',
    'login' : '1688767886'
}
input_list_attack_info = ['timestamp', 'timestamp_checksum']
input_list_confirm_attack = ['timestamp', 'timestamp_checksum', 'ckey', 'id', 'a', 'c']
url_attack = f'{server_url}/a2b.php'
login_url = f'{server_url}/login.php'
resource_url = f'{server_url}/dorf1.php'

# 1: wood    2: clay    3: stone    4: wheat
resource_type_i2s = {1 : 'WOOD', 2: 'CLAY', 3: 'STONE', 4 : 'WHEAT'}
village_class2natType = {
    'f3' : '6-4-4-4',
    'f6' : '15-1-1-1'
}
village_natType2rscType = {
    '15-1-1-1' : [4, 4, 1, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2, 4, 4],
    '6-4-4-4' : [1, 4, 1, 3, 2, 2, 3, 4, 4, 3, 3, 4, 4, 1, 4, 2, 1, 2]
}

# this dictionary contains number of available resources
# in the beginning all are set to zero.
# later we will update this dictionary.
resources = {1:0, 2:0, 3:0, 4:0}

# <-------------------------------------------------------------------------------->

# <-------------------- The Core Program -------------------->


# attack a location n times
def attack_n(loc_x, loc_y, session, num_attacks=1):
    
    # Atack Process #
    url_attack = 'http://z1000.warian.ir/a2b.php'
    lezhion_num = 100
    knight_num = 1
    attack_data = {
        'b' : '1',
        't1' : f'{lezhion_num}',
        't4' : '',
        't5' : f'{knight_num}',
        't11' : '',
        'dname' : '',
        'x' : f'{loc_x}',
        'y' : f'{loc_y}',
        'c' : '4',
        's1' : 'ok'
    }
    attack_confirmation_data = {'s1' : 'ok'}

    if num_attacks > 1:
        print(f'Starting {num_attacks} attacks to...\n\tLocation : (x={loc_x}, y={loc_y})\n\tArmies:\n\t\tLezhions={lezhion_num}, Knights={knight_num}\n')

    for i in range(1, num_attacks + 1, 1):

        # Attack Information Page #
        r = session.get(url_attack, headers=headers)
        if num_attacks > 1:
            print(f'Attack {i}/{num_attacks} : Importing Attack Data...')
        soup = BeautifulSoup(r.content, 'html.parser')
        input_list = ['timestamp', 'timestamp_checksum']
        for item in input_list:
            attack_data[item] = soup.find('input', attrs={'name': item})['value']
        r = session.post(url_attack, data=attack_data, headers=headers)
        
        
        # Atack Confirmation Page #
        soup = BeautifulSoup(r.content, 'html.parser')
        if num_attacks > 1:
            print(f'Attack {i}/{num_attacks} : Confirming Attack...')
        input_list = ['timestamp', 'timestamp_checksum', 'ckey', 'id', 'a', 'c']
        for item in input_list:
            attack_confirmation_data[item] = soup.find('input', attrs={'name': item})['value']
        session.post(url_attack, data=attack_confirmation_data, headers=headers)
        
        if num_attacks > 1:
            print(f'Attack {i}/{num_attacks} : The army has been sent to attack...')
            sleep(31)
            print(f'Attack {i}/{num_attacks} : The army is back!\n')
    
    if num_attacks > 1:
        print(f'\ndone!')


# get Current Army status. it returns how many remained and available from each army type
def getCurrentArmy(response):
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # lezh, knight
    army_list = ['line-first column-first large', 'large']
    result = []

    for army_type in army_list:
        tag = soup.find('td', attrs={'class': army_type})
        num = tag.find('a').text
        result.append(int(num))

    return result


# attack a location just once. i just used lezhion and kngight for attacking. you can change this.
def attack(loc_x, loc_y, lezh, knight, session):

    attack_data = {
        'b' : '1',
        't1' : f'{lezh}',
        't4' : '',
        't5' : f'{knight}',
        't11' : '',
        'dname' : '',
        'x' : f'{loc_x}',
        'y' : f'{loc_y}',
        'c' : '4',
        's1' : 'ok'
    }
    attack_confirmation_data = {'s1' : 'ok'}

    # Attack Information Page #
    r = session.get(url_attack, headers=headers)
    lezh_new, knight_new = getCurrentArmy(r)
    # if lezh_new < lezh or knight_new < knight:
    #     print('!!!!!!!!!!!!!!! Not Enouth Army!')
    while lezh_new < lezh or knight_new < knight:
        print('!!!!!!!!!!!!!!! Not Enouth Army!')
        r = session.get(url_attack, headers=headers)
        lezh_new, knight_new = getCurrentArmy(r)
    soup = BeautifulSoup(r.content, 'html.parser')
    for item in input_list_attack_info:
        attack_data[item] = soup.find('input', attrs={'name': item})['value']
    r = session.post(url_attack, data=attack_data, headers=headers)
    
    # Getting Distance Time #
    soup = BeautifulSoup(r.content, 'html.parser')
    server_time_str = soup.find('span', id='tp1').text
    dst_time_str = soup.find('span', id='tp2').text[1:]

    # Atack Confirmation Page #
    for item in input_list_confirm_attack:
        attack_confirmation_data[item] = soup.find('input', attrs={'name': item})['value']
    session.post(url_attack, data=attack_confirmation_data, headers=headers)

    # Src Time, Dst Time, and Distance Time #
    server_time = datetime.strptime(server_time_str, '%H:%M:%S')
    dst_time = datetime.strptime(dst_time_str, '%H:%M:%S')
    dis_time = dst_time - server_time

    # adding dis_time and dst_time to calculate when the army is back to the village
    army_bakc_time = dst_time + dis_time

    return army_bakc_time, server_time


# a function that is used for loging in to account
def login(session):
    r = session.get(login_url, headers=headers)
    if r.status_code == 200:
        print('ok HTTP request!')
    soup = BeautifulSoup(r.content, 'html.parser')
    login_data['login'] = soup.find('input', attrs={'name': 'login'})['value']
    r = session.post(login_url, data=login_data, headers=headers)
    if r.status_code == 200:
        print(f'ok Successful login!\n')


def getServerTime(session):

    r = session.get(resource_url, headers=headers)

    soup = BeautifulSoup(r.content, 'html.parser')

    server_time_str = soup.find('span', id='tp1').text
    server_time = datetime.strptime(server_time_str, '%H:%M:%S')

    return server_time


# one of most favoritable premium feature is farm list.
# you should give the farm locations and say how many times it should attack them.
# also you can change the army type. it just need a little change.
def attack_farm_list(session, num_attacks, locations_list, lezhion_num, knight_num):

    num_locations = len(locations_list)
    print(f'Starting {num_attacks} attacks to {num_locations} Locations...\n')

    # includes:
        # key: location
        # value: army back time
    current_attacks = {}

    # includes:
        # key: location
        # value: number of completed attacks to this location
    loc_num_completed_attacks = {}
    for loc in locations_list:
        loc_num_completed_attacks[f'{loc[0]},{loc[1]}'] = 0

    # number of locations that all num_attacks attacks has been sent to them
    # when it reaches to num_attacks the whole process of this function will finish.
    finished_locations = 0

    num_attacks_sent = 0
    max_num_attacks_sent = num_attacks * num_locations

    # number of seconds to wait until get server time
    # it's used to server not block us.
    # after checking all the location one time we need to rest for wait_sec seconds.
    wait_sec = 2
    wait_count = 0

    # army_is_back_soon = 0
    server_time = getServerTime(session)

    while finished_locations < num_locations:
        # try:
            # army_is_back_soon = 0
            for index, loc in enumerate(locations_list):

                loc_str = f'{loc[0]},{loc[1]}'
                count = loc_num_completed_attacks[loc_str]


                if count < num_attacks and loc_str not in current_attacks:

                    # print('here1')
                    # Attack to this Location
                    army_back_time, server_time = attack(loc[0], loc[1], lezhion_num, knight_num, session)

                    num_attacks_sent += 1
                    print(f'--> Attack To :\t({loc[0]}, {loc[1]}),\t#CmpAtt : {num_attacks_sent}/{max_num_attacks_sent}')
                    current_attacks[loc_str] = army_back_time
                    count += 1
                    loc_num_completed_attacks[loc_str] = count

                    # for last attack set that all attacks of this location have been completed!
                    if count == num_attacks:
                        finished_locations += 1
                        print(f'\n!-- Completed Attacks : {finished_locations}/{num_locations}\n')
                        # we do not specificly say all the attacks of this location is completed.abs
                        # we just state that one other n attacks is completed!

                elif loc_str in current_attacks:
                    
                    # print('here2')
                    # Prepare For New Attack to this Location.
                    army_back_time = current_attacks[loc_str]

                    # if randint(0,100) < 3:
                    # print(f'\n!--wait_count: {wait_count},\t{(army_back_time - server_time).total_seconds() - (wait_sec * wait_count)} ?< {wait_sec}')
                    
                    if (army_back_time - server_time).total_seconds() - (wait_sec * wait_count) < wait_sec:

                        wait_count = 0
                        print(f'!-- Checking Server Time')
                        server_time = getServerTime(session)

                        sleep_time = (army_back_time - server_time).total_seconds()
                        # print(f'!-- Sleep Time : {sleep_time} second(s)')
                        if sleep_time > 0:
                            wait_count += sleep_time/wait_sec
                            # print(f'!-- Sleepping {sleep_time} second(s)')
                            sleep(sleep_time)
                        
                        del current_attacks[loc_str]
                        print(f'<-- Back From :\t({loc[0]}, {loc[1]})')
                
                if index == num_locations - 1:
                    if len(current_attacks) == num_locations:
                        wait_count += 1
                        # print(f'!-- Sleepping {wait_sec} second(s)')
                        sleep(wait_sec)
        # except Exception as e:
        #     print(f'\n{e}')
        #     # print(f'\n!-- Some problem with server Response but Attacks still in progress!\n!-- Don\'t Worry!')
        #     break


# it returns each natural (wood, iron, and..) level.
def get_Naturals_Level(session):
    r = session.get(resource_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    village_map = soup.find('div', id='village_map')
    levels = village_map.find_all('div', class_='level')

    vc = village_map['class'][0] # village Class
    nType = village_class2natType[vc]
    
    naturals_level = {i : 0 for i in range(1, 19, 1)}
    i = 1
    for level in levels:
        # print(int(level.text), resource_type_i2s[village_natType2rscType[nType][i-1]])
        naturals_level[i] = int(level.text)
        i += 1

    return naturals_level, nType


# this should be implemented in future
def getBuildingsLevel(session):
    print()


# before we can order any bulding or resource to get an update, first of all we need to assure we have required resources.
def get_required_resources(soup):

    required_resources_tag = soup.find('div', class_='showCosts').find_all('span')[:4]

    required_resources_list = {}
    for resource in required_resources_tag:
        
        r_type = int(resource.find('img')['class'][0][1])
        r_num = int(resource.text)

        required_resources_list[r_type] = r_num

    return required_resources_list


# this function is used to upgrade a building in town
# return    -1: Not Enouth Resource     0: Busy     1: Upgrade Done
def build_upgrade(session, id, sleep_at_upgrading):
    build_url = f'{server_url}/build.php?id={id}'
    r = session.get(build_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    update_Num_Resources(session, soup)
    reqRsc_dic = get_required_resources(soup=soup)
    Satisfied = 1

    for key, req_rsc in reqRsc_dic.items():
        if req_rsc > resources[key]:
            Satisfied = 0
            # Not Enouth Resource
            return -1 

    if Satisfied:
        upgrade_time_str = soup.find('span', class_='clocks').text[2:]
        upgrade_time_str = '0' + upgrade_time_str
        upgrade_time = datetime.strptime(upgrade_time_str, '%H:%M:%S')
        epoch_time = datetime(1900, 1, 1, 0, 0, 0)
        upgrade_time = (upgrade_time - epoch_time).total_seconds()

        button_tag = soup.find('button', value='Upgrade level')

        if button_tag == None:
            # Maintainance Line is Busy
            return 0

        onclick_value = button_tag['onclick']
        dir_path = onclick_value.split('\'')[1]

        upgrade_url = f'{server_url}/{dir_path}'
        session.get(upgrade_url, headers=headers)
        
        if sleep_at_upgrading:
            print(f'!-- ID={id}, Upgrading')
            
            passed_time = 0
            while 1:

                time_left = upgrade_time - passed_time

                print(f'!-- ID={id}, Time left : {int(time_left)} second(s).')

                time_to_sleep = min(10, time_left)
                sleep(time_to_sleep)

                if time_to_sleep < 10:
                    break

                passed_time += time_to_sleep

            
            print(f'!-- ID={id}, Upgrade done')

        # Upgrade Done
        return 1


# return     1: Upgrade Done or Is Upgrading
def build_upgrade_handler(session, id, sleep_at_upgrading):

    result = 0
    wait_sec = 1
    while result != 1:
        try:
            result = build_upgrade(session, id, sleep_at_upgrading)
            if result != 1:
                if result == -1:
                    print(f'!-- ID={id}, Not enouth resources. waiting {wait_sec} second(s).')
                    sleep(wait_sec)
                else:
                    print(f'!-- ID={id}, Struction line busy. waiting {1+wait_sec} second(s).')
                    sleep(1+wait_sec)
                if wait_sec <= 8:
                    wait_sec *= 2
        except Exception as e:
            print(e)

    if not sleep_at_upgrading:
        print(f'!-- ID={id}, Upgrading')
    return 1


# buildings level is between 19 and 40
# not complete. We need to calculate each building level.
def upgrade_building(session, id, sleep_at_upgrading=1):

    build_upgrade_handler(session, id, sleep_at_upgrading)     

    # curr_level = buildings_level[id]
    # buildings_level[id] += 1
    # buildingT = ...
    # print(f'--> Upgrading {buildingT} (id={id}) from L{curr_level} to L{curr_level+1} is in progress!')


# natural level is between 1 and 18
def upgrade_natural(session, id, naturals_level, nType):

    curr_level = naturals_level[id]
    naturals_level[id] += 1
    rscT = resource_type_i2s[village_natType2rscType[nType][id-1]]
    print(f'\n--> Upgrading {rscT} (id={id}) from L{curr_level} to L{curr_level+1} is sent to Handler!')

    build_upgrade_handler(session, id, sleep_at_upgrading=1) 


def upgrade_village(session, vill_url):
    print()



# with this function we can update the number of resources remained in current village.
def update_Num_Resources(session, soup=None):
    if soup == None:
        r = session.get(resource_url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
    resources_list = soup.find('ul', id='res').find_all('span')[:4]

    for resource in resources_list:

        r_type = int(resource['id'][1])
        r_num = resource.text.split('/')[0]
        if r_num[-1] == 'm':
            r_num = int(r_num[:-1]) * 1000000
        else:
            r_num = int(r_num)

        resources[r_type] = r_num


def upgrade_All_naturals_to_level_x(session, level_x):

    nLevel, nType = get_Naturals_Level(session)

    min_level = 20
    for _, level in nLevel.items():
        min_level = min(level, min_level)

    for level in range(min_level+1, level_x, 1):
        for id in range(1, 19, 1):
            if nLevel[id] < level:
                upgrade_natural(session=session, id=id, naturals_level=nLevel, nType=nType)

# this is used to change current village.
# if vill_num=1 then we go to first village
def change_Village(session, vill_num):
    session.get(villages_url[vill_num-1], headers=headers)



# < -------------------- Use Case 1 --------------------->
# This code logs into the account and upgrades all the resources of the current village to level 11

with requests.Session() as s:
    login(s)
    upgrade_All_naturals_to_level_x(s, 11)


# < -------------------- Use Case 2 --------------------->
# This code logs into the account and runs the farm_list feature. first we should initialize the farm_list with locations
# we want to attack. a location has two numbers specifying it in the map: (x, y).
# also we should say how many times we want to run the farm list feature.
# the army type i have considered is lezhion and knight. you can change it. just a little change in code.

with requests.Session() as s:
    login(s)
    farm_list = [[-28, -26], [-31, -28], [-32, -25], [-27, -26], [-29, -24]]
    attack_farm_list(session=s, num_attacks=3, locations_list=farm_list, lezhion_num=20000, knight_num=8000)
  

# < -------------------- Use Case 3 --------------------->
# In this example, after we log into the account, we change to our second village. Then, we retrieve the level of each resource and print them.
# After that, we obtain the number of available resources left in the second village and print it.

with requests.Session() as s:
    login(s)
    change_Village(s, 2)
    nLevel, nType = get_Naturals_Level(s)
    print(nType, nLevel)
    update_Num_Resources(s)
    print(resources)

# < ------------------------------------------------------>
