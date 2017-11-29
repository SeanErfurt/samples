function x=CRT(n,b)
	if (length(n) == length(b))
		len = length(n);
		com_mult = 1;  %common multiple of mods            
		for i=1:len
		    com_mult = com_mult*b(i);
		end
		Cur_mod = zeros(1,len);
		for i=1:len
		    Cur_mod(i) = com_mult/b(i); 
		end

		Inv_mod = zeros(1,len);  
		x = 0;
		for i=1:len
		    Inv_mod(i) = invmodn(Cur_mod(i),b(i));
            %x = prev_x + cur_remainder * step_mod * step_remainder
		    x = x+n(i)*Cur_mod(i)*Inv_mod(i);
		end

		x=mod(x,com_mult);
	else
	    display('Length of  and b should be equal');
end