/* Program to print and play checker games.

  Skeleton program written by Artem Polyvyanyy, artem.polyvyanyy@unimelb.edu.au,
  September 2021, with the intention that it be modified by students
  to add functionality, as required by the assignment specification.

  Student Authorship Declaration:

  (1) I certify that except for the code provided in the initial skeleton file,
  the program contained in this submission is completely my own individual
  work, except where explicitly noted by further comments that provide details
  otherwise. I understand that work that has been developed by another student,
  or by me in collaboration with other students, or by non-students as a result
  of request, solicitation, or payment, may not be submitted for assessment in
  this subject. I understand that submitting for assessment work developed by
  or in collaboration with other students or non-students constitutes Academic
  Misconduct, and may be penalized by mark deductions, or by other penalties
  determined via the University of Melbourne Academic Honesty Policy, as
  described at https://academicintegrity.unimelb.edu.au.

  (2) I also certify that I have not provided a copy of this work in either
  softcopy or hardcopy or any other form to any other student, and nor will I
  do so until after the marks are released. I understand that providing my work
  to other students, regardless of my intention or any undertakings made to me
  by that other student, is also Academic Misconduct.

  (3) I further understand that providing a copy of the assignment specification
  to any form of code authoring or assignment tutoring service, or drawing the
  attention of others to such services and code that may have been made
  available via such a service, may be regarded as Student General Misconduct
  (interfering with the teaching activities of the University and/or inciting
  others to commit Academic Misconduct). I understand that an allegation of
  Student General Misconduct may arise regardless of whether or not I personally
  make use of such solutions or sought benefit from such actions.

  Signed by: Jerry Zhao 1272977
  Dated:     9/10/2021

*/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <assert.h>
#include <ctype.h>

/* some #define's from my sample solution ------------------------------------*/
#define BOARD_SIZE          8       // board size
#define ROWS_WITH_PIECES    3       // number of initial rows with pieces
#define CELL_EMPTY          '.'     // empty cell character
#define CELL_BPIECE         'b'     // black piece character
#define CELL_WPIECE         'w'     // white piece character
#define CELL_BTOWER         'B'     // black tower character
#define CELL_WTOWER         'W'     // white tower character
#define COST_PIECE          1       // one piece cost
#define COST_TOWER          3       // one tower cost
#define TREE_DEPTH          3       // minimax tree depth
#define COMP_ACTIONS        10      // number of computed actions

/* one type definition from my sample solution -------------------------------*/
typedef unsigned char board_t[BOARD_SIZE][BOARD_SIZE];  // board type

#define INITIAL 10 //for use of malloc
 
typedef struct{
	int col; //is char but treat as an int because used for board array
	int row;
} pos_t;

typedef struct{
	pos_t cur_pos;
	pos_t next_pos;
	char turn;
	char piece_type;
} move_t;

typedef struct node{
	board_t board;
	int cost;
	int noboards;
	move_t move;
	move_t prev_move;
	char turn;
	struct node **children; //array of boards (nodes)
} node_t;

void initialise_board(board_t);
void print_board(board_t);
void change_board(board_t board, move_t *cur_move);
void board_details(board_t board, move_t *cur_move, int turn_count);
void board_copy(board_t board, board_t node_board);
void potential_move(node_t *root, int depth); //go row by row and check pieces for turn and use node_t i believe in u jerry of tomorrow : )
void setup(node_t *root, int *noboards, int cur_size, int depth);
void print_error(int errnum);
void potential_bmove(node_t *root, int *noboards, int cur_size, int depth, char piece);
void potential_wmove(node_t *root, int *noboards, int cur_size, int depth, char piece);
void play_move(board_t board,int *count, int *turn_count, int check);
void check_capture(node_t *root, int* noboards, int cur_size, int depth, int dir);
void free_nodes(node_t *root);
int valid_move(board_t board, move_t *cur_move, char turn, int is_input);
int board_cost(board_t board);
int col_to_num(char input, char cell);
char num_to_col(int input);

