function prod=p2e()
	prod = 1;
	P = primes(10000);
	for i=1:1229
		prod = prod * (1 - P(i)^(-2));
	end
end