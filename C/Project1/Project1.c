/* Program to assist in the challenge of solving sudoku puzzles.

   Skeleton program written by Alistair Moffat, ammoffat@unimelb.edu.au,
   August 2021, with the intention that it be modified by students
   to add functionality, as required by the assignment specification.

   Student Authorship Declaration:

   (1) I certify that except for the code provided in the initial skeleton
   file, the  program contained in this submission is completely my own
   individual work, except where explicitly noted by further comments that
   provide details otherwise.  I understand that work that has been developed
   by another student, or by me in collaboration with other students, or by
   non-students as a result of request, solicitation, or payment, may not be
   submitted for assessment in this subject.  I understand that submitting for
   assessment work developed by or in collaboration with other students or
   non-students constitutes Academic Misconduct, and may be penalized by mark
   deductions, or by other penalties determined via the University of
   Melbourne Academic Honesty Policy, as described at
   https://academicintegrity.unimelb.edu.au.

   (2) I also certify that I have not provided a copy of this work in either
   softcopy or hardcopy or any other form to any other student, and nor will I
   do so until after the marks are released. I understand that providing my
   work to other students, regardless of my intention or any undertakings made
   to me by that other student, is also Academic Misconduct.

   (3) I further understand that providing a copy of the assignment
   specification to any form of code authoring or assignment tutoring service,
   or drawing the attention of others to such services and code that may have
   been made available via such a service, may be regarded as Student General
   Misconduct (interfering with the teaching activities of the University
   and/or inciting others to commit Academic Misconduct).  I understand that
   an allegation of Student General Misconduct may arise regardless of whether
   or not I personally make use of such solutions or sought benefit from such
   actions.

   Signed by: Jerry Zhao 1272977
   Dated:     10/9/2021

*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

/* these #defines provided as part of the initial skeleton */

#define NDIM 3		/* sudoku dimension, size of each inner square */
#define NDIG (NDIM*NDIM)
			/* total number of values in each row */
#define NGRP 3		/* number of sets each cell is a member of */
#define NSET (NGRP*NDIG)
			/* total number of sets in the sudoku */
#define NCLL (NDIG*NDIG)
			/* total number of cells in the sudoku */

#define ERROR	(-1)	/* error return value from some functions */

/* these global constant arrays provided as part of the initial skeleton,
   you may use them in your code but must not alter them in any way,
   regard them as being completely fixed. They describe the relationships
   between the cells in the sudoku and provide a basis for all of the
   sudoku processing loops */

/* there are 27 different different sets of elements that need to be
   checked against each other, this array converts set numbers to cells,
   that's why its called s2c */
int s2c[NSET][NDIM*NDIM] = {
	/* the first group of nine sets describe the sudoku's rows */
	{  0,  1,  2,  3,  4,  5,  6,  7,  8 },
	{  9, 10, 11, 12, 13, 14, 15, 16, 17 },
	{ 18, 19, 20, 21, 22, 23, 24, 25, 26 },
	{ 27, 28, 29, 30, 31, 32, 33, 34, 35 },
	{ 36, 37, 38, 39, 40, 41, 42, 43, 44 },
	{ 45, 46, 47, 48, 49, 50, 51, 52, 53 },
	{ 54, 55, 56, 57, 58, 59, 60, 61, 62 },
	{ 63, 64, 65, 66, 67, 68, 69, 70, 71 },
	{ 72, 73, 74, 75, 76, 77, 78, 79, 80 },
	/* the second group of nine sets describes the sudoku's columns */
	{  0,  9, 18, 27, 36, 45, 54, 63, 72 },
	{  1, 10, 19, 28, 37, 46, 55, 64, 73 },
	{  2, 11, 20, 29, 38, 47, 56, 65, 74 },
	{  3, 12, 21, 30, 39, 48, 57, 66, 75 },
	{  4, 13, 22, 31, 40, 49, 58, 67, 76 },
	{  5, 14, 23, 32, 41, 50, 59, 68, 77 },
	{  6, 15, 24, 33, 42, 51, 60, 69, 78 },
	{  7, 16, 25, 34, 43, 52, 61, 70, 79 },
	{  8, 17, 26, 35, 44, 53, 62, 71, 80 },
	/* the last group of nine sets describes the inner squares */
	{  0,  1,  2,  9, 10, 11, 18, 19, 20 },
	{  3,  4,  5, 12, 13, 14, 21, 22, 23 },
	{  6,  7,  8, 15, 16, 17, 24, 25, 26 },
	{ 27, 28, 29, 36, 37, 38, 45, 46, 47 },
	{ 30, 31, 32, 39, 40, 41, 48, 49, 50 },
	{ 33, 34, 35, 42, 43, 44, 51, 52, 53 },
	{ 54, 55, 56, 63, 64, 65, 72, 73, 74 },
	{ 57, 58, 59, 66, 67, 68, 75, 76, 77 },
	{ 60, 61, 62, 69, 70, 71, 78, 79, 80 },
};