int
main(int argc, char *argv[]) {
    // YOUR IMPLEMENTATION OF STAGES 0-2
    board_t board = {{0}};
    char input;
	int count, turn_count;
	count =  0;
	turn_count = 1;
	move_t cur_move;
	cur_move.turn = 'b';
	int numblk, numwht;
	numblk = numwht = 12;
	printf("BOARD SIZE: 8x8");
	printf("\n#BLACK PIECES: %d", numblk);
	printf("\n#WHITE PIECES: %d\n", numwht);	
    initialise_board(board); 
    print_board(board);
 
    while(scanf("%c", &input) == 1){
    	if(input == '-'){ //don't need to worry about the dash
    		continue;	
    	} else if(input == '\n'){
    		
    		if(count == 1 && cur_move.cur_pos.col == 'A'){
    			//only input on line is  'A', play next move
    			play_move(board, &count, &turn_count, 0);
    				
			} else if(count == 1 && cur_move.cur_pos.col == 'P'){
				//only input on line is 'P', play next 10 moves
				for(int i=0; i<COMP_ACTIONS; i++){
					play_move(board, &count, &turn_count, 0);
				}
				//check if the game is won off last move, by checking 
				//potential moves
				play_move(board, &count, &turn_count, 1);
			}				
    		continue;
    	}
    	if(count<2){ 
    		//if count < 2 that means current input is for source cell
    		if(count%2 == 0){
    			cur_move.cur_pos.col = input;	
			} else{
				// subtract '0' to change to char form of that num, which
				// will then store as int under cur_move
				cur_move.cur_pos.row = input - '0';
			}
    	} else if(count<4){
    		if(count%2 == 0){   			
    			cur_move.next_pos.col = input; 
    		} else{
    			cur_move.next_pos.row = input - '0';	
    		}
    	}
    	count += 1;
    	if(count == 4){
			if(valid_move(board, &cur_move, cur_move.turn, 1)){
				change_board(board, &cur_move);
				printf("\n=====================================\n");
				board_details(board, &cur_move, turn_count);
				print_board(board);
				turn_count += 1;
				count = 0;
				if(cur_move.turn == 'b'){ //alternate turns
					cur_move.turn = 'w';	
				} else{
					cur_move.turn = 'b';	
				}
			}	
    	}	
    }
    printf("\n");
    return EXIT_SUCCESS;            // exit program with the success code
}

void play_move(board_t board, int *count, int *turn_count, int check){
	//create root node
	node_t *root = NULL; 
	root = (node_t*) malloc(sizeof(node_t));		
	assert(root);	
	
	//establish turn with turn_count
	if(*turn_count % 2 == 0){
		root->turn = root->move.turn = 'w';
	}  else{
		root->turn = root->move.turn = 'b';	
	}
	
	board_copy(board, root->board);	
	potential_move(root, 0);
	if(check == 1){
		//just checking if there was a potential move so don't play anything
		return;	
	}
	
	if(valid_move(board, &root->move, root->turn, 1)){
		change_board(board, &root->move);
		printf("\n=====================================\n");
		printf("*** ");
		board_details(board, &root->move, *turn_count);
		print_board(board);
		*turn_count += 1;
		*count = 0;
	}
	free_nodes(root); //after playing move free the malloc'd memory	
}

void board_copy(board_t board, board_t node_board){
	//copy first array items to second array
	for(int i=0; i<8; i++){
		for(int j=0; j<8; j++){
			node_board[i][j] = board[i][j];
		}
	}
}

int board_cost(board_t board){
	int bcount, wcount, btcount, wtcount;
	bcount = wcount = btcount = wtcount = 0;
	for(int i=0; i<8; i++){
		for(int j=0; j<8; j++){
			if(board[i][j] == 'w'){
				wcount += 1;	
			} else if(board[i][j] == 'b'){
				bcount += 1;	
			} else if(board[i][j] == 'B'){
				btcount += 1;	
			} else if(board[i][j] == 'W'){
				wtcount += 1;	
			}
		}
	}
	return ((bcount + 3*btcount) - (wcount + 3*wtcount));
}

