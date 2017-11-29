function p=probPrime(M,N)
	rng('default');
	R1 = randi([1 M],1,N); % generate N integers in range [1,M]
	R2 = randi([1 M],1,N);
	n = 0; % num successes
	for i=1:N
		if gcd(R1(i), R2(i)) == 1  % coprime
			n = n + 1;
		end
	end
	p = n / N;
end