/* there are 81 cells in a dimension-3 sudoku, and each cell is a
   member of three sets, this array gets filled by the function 
   fill_c2s(), based on the defined contents of the array s2c[][] */
int c2s[NCLL][NGRP];

void
fill_c2s() {
	int s=0, d=0, c;
	for ( ; s<NSET; s++) {
		/* record the first set number each cell is part of */
		for (c=0; c<NDIM*NDIM; c++) {
			c2s[s2c[s][c]][d] = s;
		}
		if ((s+1)%(NGRP*NDIM) == 0) {
			d++;
		}
	}
#if 0
	/* this code available here if you want to see the array
	   cs2[][] that gets created, just change that 0 two lines back
	   to a 1 and recompile */
	for (c=0; c<NCLL; c++) {
		printf("cell %2d: sets ", c);
		for (s=0; s<NGRP; s++) {
			printf("%3d", c2s[c][s]);
		}
		printf("\n");
	}
	printf("\n");
#endif
	return;
}

/* find the row number a cell is in, counting from 1
*/
int
rownum(int c) {
	return 1 + (c/(NDIM*NDIM));
}

/* find the column number a cell is in, counting from 1
*/
int
colnum(int c) {
	return 1 + (c%(NDIM*NDIM));
}

/* find the minor square number a cell is in, counting from 1
*/
int
sqrnum(int c) {
	return 1 + 3*(c/NSET) + (c/NDIM)%NDIM;
}

/* If you wish to add further #defines, put them below this comment,
   then prototypes for the functions that you add

   The only thing you should alter above this line is to complete the
   Authorship Declaration 
*/


/****************************************************************/


/****************************************************************/

/* main program controls all the action
*/
#define NUMS 10
#define SNAME 4 //used for set names: 'row', 'col', 'sqr' + \0

int missing_num(int val[]);
int find_error(int grid[]);
int strategy_one(int grid[]);
void print_board(int grid[]);

int
main(int argc, char *argv[]) {

	/* all done, so pack up bat and ball and head home */
	fill_c2s();
    int val, count;
    int grid[NCLL] = {0};
    count = 0; //counter for grid index

    
    //Stage 1
    while(scanf("%d", &val) == 1){ //take input and store in grid array
    	grid[count] = val;
    	count += 1;      
    }    
    print_board(grid);
 
    //Stage 2
    if(find_error(grid)){ //stop program if sudoku has error
    	return 0;	
    }
    
    //Stage 3  
    while(strategy_one(grid));
    
    printf("\n");
    print_board(grid); //reprint board when applying all possible values
	return 0;
}

int find_error(int grid[]){
	//Stage 2 finds potential errors on the given sudoku board by 
	//tallying instances of numbers 
    int id, toterrors, seterrors, curr_cell, diff_set, first;
    char type[SNAME];
       
    toterrors = seterrors = 0;
    first = 1; //boolean for if first error
    
    for(int i=0; i<NSET; i++){
    	diff_set = 0; //set does not have error yet
    	char numcount[NUMS] = {0}; //array to count instances of numbers
    	
    	for(int j=0; j<NDIG; j++){    		
    		curr_cell = grid[s2c[i][j]];
    	
    		if(curr_cell == 0){ //move to next cell if 0
    			continue;	
    		}   		
    		
			numcount[curr_cell] += 1; //add one to the current num in the array
    		
			if(numcount[curr_cell] > 1){
					diff_set = 1; //set has an error
			}	
    	}
    	
    	if(diff_set == 1){ 
    		seterrors += 1;	
    		
			for(int u=1; u<NUMS; u++){			
				if(numcount[u] > 1){ //more than one instance of number u					
					toterrors += 1;
					
					if(first){ //print new lines for the first error occured
						printf("\n\n");
						first = 0;
					}
					if(i<=8){ 
						id = i+1;
						type[0] = 'r'; type[1] = 'o'; type[2] = 'w';
					
					}
					else if(i<=17){
						id = i-8;
						type[0] = 'c'; type[1] = 'o'; type[2] = 'l';
					}
					else{
						id = i-17;
						type[0] = 's'; type[1] = 'q'; type[2] = 'r';						
					}
					
					type[3] = '\0'; //add end of array character
					printf("set %2d (%s %d): %d instances of %d\n", i, type, 
						id, numcount[u], u);
				}
			}
		}
    }
    if (toterrors > 0){ //if any error has been found
    	printf("\n%d different sets have violations", seterrors);
    	printf("\n%d violations in total\n", toterrors);
    	return 1;	
    }
    return 0;
}