void potential_move(node_t *root, int depth){
	if(depth == TREE_DEPTH){
		return;	
	}	
	char turn = root->turn;
	int noboards = root->noboards = 0;	
	int big_cost, small_cost; 
	size_t cur_size = INITIAL;
	root->children = (node_t**) malloc(cur_size*sizeof(node_t*));
	assert(root->children);
	
	for(int i=0; i<8; i++){ 
		for(int j=0; j<8; j++){
			//set current position
			//add 1 to the row because valid_move works with rows 1-8
			root->move.cur_pos.row = i+1; 
			root->move.cur_pos.col = j;
			
			if(turn == 'b'){
				if(root->board[i][j] == CELL_BPIECE){		
					potential_bmove(root, &noboards, cur_size, depth,
						CELL_BPIECE);	
				} else if(root->board[i][j] == CELL_BTOWER){
					potential_bmove(root, &noboards, cur_size, depth,
						CELL_BTOWER);	
				}
			} else if(turn == 'w'){
				if(root->board[i][j] == CELL_WPIECE){
					//check potential moves bottom right and left
					potential_wmove(root, &noboards, cur_size, depth, CELL_WPIECE);
				} else if(root->board[i][j] == CELL_WTOWER){
					potential_wmove(root, &noboards, cur_size, depth,
						CELL_WTOWER);
				}			
			}
		}
	}
	root->noboards = noboards;
		
	if(depth == 0){ //check for win
		if(noboards == 0){
			//no possible moves for root board
			if(turn == 'b'){
				printf("\nWHITE WIN!\n");	
				exit(1);
			} else{
				printf("\nBLACK WIN!\n");	
				exit(1);
			}
		}
	}
	//after possible moves for specific board have been found
	if(turn =='b'){
		if(noboards == 0 && depth != 2){
			//if a non-final board doesn't have any moves and is blacks turn
			//then assign INT_MIN so white will choose it
			root->cost = INT_MIN; 
			return; 
		}
		
		for(int k=0; k<noboards; k++){
			if(k==0){
				big_cost = root->children[k]->cost;
				if(depth == 0){
					root->move = root->children[k]->prev_move;	
				}
			} else{
				if(root->children[k]->cost > big_cost){
					big_cost = root->children[k]->cost;
					if(depth == 0){
						root->move = root->children[k]->prev_move;	
					}
				}
			}
		}
		root->cost = big_cost;
	}
	
	else if(turn == 'w'){	
		if(noboards == 0 && depth != 2){
			//assign INT_MAX to the non-final board if white can't move
			root->cost = INT_MAX; 
			return;
		}
		for(int k=0; k<noboards; k++){
			if(k==0){
				small_cost = root->children[k]->cost;
				if(depth == 0){
					root->move = root->children[k]->prev_move;	
				}
			} else{
				if(root->children[k]->cost < small_cost){
					small_cost = root->children[k]->cost;
					if(depth == 0){	
						root->move = root->children[k]->prev_move;	
					}
				}
			}
		}	
		root->cost = small_cost;
	}
}

