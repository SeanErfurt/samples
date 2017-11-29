function [factors]=pFact(x)
    % returns prime factorization of x
    
    factors = containers.Map('KeyType','double','ValueType','int8');
    i = floor(sqrt(x));
    while i ~= 0
        if isprime(i) ~= true %subtract from trial number until prime again
            i = i - 1;
            continue;
        end
        r = x / i;
        if mod(r,1) == 0    %if remainder is an integer
            x = r;
            try
                factors(i) = factors(i) + 1;
            catch
                factors(i) = 1;
            end
            continue;       %try again with same number until not a divisor
        end
        i = i - 1;          %try new number
    end
    if x > 1
        factors(x) = 1;
    end
end