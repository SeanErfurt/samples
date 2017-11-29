function [result] = invmod(a,n)
    % This function calculates the inverse of an element a (mod n)
    % It uses the extended euclidean algorithm

    [gcd,x,q] = ext_euclid_gcd(a,n);
    if (gcd ~= 1)
        disp('No Inverse');
        result = [];
    else
        result = mod(x,n);
    end
end