void free_nodes(node_t *root){
	if(root->children == NULL){
		//no children boards
		free(root);
		root = NULL;
	} else{
		for(int i=0; i<root->noboards; i++){
			free_nodes(root->children[i]);
		}
	}
}
void check_capture(node_t *root, int* noboards, int cur_size, int depth, int dir){
	char piece, tower;
	
	if(root->turn == 'b'){
		piece = CELL_WPIECE; //wanted piece for capture
		tower = CELL_WTOWER; //wanted tower for capture
	} else{
		piece = CELL_BPIECE;
		tower = CELL_BTOWER;
	}
	if(root->board[root->move.next_pos.row -1][root->move.next_pos.col]
			== piece || root->board[root->move.next_pos.row -1]
			[root->move.next_pos.col] == tower){
			
		if(dir == 1){	
			//top right capture
			root->move.next_pos.row = root->move.next_pos.row - 1;
			root->move.next_pos.col = root->move.next_pos.col + 1 ;
			setup(root, noboards, cur_size, depth);		
		} else if(dir == 2){
			//bottom right
			root->move.next_pos.row = root->move.next_pos.row + 1;
			root->move.next_pos.col = root->move.next_pos.col + 1;
			setup(root, noboards, cur_size, depth);	
		} else if(dir == 3){
			//check bottom left capture					
			//if there is a white piece in the next_pos, then try capture
			root->move.next_pos.row = root->move.next_pos.row + 1;
			root->move.next_pos.col = root->move.next_pos.col - 1 ;
			setup(root, noboards, cur_size, depth);		
		} else if(dir == 4){
			//check top left capture
			root->move.next_pos.row = root->move.next_pos.row - 1;
			root->move.next_pos.col = root->move.next_pos.col - 1 ;
			setup(root, noboards, cur_size, depth);		
		}	
	}	
}

void potential_wmove(node_t *root, int* noboards, int cur_size, 
	int depth, char piece){
	if(piece == CELL_WPIECE){
		//check valid moves for bottom right 
		root->move.next_pos.col = root->move.cur_pos.col + 1;
		root->move.next_pos.row = root->move.cur_pos.row + 1;	
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 2);
		
		//bottom left moves
		root->move.next_pos.row = root->move.cur_pos.row + 1;
		root->move.next_pos.col = root->move.cur_pos.col - 1;
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 3);	
	}
	else if(piece == CELL_WTOWER){
		//top right
		root->move.next_pos.row = root->move.cur_pos.row - 1;
		root->move.next_pos.col = root->move.cur_pos.col + 1;
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 1);
			
		//bottom right
		root->move.next_pos.row = root->move.cur_pos.row + 1;
		root->move.next_pos.col = root->move.cur_pos.col + 1;
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 2);

		//bottom left
		root->move.next_pos.col = root->move.cur_pos.col -1;	
		root->move.next_pos.row = root->move.cur_pos.row + 1;
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 3);

		//top left
		root->move.next_pos.col = root->move.cur_pos.col -1;
		root->move.next_pos.row = root->move.cur_pos.row - 1;
		setup(root, noboards, cur_size, depth);	
		check_capture(root, noboards, cur_size, depth, 4);
	}	
}

void potential_bmove(node_t *root, int* noboards, int cur_size, 
	int depth, char piece){
	//set next_pos to top right square
	root->move.next_pos.row = root->move.cur_pos.row - 1;
	root->move.next_pos.col = root->move.cur_pos.col + 1;
	
	if(piece == CELL_BPIECE){
		//check top right and top left space for moves
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 1);

		root->move.next_pos.row = root->move.cur_pos.row -1;
		root->move.next_pos.col = root->move.cur_pos.col - 1;
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 4);	
	}
	
	else if(piece == CELL_BTOWER){
		//top right
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 1);
			
		//bottom right
		root->move.next_pos.col = root->move.cur_pos.col + 1;
		root->move.next_pos.row = root->move.cur_pos.row + 1;
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 2);

		//bottom left
		root->move.next_pos.col = root->move.cur_pos.col -1;
		root->move.next_pos.row = root->move.cur_pos.row + 1;	
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 3);
		
		//top left	
		root->move.next_pos.col = root->move.cur_pos.col - 1;
		root->move.next_pos.row = root->move.cur_pos.row - 1;
		setup(root, noboards, cur_size, depth);
		check_capture(root, noboards, cur_size, depth, 4);
	}		
}

