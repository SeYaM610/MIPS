addi $sp, $zero, 0
addi $t0, $zero, 1
addi $sp, $sp, 1
sw   $t0, 0($sp)
addi $t0, $zero, 2
addi $sp, $sp, 1
sw   $t0, 0($sp)
addi $t0, $zero, 1
addi $sp, $sp, 1
sw   $t0, 0($sp)
addi $t0, $zero, 2
addi $sp, $sp, 1
sw   $t0, 0($sp)

addi $t1, $zero, 0
addi $t2, $zero, 0
addi $t4, $zero, 4

loop:
beq $t2, $t4, end
lw   $t3, 0($sp)
addi $sp, $sp, -1
add  $t1, $t1, $t3
addi $t2, $t2, 1
j loop
end: