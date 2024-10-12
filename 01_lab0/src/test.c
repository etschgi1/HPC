#include <stdio.h>
#include <stdlib.h>


double multsum(double* a,double* b_transposed, size_t offset, size_t size){
    double acc = 0;
    for (size_t i = offset; i < (size+offset); i++)
    {
        acc += a[i]*b_transposed[i];
    }
    return acc;
}

int main(int argc, char *argv[]) {
    double* a = (double*)malloc(sizeof(double)*5);
    double* b = (double*)malloc(sizeof(double)*5);
    for (size_t i = 0; i < 5; i++)
    {
        a[i] = i+1;
        b[i] = i+1;
    }
    double res = multsum(a,b, 0, 5);
    printf("Res: %.2f", res);
    free(a);
    free(b);
    return 0;
}