void setup(node_t *root, int* noboards, int cur_size, int depth){
	//validates possible moves and creates children boards
	if(valid_move(root->board, &root->move, root->turn, 0)){
		if(*noboards == cur_size){
			//increase size allocated size of root->children using realloc
			cur_size *= 2;
			root->children = (node_t**)realloc(root->children, 
				cur_size*sizeof(node_t*));
			
			assert(root->children);
			
		}

		root->children[*noboards] = (node_t*) malloc(sizeof(node_t));
		root->children[*noboards]->children = NULL;
		board_copy(root->board, root->children[*noboards]->board);
		change_board(root->children[*noboards]->board, &root->move);
		//keep the move that has been validated so that it can be
		//propogated to root of the board later
		root->children[*noboards]->prev_move = root->move;
		root->move.turn = root->turn;
		
		if(root->turn == 'w'){ //alternate turn for child board
			root->children[*noboards]->turn = 'b';
		}
		else if(root->turn == 'b'){
			root->children[*noboards]->turn = 'w';
		}

		if(depth == 2){ 
			//for all the boards at the bottom of tree, give a board cost
			root->children[*noboards]->cost = board_cost(root->children[*noboards]->board);	
		}
		//recursion, call back potential_move, this time with a child board
		//as the 'root'
		potential_move(root->children[*noboards], depth+1);		
		*noboards += 1;
	
	}
}

void board_details(board_t board, move_t *cur_move, int turn_count){
	char cur_col, next_col;
	if(!isalpha(cur_move->cur_pos.col)){
		
		cur_col = num_to_col(cur_move->cur_pos.col);	
	}
	else{
		cur_col = 	cur_move->cur_pos.col;
	}
	if(!isalpha(cur_move->next_pos.col)){
		next_col = num_to_col(cur_move->next_pos.col);
	}
	else{
		next_col = cur_move->next_pos.col;
	}
	int cur_row = cur_move->cur_pos.row; 
	int next_row = cur_move->next_pos.row;
	int wcount, bcount, wtcount, btcount;
	wcount = bcount = wtcount = btcount = 0;
	
	for(int i=0; i<8; i++){
		for(int j=0; j<8; j++){
			if(board[i][j] == 'w'){
				wcount += 1;	
			}
			else if(board[i][j] == 'b'){
				bcount += 1;	
			}
			else if(board[i][j] == 'B'){
				btcount += 1;	
			}
			else if(board[i][j] == 'W'){
				wtcount += 1;	
			}
		}
	}
	if(cur_move->turn == 'b'){
		printf("BLACK ");
	}
	else{
		printf("WHITE ");	
	}
	printf("ACTION #%d: %c%d-%c%d\n", turn_count, cur_col, cur_row,
		next_col, next_row);
	printf("BOARD COST: %d\n", (bcount + 3*btcount) - (wcount + 3*wtcount));
}

void change_board(board_t board, move_t *cur_move){	
	int cur_col, next_col;
	
	if(isalpha(cur_move->next_pos.col)){
		cur_col = col_to_num(cur_move->cur_pos.col, 's');
	}
	else{
		cur_col = cur_move->cur_pos.col;
	}
	
	int cur_row = cur_move->cur_pos.row - 1; //make rows 0-7 rather than 1-8
	if(isalpha(cur_move->next_pos.col)){
			next_col = col_to_num(cur_move->next_pos.col, 't');
	}
	else{
		next_col = cur_move->next_pos.col;	
	}
	int next_row = cur_move->next_pos.row - 1; 
	char piece = board[cur_row][cur_col];
	int midrow = (cur_row + next_row)/2;
	int midcol = (cur_col + next_col)/2;
	board[cur_row][cur_col] = CELL_EMPTY;
	
	if(cur_move->turn == 'b' && next_row == 0){	
		//promote to tower
		if((next_row == cur_row + 2 || next_row == cur_row - 2) && 
			(next_col == cur_col + 2 || next_col == cur_col  - 2)){
		
			board[midrow][midcol] = CELL_EMPTY;
			board[next_row][next_col] = piece;
		}
		board[next_row][next_col] = CELL_BTOWER;	
	}
	
	else if (cur_move->turn == 'w' && next_row == 7){
		if((next_row == cur_row + 2 || next_row == cur_row - 2) && 
			(next_col == cur_col + 2 || next_col == cur_col  - 2)){

			board[midrow][midcol] = CELL_EMPTY;
			board[next_row][next_col] = piece;
		}
		board[next_row][next_col] = CELL_WTOWER;	
	}
	else if((next_row == cur_row + 2 || next_row == cur_row - 2) && 
		(next_col == cur_col + 2 || next_col == cur_col  - 2)){
			//if capture move
			
			board[midrow][midcol] = CELL_EMPTY;
			board[next_row][next_col] = piece;
		}	
	else{ //normal move
		board[next_row][next_col] = piece;
	}
}


