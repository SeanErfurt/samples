function x=RiemannZeta(s, steps)
	x = 0;
	for n=1:steps
		x = x + n^(-s);
	end
end