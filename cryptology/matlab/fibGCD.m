function [result]=fibGCD(n)
    %get gcd for F_n, F_n-1 in Fibonnaci sequence
    %get fibonacci numbers
    fib=zeros(1,n);
    fib(1)=1;
    fib(2)=1;
    k=3;
    while k <= n
        fib(k)=fib(k-2)+fib(k-1);
        k=k+1;
    end
    k = k-1;
    F_n = fib(k)
    F_p = fib(k-1)
    result = ext_euclid_gcd(fib(k),fib(k-1));
end