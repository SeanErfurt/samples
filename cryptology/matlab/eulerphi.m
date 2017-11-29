function phi=eulerphi(n)
if (n>1 && mod(n,1)==0)
    f=factor(n);
l=length(f);
phi=1;
for i=1:l
    phi=phi*(f(i)-1);
end
elseif (n==1)
    phi=1;
else
    display('Invalid number entered');
end
