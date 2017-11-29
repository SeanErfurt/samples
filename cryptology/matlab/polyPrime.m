function [indices,pxs,vals]=polyPrime(x)
    indices = zeros(1,x+1);
    pxs = zeros(1,x+1);
    vals = zeros(1,x+1);
    
    for i=0:x
        indices(i+1) = i;
        px = i^4 + 29* i^2 + 101;
        pxs(i+1) = px;
        if px > 0
            vals(i+1) = isprime(px);
        else    %negative numbers are not prime
            vals(i+1) = 0;
    end
end