int valid_move(board_t board, move_t *cur_move, char turn, int is_input){	
	int cur_col, next_col;
	if(isalpha(cur_move->next_pos.col)){
		cur_col = col_to_num(cur_move->cur_pos.col, 's');
	}
	else{
		cur_col = cur_move->cur_pos.col;
	}
	
	int cur_row = cur_move->cur_pos.row - 1; //make rows 0-7 rather than 1-8

	if(isalpha(cur_move->next_pos.col)){
			next_col = col_to_num(cur_move->next_pos.col, 't');
	}
	else{
		next_col = cur_move->next_pos.col;	
	}
	int next_row = cur_move->next_pos.row - 1; 
	int mid_col, mid_row; //to check for capture moves
	int errnum = 0;
	char cpiece, ctower; //wanted pieces for capture
	
	mid_col = (cur_col + next_col)/2 ;
	mid_row = (cur_row + next_row)/2;
	if(turn == 'b'){
		cpiece = CELL_WPIECE;
		ctower = CELL_WTOWER;
	}
	else{
		cpiece = CELL_BPIECE;
		ctower = CELL_BTOWER;
	}

	if(cur_row < 0 || cur_row > 7 || cur_col < 0 || cur_col > 7){
		errnum = 1;
	}
	
	else if(next_row < 0 || next_row > 7 || next_col < 0 || next_col > 7){
		errnum = 2;
	}	
	//check cur_pos has a piece
	else if(board[cur_row][cur_col] == CELL_EMPTY){
		errnum = 3;	
	}
	//check next_pos isn't occupied
	else if(board[next_row][next_col] != CELL_EMPTY){
		errnum = 4;	
	}
	else if(board[cur_row][cur_col] == cpiece || 
		board[cur_row][cur_col] == ctower){
		//black trying to move white piece or vice versa
		errnum = 5;	
	}
	
	//check for legal move
	else if(board[cur_row][cur_col] == CELL_WPIECE){
		
		//normal white cell can only move 1 row down and 1 column to
		//left or right
		if((cur_col != next_col+1 && cur_col != next_col-1) || 
			cur_row != next_row - 1){
			
			if(cur_row == next_row - 2 && (cur_col == next_col + 2 || 
				cur_col == next_col - 2)){
				
				if((board[mid_row][mid_col] == CELL_BPIECE || 
					board[mid_row][mid_col] == CELL_BTOWER) && 
					board[next_row][next_col] == CELL_EMPTY){
					//it is capture
					return 1;
				}								
			}
			errnum = 6;	
		}
	}
	else if(board[cur_row][cur_col] == CELL_BPIECE){
		//black pieces can only move top right or top left squares
		if((cur_col != next_col+1 && cur_col != next_col-1) || 
			cur_row != next_row + 1){
		
			//check if it is a capture
			if(cur_row == next_row + 2 && (cur_col == next_col + 2 || 
				cur_col == next_col - 2)){
				
				if((board[mid_row][mid_col] == CELL_WPIECE || 
					board[mid_row][mid_col] == CELL_WTOWER) && 
					board[next_row][next_col] == CELL_EMPTY){
					//it is capture	
					return 1;			
				}								
			}
			errnum = 6;
		}
	}
	else if(board[cur_row][cur_col] == CELL_BTOWER || 
		board[cur_row][cur_col] == CELL_WTOWER){
		
		if((cur_col != next_col + 1 && cur_col != next_col - 1) || 
			(cur_row != next_row + 1 && cur_row != next_row - 1)){
			//look at towers capturing
			
			if((cur_row == next_row + 2 || cur_row == next_row - 2) &&
			(cur_col == next_col + 2 || cur_col == next_col - 2)){
		
				if((board[mid_row][mid_col] == cpiece || board[mid_row]
					[mid_col] == ctower) && board[next_row][next_col] == 
					CELL_EMPTY){					
					
					return 1;
				}
			}	
			errnum = 6;
		}
	}		
	
	if(errnum && is_input){ //if error found and is an input from txt
		print_error(errnum);
		return 0;
	}	
	else if(errnum){
		return 0;	
	}
	return 1;
}

