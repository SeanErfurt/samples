# by Sean Erfurt.
# press F5 for documentation. stats.py is usable as a module.

def mean(nums):
    total = 0
    for num in nums:
        total += num
    return total/len(nums)

def mode(nums):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num,0) + 1
    maxval = max(counts.values())
    mode = 0.0
    for key in counts:
        if counts.get(key, 0) == maxval:
            mode = float(key) 
    return mode


def stDev(nums, xbar):
    sumDevSq = 0
    for num in nums:
        dev = xbar - num
        sumDevSq += dev**2
    return (sumDevSq/(len(nums)-1))**.5


def median(nums):
    nums.sort()
    size = len(nums)
    midPos = int(size/2)
    if size % 2 == 0:
        median = (nums[midPos] + nums[midPos-1])/2
    else:
        median = nums[midPos]
    return median


'''def _stripzeroes(string):
    if string.rfind("0") >= 0: # looks for a zero, prime read
        i = string[string.rfind("0")] # i should equal 0 here
        while i == 0:
              index = string.rfind("0") # gives index of the 0
              string[:index]      # removes 0
              i = string[string.rfind("0")] # updates i
    return string''' # not sure if this works, turns out unnecessary

def stats(nums):
    xbar = mean(nums)
    mod = mode(nums)
    std = stDev(nums, xbar)
    med = median(nums)

    print("\nThe mean is %0.3f"%(xbar))
    print("The median is", med)
    print("The mode is", mod)
    print("The standard deviation is %0.3f"%(std))

if __name__=='__main__':
    print('''This program computes the mean, median, mode, and standard
deviation of a list of numbers. Enter your list in the format:
stats([<list>]) where <list> is numbers separated by commas.\n''')
