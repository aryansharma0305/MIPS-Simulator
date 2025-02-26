
main:
    li $t0, 10
    li $t1, 1       

loop:
    beq $t0, 0, end  
    beq $t0, 1, end  
    mult $t1, $t0
    mflo $t1
    addi $t0, $t0, -1  
    j loop       

end:
    move $v0, $t1    
           
