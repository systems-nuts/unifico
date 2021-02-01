
void swap(int v[], int k)
{
	int temp;
	temp = v[k];
	v[k] = v[k + 1];
	v[k + 1] = temp;
}
