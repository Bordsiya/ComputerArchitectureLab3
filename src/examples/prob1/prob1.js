// Euler 1 problem
int sum = 5
int i = 0
while (i < 1000)
	if (i % 3 == 0)
	    if (i % 5 == 0)
	        sum += 1
	    endif
	endif
	i += 1
endwhile
print(sum, int)