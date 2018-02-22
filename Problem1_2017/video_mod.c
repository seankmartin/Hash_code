#include <stdio.h>
#include <windows.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

int V, E, R, C, X;
int *video_size;
int **request;
double **cache_score;
int amount_end;
int **results;
int **indexes;
int current;
double alpha, beta, gam, zeta, eta;

//Data structures
typedef struct endpoint {
  int latency_d, num_caches;
  int *latency;
  int *cache_id;
} endpoint;

endpoint **eps;
//functions on data structures

endpoint *make_endpoint(int num_c) {
  endpoint *ep = calloc(1, sizeof(endpoint));
  ep->cache_id = malloc(num_c * sizeof(int));
  ep->latency = malloc(num_c * sizeof(int));
  return ep;
}

void read_file(char *file_name) {
  FILE *file;
  int i, j;
  char temp;
  endpoint *ep;
  int temp_l, temp_c;
  if ((file = fopen(file_name,"r")) == NULL) {
    fprintf(stderr, "ERROR FILE NO OPEN\n");
    exit(-1);
  }

  //Do file reading
  fscanf(file, "%d %d %d %d %d\n", &V, &E, &R, &C, &X);
  fprintf(stderr,"%d %d %d %d %d\n", V, E, R, C, X);

  //Video size
  video_size = malloc(V * sizeof(int));
  for(i = 0; i < V; ++i) {
    fscanf(file, "%d", &video_size[i]);
    //Takes out the space and newline char
    fscanf(file, "%c", &temp);
  }
  fprintf(stderr, "\n");
  //Endpoints
  eps = calloc(E, sizeof(endpoint*));
  for(i = 0; i < E; ++i) {
    fscanf(file, "%d %d\n", &temp_l, &temp_c);
    eps[i] = make_endpoint(temp_c);
    eps[i]->latency_d = temp_l;
    eps[i]->num_caches = temp_c;
    for(j = 0; j < eps[i]->num_caches; ++j){
      fscanf(file, "%d %d\n", &eps[i]->cache_id[j], &eps[i]->latency[j]);
    }
  }

  //Requests
  request = malloc(R * sizeof(int*));
  for(i = 0; i < R; ++i) {
    request[i] = malloc(3 * sizeof(int));
    fscanf(file,"%d %d %d\n", &request[i][0], &request[i][1], &request[i][2]);
  }

  if (fclose(file) == EOF) {
    fprintf(stderr, "ERROR FILE NO CLOSE\n");
    exit(-1);
  }
}

//compute answer
double importance(int size, int ld, int rn) {
  return exp(alpha * (1.0 / (double)size )) * log(beta * ld) * log(gam * rn);
}

double imp_cache(double imp, int lc) {
  return imp * exp( zeta * 1.0 / (double)lc );
}

void compute_importance(int vid_id, endpoint *ep, int num_r) {
  int i;
  double result;
  double orig_imp;
  if(video_size[vid_id] > X) orig_imp = 0;
  else orig_imp = importance(video_size[vid_id], ep->latency_d,  num_r);
  for(i = 0; i < ep->num_caches; ++i) {
    result = imp_cache(orig_imp, ep->latency[i]);
    cache_score[ep->cache_id[i]][vid_id] += result;
  }
}

void find_answer() {
  int i;
  endpoint *ep;
  for(i = 0; i < R; ++i) {
    ep = eps[request[i][1]];
    compute_importance(request[i][0], ep, request[i][2]);
  }
}


int cmpfunc (const void *a, const void *b) {
  return (cache_score[current][*(int*)b]
      - cache_score[current][*(int*)a]);
}

void sort(int n) {
  current = n;
  qsort(indexes[n], V, sizeof(int), cmpfunc);
}

void print_importance() {
  int i, j;
  FILE *file;

  if ((file = fopen("output.txt","w")) == NULL) {
    fprintf(stderr, "ERROR FILE NO OPEN\n");
    exit(-1);
  }
  for(i = 0; i < C; ++i) {
    for(j = 0; j < V; ++j) {
      fprintf(file, "%lf,", cache_score[i][indexes[i][j]]);
    }
    fprintf(file, "\n");
  }
  if (fclose(file) == EOF) {
    fprintf(stderr, "ERROR FILE NO CLOSE\n");
    exit(-1);
  }
}