void print_error(int errnum){
	if(errnum == 1){
		printf("\nERROR: Source cell is outside of the board.");	
	}	
	else if(errnum == 2){
		printf("\nERROR: Target cell is outside of the board.");	
	}
	else if(errnum == 3){
		printf("\nERROR: Source cell is empty.");
	}
	else if(errnum == 4){
		printf("\nERROR: Target cell is not empty.");
	}
	else if(errnum == 5){
		printf("\nERROR: Source cell holds opponent's piece/tower.");	
	}
	else{ //errnum 6
		printf("\nERROR: Illegal action.");	
	}
}

int col_to_num(char input, char cell){
	//takes a source cell 's' or target cell 't' and changes column to num
	if(input == 'A'){
		return 0;
	} else if(input == 'B'){
		return 1;	
	} else if(input == 'C'){
		return 2;
	} else if(input == 'D'){
		return 3;	
	} else if(input == 'E'){
		return 4;	
	} else if(input == 'F'){
		return 5;	
	} else if(input == 'G'){
		return 6;	
	} else if(input == 'H'){
		return 7;	
	} else{
		//error check if column is outside of bounds
		if(cell ==	's'){
			printf("\nERROR: Source cell is outside of the board.\n");	
		}
		else{
			printf("\nERROR: Target cell is outside of the board.\n");		
		}
		exit(0);
	}
}

char num_to_col(int input){
	if(input == 0){
		return 'A';	
	} else if(input == 1){
		return 'B';	
	} else if(input == 2){
		return 'C';	
	} else if(input == 3){
		return 'D';	
	} else if(input == 4){
		return 'E';	
	} else if(input == 5){
		return 'F';	
	} else if(input == 6){
		return 'G';	
	} else{
		return 'H';	
	}	
}

void initialise_board(board_t board){	
	for(int i=0; i<BOARD_SIZE; i++){
		if (i==3 || i == 4){ //initially the middle rows are just dots
			for(int k=0; k<BOARD_SIZE; k++){
				board[i][k] = CELL_EMPTY;	
			}
			continue;
		}			
		for(int j=0; j<BOARD_SIZE; j++){
			board[i][j] = CELL_EMPTY;
			//determine where to put pieces based on row i and col j position
			if(i<3 && i%2 == 0){ 			
				if(j%2 != 0){
					board[i][j] = CELL_WPIECE ;
				}
			}
			else if(i<3 && i%2 != 0){
				if(j%2 == 0){
					board[i][j] = CELL_WPIECE ;
				}
			}			
			else if (i>4 && i%2 != 0){
				if(j%2 == 0){
					board[i][j] = CELL_BPIECE ;	
				}
			}
			else{ //i>4 and i%2 == 0
				if(j%2 != 0){
					board[i][j] = CELL_BPIECE ;	
				}
			}		
		}
	}	
}

void
print_board(board_t board){
	printf("     A   B   C   D   E   F   G   H\n");
	for(int i=0; i<BOARD_SIZE; i++){
		printf("   +---+---+---+---+---+---+---+---+\n");	
		printf("%2d", i+1); //print out row num
		
		for(int j=0; j<BOARD_SIZE; j++){
			if(j==0){ //spacings
				printf(" ");	
			}
			printf("| %c ", board[i][j]);
		}	
		printf("|\n");	
	}
	printf("   +---+---+---+---+---+---+---+---+");	
}
//algorithms are fun!!!
/* THE END -------------------------------------------------------------------*/





