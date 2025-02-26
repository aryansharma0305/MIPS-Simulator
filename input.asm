main:
    addi $t0, $t0, 20      
    addi $t1, $t1, 0        
    addi $t2, $t2, 1        
    addi $t3, $t3, 2        

    beq $t0, 0, end_fib  
    beq $t0, 1, end_fib  

loop_fib:
    beq $t3, $t0, end_fib
    add $t4, $t1, $t2
    move $t1, $t2      
    move $t2, $t4      
    addi $t3, $t3, 1   
    j loop_fib         

end_fib:
    move $v0, $t2    
    nop