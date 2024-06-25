def test (): 
    with open('aaa.txt', 'r') as file:
        lines = file.readlines()
        lines = [line.replace('\n','') for line in lines]
        return lines
        
    
az =test()
print(az)