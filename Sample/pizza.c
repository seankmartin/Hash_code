#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

int R, C, L, H;

int **read_file(char *file_name) {
  FILE *file;
  char temp;
  int i, j;
  if ((file = fopen(file_name,"r")) == NULL) {
    fprintf(stderr, "ERROR FILE NO OPEN\n");
    exit(-1);
  }
  fscanf(file,"%d %d %d %d\n", &R, &C, &L, &H);
  int **array = malloc(R * sizeof(int*));
  if (array == NULL) fprintf(stderr, "ERROR MEM ERR\n");
  for (i = 0; i < R; ++i) {
    array[i] = malloc(C * sizeof(int));
    if (array[i] == NULL) fprintf(stderr, "ERROR MEM ERR\n");
  }

  for (i = 0; i < R; ++i) {
    for (j = 0; j < C; ++j) {
      fscanf(file, "%c", &temp);
      //1 if Mushroom, 0 if Tomatoe
      array[i][j] = ((temp == 'M')? 1:0);
    }
    fscanf(file, "%c", &temp);
  }
  if (fclose(file) == EOF) {
    fprintf(stderr, "ERROR FILE NO CLOSE\n");
    exit(-1);
  }
  return array;
}

typedef struct pizza_slice {
  int r1, r2, c1, c2;
} pizza_slice;

pizza_slice *make_slice() {
  pizza_slice *s = malloc(sizeof(pizza_slice));
}

typedef struct sliced_pizza {
  int num_slices;
  int capacity;
  pizza_slice** slice;
} sliced_pizza;

sliced_pizza *make_pizza() {
  sliced_pizza *p = malloc(sizeof(sliced_pizza));
  p->num_slices = 0;
  p->capacity = 200;
  p->slice = malloc(p->capacity *sizeof(pizza_slice*));
  return p;
}

void add_to_pizza(pizza_slice *s, sliced_pizza *p) {
  if(p->num_slices == p->capacity) {
    p->capacity *= 2;
    p->slice = realloc(p->slice, p->capacity * sizeof(pizza_slice*));
  }
  p->slice[p->num_slices++] = s;
}

int size(pizza_slice *p) {
  return (p->r2 - p->r1 + 1) * (p->c2 - p->c1 + 1);
};

int find_slice( int *start_x, int *start_y, int min,
                int **pizza, sliced_pizza *p, pizza_slice *s) {
  int i, j;
  int min_x = *start_x;
  int min_y = *start_y;
  int max_x = *start_x;
  int max_y = *start_y;
  int back_up_x;
  int back_up_y;
  int moved_column = 0;
  int count = 0;
  int other_cnt = 0;
  int end_x, end_y;

  //check if single rectangle fits
  if(*start_y != 0){
    for(i = *start_y; i < R; ++i) {
      max_y = i;
      if(pizza[i][*start_x] == min) {
        if(count == 1) {
          back_up_y = i;
          back_up_x = *start_x;
        }
        ++count;
      }
      else ++other_cnt;
      if((count >= L) && (other_cnt >= L)) {
        if(max_y - *start_y > H - 1){
          *start_x = back_up_x;
          *start_y = back_up_y;
          return 0;
        }
        if(R - *start_y <= H) max_y = R - 1;
        s->r1 = min_y;
        s->r2 = max_y;
        s->c1 = min_x;
        s->c2 = max_x;
        if((i + 1) == R) {
          ++*start_x;
          *start_y = 0;
        }
        else {
          *start_y = i + 1;
        }
        return 1;
      }
    }
  }
  //check if full rectangle fits
  min_y = 0;
  if(*start_y != 0){
    *start_x += 1;
    *start_y = 0;
  }
  min_x = *start_x;
  max_x = *start_x;
  count = 0;
  other_cnt = 0;
  max_y = 0;
  for(j = *start_x; j < C; ++j) {
    max_x = j;
    for(i = 0; i < R; ++i) {
      if(i > max_y) max_y = i;
      if(pizza[i][j] == min) {
        if(count == 1) {
          back_up_y = i;
          back_up_x = j;
        }
        ++count;
      }
      else ++other_cnt;
      if((count >= L) && (other_cnt >= L)) {
        if(min_x == max_x) {
          if(R <= H) max_y = R - 1;
          if(R * (C - max_x) <= H) max_x = C - 1;
        }
        s->r1 = min_y;
        s->r2 = max_y;
        s->c1 = min_x;
        s->c2 = max_x;
        if(size(s) > H) {
          *start_x = back_up_x;
          *start_y = back_up_y;
          return 0;
        }
        if((max_y + 1) == R) {
        *start_x = max_x + 1;
        *start_y = 0;
        }
        else {
          *start_x = max_x;
          *start_y = max_y + 1;
        }
        return 1;
      }
    }
  }
  *start_x = j;
  *start_y = i;
  return 0;
}

void compute_slices(int **pizza, sliced_pizza *p, int min) {
  int start_x = 0;
  int start_y = 0;
  int check;
  pizza_slice *s;
  while((start_x <= C - 1) && (start_y <= R - 1)) {
    s = make_slice();
    check = find_slice(&start_x, &start_y, min, pizza, p, s);
    if (check == 1) add_to_pizza(s, p);
  }
}

//This failed
void second_pass(sliced_pizza *p) {
  int **done;
  int finished = 0;
  int i, j, k;
  pizza_slice *s;
  done = calloc(R, sizeof(int*));
  for(i = 0; i < C; ++i) {
    done[i] = calloc(C, sizeof(int));
  }

  for(i = 0; i < p->num_slices; ++i) {
    s = p->slice[i];
    for(j = s->c1; j <= s->c2; ++j) {
      for(k = s->r1; k <= s->r2; ++k) {
        done[k][j] = 1;
      }
    }
  }
  for(i = 0; i < p->num_slices; ++i) {
    s = p->slice[i];
    if(s->c1 == s->c2) {
      j = s->r2;
      finished = 0;
      while((size(s) < H) && (!finished) && (s->r2 < R - 1)){
        if(done[j + 1][s->c1] == 1) finished = 1;
        else {
          ++j;
          s->r2 = j;
        }
      }
    }
  }
  fprintf(stderr, "managed to complete\n");
}

void print_answer(char *ans, sliced_pizza *p){
  FILE *file;
  int i;
  pizza_slice *s;
  int len = strlen(ans);
  char *result = malloc((len + 2) *sizeof(char));
  memcpy(result, ans, len - 2);
  result[len - 2] = 'o';
  result[len - 1] = 'u';
  result[len] = 't';
  result[len + 1] = '\0';

  if ((file = fopen(result, "w")) == NULL) {
    fprintf(stderr, "ERROR FILE NO OPEN\n");
    exit(-1);
  }
  fprintf(file, "%d\n", p->num_slices);
  for(i = 0; i < p->num_slices; ++i){
    s = p->slice[i];
    fprintf(file, "%d %d %d %d\n", s->r1, s->c1, s->r2, s->c2);
  }
}

int main(int argc, char **argv) {
  int i, j;
  int **pizza;
  int pizza_size;
  int count = 0;
  sliced_pizza *p;
  fprintf(stderr, "%s\n", argv[1]);
  pizza = read_file(argv[1]);
  p = make_pizza();
  pizza_size = R * C;
  //determines if the pizza contains less mushrooms or tomatoes.
  int min_is_mushroom = (pizza_size - count < count) ? 0 : 1;
  fprintf(stderr, "mushroom min? %d\n", min_is_mushroom);
  compute_slices(pizza, p, min_is_mushroom);
  second_pass(p);
  print_answer(argv[1], p);
  return 0;
}