void put_in_cache() {
  int i, j, k;
  int max;
  amount_end = 0;
  int *amount = calloc(C, sizeof(int));
  int *done = calloc(C, sizeof(int));
  int *count = calloc(C, sizeof(int));
  int finished = 0;
  int fin = 0;
  int temp;
  int first = 1;

  while (!finished) {
    max = 0;
    for(i = 0; i < C; ++i) {
      finished = 1;
      if (!done[i]) {
        if (cache_score[i][indexes[i][0]] > cache_score[max][indexes[max][0]]) max = i;
        if (cache_score[i][indexes[i][0]] == 0) {
          done[i] = 1;
        }
        else finished = 0;
      }
    }
    if(!finished) {
      if(amount[max] + video_size[indexes[max][0]] <= X) {
        amount[max] += video_size[indexes[max][0]];
        if(amount[max] == X) done[max] = 1;
        cache_score[max][indexes[max][0]] = 0;
        results[max][count[max]] = indexes[max][0];
        ++count[max];
        for(k = 0; k < C; ++k) {
          if(!done[k]) {
            cache_score[k][indexes[max][0]] *= eta;
            i = 0;
            fin = 0;
            while(!fin) {
              if(indexes[k][i] == indexes[max][0]) {
                fin = 1;
              }
              else {
                ++i;
              }
            }
            fin = 0;
            while(!fin) {
              fin = 1;
              if(i != V - 1)
                if(cache_score[k][indexes[k][i]] < cache_score[k][indexes[k][i + 1]]) {
                  temp = indexes[k][i];
                  indexes[k][i] = indexes[k][i + 1];
                  indexes[k][i + 1] = temp;
                  ++i;
                  fin = 0;
                }
            }
          }
        }
      }
      else {
        cache_score[max][indexes[max][0]] = 0;
        i = 0;
        fin = 0;
        k = max;
        while(!fin) {
          fin = 1;
          if(i != V - 1)
            if(cache_score[k][indexes[k][i]] < cache_score[k][indexes[k][i + 1]]) {
              temp = indexes[k][i];
              indexes[k][i] = indexes[k][i + 1];
              indexes[k][i + 1] = temp;
              ++i;
              fin = 0;
            }
          }
        }
    }
  }

  for(i = 0; i < C; ++i) {
    if (amount[i] > 0) ++amount_end;
  }
}

void print_answer(char *file_name) {
  FILE *file;
  int len = strlen(file_name);
  int i, j;
  char *output_name = malloc((len + 2) * sizeof(char));
  if(output_name == NULL) {
    fprintf(stderr, "ERROR: malloc failed\n");
    exit(-1);
  }
  memcpy(output_name, file_name, len - 2);
  output_name[len - 2] = 'o';
  output_name[len - 1] = 'u';
  output_name[len] = 't';
  output_name[len + 1] = '\0';

  if ((file = fopen(output_name, "w")) == NULL) {
    fprintf(stderr, "ERROR FILE NO OPEN\n");
    exit(-1);
  }

  //print to file
  fprintf(file, "%d\n", amount_end);

  for(i = 0; i < amount_end; ++i) {
    fprintf(file, "%d ", i);
    for(j = 0; j < V; ++j) {
      if(results[i][j] != -1)
      fprintf(file, "%d ", results[i][j]);
    }
    fprintf(file, "\n");
  }

  if(fclose(file) == EOF) {
    fprintf(stderr, "ERROR: file won't close\n");
    exit(-1);
  }
}

int main(int argc, char** argv) {
  //read file and print answer both will use
  //use argv[1] as the argument
  int i, j;
  read_file(argv[1]);
  alpha = atof(argv[2]);
  beta = atof(argv[3]);
  gam = atof(argv[4]);
  zeta = atof(argv[5]);
  eta = atof(argv[6]);
  if(eta > 1) {
    fprintf(stderr, "Can't increase weight of videos if already appeared\n");
    exit(-1);
  }
  cache_score = malloc(C * sizeof(double*));
  results = malloc(C * sizeof(int*));
  indexes = malloc(C * sizeof(int*));
  for(i = 0; i < C; ++i) {
    cache_score[i] = calloc(V, sizeof(double));
    results[i] = calloc(V, sizeof(int));
    indexes[i] = calloc(V, sizeof(int));
    for(j = 0; j < V; ++j) {
      results[i][j] = -1;
      indexes[i][j] = j;
    }
  }
  find_answer();
  for(i = 0; i < C; ++i) sort(i);
  print_importance();
  put_in_cache();
  print_answer(argv[1]);

  return 0;
}