int strategy_one(int grid[]){
	//strategy 1 checks over cells one by one, and finds any possible 
	//solutions and only changes them after iterating all cells
	
    int value, changed, first, tvalues, curr_cell;
    int grid_copy[NCLL]; 
    
    first = 1; //checker for first change within the function call
    changed = 0; 
    
    for (int i=0; i<NCLL; i++){ 
    	//grid copy used to make changes at the end to final grid
    	grid_copy[i]=grid[i]; 
    }
    
    //check over each cell
    for(int i=0; i<NCLL; i++){   	
    	int numcount[11] = {0}; 
    	tvalues = 0; //values taken by other cells in same set
    	
    	if(grid[i] == 0){ 		
    		//check over each set that i belongs to and each set's 
    		//cell values
    		for(int j=0; j<NGRP; j++){		 
    			for(int k=0; k<NDIG; k++){ 
    				curr_cell = grid[s2c[c2s[i][j]][k]];
    	
    				if(curr_cell == 0){ //don't count zeros   			
						continue;
    				}			
					numcount[curr_cell] += 1; //add one to the number in array		  						
    			}
    		}
    	
    		//iterate over numcount array and check how many unique numbers
    		//have occured
    		for (int l=1; l<NUMS; l++){ 
    			if(numcount[l] >= 1){
    				tvalues +=1; 
    			}
    		}
    		  
    		if(tvalues == 8){ //found solution, only one possible answer
    			if(first){ 
    				printf("\n\nstrategy one");
    				first = 0;
    			}  			
    			//print out the unknown cell position and its found value
				int row = c2s[i][0] + 1; 
				int col = c2s[i][1] - 8;
    			value = missing_num(numcount);   			
    			printf("\nrow %d col %d must be %d", row, col, value);
    			grid_copy[i] = value; 
    			changed = 1; //acts as boolean value for while loop in main
    		}
    	}   		
    } 
    
    for (int i=0; i<NCLL; i++){ 
    	grid[i]=grid_copy[i];	
    }
    return changed;
}

void print_board(int grid[]){
	//print every cell and format with horizontal and vertical lines
	int unknowns = 0;
	
	for(int i=0; i<NCLL; i++){
    	if (i%NDIG != 0){ 
    		//add spaces if not first or last number in row
    		printf(" ");	
    	}
    	if (i%NDIG == 0){ 
    		printf("\n");	  		
    	}
    	else if(i%NDIM == 0){
    		printf("| ");	
    	}    	
    	if (i>0 && i%NSET == 0){
    		printf("------+-------+------\n");
    	}    	
    	if(grid[i] == 0){ //replace 0s with .'s and count as unknown
    		unknowns += 1; 
    		printf(".");	    		
    	} 	
    	else{
    		printf("%d", grid[i]);
    	}     	   	
    }
    
    printf("\n\n%2d cells are unknown", unknowns);
    if(unknowns == 0){
    	printf("\n\nta daa!!!\n");	//magic!
    }
}

int missing_num(int val[]){
	//find missing num using the sum of numbers 1-9 and the sum of numbers
	//in given array
	int total = 45; 
	int sum = 0;

	for(int i=1; i<NUMS; i++){
		if(val[i] >= 1){
			sum += i;
		}
	}
	return (total-sum);	
}

//algorithms are fun!!!!
/****************************************************************/