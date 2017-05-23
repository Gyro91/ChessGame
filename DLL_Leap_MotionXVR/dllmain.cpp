// dllmain.cpp : Defines the entry point for the DLL application.
#include "stdafx.h"

#include <windows.h>
#include <stdio.h>
#include <iostream> 
#include <vector> 
#include <string> 
using namespace std;

#define SIZE_BUFF 163
#define Y_OFFSET_RIGHT_HAND 2
#define Y_OFFSET_LEFT_HAND 83
#define FLOAT_SIZE 4
#define START_RIGHT_HAND 1
#define START_LEFT_HAND 82
#define NUM_FLOAT_HAND 81

float x[SIZE_BUFF];
unsigned char* mybuffer;

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
					 )
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}

unsigned char *OpenSharedMemoryBuffer(char *name,int buf_size)
{

	//Apre un nmemory buffer. Se non esiste lo crea.
	HANDLE hMapFile;

	hMapFile = CreateFileMapping(
		INVALID_HANDLE_VALUE,    // use paging file
		NULL,                    // default security
		PAGE_READWRITE,          // read/write access
		0,                       // maximum object size (high-order DWORD)
		buf_size,                // maximum object size (low-order DWORD)
		name);                 // name of mapping object

	if (hMapFile == NULL) {
		printf("Could not create file mapping object.\n");
		return NULL;
	}

	return (unsigned char*)MapViewOfFile(hMapFile,   // handle to map object
		FILE_MAP_ALL_ACCESS, // read/write permission
		0,
		0,
		buf_size);

}


extern "C" __declspec(dllexport) char * __XVR_INIT (void *XVR_pointer)
{
	//New feature from 0141. This function is optional. If you declare it XVR will execute it after loading the DLL
	//You can use it to do initialisation code, as well as to get internal parameters from the XVR virtual machine	
	
	mybuffer = OpenSharedMemoryBuffer("LeapBuffer", (4*SIZE_BUFF));

	return(NULL); 
} 

extern "C" __declspec(dllexport) void get_seq_number(float* out)
{	
	memcpy(out, &mybuffer[0], FLOAT_SIZE);
}

/*
*	ottimizzo dicendo che y del palmo è sempre maggiore di 0
*	la funzione restituisce 1 se la mano è assente
*/
extern "C" __declspec(dllexport) int get_right_hand(float* out)
{	
	float test;
	
	memcpy(&test, &mybuffer[(Y_OFFSET_RIGHT_HAND * FLOAT_SIZE)],
		FLOAT_SIZE);
	
	if (test == 0) 
		return 1;
	
	memcpy(out, &mybuffer[START_RIGHT_HAND * FLOAT_SIZE], 
		(FLOAT_SIZE * NUM_FLOAT_HAND));
	
	return 0;
}

extern "C" __declspec(dllexport) int get_left_hand(float* out)
{	
	float test;
	
	memcpy(&test, &mybuffer[(Y_OFFSET_LEFT_HAND * FLOAT_SIZE)], 
		FLOAT_SIZE);
	
	if (test == 0) 
		return 1;
	
	memcpy(out, &mybuffer[START_LEFT_HAND * FLOAT_SIZE], 
		(FLOAT_SIZE * NUM_FLOAT_HAND));
	
	return 0;
}