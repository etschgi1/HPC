// This is the starting points of GPU
RunGPUPowerMethod(N); // burner run!
// Step 1
printf(">>>Step 1\n");
GLOBAL_MEM = true;
for(int i = 0; i < 5; ++i){
  RunGPUPowerMethod(N);
  CleanGPU();
}
GLOBAL_MEM = false;
printf(">>>Step 1 shared mem\n");
for(int i = 0; i < 5; ++i){
  RunGPUPowerMethod(N);
  CleanGPU();
}
// Step 2:
PRINTLEVEL = 0;
int Ns[] = {50, 500, 2000, 4000, 5000};
for(int i = 0; i < 1; ++i){
 N = Ns[i];
 double time = RunGPUPowerMethod(N);
 printf("%d - GPU: run time = %f secs.\n",N,time);
 CleanGPU();
}
Cleanup();