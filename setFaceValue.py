import requests
import time
import sys

def setFaceValue(url):
    pass

def ethToWei(eth):
    eth = float(eth)
    wei = eth * (10**18)
    return int(wei)

def getFiles(val):
    return {
        'facevaluelimit': (None, str(val)),
    }

def getConfigs(filename):
    with open(filename) as config:
        lines = config.readlines()
        return [line.rstrip('\n') for line in lines]

def parseConfigs(raw_configs):
    values = {}
    nodes = []
    for line in raw_configs:
        if len(line) == 0 or line[0] == '#': continue
        parsed_line = line.split(' ')
        if parsed_line[0] == 'NODE':
            nodes.append({'url':parsed_line[1],'val':parsed_line[2]})
        else:
            values[parsed_line[0]] = parsed_line[1]
    return values, nodes


if __name__ == '__main__':
    
    config_file = sys.argv[1]
    print (config_file)
    
    while True:
        values, nodes = parseConfigs(getConfigs(config_file))
        
        for node in nodes:
            url = node['url']
            if url[-1] != '/': url += '/'
            url += 'setFaceValueLimit'
            print(url)
            
            ethVal = values.get(node['val'])
            weiVal = ethToWei(ethVal)
            print(str(weiVal))
            print(getFiles(weiVal))
            
            try:
                response = requests.post(url, files=getFiles(weiVal))
            except:
                print('error with node: ',node['url'])
                
        refresh = values.get('REFRESH')
        if refresh is None:
            refresh = 60
        else:
            refresh = float(refresh)
        
        print(refresh)
        time.sleep(refresh)

        

