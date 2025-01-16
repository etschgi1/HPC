__global__ void Av_ProductGlobal(float* g_MatA, float* g_VecV, float* g_VecW, int N)
{
    int row = blockIdx.x * blockDim.x + threadIdx.x;
    if (row >= N) return;

    float sum = 0.0f;
    for (int col = 0; col < N; col++) {
        sum += g_MatA[row * N + col] * g_VecV[col];
    }
    g_VecW[row] = sum;
}