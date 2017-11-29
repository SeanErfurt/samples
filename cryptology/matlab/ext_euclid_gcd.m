function [gcd,x,y]=ext_euclid_gcd(a, b)
    % returns gcd (greatest common divisor) and x,y s.t. x*a + y*b = gcd(a,b)
    if (a == 0)
        if (b == 0)
            x = 0;
            y = 0;
            gcd = 0;
            return
        else
            x = 0;
            y = 1;
            gcd = abs(b); %gcd of num and 0 is |num|
            return
        end
    else
        if (b == 0)
            x = 1;
            y = 0;
            gcd = abs(a);
            return
        end
    end
    %if neither 0, continue
    %if badly ordered, swap
    swapped = false;
    if (abs(a) < abs(b))
        var = a;
        a = b;
        b = var;
        swapped = true;
    end
    s = 0;
    t = 1;
    r = b;
    old_s = 1;
    old_t = 0;
    old_r = a;

    while r ~= 0
        quotient = floor(old_r / r);
        rTemp = r;
        r = mod(old_r, r); %modulo remainder function
        old_r = rTemp;
        sTemp = s;
        s = old_s - quotient * sTemp;
        old_s = sTemp;
        tTemp = t;
        t = old_t - quotient * tTemp;
        old_t = tTemp;
    end
    %output gcd, x, and y in appropriate slots
    if (swapped)
        if (old_r < 0)
            %gcd can not be negative, switch all signs if last remainder is.
            y = -1 * old_s;
            x = -1 * old_t;
            gcd = -1 * old_r;
        else
            y = old_s;
            x = old_t;
            gcd = old_r;
        end
    else
        if (old_r < 0)
            x = -1 * old_s;
            y = -1 * old_t;
            gcd = -1 * old_r;
        else
            x = old_s;
            y = old_t;
            gcd = old_r;
        end
    end
end